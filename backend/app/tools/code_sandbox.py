import ast
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


_FORBIDDEN_IMPORTS = {
    "os",
    "subprocess",
    "socket",
    "shutil",
    "ctypes",
    "importlib",
    "urllib",
    "requests",
    "httpx",
    "http",
    "ftplib",
    "pathlib",
    "multiprocessing",
    "threading",
}

_FORBIDDEN_CALLS = {"eval", "exec", "compile", "__import__", "open", "breakpoint", "input"}


def analyze_python_static(code: str) -> Dict[str, Any]:
    """Inspect Python code via AST to flag syntax errors or forbidden host/network calls."""
    issues: List[str] = []
    try:
        tree = ast.parse(code or "")
    except SyntaxError as exc:
        return {
            "safe": False,
            "syntax_valid": False,
            "issues": [f"SyntaxError at line {exc.lineno}: {exc.msg}"],
        }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_mod = alias.name.split(".")[0]
                if root_mod in _FORBIDDEN_IMPORTS:
                    issues.append(f"Blocked import '{root_mod}' in sandbox policy.")
        elif isinstance(node, ast.ImportFrom):
            root_mod = (node.module or "").split(".")[0]
            if root_mod in _FORBIDDEN_IMPORTS:
                issues.append(f"Blocked import from '{root_mod}' in sandbox policy.")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN_CALLS:
                issues.append(f"Blocked builtin call '{node.func.id}' in sandbox policy.")
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            issues.append(f"Blocked dunder attribute '{node.attr}' access.")

    return {
        "safe": len(issues) == 0,
        "syntax_valid": True,
        "issues": issues,
    }


def execute_python_sandbox(
    code: str,
    stdin_data: str = "",
    test_cases: Optional[List[Dict[str, Any]]] = None,
    timeout_seconds: float = 4.0,
) -> Dict[str, Any]:
    """Execute Python snippets inside a resource-limited, network-disabled temporary sandbox."""
    analysis = analyze_python_static(code)
    if not analysis["safe"]:
        return {
            "status": "blocked",
            "syntax_valid": analysis["syntax_valid"],
            "issues": analysis["issues"],
            "stdout": "",
            "stderr": "\n".join(analysis["issues"]),
            "exit_code": -1,
            "timed_out": False,
            "test_results": [],
        }

    timeout = max(0.5, min(float(timeout_seconds), 8.0))
    max_output_bytes = 65536

    prelude = (
        "import builtins as _b\n"
        "_orig_import = _b.__import__\n"
        f"_blocked = {sorted(_FORBIDDEN_IMPORTS)!r}\n"
        "def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):\n"
        "    if name.split('.')[0] in _blocked:\n"
        "        raise ImportError(f'Sandbox blocked module: {name}')\n"
        "    return _orig_import(name, globals, locals, fromlist, level)\n"
        "_b.__import__ = _safe_import\n"
        "for _fn in ('open', 'eval', 'exec', 'compile'):\n"
        "    if hasattr(_b, _fn):\n"
        "        delattr(_b, _fn)\n"
    )

    def _run_once(snippet_code: str, stdin_txt: str) -> Dict[str, Any]:
        with tempfile.TemporaryDirectory(prefix="mv_sandbox_") as tmpdir:
            script_path = Path(tmpdir) / "user_code.py"
            script_path.write_text(prelude + "\n" + snippet_code, encoding="utf-8")
            safe_env = {
                "PYTHONNOUSERSITE": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
                "LANG": "C.UTF-8",
                "PATH": os.path.dirname(sys.executable),
            }
            try:
                proc = subprocess.run(
                    [sys.executable, "-I", str(script_path)],
                    input=stdin_txt,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=tmpdir,
                    env=safe_env,
                )
                return {
                    "stdout": (proc.stdout or "")[:max_output_bytes],
                    "stderr": (proc.stderr or "")[:max_output_bytes],
                    "exit_code": proc.returncode,
                    "timed_out": False,
                }
            except subprocess.TimeoutExpired as exc:
                return {
                    "stdout": (exc.stdout or "")[:max_output_bytes] if isinstance(exc.stdout, str) else "",
                    "stderr": f"Execution timed out after {timeout}s.",
                    "exit_code": -1,
                    "timed_out": True,
                }

    main_res = _run_once(code, stdin_data)
    test_results: List[Dict[str, Any]] = []
    if test_cases and not main_res["timed_out"]:
        for idx, tc in enumerate(test_cases[:15]):
            tc_stdin = str(tc.get("input", ""))
            expected = str(tc.get("expected", "")).strip()
            call_expr = tc.get("call")
            snippet = code if not call_expr else f"{code}\nprint('__MV_TEST__', {call_expr})"
            if call_expr and not analyze_python_static(snippet)["safe"]:
                test_results.append({"case": idx + 1, "passed": False, "error": "Unsafe test call expression"})
                continue
            tc_run = _run_once(snippet, tc_stdin)
            raw_out = tc_run["stdout"].strip()
            if call_expr and "__MV_TEST__" in raw_out:
                actual = raw_out.split("__MV_TEST__")[-1].strip()
            else:
                actual = raw_out
            passed = (tc_run["exit_code"] == 0) and (actual == expected)
            test_results.append({
                "case": idx + 1,
                "input": tc_stdin or call_expr or "",
                "expected": expected,
                "actual": actual,
                "passed": passed,
                "stderr": tc_run["stderr"],
            })

    status = "timeout" if main_res["timed_out"] else ("succeeded" if main_res["exit_code"] == 0 else "runtime_error")
    return {
        "status": status,
        "syntax_valid": True,
        "issues": [],
        **main_res,
        "test_results": test_results,
    }
