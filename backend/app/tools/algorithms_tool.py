import ast
import heapq
from collections import deque
from typing import Any, Dict, List, Optional


def run_algorithm_trace(
    algorithm: str,
    array: Optional[List[int]] = None,
    target: Optional[int] = None,
    graph: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    start_node: Optional[str] = None,
) -> Dict[str, Any]:
    """Produce deterministic, step-by-step execution traces for sorting, searching, and graph algorithms."""
    alg = algorithm.strip().lower()
    arr = list(array if array is not None else [38, 27, 43, 3, 9, 82, 10])
    if len(arr) > 40:
        raise ValueError("Input array length is capped at 40 elements for interactive traces.")

    steps: List[Dict[str, Any]] = []
    comparisons = 0
    swaps = 0

    if alg == "bubble_sort":
        a = list(arr)
        n = len(a)
        sorted_idx: List[int] = []
        for i in range(n):
            for j in range(0, n - i - 1):
                comparisons += 1
                swapped_pair: List[int] = []
                if a[j] > a[j + 1]:
                    a[j], a[j + 1] = a[j + 1], a[j]
                    swaps += 1
                    swapped_pair = [j, j + 1]
                steps.append({
                    "step": len(steps) + 1,
                    "array": list(a),
                    "comparing": [j, j + 1],
                    "swapped": swapped_pair,
                    "sorted": list(sorted_idx),
                    "description": f"Compare index {j} ({a[j]}) and {j+1} ({a[j+1]})",
                })
            sorted_idx.append(n - 1 - i)
        return {"algorithm": "bubble_sort", "complexity": "Time: O(n^2), Space: O(1)", "comparisons": comparisons, "swaps": swaps, "final_array": a, "steps": steps}

    if alg == "selection_sort":
        a = list(arr)
        n = len(a)
        sorted_idx = []
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                comparisons += 1
                if a[j] < a[min_idx]:
                    min_idx = j
                steps.append({
                    "step": len(steps) + 1,
                    "array": list(a),
                    "comparing": [min_idx, j],
                    "swapped": [],
                    "sorted": list(sorted_idx),
                    "description": f"Scan minimum at index {min_idx} ({a[min_idx]}) vs {j} ({a[j]})",
                })
            if min_idx != i:
                a[i], a[min_idx] = a[min_idx], a[i]
                swaps += 1
            sorted_idx.append(i)
            steps.append({
                "step": len(steps) + 1,
                "array": list(a),
                "comparing": [],
                "swapped": [i, min_idx] if min_idx != i else [],
                "sorted": list(sorted_idx),
                "description": f"Place minimum {a[i]} at position {i}",
            })
        return {"algorithm": "selection_sort", "complexity": "Time: O(n^2), Space: O(1)", "comparisons": comparisons, "swaps": swaps, "final_array": a, "steps": steps}

    if alg == "insertion_sort":
        a = list(arr)
        for i in range(1, len(a)):
            key = a[i]
            j = i - 1
            while j >= 0 and a[j] > key:
                comparisons += 1
                a[j + 1] = a[j]
                swaps += 1
                steps.append({
                    "step": len(steps) + 1,
                    "array": list(a),
                    "comparing": [j, j + 1],
                    "swapped": [j, j + 1],
                    "sorted": list(range(i)),
                    "description": f"Shift {a[j]} right to insert {key}",
                })
                j -= 1
            if j >= 0:
                comparisons += 1
            a[j + 1] = key
            steps.append({
                "step": len(steps) + 1,
                "array": list(a),
                "comparing": [j + 1],
                "swapped": [],
                "sorted": list(range(i + 1)),
                "description": f"Insert key {key} at index {j + 1}",
            })
        return {"algorithm": "insertion_sort", "complexity": "Time: O(n^2), Space: O(1)", "comparisons": comparisons, "swaps": swaps, "final_array": a, "steps": steps}

    if alg == "merge_sort":
        a = list(arr)

        def _merge_sort(lo: int, hi: int):
            nonlocal comparisons, swaps
            if lo >= hi:
                return
            mid = (lo + hi) // 2
            _merge_sort(lo, mid)
            _merge_sort(mid + 1, hi)
            left = a[lo : mid + 1]
            right = a[mid + 1 : hi + 1]
            i = j = 0
            k = lo
            while i < len(left) and j < len(right):
                comparisons += 1
                if left[i] <= right[j]:
                    a[k] = left[i]
                    i += 1
                else:
                    a[k] = right[j]
                    j += 1
                    swaps += 1
                steps.append({
                    "step": len(steps) + 1,
                    "array": list(a),
                    "comparing": [k],
                    "swapped": [],
                    "sorted": [],
                    "description": f"Merge range [{lo}..{hi}] placed {a[k]} at index {k}",
                })
                k += 1
            while i < len(left):
                a[k] = left[i]
                i += 1
                k += 1
            while j < len(right):
                a[k] = right[j]
                j += 1
                k += 1
            steps.append({
                "step": len(steps) + 1,
                "array": list(a),
                "comparing": list(range(lo, hi + 1)),
                "swapped": [],
                "sorted": list(range(lo, hi + 1)) if lo == 0 and hi == len(a) - 1 else [],
                "description": f"Merged slice [{lo}..{hi}]",
            })

        _merge_sort(0, len(a) - 1)
        return {"algorithm": "merge_sort", "complexity": "Time: O(n log n), Space: O(n)", "comparisons": comparisons, "swaps": swaps, "final_array": a, "steps": steps}

    if alg == "quick_sort":
        a = list(arr)

        def _qs(lo: int, hi: int):
            nonlocal comparisons, swaps
            if lo >= hi:
                return
            pivot = a[hi]
            i = lo
            for j in range(lo, hi):
                comparisons += 1
                if a[j] <= pivot:
                    a[i], a[j] = a[j], a[i]
                    swaps += 1
                    steps.append({
                        "step": len(steps) + 1,
                        "array": list(a),
                        "comparing": [j, hi],
                        "swapped": [i, j] if i != j else [],
                        "sorted": [],
                        "description": f"Partition around pivot {pivot}: place {a[i]} at {i}",
                    })
                    i += 1
            a[i], a[hi] = a[hi], a[i]
            swaps += 1
            steps.append({
                "step": len(steps) + 1,
                "array": list(a),
                "comparing": [i],
                "swapped": [i, hi],
                "sorted": [i],
                "description": f"Pivot {pivot} fixed at index {i}",
            })
            _qs(lo, i - 1)
            _qs(i + 1, hi)

        _qs(0, len(a) - 1)
        return {"algorithm": "quick_sort", "complexity": "Avg O(n log n), Worst O(n^2)", "comparisons": comparisons, "swaps": swaps, "final_array": a, "steps": steps}

    if alg == "linear_search":
        tgt = target if target is not None else arr[len(arr) // 2]
        found_idx = -1
        for i, val in enumerate(arr):
            comparisons += 1
            matched = val == tgt
            steps.append({
                "step": len(steps) + 1,
                "array": list(arr),
                "comparing": [i],
                "swapped": [],
                "sorted": [i] if matched else [],
                "description": f"Check index {i} ({val}) == {tgt}: {matched}",
            })
            if matched:
                found_idx = i
                break
        return {"algorithm": "linear_search", "target": tgt, "found_index": found_idx, "comparisons": comparisons, "complexity": "Time: O(n), Space: O(1)", "steps": steps}

    if alg == "binary_search":
        sorted_arr = sorted(arr)
        tgt = target if target is not None else sorted_arr[len(sorted_arr) // 2]
        lo, hi = 0, len(sorted_arr) - 1
        found_idx = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            comparisons += 1
            steps.append({
                "step": len(steps) + 1,
                "array": list(sorted_arr),
                "comparing": [lo, mid, hi],
                "swapped": [],
                "sorted": [mid] if sorted_arr[mid] == tgt else [],
                "description": f"Window [{lo}..{hi}], mid={mid} ({sorted_arr[mid]}) vs target {tgt}",
            })
            if sorted_arr[mid] == tgt:
                found_idx = mid
                break
            if sorted_arr[mid] < tgt:
                lo = mid + 1
            else:
                hi = mid - 1
        return {
            "algorithm": "binary_search",
            "sorted_input": sorted_arr,
            "target": tgt,
            "found_index": found_idx,
            "comparisons": comparisons,
            "complexity": "Time: O(log n), Space: O(1)",
            "steps": steps,
        }

    if alg in {"bfs", "dfs", "dijkstra"}:
        adj = graph or {
            "A": [{"to": "B", "weight": 4}, {"to": "C", "weight": 2}],
            "B": [{"to": "C", "weight": 5}, {"to": "D", "weight": 10}],
            "C": [{"to": "E", "weight": 3}],
            "D": [{"to": "F", "weight": 11}],
            "E": [{"to": "D", "weight": 4}],
            "F": [],
        }
        start = start_node or next(iter(adj.keys()))
        if start not in adj:
            raise ValueError(f"Start node '{start}' does not exist in graph.")

        if alg == "bfs":
            visited: List[str] = []
            seen = {start}
            q = deque([start])
            while q:
                curr = q.popleft()
                visited.append(curr)
                for edge in adj.get(curr, []):
                    nxt = edge["to"]
                    if nxt not in seen:
                        seen.add(nxt)
                        q.append(nxt)
                steps.append({"step": len(steps) + 1, "current": curr, "visited": list(visited), "frontier": list(q)})
            return {"algorithm": "bfs", "order": visited, "complexity": "Time: O(V + E)", "steps": steps}

        if alg == "dfs":
            visited = []
            seen = set()
            stack = [start]
            while stack:
                curr = stack.pop()
                if curr in seen:
                    continue
                seen.add(curr)
                visited.append(curr)
                for edge in reversed(adj.get(curr, [])):
                    if edge["to"] not in seen:
                        stack.append(edge["to"])
                steps.append({"step": len(steps) + 1, "current": curr, "visited": list(visited), "frontier": list(stack)})
            return {"algorithm": "dfs", "order": visited, "complexity": "Time: O(V + E)", "steps": steps}

        # Dijkstra with strict non-negative edge validation
        for u, edges in adj.items():
            for edge in edges:
                if float(edge.get("weight", 1)) < 0:
                    raise ValueError(f"Dijkstra requires non-negative edge weights (found negative weight from {u}).")

        dist: Dict[str, float] = {node: float("inf") for node in adj}
        for edges in adj.values():
            for e in edges:
                dist.setdefault(e["to"], float("inf"))
        dist[start] = 0.0
        parent: Dict[str, Optional[str]] = {start: None}
        pq: List[Any] = [(0.0, start)]
        visited_set = set()
        while pq:
            d, u = heapq.heappop(pq)
            if u in visited_set:
                continue
            visited_set.add(u)
            for edge in adj.get(u, []):
                v = edge["to"]
                w = float(edge.get("weight", 1))
                if d + w < dist[v]:
                    dist[v] = d + w
                    parent[v] = u
                    heapq.heappush(pq, (dist[v], v))
            steps.append({
                "step": len(steps) + 1,
                "current": u,
                "visited": sorted(visited_set),
                "distances": {k: (None if val == float("inf") else val) for k, val in dist.items()},
            })
        return {
            "algorithm": "dijkstra",
            "distances": {k: (None if val == float("inf") else val) for k, val in dist.items()},
            "parents": parent,
            "complexity": "Time: O((V + E) log V)",
            "steps": steps,
        }

    raise ValueError(f"Unsupported algorithm '{algorithm}'")


def run_data_structure_ops(structure: str, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Simulate stack, queue, linked list, or binary search tree operations step-by-step."""
    kind = structure.strip().lower()
    trace: List[Dict[str, Any]] = []

    if kind == "stack":
        items: List[Any] = []
        for op in operations:
            act = op.get("op", "").lower()
            val = op.get("value")
            if act == "push":
                items.append(val)
            elif act == "pop" and items:
                items.pop()
            trace.append({"op": act, "value": val, "state": list(items)})
        return {"structure": "stack", "final_state": items, "trace": trace}

    if kind == "queue":
        q: List[Any] = []
        for op in operations:
            act = op.get("op", "").lower()
            val = op.get("value")
            if act == "enqueue":
                q.append(val)
            elif act == "dequeue" and q:
                q.pop(0)
            trace.append({"op": act, "value": val, "state": list(q)})
        return {"structure": "queue", "final_state": q, "trace": trace}

    if kind == "linked_list":
        nodes: List[Any] = []
        for op in operations:
            act = op.get("op", "").lower()
            val = op.get("value")
            if act in {"append", "insert"}:
                nodes.append(val)
            elif act == "prepend":
                nodes.insert(0, val)
            elif act == "delete" and val in nodes:
                nodes.remove(val)
            trace.append({
                "op": act,
                "value": val,
                "state": [{"value": n, "next": nodes[idx + 1] if idx + 1 < len(nodes) else None} for idx, n in enumerate(nodes)],
            })
        return {"structure": "linked_list", "final_state": nodes, "trace": trace}

    if kind == "bst":
        root: Optional[Dict[str, Any]] = None

        def _insert(node: Optional[Dict[str, Any]], val: float) -> Dict[str, Any]:
            if node is None:
                return {"value": val, "left": None, "right": None}
            if val < node["value"]:
                node["left"] = _insert(node["left"], val)
            elif val > node["value"]:
                node["right"] = _insert(node["right"], val)
            return node

        def _inorder(node: Optional[Dict[str, Any]]) -> List[float]:
            if not node:
                return []
            return _inorder(node["left"]) + [node["value"]] + _inorder(node["right"])

        def _clone(node: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
            if not node:
                return None
            return {"value": node["value"], "left": _clone(node["left"]), "right": _clone(node["right"])}

        for op in operations:
            act = op.get("op", "").lower()
            val = op.get("value")
            if act == "insert" and val is not None:
                root = _insert(root, float(val))
            trace.append({"op": act, "value": val, "inorder": _inorder(root), "tree": _clone(root)})
        return {"structure": "bst", "inorder": _inorder(root), "tree": root, "trace": trace}

    raise ValueError(f"Unsupported data structure '{structure}'")


def generate_pseudocode(code: str, language: str = "python") -> Dict[str, Any]:
    """Generate clean structured pseudocode and static complexity estimates from Python source."""
    src = (code or "").strip()
    if not src:
        raise ValueError("Source code cannot be empty")

    if language.lower() == "python":
        try:
            tree = ast.parse(src)
        except SyntaxError as exc:
            return {"pseudocode": f"Syntax error at line {exc.lineno}: {exc.msg}", "complexity_hint": "Unknown", "lines": []}

        lines: List[str] = []
        max_loop_depth = 0

        def _visit(node: ast.AST, indent: int, loop_depth: int):
            nonlocal max_loop_depth
            max_loop_depth = max(max_loop_depth, loop_depth)
            pad = "  " * indent
            if isinstance(node, ast.FunctionDef):
                args = ", ".join(a.arg for a in node.args.args)
                lines.append(f"{pad}PROCEDURE {node.name}({args})")
                for stmt in node.body:
                    _visit(stmt, indent + 1, loop_depth)
                lines.append(f"{pad}END PROCEDURE")
            elif isinstance(node, ast.For):
                lines.append(f"{pad}FOR EACH {ast.unparse(node.target)} IN {ast.unparse(node.iter)} DO")
                for stmt in node.body:
                    _visit(stmt, indent + 1, loop_depth + 1)
                lines.append(f"{pad}END FOR")
            elif isinstance(node, ast.While):
                lines.append(f"{pad}WHILE {ast.unparse(node.test)} DO")
                for stmt in node.body:
                    _visit(stmt, indent + 1, loop_depth + 1)
                lines.append(f"{pad}END WHILE")
            elif isinstance(node, ast.If):
                lines.append(f"{pad}IF {ast.unparse(node.test)} THEN")
                for stmt in node.body:
                    _visit(stmt, indent + 1, loop_depth)
                if node.orelse:
                    lines.append(f"{pad}ELSE")
                    for stmt in node.orelse:
                        _visit(stmt, indent + 1, loop_depth)
                lines.append(f"{pad}END IF")
            elif isinstance(node, ast.Return):
                val = ast.unparse(node.value) if node.value else "NOTHING"
                lines.append(f"{pad}RETURN {val}")
            elif isinstance(node, (ast.Assign, ast.AugAssign)):
                lines.append(f"{pad}SET {ast.unparse(node)}")
            elif isinstance(node, ast.Expr):
                lines.append(f"{pad}EVALUATE {ast.unparse(node)}")

        for item in tree.body:
            _visit(item, 0, 0)

        complexity = "O(1)"
        if max_loop_depth == 1:
            complexity = "O(n) linear loop depth"
        elif max_loop_depth == 2:
            complexity = "O(n^2) nested loop depth"
        elif max_loop_depth >= 3:
            complexity = f"O(n^{max_loop_depth}) nested loop depth"
        return {"pseudocode": "\n".join(lines), "lines": lines, "complexity_hint": complexity}

    raw_lines = [ln.strip() for ln in src.splitlines() if ln.strip()]
    return {
        "pseudocode": "\n".join(f"STEP {i + 1}: {ln}" for i, ln in enumerate(raw_lines)),
        "lines": raw_lines,
        "complexity_hint": "Static loop inspection only available for Python AST",
    }
