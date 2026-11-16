import math
import re
from typing import Any, Dict, List, Optional, Tuple

_FORBIDDEN_TOKENS = ("__", "import", "lambda", "eval", "exec", "open", "getattr", "setattr", "class")
_CACHED_LIBS: Optional[Tuple[Any, Any, Any, Any]] = None


def _get_math_libs():
    """Lazy-load numpy and sympy so application startup stays fast."""
    global _CACHED_LIBS
    if _CACHED_LIBS is None:
        import numpy as np
        import sympy as sp
        from sympy.parsing.sympy_parser import (
            parse_expr,
            standard_transformations,
            implicit_multiplication_application,
            convert_xor,
        )
        transforms = standard_transformations + (implicit_multiplication_application, convert_xor)
        _CACHED_LIBS = (np, sp, parse_expr, transforms)
    return _CACHED_LIBS


def parse_safe_expr(expr_str: str, variables: Optional[List[str]] = None) -> Any:
    """Parse a mathematical string into a SymPy expression using a restricted symbol grammar."""
    _, sp, parse_expr, transforms = _get_math_libs()
    raw = (expr_str or "").strip()
    if not raw or len(raw) > 400:
        raise ValueError("Expression must be between 1 and 400 characters.")
    lower = raw.lower()
    for bad in _FORBIDDEN_TOKENS:
        if bad in lower:
            raise ValueError(f"Unsupported token '{bad}' in mathematical expression.")
    if "." in re.sub(r"\d+\.\d+", "", raw):
        raise ValueError("Attribute access is not permitted in expressions.")

    allowed_funcs: Dict[str, Any] = {
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "cot": sp.cot,
        "sec": sp.sec,
        "csc": sp.csc,
        "asin": sp.asin,
        "acos": sp.acos,
        "atan": sp.atan,
        "sinh": sp.sinh,
        "cosh": sp.cosh,
        "tanh": sp.tanh,
        "exp": sp.exp,
        "log": sp.log,
        "ln": sp.log,
        "sqrt": sp.sqrt,
        "abs": sp.Abs,
        "Abs": sp.Abs,
        "pi": sp.pi,
        "e": sp.E,
        "E": sp.E,
        "oo": sp.oo,
        "inf": sp.oo,
    }
    vars_list = variables or ["x", "y", "z", "t", "n"]
    local_dict = dict(allowed_funcs)
    for v in vars_list:
        if re.match(r"^[a-zA-Z]\w{0,10}$", v):
            local_dict[v] = sp.Symbol(v, real=True)

    return parse_expr(raw, local_dict=local_dict, transformations=transforms, evaluate=True)


def _extract_domain_notes(expr: Any, var: Any) -> List[str]:
    _, sp, _, _ = _get_math_libs()
    notes: List[str] = []
    try:
        _, denom = sp.fraction(sp.together(expr))
        if denom != 1 and denom.has(var):
            poles = sp.solve(denom, var)
            if poles:
                notes.append(f"Denominator cannot be zero: {var} != {', '.join(str(p) for p in poles[:5])}")
    except Exception:
        pass
    if expr.has(sp.log):
        notes.append("Logarithm arguments must be strictly positive (> 0) over the real domain.")
    if expr.has(sp.sqrt) or any(
        isinstance(a, sp.Pow) and a.exp.is_Rational and not a.exp.is_Integer and a.exp.q % 2 == 0
        for a in expr.atoms(sp.Pow)
    ):
        notes.append("Even-root radicands must be non-negative (>= 0) over the real domain.")
    return notes


def verify_equivalence(expected_expr: str, student_expr: str, variable: str = "x") -> Dict[str, Any]:
    """Check symbolic and numeric equivalence between two mathematical expressions."""
    _, sp, _, _ = _get_math_libs()
    var = sp.Symbol(variable, real=True)
    try:
        if "=" in expected_expr and "=" in student_expr:
            lhs1, rhs1 = expected_expr.split("=", 1)
            lhs2, rhs2 = student_expr.split("=", 1)
            e1 = parse_safe_expr(lhs1, [variable]) - parse_safe_expr(rhs1, [variable])
            e2 = parse_safe_expr(lhs2, [variable]) - parse_safe_expr(rhs2, [variable])
            diff = sp.simplify(e1 - e2)
            ratio = sp.simplify(e1 / e2) if e2 != 0 else None
            equivalent = diff == 0 or (ratio is not None and not ratio.has(var) and ratio != 0)
        else:
            e1 = parse_safe_expr(expected_expr, [variable])
            e2 = parse_safe_expr(student_expr, [variable])
            diff = sp.simplify(e1 - e2)
            equivalent = diff == 0
            if not equivalent:
                expanded = sp.simplify(sp.expand(e1 - e2))
                equivalent = expanded == 0
                diff = expanded

        formatting_only = equivalent and expected_expr.replace(" ", "") != student_expr.replace(" ", "")
        return {
            "is_equivalent": bool(equivalent),
            "formatting_diff_only": bool(formatting_only),
            "symbolic_difference": str(diff),
            "normalized_expected": str(sp.simplify(e1)),
            "normalized_student": str(sp.simplify(e2)),
            "verification_status": "verified_by_tool",
            "explanation": (
                "Expressions are algebraically equivalent."
                if equivalent
                else f"Expressions differ by {diff}."
            ),
        }
    except Exception as exc:
        return {
            "is_equivalent": False,
            "formatting_diff_only": False,
            "symbolic_difference": None,
            "verification_status": "inconclusive",
            "explanation": f"Could not verify expression equivalence: {str(exc)}",
        }


def run_math_operation(
    operation: str,
    expression: str,
    variable: str = "x",
    lower: Optional[float] = None,
    upper: Optional[float] = None,
    point: Optional[float] = None,
    order: int = 5,
    matrix_a: Optional[List[List[float]]] = None,
    matrix_b: Optional[List[List[float]]] = None,
    compare_expression: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute deterministic SymPy symbolic or matrix calculations."""
    _, sp, _, _ = _get_math_libs()
    op = operation.strip().lower()
    if op == "verify_equivalence":
        if compare_expression is None:
            raise ValueError("compare_expression is required for verify_equivalence")
        return verify_equivalence(expression, compare_expression, variable=variable)

    if op == "matrix_ops":
        if not matrix_a:
            raise ValueError("matrix_a is required for matrix operations")
        mat_a = sp.Matrix(matrix_a)
        out: Dict[str, Any] = {
            "operation": "matrix_ops",
            "shape_a": [mat_a.rows, mat_a.cols],
            "transpose_a": [[float(x) if x.is_number else str(x) for x in row] for row in mat_a.T.tolist()],
        }
        if mat_a.rows == mat_a.cols:
            det = mat_a.det()
            out["determinant"] = str(det)
            out["trace"] = str(mat_a.trace())
            if det != 0:
                inv = mat_a.inv()
                out["inverse"] = [[str(x) for x in row] for row in inv.tolist()]
            else:
                out["inverse"] = None
                out["warning"] = "Matrix is singular (determinant is 0); inverse does not exist."
            try:
                out["eigenvalues"] = {str(k): int(v) for k, v in mat_a.eigenvals().items()}
            except Exception:
                out["eigenvalues"] = {}
        if matrix_b:
            mat_b = sp.Matrix(matrix_b)
            if mat_a.shape == mat_b.shape:
                out["sum"] = [[str(x) for x in row] for row in (mat_a + mat_b).tolist()]
            if mat_a.cols == mat_b.rows:
                out["product"] = [[str(x) for x in row] for row in (mat_a * mat_b).tolist()]
        return out

    var = sp.Symbol(variable, real=True)
    if "=" in expression and op == "solve":
        lhs_s, rhs_s = expression.split("=", 1)
        expr = parse_safe_expr(lhs_s, [variable]) - parse_safe_expr(rhs_s, [variable])
    else:
        expr = parse_safe_expr(expression, [variable])

    domain_notes = _extract_domain_notes(expr, var)
    result_obj: Any

    if op == "simplify":
        result_obj = sp.simplify(expr)
    elif op == "solve":
        result_obj = sp.solve(expr, var)
    elif op == "diff":
        result_obj = sp.diff(expr, var)
    elif op == "integrate":
        if lower is not None and upper is not None:
            result_obj = sp.integrate(expr, (var, lower, upper))
        else:
            result_obj = sp.integrate(expr, var)
    elif op == "limit":
        target = point if point is not None else 0
        result_obj = sp.limit(expr, var, target)
    elif op == "series":
        target = point if point is not None else 0
        result_obj = sp.series(expr, var, target, n=max(2, min(order, 12)))
    else:
        raise ValueError(f"Unsupported math operation '{operation}'")

    latex_out = sp.latex(result_obj) if not isinstance(result_obj, list) else ", ".join(sp.latex(r) for r in result_obj)
    return {
        "operation": op,
        "input_expression": str(expr),
        "result": [str(r) for r in result_obj] if isinstance(result_obj, list) else str(result_obj),
        "latex": latex_out,
        "domain_restrictions": domain_notes,
        "verification_status": "verified_by_tool",
    }


def sample_function_1d(
    expression: str,
    variable: str = "x",
    x_min: float = -10.0,
    x_max: float = 10.0,
    points: int = 160,
    include_derivative: bool = True,
) -> Dict[str, Any]:
    """Sample a 1D function (and optionally its derivative) while flagging singularities."""
    np, sp, _, _ = _get_math_libs()
    if x_max <= x_min:
        raise ValueError("x_max must be greater than x_min")
    count = max(20, min(points, 400))
    var = sp.Symbol(variable, real=True)
    expr = parse_safe_expr(expression, [variable])
    domain_notes = _extract_domain_notes(expr, var)
    f_num = sp.lambdify(var, expr, modules=["numpy"])

    deriv_expr = sp.diff(expr, var) if include_derivative else None
    df_num = sp.lambdify(var, deriv_expr, modules=["numpy"]) if deriv_expr is not None else None

    xs = np.linspace(x_min, x_max, count)
    series: List[Dict[str, Optional[float]]] = []

    for xv in xs:
        y_val: Optional[float] = None
        dy_val: Optional[float] = None
        try:
            raw_y = complex(f_num(float(xv)))
            if abs(raw_y.imag) < 1e-9 and math.isfinite(raw_y.real) and abs(raw_y.real) < 1e6:
                y_val = round(float(raw_y.real), 6)
        except Exception:
            y_val = None

        if df_num is not None:
            try:
                raw_dy = complex(df_num(float(xv)))
                if abs(raw_dy.imag) < 1e-9 and math.isfinite(raw_dy.real) and abs(raw_dy.real) < 1e6:
                    dy_val = round(float(raw_dy.real), 6)
            except Exception:
                dy_val = None

        series.append({"x": round(float(xv), 6), "y": y_val, "dy": dy_val})

    return {
        "expression": str(expr),
        "derivative": str(deriv_expr) if deriv_expr is not None else None,
        "latex": sp.latex(expr),
        "domain_restrictions": domain_notes,
        "points": series,
    }


def sample_function_2d(
    expression: str,
    x_min: float = -4.0,
    x_max: float = 4.0,
    y_min: float = -4.0,
    y_max: float = 4.0,
    grid_size: int = 24,
) -> Dict[str, Any]:
    """Sample a 2D multivariable function f(x, y) over a bounded grid."""
    np, sp, _, _ = _get_math_libs()
    n = max(8, min(grid_size, 40))
    x_sym, y_sym = sp.Symbol("x", real=True), sp.Symbol("y", real=True)
    expr = parse_safe_expr(expression, ["x", "y"])
    f_xy = sp.lambdify((x_sym, y_sym), expr, modules=["numpy"])

    xs = np.linspace(x_min, x_max, n)
    ys = np.linspace(y_min, y_max, n)
    z_grid: List[List[Optional[float]]] = []
    for yv in ys:
        row: List[Optional[float]] = []
        for xv in xs:
            try:
                val = complex(f_xy(float(xv), float(yv)))
                if abs(val.imag) < 1e-9 and math.isfinite(val.real) and abs(val.real) < 1e6:
                    row.append(round(float(val.real), 5))
                else:
                    row.append(None)
            except Exception:
                row.append(None)
        z_grid.append(row)

    return {
        "expression": str(expr),
        "latex": sp.latex(expr),
        "x": [round(float(v), 5) for v in xs],
        "y": [round(float(v), 5) for v in ys],
        "z": z_grid,
    }


def run_numerical_method(
    method: str,
    expression: str,
    a: float = 0.0,
    b: float = 2.0,
    x0: float = 1.0,
    x1: float = 1.5,
    tol: float = 1e-6,
    max_iter: int = 30,
    steps: int = 8,
    points_xy: Optional[List[List[float]]] = None,
) -> Dict[str, Any]:
    """Execute standard numerical analysis methods with iteration tables and convergence checks."""
    _, sp, _, _ = _get_math_libs()
    m = method.strip().lower()
    var = sp.Symbol("x", real=True)
    expr = parse_safe_expr(expression, ["x"])
    f = sp.lambdify(var, expr, modules=["numpy"])
    max_it = max(1, min(max_iter, 100))

    def _eval(val: float) -> float:
        res = complex(f(float(val)))
        if abs(res.imag) > 1e-9 or not math.isfinite(res.real):
            raise ValueError(f"Function undefined or non-finite at x={val}")
        return float(res.real)

    if m == "bisection":
        fa = _eval(a)
        fb = _eval(b)
        if fa * fb > 0:
            return {
                "method": "bisection",
                "converged": False,
                "warning": f"Root bracketing failed: f({a})={fa:.6g} and f({b})={fb:.6g} have the same sign.",
                "iterations": [],
                "result": None,
            }
        rows = []
        lo, hi = float(a), float(b)
        converged = False
        mid = lo
        for it in range(1, max_it + 1):
            mid = 0.5 * (lo + hi)
            fm = _eval(mid)
            err = 0.5 * abs(hi - lo)
            rows.append({"iteration": it, "a": round(lo, 8), "b": round(hi, 8), "x": round(mid, 8), "fx": round(fm, 10), "error": round(err, 10)})
            if abs(fm) < tol or err < tol:
                converged = True
                break
            if _eval(lo) * fm < 0:
                hi = mid
            else:
                lo = mid
        return {"method": "bisection", "converged": converged, "result": round(mid, 8), "iterations": rows, "warning": None if converged else "Max iterations reached without meeting tolerance."}

    if m == "newton_raphson":
        df_expr = sp.diff(expr, var)
        df = sp.lambdify(var, df_expr, modules=["numpy"])
        curr = float(x0)
        rows = []
        converged = False
        for it in range(1, max_it + 1):
            fx = _eval(curr)
            dfx_c = complex(df(curr))
            dfx = float(dfx_c.real)
            if abs(dfx) < 1e-12:
                return {"method": "newton_raphson", "converged": False, "result": curr, "iterations": rows, "warning": f"Derivative near zero at x={curr:.6g}."}
            nxt = curr - fx / dfx
            err = abs(nxt - curr)
            rows.append({"iteration": it, "x": round(nxt, 8), "fx": round(_eval(nxt), 10), "dfx": round(dfx, 8), "error": round(err, 10)})
            curr = nxt
            if err < tol or abs(_eval(curr)) < tol:
                converged = True
                break
        return {"method": "newton_raphson", "derivative": str(df_expr), "converged": converged, "result": round(curr, 8), "iterations": rows, "warning": None if converged else "Did not converge within max_iter."}

    if m == "secant":
        p0, p1 = float(x0), float(x1)
        rows = []
        converged = False
        for it in range(1, max_it + 1):
            f0, f1 = _eval(p0), _eval(p1)
            denom = f1 - f0
            if abs(denom) < 1e-12:
                return {"method": "secant", "converged": False, "result": p1, "iterations": rows, "warning": "Secant denominator near zero."}
            p2 = p1 - f1 * (p1 - p0) / denom
            err = abs(p2 - p1)
            rows.append({"iteration": it, "x": round(p2, 8), "fx": round(_eval(p2), 10), "error": round(err, 10)})
            p0, p1 = p1, p2
            if err < tol:
                converged = True
                break
        return {"method": "secant", "converged": converged, "result": round(p1, 8), "iterations": rows, "warning": None if converged else "Did not converge within max_iter."}

    if m in {"trapezoidal", "simpson"}:
        n_steps = max(2, min(steps, 200))
        if m == "simpson" and n_steps % 2 != 0:
            n_steps += 1
        h = (b - a) / n_steps
        xs = [a + i * h for i in range(n_steps + 1)]
        ys = [_eval(xv) for xv in xs]
        if m == "trapezoidal":
            approx = h * (0.5 * ys[0] + sum(ys[1:-1]) + 0.5 * ys[-1])
        else:
            approx = (h / 3.0) * (
                ys[0] + ys[-1] + 4 * sum(ys[1:-1:2]) + 2 * sum(ys[2:-2:2])
            )
        exact = None
        abs_error = None
        try:
            exact_sym = sp.N(sp.integrate(expr, (var, a, b)))
            if exact_sym.is_real and math.isfinite(float(exact_sym)):
                exact = round(float(exact_sym), 8)
                abs_error = round(abs(exact - approx), 10)
        except Exception:
            pass
        table = [{"i": i, "x": round(xs[i], 6), "fx": round(ys[i], 6)} for i in range(len(xs))]
        return {
            "method": m,
            "steps": n_steps,
            "step_size": round(h, 8),
            "result": round(approx, 8),
            "exact_reference": exact,
            "absolute_error": abs_error,
            "iterations": table,
            "converged": True,
        }

    if m == "lagrange_interpolation":
        pts = points_xy or [[0, 1], [1, 3], [2, 2]]
        if len(pts) < 2 or len(pts) > 12:
            raise ValueError("Provide between 2 and 12 (x, y) points for Lagrange interpolation.")
        poly = sp.Integer(0)
        for i, (xi, yi) in enumerate(pts):
            term = sp.Float(yi)
            for j, (xj, _) in enumerate(pts):
                if i != j:
                    if xi == xj:
                        raise ValueError("Duplicate x coordinates are not permitted.")
                    term *= (var - sp.Float(xj)) / (sp.Float(xi) - sp.Float(xj))
            poly += term
        expanded = sp.expand(poly)
        return {
            "method": "lagrange_interpolation",
            "polynomial": str(expanded),
            "latex": sp.latex(expanded),
            "converged": True,
            "iterations": [{"point": i + 1, "x": p[0], "y": p[1]} for i, p in enumerate(pts)],
        }

    raise ValueError(f"Unsupported numerical method '{method}'")
