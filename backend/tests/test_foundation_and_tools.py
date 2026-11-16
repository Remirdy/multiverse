import io
import zipfile
import pytest
from docx import Document as DocxDocument
from pptx import Presentation
from pypdf import PdfReader

from app.execution.engine import execution_engine, ExecutionBudget, set_test_provider_fake
from app.exports.export_service import export_service
from app.providers.base import ProviderResponse
from app.providers.local_openai import validate_provider_url
from app.providers.registry import model_registry
from app.tools.algorithms_tool import generate_pseudocode, run_algorithm_trace, run_data_structure_ops
from app.tools.code_sandbox import analyze_python_static, execute_python_sandbox
from app.tools.document_tool import parse_document_bytes, validate_citations
from app.tools.electronics_tool import solve_circuit
from app.tools.math_tool import (
    parse_safe_expr,
    run_math_operation,
    run_numerical_method,
    sample_function_1d,
    sample_function_2d,
    verify_equivalence,
)


def test_provider_capabilities_and_url_validation():
    vl = model_registry.get("nvidia/nemotron-3.5-super-vl-120b-a12b")
    assert vl is not None
    assert vl.capabilities["vision"] is True
    assert validate_provider_url("http://127.0.0.1:11434/v1/") == "http://127.0.0.1:11434/v1"
    with pytest.raises(ValueError):
        validate_provider_url("http://169.254.169.254/latest/meta-data/")
    with pytest.raises(ValueError):
        validate_provider_url("ftp://127.0.0.1:11434")


@pytest.mark.asyncio
async def test_local_only_policy_blocks_external_models():
    async def fake_runner(model_id, prompt, system_prompt, timeout, attachments):
        return ProviderResponse(
            model_id=model_id,
            model_name=model_id,
            provider="Fake",
            response_text="ok",
            status="success",
        )

    set_test_provider_fake(fake_runner)
    try:
        res = await execution_engine.execute_model(
            model_id="poolside/laguna-xs-2.1",
            prompt="hello",
            budget=ExecutionBudget(local_only=True),
        )
        assert res.status == "error"
        assert "Local-only policy" in (res.error_message or "")
    finally:
        set_test_provider_fake(None)


def test_math_sympy_and_numerical_methods():
    with pytest.raises(ValueError):
        parse_safe_expr("__import__('os').system('ls')")

    eq = verify_equivalence("2*(x + 1)", "2*x + 2")
    assert eq["is_equivalent"] is True
    assert eq["verification_status"] == "verified_by_tool"

    diff_res = run_math_operation("diff", "x^3 + log(x)", variable="x")
    assert "3*x**2" in diff_res["result"]
    assert any("positive" in note.lower() for note in diff_res["domain_restrictions"])

    plot1d = sample_function_1d("1/x", x_min=-1, x_max=1, points=21)
    assert any(pt["y"] is None for pt in plot1d["points"])

    plot2d = sample_function_2d("x^2 + y^2", grid_size=8)
    assert len(plot2d["z"]) == 8

    bis_bad = run_numerical_method("bisection", "x^2 + 1", a=-1, b=1)
    assert bis_bad["converged"] is False
    assert bis_bad["warning"] is not None

    newt = run_numerical_method("newton_raphson", "x^2 - 4", x0=3.0)
    assert newt["converged"] is True
    assert abs(newt["result"] - 2.0) < 1e-5

    simp = run_numerical_method("simpson", "x^2", a=0.0, b=3.0, steps=6)
    assert abs(simp["result"] - 9.0) < 1e-5


def test_algorithms_data_structures_and_electronics():
    for alg in ["bubble_sort", "selection_sort", "insertion_sort", "merge_sort", "quick_sort"]:
        res = run_algorithm_trace(alg, [5, 1, 4, 2, 8])
        assert res["final_array"] == [1, 2, 4, 5, 8]
        assert len(res["steps"]) > 0

    bsearch = run_algorithm_trace("binary_search", [10, 3, 7, 1, 9], target=7)
    assert bsearch["found_index"] == 2

    dijk = run_algorithm_trace("dijkstra")
    assert dijk["distances"]["D"] == 9.0
    with pytest.raises(ValueError):
        run_algorithm_trace("dijkstra", graph={"A": [{"to": "B", "weight": -2}], "B": []})

    bst = run_data_structure_ops("bst", [{"op": "insert", "value": 5}, {"op": "insert", "value": 2}, {"op": "insert", "value": 8}])
    assert bst["inorder"] == [2.0, 5.0, 8.0]

    pseudo = generate_pseudocode("def f(n):\n    for i in range(n):\n        pass\n    return n")
    assert "PROCEDURE f(n)" in pseudo["pseudocode"]
    assert "O(n)" in pseudo["complexity_hint"]

    kvl = solve_circuit("kvl_kcl_loop", {"v1": 12, "r1": 100, "r2": 200, "r3": 200})
    assert kvl["values"]["kcl_residual_a"] == 0.0
    assert kvl["values"]["node_voltage_v"] == 6.0


def test_code_sandbox_isolation_and_execution():
    bad = analyze_python_static("import os\nos.system('whoami')")
    assert bad["safe"] is False

    res_blocked = execute_python_sandbox("import socket\nprint('x')")
    assert res_blocked["status"] == "blocked"

    res_ok = execute_python_sandbox(
        "def add(a, b):\n    return a + b\nprint(add(2, 3))",
        test_cases=[{"call": "add(10, 15)", "expected": "25"}],
    )
    assert res_ok["status"] == "succeeded"
    assert res_ok["stdout"].strip() == "5"
    assert res_ok["test_results"][0]["passed"] is True


def test_exports_and_turkish_unicode_roundtrip():
    turkish_text = "Öğrenci çalışma raporu: ğüşıöçĞÜŞİÖÇ [Page 1]"
    sections = [{"heading": "Bölüm 1", "body": turkish_text, "bullets": ["Madde 1: Çözüm"]}]

    pdf_out = export_service.generate("pdf", "Türkçe Rapor", sections=sections)
    reader = PdfReader(io.BytesIO(pdf_out["bytes"]))
    assert len(reader.pages) >= 1
    assert "Sayfa" in pdf_out["media_type"] or len(reader.pages[0].extract_text() or "") > 10

    docx_out = export_service.generate("docx", "Türkçe Rapor", sections=sections)
    docx_doc = DocxDocument(io.BytesIO(docx_out["bytes"]))
    assert any("ğüşıöç" in p.text for p in docx_doc.paragraphs)

    pptx_out = export_service.generate(
        "pptx",
        "Sunum Başlığı",
        slides=[{"title": "Giriş", "bullets": ["Türkçe karakterler: ğüşıöç"], "speaker_notes": "Not"}],
    )
    prs = Presentation(io.BytesIO(pptx_out["bytes"]))
    assert len(prs.slides) == 2

    ics_out = export_service.generate("ics", "Plan", ics_sessions=[{"date": "2026-12-01", "course": "Math", "topic": "Integrals"}])
    assert b"BEGIN:VCALENDAR" in ics_out["bytes"]


def test_document_zip_traversal_blocked_and_citations():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../../evil.txt", "malicious")
    with pytest.raises(ValueError, match="Unsafe archive"):
        parse_document_bytes("bad.docx", buf.getvalue())

    cit = validate_citations("See 10.1000/xyz123 and [Page 2]", source_chunks=[{"page": 1, "text": "x"}])
    assert cit["dois"][0]["doi"] == "10.1000/xyz123"
    assert cit["missing_source_pages"] == [2]
