import io
import json
import pytest
from httpx import AsyncClient, ASGITransport
from reportlab.pdfgen import canvas

from app.main import app
from app.database.session import init_db
from app.execution.engine import execution_engine, set_test_provider_fake
from app.providers.base import ProviderResponse
from app.workflows.engine import validate_webhook_url, sanitize_imported_workflow


@pytest.mark.asyncio
async def test_council_full_partial_retry_and_export():
    await init_db()

    async def fake_model(model_id, prompt, system_prompt, timeout, attachments):
        if model_id == "poolside/laguna-xs-2.1" and "Original User Question" not in prompt:
            return ProviderResponse(
                model_id=model_id,
                model_name="Laguna",
                provider="Fake",
                status="error",
                error_message="Simulated transient failure",
            )
        if "Critique each candidate" in prompt:
            return ProviderResponse(
                model_id=model_id,
                model_name=model_id,
                provider="Fake",
                status="success",
                response_text=json.dumps({
                    "summary": "Candidate A is clear.",
                    "critiques": [{"candidate": "Candidate A", "strengths": ["Clear"], "flaws": []}],
                    "disagreements": ["Check edge case x=2"],
                }),
                usage={"total_tokens": 40},
            )
        return ProviderResponse(
            model_id=model_id,
            model_name=model_id,
            provider="Fake",
            status="success",
            response_text="Solution: x = 2 or x = 3",
            usage={"total_tokens": 50},
        )

    set_test_provider_fake(fake_model)
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(
                "/api/council/sessions",
                json={
                    "prompt": "Solve x^2 - 5*x + 6 = 0",
                    "members": [
                        {"role_id": "mathematician", "model_id": "nvidia/nemotron-3.5-lightning-30b-a3b"},
                        {"role_id": "critic", "model_id": "poolside/laguna-xs-2.1"},
                        {"role_id": "teacher", "model_id": "nvidia/nemotron-3-ultra-550b-a55b"},
                    ],
                    "chair_model_id": "nvidia/nemotron-3-ultra-550b-a55b",
                    "review_rounds": 1,
                },
            )
            assert res.status_code == 201
            session = res.json()
            assert session["status"] == "partially_succeeded"
            assert any(v["tool"] == "sympy" and v["status"] == "verified_by_tool" for v in session["verifications"])
            assert len(session["disagreements"]) >= 1

            # Retry failed member with fake fixed
            async def fake_ok(model_id, prompt, system_prompt, timeout, attachments):
                return ProviderResponse(
                    model_id=model_id, model_name=model_id, provider="Fake", status="success", response_text="Fixed: x = 2, 3"
                )

            set_test_provider_fake(fake_ok)
            retry_res = await client.post(f"/api/council/sessions/{session['id']}/retry-member", json={"member_index": 1})
            assert retry_res.status_code == 200
            assert retry_res.json()["status"] == "succeeded"

            exp_res = await client.post(
                f"/api/council/sessions/{session['id']}/export",
                json={"format": "pdf", "include_full": True},
            )
            assert exp_res.status_code == 200
            dl = await client.get(exp_res.json()["download_url"])
            assert dl.status_code == 200
            assert dl.content.startswith(b"%PDF")
    finally:
        set_test_provider_fake(None)


@pytest.mark.asyncio
async def test_workflow_cycles_branching_approval_ssrf_and_import():
    await init_db()

    # SSRF validation blocks loopback & metadata
    with pytest.raises(ValueError):
        validate_webhook_url("http://127.0.0.1:8000/secret")
    with pytest.raises(ValueError):
        validate_webhook_url("http://169.254.169.254/latest")
    with pytest.raises(ValueError):
        validate_webhook_url("http://10.0.0.5/internal")

    # Import strips secrets and disables code/webhook nodes until owner approves
    sanitized = sanitize_imported_workflow({
        "name": "Untrusted Import",
        "graph": {
            "nodes": [
                {"id": "n1", "type": "code", "config": {"code": "print(1)", "api_key": "secret-leak", "approved_by_owner": True}},
            ],
            "edges": [],
        },
    })
    assert sanitized["graph"]["nodes"][0]["config"]["api_key"] == ""
    assert sanitized["graph"]["nodes"][0]["config"]["approved_by_owner"] is False

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Cycle rejection
        bad = await client.post(
            "/api/workflows",
            json={
                "name": "Cyclic",
                "graph": {
                    "nodes": [
                        {"id": "a", "type": "input", "position": {"x": 0, "y": 0}, "config": {}},
                        {"id": "b", "type": "transform", "position": {"x": 100, "y": 0}, "config": {}},
                    ],
                    "edges": [
                        {"id": "e1", "source": "a", "target": "b"},
                        {"id": "e2", "source": "b", "target": "a"},
                    ],
                },
            },
        )
        assert bad.status_code == 400
        assert "Cycle detected" in bad.json()["detail"]

        # Branching + Approval pause/resume + Export artifact
        wf_res = await client.post(
            "/api/workflows",
            json={
                "name": "Branch & Approve",
                "graph": {
                    "nodes": [
                        {"id": "in1", "type": "input", "position": {"x": 0, "y": 0}, "config": {"default_text": "hello"}},
                        {"id": "cond", "type": "condition", "position": {"x": 150, "y": 0}, "config": {"field": "in1.text", "operator": "contains", "value": "hello"}},
                        {"id": "t_branch", "type": "approval", "position": {"x": 300, "y": 0}, "config": {"message": "Approve export"}},
                        {"id": "f_branch", "type": "transform", "position": {"x": 300, "y": 120}, "config": {"template": "skipped"}},
                        {"id": "exp", "type": "export", "position": {"x": 500, "y": 0}, "config": {"format": "md", "title": "Approved Doc", "content_template": "{{t_branch.output}}"}},
                    ],
                    "edges": [
                        {"id": "e1", "source": "in1", "target": "cond"},
                        {"id": "e2", "source": "cond", "sourceHandle": "true", "target": "t_branch"},
                        {"id": "e3", "source": "cond", "sourceHandle": "false", "target": "f_branch"},
                        {"id": "e4", "source": "t_branch", "sourceHandle": "approved", "target": "exp"},
                    ],
                },
            },
        )
        assert wf_res.status_code == 201
        wf_id = wf_res.json()["id"]

        run_res = await client.post(f"/api/workflows/{wf_id}/runs", json={"inputs": {"text": "hello world"}})
        assert run_res.status_code == 201
        run_data = run_res.json()
        assert run_data["status"] == "waiting_for_approval"
        assert run_data["node_states"]["f_branch"]["status"] == "skipped"

        app_res = await client.post(f"/api/workflows/runs/{run_data['id']}/approve", json={"node_id": "t_branch", "approved": True})
        assert app_res.status_code == 200
        finished = app_res.json()
        assert finished["status"] == "succeeded"
        assert finished["outputs"]["exp"]["artifact_id"] is not None


@pytest.mark.asyncio
async def test_study_lab_pdf_intake_verifier_flashcards_exam_analytics_and_planner():
    await init_db()

    async def fake_study_model(model_id, prompt, system_prompt, timeout, attachments):
        return ProviderResponse(
            model_id=model_id,
            model_name=model_id,
            provider="Fake",
            status="success",
            response_text="Grounded answer citing [Page 1].",
        )

    set_test_provider_fake(fake_study_model)
    try:
        # Build small fixture PDF with question
        pdf_buf = io.BytesIO()
        c = canvas.Canvas(pdf_buf)
        c.drawString(72, 720, "1. Calculate the derivative of x^2 + 3x.")
        c.showPage()
        c.save()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            up = await client.post(
                "/api/study/documents/upload",
                files={"file": ("hw1.pdf", pdf_buf.getvalue(), "application/pdf")},
            )
            assert up.status_code == 200
            doc = up.json()
            assert len(doc["parsed"]["questions"]) >= 1

            # Homework Verifier with SymPy equivalence
            ver = await client.post(
                "/api/study/assignments/verify-homework",
                json={
                    "question": "Expand (x + 2)^2",
                    "student_solution": "x^2 + 4*x + 4",
                    "expected_answer": "(x + 2)^2",
                    "model_id": "nvidia/nemotron-3.5-lightning-30b-a3b",
                    "language": "en",
                },
            )
            assert ver.status_code == 200
            assert ver.json()["verification_badge"] == "verified_by_tool"
            assert ver.json()["deterministic_check"]["is_equivalent"] is True

            # Notebook + PDF Chat
            nb = await client.post(
                "/api/study/notebooks",
                json={"title": "Calc 101", "course": "Math", "sources": [doc["id"]]},
            )
            assert nb.status_code == 201
            nb_id = nb.json()["id"]

            chat = await client.post(
                f"/api/study/notebooks/{nb_id}/pdf-chat",
                json={"question": "What is the derivative question?", "model_id": "nvidia/nemotron-3-ultra-550b-a55b", "document_ids": [doc["id"]]},
            )
            assert chat.status_code == 200
            assert chat.json()["source_grounded"] is True
            assert len(chat.json()["citations"]) >= 1

            # SM-2 Flashcards
            dk = await client.post(
                "/api/study/decks",
                json={"title": "Derivatives", "course": "Math", "cards": [{"front": "d/dx(x^2)", "back": "2x"}]},
            )
            assert dk.status_code == 201
            card_id = dk.json()["cards"][0]["id"]
            rev1 = await client.post(f"/api/study/decks/{dk.json()['id']}/review", json={"card_id": card_id, "rating": "good"})
            assert rev1.json()["cards"][0]["interval_days"] == 1
            rev2 = await client.post(f"/api/study/decks/{dk.json()['id']}/review", json={"card_id": card_id, "rating": "good"})
            assert rev2.json()["cards"][0]["interval_days"] == 6

            # Exam Simulator + Analytics
            ex = await client.post(
                "/api/study/exams",
                json={
                    "title": "Math Quiz",
                    "mode": "exam",
                    "questions": [
                        {"id": "q1", "question_text": "d/dx(x^3)", "question_type": "math", "correct_answer": "3*x^2", "topic": "Calculus", "difficulty": "easy"},
                        {"id": "q2", "question_text": "2+2=5", "question_type": "true_false", "correct_answer": "False", "topic": "Arithmetic", "difficulty": "easy"},
                    ],
                },
            )
            assert ex.status_code == 201
            sub = await client.post(
                f"/api/study/exams/{ex.json()['id']}/submit",
                json={"answers": {"q1": "3*x^2", "q2": "True"}, "elapsed_seconds": 45},
            )
            assert sub.status_code == 200
            assert sub.json()["score_percent"] == 50.0

            analytics = await client.get("/api/study/analytics")
            assert analytics.status_code == 200
            assert analytics.json()["has_sufficient_data"] is True
            assert any(w["topic"] == "Arithmetic" for w in analytics.json()["weaknesses"])

            # Study Planner + ICS export
            pl = await client.post(
                "/api/study/planner",
                json={"title": "Finals", "exam_date": "2026-12-10", "daily_hours": 2.0, "courses": [{"name": "Math", "priority": 3, "topics": ["Arithmetic"]}]},
            )
            assert pl.status_code == 201
            ics = await client.post(f"/api/study/planner/{pl.json()['id']}/export-ics")
            assert ics.status_code == 200

            # Presentation Maker (.pptx)
            pptx = await client.post(
                "/api/study/presentations/generate",
                json={"title": "Review Slides", "subtitle": "Calc", "slides": [{"title": "Intro", "bullets": ["Point 1"]}]},
            )
            assert pptx.status_code == 200
            assert pptx.json()["filename"].endswith(".pptx")
    finally:
        set_test_provider_fake(None)
