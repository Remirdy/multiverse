import asyncio
import ipaddress
import json
import re
import socket
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.council.service import council_service
from app.database.models import (
    ArtifactRecord,
    StudyNotebookRecord,
    WorkflowRecord,
    WorkflowRunRecord,
    generate_uuid,
    get_utc_now,
)
from app.execution.engine import ExecutionBudget, execution_engine, job_manager
from app.exports.export_service import export_service
from app.services.artifact_service import artifact_service
from app.tools.code_sandbox import execute_python_sandbox
from app.tools.document_tool import parse_document_bytes
from app.tools.math_tool import run_math_operation
from app.workflows.templates import BUILTIN_WORKFLOW_TEMPLATES, NODE_CATALOG


MAX_GRAPH_NODES = 50
MAX_LOOP_ITEMS = 20
_SECRET_KEY_PATTERN = re.compile(r"(api[_-]?key|secret|token|password|authorization)", re.IGNORECASE)


def _node_catalog_map() -> Dict[str, Dict[str, Any]]:
    return {item["type"]: item for item in NODE_CATALOG}


def render_template(template: str, context: Dict[str, Any]) -> str:
    """Safely substitute {{path.to.value}} placeholders without eval."""
    if not template:
        return ""

    def _lookup(path: str) -> str:
        parts = [p.strip() for p in path.split(".") if p.strip()]
        curr: Any = context
        for part in parts:
            if isinstance(curr, dict) and part in curr:
                curr = curr[part]
            else:
                return ""
        if curr is None:
            return ""
        if isinstance(curr, (dict, list)):
            return json.dumps(curr, ensure_ascii=False)
        return str(curr)

    return re.sub(r"\{\{([^{}]{1,80})\}\}", lambda m: _lookup(m.group(1)), str(template))


def eval_condition(config: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Evaluate restricted typed condition operators over workflow state."""
    field_path = str(config.get("field") or "prev.output")
    operator = str(config.get("operator") or "not_empty").lower()
    expected = config.get("value", "")

    actual_str = render_template(f"{{{{{field_path}}}}}", context).strip()
    if operator == "not_empty":
        return bool(actual_str)
    if operator == "empty":
        return not bool(actual_str)
    if operator == "equals":
        return actual_str == str(expected)
    if operator == "not_equals":
        return actual_str != str(expected)
    if operator == "contains":
        return str(expected).lower() in actual_str.lower()
    if operator in {"gt", "gte", "lt", "lte"}:
        try:
            a_num = float(actual_str)
            b_num = float(expected)
        except Exception:
            return False
        if operator == "gt":
            return a_num > b_num
        if operator == "gte":
            return a_num >= b_num
        if operator == "lt":
            return a_num < b_num
        return a_num <= b_num
    return False


def validate_webhook_url(url: str) -> str:
    """Block private, loopback, link-local, metadata, and non-HTTP URLs against SSRF."""
    parsed = urlparse((url or "").strip())
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Webhook URL must use http or https.")
    host = parsed.hostname
    if not host:
        raise ValueError("Webhook URL must specify a host.")
    if host.lower() in {"localhost", "metadata.google.internal", "metadata"}:
        raise ValueError(f"Blocked internal host '{host}' in webhook URL.")

    def _check_ip(addr_str: str):
        ip = ipaddress.ip_address(addr_str)
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise ValueError(f"Blocked non-public IP address '{addr_str}' in webhook URL.")

    try:
        _check_ip(host)
    except ValueError as exc:
        if "Blocked" in str(exc):
            raise
        try:
            infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
            for info in infos:
                sock_ip = info[4][0]
                _check_ip(sock_ip)
        except socket.gaierror:
            pass

    return parsed.geturl()


def sanitize_imported_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate imported workflow JSON, strip secrets, and require explicit owner approval on external/code nodes."""
    if not isinstance(payload, dict):
        raise ValueError("Imported workflow must be a JSON object.")
    raw_graph = payload.get("graph") if "graph" in payload else payload
    if not isinstance(raw_graph, dict):
        raise ValueError("Workflow graph missing or invalid.")
    nodes = raw_graph.get("nodes")
    edges = raw_graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("Workflow graph must contain 'nodes' and 'edges' arrays.")
    if len(nodes) > MAX_GRAPH_NODES:
        raise ValueError(f"Imported workflow exceeds maximum node limit ({MAX_GRAPH_NODES}).")

    def _strip_secrets(obj: Any) -> Any:
        if isinstance(obj, dict):
            cleaned = {}
            for k, v in obj.items():
                if _SECRET_KEY_PATTERN.search(str(k)):
                    cleaned[k] = ""
                else:
                    cleaned[k] = _strip_secrets(v)
            return cleaned
        if isinstance(obj, list):
            return [_strip_secrets(x) for x in obj]
        return obj

    sanitized_nodes = []
    warnings: List[str] = []
    catalog = _node_catalog_map()
    for n in nodes:
        node_copy = json.loads(json.dumps(n))
        cfg = _strip_secrets(node_copy.get("config") or {})
        ntype = node_copy.get("type", "")
        if ntype in {"code", "webhook"}:
            cfg["approved_by_owner"] = False
            warnings.append(f"Imported '{ntype}' node '{node_copy.get('id')}' disabled until owner approves.")
        if ntype not in catalog:
            warnings.append(f"Unsupported node type '{ntype}' on node '{node_copy.get('id')}'.")
        node_copy["config"] = cfg
        sanitized_nodes.append(node_copy)

    graph = {"nodes": sanitized_nodes, "edges": edges}
    validation = workflow_engine.validate_graph(graph)
    return {
        "name": str(payload.get("name") or "Imported Workflow")[:180],
        "description": str(payload.get("description") or "")[:500],
        "graph": graph,
        "validation": validation,
        "import_warnings": warnings,
    }


class WorkflowEngine:
    """Validates, compiles, and executes typed DAG workflows with pause/resume and retry."""

    def __init__(self):
        self._template_lock = asyncio.Lock()

    async def ensure_templates(self, db: AsyncSession) -> List[Dict[str, Any]]:
        async with self._template_lock:
            res = await db.execute(select(WorkflowRecord).where(WorkflowRecord.is_template == True))  # noqa: E712
            existing = {w.id: w for w in res.scalars().all()}
            changed = False
            for tpl in BUILTIN_WORKFLOW_TEMPLATES:
                if tpl["id"] not in existing:
                    db.add(
                        WorkflowRecord(
                            id=tpl["id"],
                            name=tpl["name"],
                            description=tpl["description"],
                            version=1,
                            graph_json=json.dumps(tpl["graph"], ensure_ascii=False),
                            is_template=True,
                        )
                    )
                    changed = True
            if changed:
                await db.commit()
                res = await db.execute(select(WorkflowRecord).where(WorkflowRecord.is_template == True))  # noqa: E712
                existing = {w.id: w for w in res.scalars().all()}
            return [self.serialize_workflow(w) for w in existing.values()]

    def validate_graph(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        nodes = graph.get("nodes") or []
        edges = graph.get("edges") or []
        errors: List[str] = []
        warnings: List[str] = []
        catalog = _node_catalog_map()

        if len(nodes) == 0:
            errors.append("Workflow must contain at least one node.")
        if len(nodes) > MAX_GRAPH_NODES:
            errors.append(f"Workflow exceeds maximum node count ({MAX_GRAPH_NODES}).")

        node_map: Dict[str, Dict[str, Any]] = {}
        for n in nodes:
            nid = n.get("id")
            ntype = n.get("type")
            if not nid:
                errors.append("Found a node without an 'id'.")
                continue
            if nid in node_map:
                errors.append(f"Duplicate node ID '{nid}'.")
                continue
            node_map[nid] = n
            if ntype not in catalog:
                errors.append(f"Unknown node type '{ntype}' on node '{nid}'.")
            elif not catalog[ntype].get("available", True):
                warnings.append(f"Node '{nid}' ({ntype}) is unavailable: {catalog[ntype].get('unavailable_reason')}")

        adj: Dict[str, List[str]] = defaultdict(list)
        indegree: Dict[str, int] = {nid: 0 for nid in node_map}
        for e in edges:
            src = e.get("source")
            tgt = e.get("target")
            if src not in node_map:
                errors.append(f"Edge references missing source node '{src}'.")
                continue
            if tgt not in node_map:
                errors.append(f"Edge references missing target node '{tgt}'.")
                continue
            if src == tgt:
                errors.append(f"Self-loop detected on node '{src}'.")
                continue
            adj[src].append(tgt)
            indegree[tgt] += 1

        # Kahn's topological sort for strict cycle rejection
        q = deque([nid for nid, deg in indegree.items() if deg == 0])
        topo_order: List[str] = []
        while q:
            curr = q.popleft()
            topo_order.append(curr)
            for nxt in adj[curr]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    q.append(nxt)

        if len(topo_order) != len(node_map):
            errors.append("Cycle detected in workflow graph; cycles are rejected outside bounded loop nodes.")

        est_calls = 0
        for n in nodes:
            ntype = n.get("type")
            cfg = n.get("config") or {}
            if ntype == "model":
                est_calls += 1
            elif ntype == "council":
                est_calls += 5
            elif ntype == "loop":
                est_calls += min(int(cfg.get("max_iterations", 5)), MAX_LOOP_ITEMS)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "topological_order": topo_order,
            "estimated_calls": est_calls,
        }

    async def run_workflow(
        self,
        db: AsyncSession,
        workflow: WorkflowRecord,
        inputs: Optional[Dict[str, Any]] = None,
        budget: Optional[ExecutionBudget] = None,
    ) -> Dict[str, Any]:
        graph = json.loads(workflow.graph_json)
        validation = self.validate_graph(graph)
        if not validation["valid"]:
            raise ValueError("; ".join(validation["errors"]))

        effective_budget = execution_engine.resolve_budget(budget)
        job_id = await job_manager.create_job("workflow", budget=effective_budget, db=db)

        run_id = generate_uuid()
        run_rec = WorkflowRunRecord(
            id=run_id,
            workflow_id=workflow.id,
            workflow_version=workflow.version,
            status="running",
            inputs_json=json.dumps(inputs or {}, ensure_ascii=False),
            node_states_json="{}",
            outputs_json="{}",
            usage_json=json.dumps({"calls": 0, "tokens": 0}),
            job_id=job_id,
        )
        db.add(run_rec)
        await db.commit()

        return await self._execute_from_state(db, workflow, run_rec, effective_budget)

    async def _execute_from_state(
        self,
        db: AsyncSession,
        workflow: WorkflowRecord,
        run_rec: WorkflowRunRecord,
        budget: ExecutionBudget,
    ) -> Dict[str, Any]:
        graph = json.loads(workflow.graph_json)
        nodes = {n["id"]: n for n in graph.get("nodes", [])}
        edges = graph.get("edges", [])
        validation = self.validate_graph(graph)
        topo_order: List[str] = validation["topological_order"]

        incoming_edges: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for e in edges:
            incoming_edges[e["target"]].append(e)

        inputs = json.loads(run_rec.inputs_json or "{}")
        node_states: Dict[str, Dict[str, Any]] = json.loads(run_rec.node_states_json or "{}")
        outputs: Dict[str, Any] = json.loads(run_rec.outputs_json or "{}")
        call_counter: Dict[str, int] = json.loads(run_rec.usage_json or '{"calls": 0, "tokens": 0}')

        context: Dict[str, Any] = {"input": inputs}
        for nid, out_val in outputs.items():
            context[nid] = out_val

        # Topological depth grouping so independent branches execute concurrently
        depth: Dict[str, int] = {}
        for nid in topo_order:
            inc = incoming_edges.get(nid, [])
            depth[nid] = 0 if not inc else 1 + max(depth[e["source"]] for e in inc)
        levels: Dict[int, List[str]] = defaultdict(list)
        for nid in topo_order:
            levels[depth[nid]].append(nid)

        paused_for_approval = False
        any_failed = False

        for lvl in sorted(levels.keys()):
            if await job_manager.check_canceled(run_rec.job_id, db=db):
                run_rec.status = "canceled"
                break

            batch_ids = [
                nid for nid in levels[lvl]
                if node_states.get(nid, {}).get("status") not in {"succeeded", "skipped", "rejected"}
            ]
            if not batch_ids:
                continue

            async def _run_node(nid: str) -> Dict[str, Any]:
                node = nodes[nid]
                ntype = node["type"]
                cfg = node.get("config") or {}
                inc = incoming_edges.get(nid, [])

                # Check incoming branch conditions
                active_parents: List[str] = []
                if inc:
                    for edge in inc:
                        src_id = edge["source"]
                        src_state = node_states.get(src_id, {})
                        src_status = src_state.get("status")
                        if src_status == "skipped":
                            continue
                        if src_status == "failed":
                            continue
                        handle = edge.get("sourceHandle")
                        src_out = outputs.get(src_id, {})
                        if nodes[src_id]["type"] == "condition" and handle in {"true", "false"}:
                            cond_val = "true" if src_out.get("result") else "false"
                            if handle != cond_val:
                                continue
                        if nodes[src_id]["type"] == "approval" and handle in {"approved", "rejected"}:
                            appr_val = "approved" if src_out.get("approved") else "rejected"
                            if handle != appr_val:
                                continue
                        active_parents.append(src_id)

                    if not active_parents:
                        return {
                            "nid": nid,
                            "status": "skipped",
                            "output": {"output": ""},
                            "logs": ["Skipped because no incoming branch was active."],
                        }

                # Prepare prev shortcut from first active parent
                local_ctx = dict(context)
                if active_parents:
                    first_out = outputs.get(active_parents[0], {})
                    local_ctx["prev"] = first_out if isinstance(first_out, dict) else {"output": first_out}
                    local_ctx["branches"] = [outputs.get(pid, {}) for pid in active_parents]
                else:
                    local_ctx["prev"] = {"output": inputs.get("text", inputs.get("question", ""))}

                start_ts = get_utc_now().isoformat()
                logs: List[str] = []

                try:
                    if ntype == "input":
                        text_val = inputs.get("text") or inputs.get("question") or cfg.get("default_text", "")
                        out = {"text": text_val, "output": text_val, "data": inputs, "artifact_id": inputs.get("artifact_id")}
                        return {"nid": nid, "status": "succeeded", "output": out, "logs": ["Input loaded."], "started_at": start_ts}

                    if ntype == "prompt_template":
                        rendered = render_template(cfg.get("template", "{{prev.output}}"), local_ctx)
                        return {"nid": nid, "status": "succeeded", "output": {"prompt": rendered, "output": rendered}, "logs": ["Prompt rendered."], "started_at": start_ts}

                    if ntype == "transform":
                        mode = cfg.get("mode", "template")
                        if mode == "uppercase":
                            res_txt = render_template("{{prev.output}}", local_ctx).upper()
                        elif mode == "json_field":
                            field = cfg.get("field", "output")
                            res_txt = render_template(f"{{{{prev.{field}}}}}", local_ctx)
                        else:
                            res_txt = render_template(cfg.get("template", "{{prev.output}}"), local_ctx)
                        return {"nid": nid, "status": "succeeded", "output": {"output": res_txt}, "logs": [f"Transform ({mode}) completed."], "started_at": start_ts}

                    if ntype == "merge":
                        strategy = cfg.get("strategy", "any")
                        if strategy == "all" and len(active_parents) < len(inc):
                            return {"nid": nid, "status": "skipped", "output": {"output": ""}, "logs": ["Merge 'all' skipped due to inactive branch."], "started_at": start_ts}
                        sep = str(cfg.get("separator", "\n\n---\n\n"))
                        parts = []
                        for pid in active_parents:
                            po = outputs.get(pid, {})
                            parts.append(str(po.get("output") or po.get("text") or json.dumps(po, ensure_ascii=False)))
                        merged = sep.join(p for p in parts if p)
                        return {"nid": nid, "status": "succeeded", "output": {"merged": merged, "output": merged}, "logs": [f"Merged {len(parts)} branch(es)."], "started_at": start_ts}

                    if ntype == "condition":
                        passed = eval_condition(cfg, local_ctx)
                        return {"nid": nid, "status": "succeeded", "output": {"result": passed, "branch": "true" if passed else "false", "output": str(passed)}, "logs": [f"Condition evaluated to {passed}."], "started_at": start_ts}

                    if ntype == "model":
                        model_id = cfg.get("model_id", "poolside/laguna-xs-2.1")
                        prompt_str = render_template(cfg.get("prompt_template", "{{prev.output}}"), local_ctx)
                        sys_str = render_template(cfg.get("system_prompt", ""), local_ctx) or None
                        res = await execution_engine.execute_model(
                            model_id=model_id,
                            prompt=prompt_str,
                            system_prompt=sys_str,
                            budget=budget,
                            call_counter=call_counter,
                            job_id=run_rec.job_id,
                        )
                        if res.status != "success":
                            return {"nid": nid, "status": "failed", "output": {"output": "", "error": res.error_message}, "logs": [res.error_message or "Model call failed"], "started_at": start_ts}
                        return {"nid": nid, "status": "succeeded", "output": {"text": res.response_text, "output": res.response_text, "model_id": model_id}, "logs": [f"Model {model_id} succeeded in {res.response_time_ms}ms."], "started_at": start_ts}

                    if ntype == "council":
                        prompt_str = render_template(cfg.get("prompt_template", "{{prev.output}}"), local_ctx)
                        preset_id = cfg.get("preset_id", "general_review")
                        presets = await council_service.ensure_builtin_presets(db)
                        chosen = next((p for p in presets if p["id"] == preset_id), presets[0])
                        cs = await council_service.run_session(
                            db=db,
                            prompt=prompt_str,
                            members=chosen["config"]["members"],
                            chair_model_id=chosen["config"]["chair_model_id"],
                            preset_id=preset_id,
                            review_rounds=int(cfg.get("review_rounds", 1)),
                            budget=budget,
                        )
                        synth_text = (cs.get("synthesis") or {}).get("final_answer", "")
                        return {
                            "nid": nid,
                            "status": "succeeded" if cs["status"] in {"succeeded", "partially_succeeded"} else "failed",
                            "output": {"synthesis": synth_text, "output": synth_text, "session_id": cs["id"], "disagreements": cs.get("disagreements", [])},
                            "logs": [f"Council session {cs['id']} finished ({cs['status']})."],
                            "started_at": start_ts,
                        }

                    if ntype == "loop":
                        raw_items = inputs.get("items")
                        if not isinstance(raw_items, list):
                            raw_items = [ln.strip() for ln in render_template("{{prev.output}}", local_ctx).splitlines() if ln.strip()]
                        max_it = max(1, min(int(cfg.get("max_iterations", 10)), MAX_LOOP_ITEMS))
                        bounded_items = raw_items[:max_it]
                        model_id = cfg.get("model_id", "nvidia/nemotron-3.5-bolt-e4b")
                        results_list = []
                        for item in bounded_items:
                            item_ctx = {**local_ctx, "item": item}
                            p_txt = render_template(cfg.get("prompt_template", "{{item}}"), item_ctx)
                            res = await execution_engine.execute_model(
                                model_id=model_id, prompt=p_txt, budget=budget, call_counter=call_counter, job_id=run_rec.job_id
                            )
                            results_list.append({"item": item, "status": res.status, "output": res.response_text or res.error_message})
                        joined = "\n\n".join(str(r["output"]) for r in results_list)
                        return {"nid": nid, "status": "succeeded", "output": {"results": results_list, "output": joined}, "logs": [f"Processed {len(bounded_items)} item(s)."], "started_at": start_ts}

                    if ntype == "math":
                        expr_str = render_template(cfg.get("expression", "{{prev.output}}"), local_ctx)
                        res = run_math_operation(
                            operation=cfg.get("operation", "simplify"),
                            expression=expr_str,
                            variable=cfg.get("variable", "x"),
                            compare_expression=cfg.get("compare_expression"),
                        )
                        return {"nid": nid, "status": "succeeded", "output": {"result": res.get("result"), "latex": res.get("latex"), "output": str(res.get("result"))}, "logs": ["SymPy evaluation completed."], "started_at": start_ts}

                    if ntype == "code":
                        if cfg.get("approved_by_owner") is False:
                            return {"nid": nid, "status": "failed", "output": {"output": ""}, "logs": ["Code node from imported workflow requires explicit owner approval."], "started_at": start_ts}
                        code_src = render_template(cfg.get("code", ""), local_ctx)
                        sb = execute_python_sandbox(code_src, timeout_seconds=float(cfg.get("timeout", 4.0)))
                        ok = sb["status"] == "succeeded"
                        return {"nid": nid, "status": "succeeded" if ok else "failed", "output": {"stdout": sb["stdout"], "stderr": sb["stderr"], "exit_code": sb["exit_code"], "output": sb["stdout"] or sb["stderr"]}, "logs": [f"Sandbox status: {sb['status']}"], "started_at": start_ts}

                    if ntype == "diagram":
                        raw_body = render_template(cfg.get("source_template", "{{prev.output}}"), local_ctx)
                        diag_type = cfg.get("diagram_type", "flowchart TD")
                        mermaid_txt = raw_body if raw_body.strip().startswith(("flowchart", "graph", "sequenceDiagram", "classDiagram")) else f"{diag_type}\n  A[Input] --> B[Processed]"
                        return {"nid": nid, "status": "succeeded", "output": {"mermaid": mermaid_txt, "output": mermaid_txt}, "logs": ["Structured diagram created."], "started_at": start_ts}

                    if ntype == "pdf_document":
                        art_id = cfg.get("artifact_id") or inputs.get("artifact_id")
                        if not art_id:
                            return {"nid": nid, "status": "failed", "output": {"output": ""}, "logs": ["No document artifact_id provided."], "started_at": start_ts}
                        rec = await artifact_service.get_record(db, art_id)
                        if rec is None:
                            return {"nid": nid, "status": "failed", "output": {"output": ""}, "logs": [f"Artifact '{art_id}' not found."], "started_at": start_ts}
                        parsed = parse_document_bytes(rec.filename, artifact_service.read_bytes(rec), rec.media_type)
                        return {"nid": nid, "status": "succeeded", "output": {"text": parsed["extracted_text"], "questions": parsed["questions"], "chunks": parsed["chunks"], "output": parsed["extracted_text"]}, "logs": [f"Parsed {rec.filename}."], "started_at": start_ts}

                    if ntype == "file":
                        action = cfg.get("action", "write")
                        if action == "read":
                            art_id = cfg.get("artifact_id") or inputs.get("artifact_id")
                            rec = await artifact_service.get_record(db, art_id) if art_id else None
                            if rec is None:
                                return {"nid": nid, "status": "failed", "output": {"output": ""}, "logs": ["Artifact not found."], "started_at": start_ts}
                            txt = artifact_service.read_bytes(rec).decode("utf-8", errors="replace")
                            return {"nid": nid, "status": "succeeded", "output": {"text": txt, "output": txt, "artifact_id": rec.id}, "logs": [f"Read {rec.filename}."], "started_at": start_ts}
                        txt = render_template("{{prev.output}}", local_ctx)
                        art = await artifact_service.save_bytes(db, txt.encode("utf-8"), cfg.get("filename", "workflow_file.txt"), "text/plain; charset=utf-8", origin_type="workflow_run", origin_id=run_rec.id)
                        return {"nid": nid, "status": "succeeded", "output": {"artifact_id": art["id"], "download_url": art["download_url"], "output": art["download_url"]}, "logs": [f"Saved artifact {art['filename']}."], "started_at": start_ts}

                    if ntype == "memory":
                        nb_id = cfg.get("notebook_id") or inputs.get("notebook_id")
                        if not nb_id:
                            return {"nid": nid, "status": "succeeded", "output": {"notes": "", "output": ""}, "logs": ["No notebook_id selected; returning empty memory."], "started_at": start_ts}
                        res = await db.execute(select(StudyNotebookRecord).where(StudyNotebookRecord.id == nb_id))
                        nb = res.scalar_one_or_none()
                        if nb is None:
                            return {"nid": nid, "status": "failed", "output": {"output": ""}, "logs": ["Notebook not found."], "started_at": start_ts}
                        if cfg.get("mode") == "append":
                            nb.notes_markdown = (nb.notes_markdown + "\n\n" + render_template("{{prev.output}}", local_ctx)).strip()
                            await db.commit()
                        return {"nid": nid, "status": "succeeded", "output": {"notes": nb.notes_markdown, "output": nb.notes_markdown}, "logs": [f"Accessed notebook '{nb.title}'."], "started_at": start_ts}

                    if ntype == "approval":
                        existing_state = node_states.get(nid, {})
                        if existing_state.get("decision") == "approved":
                            return {"nid": nid, "status": "succeeded", "output": {"approved": True, "output": render_template("{{prev.output}}", local_ctx)}, "logs": ["Approved by user."], "started_at": start_ts}
                        if existing_state.get("decision") == "rejected":
                            return {"nid": nid, "status": "rejected", "output": {"approved": False, "output": ""}, "logs": ["Rejected by user."], "started_at": start_ts}
                        return {"nid": nid, "status": "waiting_for_approval", "output": {"summary": render_template("{{prev.output}}", local_ctx)[:1000], "message": cfg.get("message", "Approval required.")}, "logs": ["Paused awaiting user approval."], "started_at": start_ts}

                    if ntype == "webhook":
                        if cfg.get("approved_by_owner") is False:
                            return {"nid": nid, "status": "failed", "output": {"output": ""}, "logs": ["Imported webhook requires owner approval."], "started_at": start_ts}
                        existing_state = node_states.get(nid, {})
                        if cfg.get("require_approval", True) and existing_state.get("decision") != "approved":
                            if existing_state.get("decision") == "rejected":
                                return {"nid": nid, "status": "rejected", "output": {"output": ""}, "logs": ["Webhook call rejected by user."], "started_at": start_ts}
                            return {"nid": nid, "status": "waiting_for_approval", "output": {"url": cfg.get("url", ""), "payload": render_template("{{prev.output}}", local_ctx)[:500]}, "logs": ["Webhook call awaiting approval."], "started_at": start_ts}
                        safe_url = validate_webhook_url(cfg.get("url", ""))
                        method = str(cfg.get("method", "POST")).upper()
                        body_txt = render_template(cfg.get("body_template", "{{prev.output}}"), local_ctx)
                        async with httpx.AsyncClient(timeout=8.0, follow_redirects=False) as client:
                            resp = await client.request(method, safe_url, json={"payload": body_txt})
                        return {"nid": nid, "status": "succeeded" if 200 <= resp.status_code < 400 else "failed", "output": {"status_code": resp.status_code, "body": resp.text[:262144], "output": resp.text[:4096]}, "logs": [f"HTTP {method} returned {resp.status_code}."], "started_at": start_ts}

                    if ntype == "export":
                        fmt = cfg.get("format", "md")
                        title = cfg.get("title", workflow.name)
                        body = render_template(cfg.get("content_template", "{{prev.output}}"), local_ctx)
                        rendered = export_service.generate(
                            fmt=fmt,
                            title=title,
                            sections=[{"heading": title, "body": body}],
                            json_payload={"title": title, "content": body, "inputs": inputs},
                        )
                        art = await artifact_service.save_bytes(
                            db=db,
                            data=rendered["bytes"],
                            filename=f"workflow_{run_rec.id[:8]}.{rendered['ext']}",
                            media_type=rendered["media_type"],
                            origin_type="workflow_export",
                            origin_id=run_rec.id,
                        )
                        return {"nid": nid, "status": "succeeded", "output": {"artifact_id": art["id"], "download_url": art["download_url"], "output": art["download_url"]}, "logs": [f"Exported {art['filename']}."], "started_at": start_ts}

                    return {"nid": nid, "status": "failed", "output": {"output": ""}, "logs": [f"Node type '{ntype}' is unavailable or not configured."], "started_at": start_ts}
                except Exception as exc:
                    return {"nid": nid, "status": "failed", "output": {"output": ""}, "logs": [f"Node error: {str(exc)}"], "started_at": start_ts}

            batch_results = await asyncio.gather(*[_run_node(nid) for nid in batch_ids])
            for res in batch_results:
                nid = res["nid"]
                node_states[nid] = {
                    **(node_states.get(nid) or {}),
                    "status": res["status"],
                    "logs": res["logs"],
                    "started_at": res.get("started_at"),
                    "finished_at": get_utc_now().isoformat(),
                }
                outputs[nid] = res["output"]
                context[nid] = res["output"]
                if res["status"] == "waiting_for_approval":
                    paused_for_approval = True
                if res["status"] == "failed":
                    any_failed = True

                if run_rec.job_id:
                    await job_manager.append_event(
                        run_rec.job_id,
                        "node_completed",
                        {"node_id": nid, "status": res["status"], "logs": res["logs"]},
                        status="running",
                        progress_phase=f"node:{nid}",
                        usage=call_counter,
                        db=db,
                    )

            if paused_for_approval:
                break

        if run_rec.status != "canceled":
            if paused_for_approval:
                run_rec.status = "waiting_for_approval"
            elif any_failed:
                run_rec.status = "partially_succeeded"
            else:
                run_rec.status = "succeeded"

        run_rec.node_states_json = json.dumps(node_states, ensure_ascii=False)
        run_rec.outputs_json = json.dumps(outputs, ensure_ascii=False)
        run_rec.usage_json = json.dumps(call_counter, ensure_ascii=False)
        run_rec.updated_at = get_utc_now()
        await db.commit()

        if run_rec.job_id:
            await job_manager.append_event(
                run_rec.job_id,
                "workflow_status",
                {"run_id": run_rec.id, "status": run_rec.status},
                status=run_rec.status,
                progress_phase=run_rec.status,
                usage=call_counter,
                result={"run_id": run_rec.id},
                db=db,
            )

        return self.serialize_run(run_rec)

    async def approve_run(
        self,
        db: AsyncSession,
        run_id: str,
        node_id: str,
        approved: bool,
    ) -> Dict[str, Any]:
        res = await db.execute(select(WorkflowRunRecord).where(WorkflowRunRecord.id == run_id))
        run_rec = res.scalar_one_or_none()
        if run_rec is None:
            raise ValueError("Workflow run not found.")
        wf_res = await db.execute(select(WorkflowRecord).where(WorkflowRecord.id == run_rec.workflow_id))
        workflow = wf_res.scalar_one_or_none()
        if workflow is None:
            raise ValueError("Parent workflow not found.")

        node_states = json.loads(run_rec.node_states_json or "{}")
        if node_id not in node_states or node_states[node_id].get("status") != "waiting_for_approval":
            raise ValueError(f"Node '{node_id}' is not waiting for approval.")

        node_states[node_id]["decision"] = "approved" if approved else "rejected"
        node_states[node_id]["status"] = "pending_resume"
        run_rec.node_states_json = json.dumps(node_states, ensure_ascii=False)
        run_rec.status = "running"
        await db.commit()
        return await self._execute_from_state(db, workflow, run_rec, execution_engine.resolve_budget(None))

    async def retry_node(self, db: AsyncSession, run_id: str, node_id: str) -> Dict[str, Any]:
        res = await db.execute(select(WorkflowRunRecord).where(WorkflowRunRecord.id == run_id))
        run_rec = res.scalar_one_or_none()
        if run_rec is None:
            raise ValueError("Workflow run not found.")
        wf_res = await db.execute(select(WorkflowRecord).where(WorkflowRecord.id == run_rec.workflow_id))
        workflow = wf_res.scalar_one_or_none()
        if workflow is None:
            raise ValueError("Parent workflow not found.")

        graph = json.loads(workflow.graph_json)
        adj: Dict[str, List[str]] = defaultdict(list)
        for e in graph.get("edges", []):
            adj[e["source"]].append(e["target"])

        # Invalidate target node and all downstream dependents
        to_reset: Set[str] = set()
        queue = deque([node_id])
        while queue:
            curr = queue.popleft()
            if curr in to_reset:
                continue
            to_reset.add(curr)
            for nxt in adj[curr]:
                queue.append(nxt)

        node_states = json.loads(run_rec.node_states_json or "{}")
        outputs = json.loads(run_rec.outputs_json or "{}")
        for nid in to_reset:
            node_states.pop(nid, None)
            outputs.pop(nid, None)

        run_rec.node_states_json = json.dumps(node_states, ensure_ascii=False)
        run_rec.outputs_json = json.dumps(outputs, ensure_ascii=False)
        run_rec.status = "running"
        await db.commit()
        return await self._execute_from_state(db, workflow, run_rec, execution_engine.resolve_budget(None))

    @staticmethod
    def serialize_workflow(rec: WorkflowRecord) -> Dict[str, Any]:
        return {
            "id": rec.id,
            "name": rec.name,
            "description": rec.description,
            "version": rec.version,
            "graph": json.loads(rec.graph_json) if rec.graph_json else {"nodes": [], "edges": []},
            "is_template": rec.is_template,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
            "updated_at": rec.updated_at.isoformat() if rec.updated_at else None,
        }

    @staticmethod
    def serialize_run(rec: WorkflowRunRecord) -> Dict[str, Any]:
        return {
            "id": rec.id,
            "workflow_id": rec.workflow_id,
            "workflow_version": rec.workflow_version,
            "status": rec.status,
            "inputs": json.loads(rec.inputs_json) if rec.inputs_json else {},
            "node_states": json.loads(rec.node_states_json) if rec.node_states_json else {},
            "outputs": json.loads(rec.outputs_json) if rec.outputs_json else {},
            "usage": json.loads(rec.usage_json) if rec.usage_json else {},
            "job_id": rec.job_id,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
            "updated_at": rec.updated_at.isoformat() if rec.updated_at else None,
        }


workflow_engine = WorkflowEngine()
