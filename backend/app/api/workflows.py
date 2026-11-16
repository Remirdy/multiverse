import json
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import WorkflowRecord, WorkflowRunRecord, generate_uuid, get_utc_now
from app.database.session import get_db
from app.execution.engine import ExecutionBudget
from app.workflows.engine import sanitize_imported_workflow, workflow_engine
from app.workflows.templates import NODE_CATALOG

router = APIRouter(prefix="/workflows", tags=["Workflows"])


class WorkflowPayload(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    graph: Dict[str, Any]


class WorkflowRunRequest(BaseModel):
    inputs: Dict[str, Any] = Field(default_factory=dict)
    budget: Optional[ExecutionBudget] = None


class WorkflowApprovalRequest(BaseModel):
    node_id: str
    approved: bool = True


class RetryNodeRequest(BaseModel):
    node_id: str


@router.get("/node-catalog")
async def get_node_catalog():
    return NODE_CATALOG


@router.get("/templates")
async def list_workflow_templates(db: AsyncSession = Depends(get_db)):
    return await workflow_engine.ensure_templates(db)


@router.get("")
async def list_workflows(
    include_templates: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
):
    await workflow_engine.ensure_templates(db)
    stmt = select(WorkflowRecord).order_by(desc(WorkflowRecord.updated_at))
    if not include_templates:
        stmt = select(WorkflowRecord).where(WorkflowRecord.is_template == False).order_by(desc(WorkflowRecord.updated_at))  # noqa: E712
    res = await db.execute(stmt)
    return [workflow_engine.serialize_workflow(w) for w in res.scalars().all()]


@router.post("/validate")
async def validate_workflow_graph(payload: Dict[str, Any]):
    graph = payload.get("graph") if "graph" in payload else payload
    return workflow_engine.validate_graph(graph)


@router.post("/import")
async def import_workflow(payload: Dict[str, Any], save: bool = Query(default=False), db: AsyncSession = Depends(get_db)):
    try:
        sanitized = sanitize_imported_workflow(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if save and sanitized["validation"]["valid"]:
        rec = WorkflowRecord(
            id=generate_uuid(),
            name=sanitized["name"],
            description=sanitized["description"],
            version=1,
            graph_json=json.dumps(sanitized["graph"], ensure_ascii=False),
            is_template=False,
        )
        db.add(rec)
        await db.commit()
        sanitized["saved_workflow"] = workflow_engine.serialize_workflow(rec)
    return sanitized


@router.post("", status_code=201)
async def create_workflow(req: WorkflowPayload, db: AsyncSession = Depends(get_db)):
    validation = workflow_engine.validate_graph(req.graph)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail="; ".join(validation["errors"]))

    rec = WorkflowRecord(
        id=generate_uuid(),
        name=req.name.strip(),
        description=req.description.strip(),
        version=1,
        graph_json=json.dumps(req.graph, ensure_ascii=False),
        is_template=False,
    )
    db.add(rec)
    await db.commit()
    return workflow_engine.serialize_workflow(rec)


@router.get("/runs/{run_id}")
async def get_workflow_run(run_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(WorkflowRunRecord).where(WorkflowRunRecord.id == run_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return workflow_engine.serialize_run(rec)


@router.post("/runs/{run_id}/approve")
async def approve_workflow_run(
    run_id: str,
    req: WorkflowApprovalRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await workflow_engine.approve_run(db, run_id, req.node_id, req.approved)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/runs/{run_id}/retry-node")
async def retry_workflow_node(
    run_id: str,
    req: RetryNodeRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await workflow_engine.retry_node(db, run_id, req.node_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(WorkflowRecord).where(WorkflowRecord.id == workflow_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow_engine.serialize_workflow(rec)


@router.put("/{workflow_id}")
async def update_workflow(workflow_id: str, req: WorkflowPayload, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(WorkflowRecord).where(WorkflowRecord.id == workflow_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    validation = workflow_engine.validate_graph(req.graph)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail="; ".join(validation["errors"]))

    rec.name = req.name.strip()
    rec.description = req.description.strip()
    rec.version = rec.version + 1
    rec.graph_json = json.dumps(req.graph, ensure_ascii=False)
    rec.updated_at = get_utc_now()
    await db.commit()
    return workflow_engine.serialize_workflow(rec)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(WorkflowRecord).where(WorkflowRecord.id == workflow_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    await db.delete(rec)
    await db.commit()
    return None


@router.post("/{workflow_id}/clone", status_code=201)
async def clone_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(WorkflowRecord).where(WorkflowRecord.id == workflow_id))
    src = res.scalar_one_or_none()
    if src is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    clone = WorkflowRecord(
        id=generate_uuid(),
        name=f"{src.name} (Copy)",
        description=src.description,
        version=1,
        graph_json=src.graph_json,
        is_template=False,
    )
    db.add(clone)
    await db.commit()
    return workflow_engine.serialize_workflow(clone)


@router.get("/{workflow_id}/export")
async def export_workflow_json(workflow_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(WorkflowRecord).where(WorkflowRecord.id == workflow_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    data = workflow_engine.serialize_workflow(rec)
    return {
        "schema_version": 1,
        "name": data["name"],
        "description": data["description"],
        "version": data["version"],
        "compatible_node_types": sorted({n.get("type") for n in data["graph"].get("nodes", [])}),
        "graph": data["graph"],
    }


@router.post("/{workflow_id}/runs", status_code=201)
async def run_workflow(workflow_id: str, req: WorkflowRunRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(WorkflowRecord).where(WorkflowRecord.id == workflow_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    try:
        return await workflow_engine.run_workflow(db, rec, inputs=req.inputs, budget=req.budget)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{workflow_id}/runs")
async def list_workflow_runs(workflow_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(WorkflowRunRecord)
        .where(WorkflowRunRecord.workflow_id == workflow_id)
        .order_by(desc(WorkflowRunRecord.created_at))
    )
    return [workflow_engine.serialize_run(r) for r in res.scalars().all()]
