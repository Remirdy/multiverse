import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    ExamRecord,
    FlashcardDeckRecord,
    QuestionBankItemRecord,
    StudyAssignmentRecord,
    StudyNotebookRecord,
    StudyPlanRecord,
    generate_uuid,
    get_utc_now,
)
from app.database.session import get_db
from app.execution.engine import execution_engine
from app.exports.export_service import export_service
from app.services.artifact_service import artifact_service
from app.study.service import study_service
from app.tools.algorithms_tool import generate_pseudocode, run_algorithm_trace, run_data_structure_ops
from app.tools.code_sandbox import execute_python_sandbox
from app.tools.document_tool import check_local_tooling, validate_citations
from app.tools.electronics_tool import solve_circuit
from app.tools.math_tool import (
    run_math_operation,
    run_numerical_method,
    sample_function_1d,
    sample_function_2d,
)

router = APIRouter(prefix="/study", tags=["Study Lab"])


# --- Request Schemas ---
class UpdateDocumentQuestionsRequest(BaseModel):
    questions: List[Dict[str, Any]]


class CreateAssignmentRequest(BaseModel):
    title: str = Field(..., min_length=1)
    course: str = "General"
    notebook_id: Optional[str] = None
    artifact_id: Optional[str] = None
    mode: str = "step_by_step"
    questions: List[Dict[str, Any]] = Field(default_factory=list)


class SolveAssignmentRequest(BaseModel):
    model_id: str = "nvidia/nemotron-3.5-lightning-30b-a3b"
    mode: str = "step_by_step"
    language: str = "en"
    difficulty: str = "intermediate"
    question_ids: Optional[List[str]] = None


class VerifyHomeworkRequest(BaseModel):
    question: str = Field(..., min_length=1)
    student_solution: str = Field(..., min_length=1)
    expected_answer: Optional[str] = None
    rubric: Optional[str] = None
    model_id: str = "nvidia/nemotron-3.5-lightning-30b-a3b"
    language: str = "en"


class TutorRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    model_id: str = "nvidia/nemotron-3-ultra-550b-a55b"
    level: str = "intermediate"
    language: str = "en"
    mode: str = "tutor"  # tutor | clarify_step | professor_practice
    context_text: Optional[str] = None


class LanguageTutorRequest(BaseModel):
    text: str = Field(..., min_length=1)
    target_language: str = "English"
    learner_level: str = "B1"
    task: str = "grammar_and_correction"  # grammar_and_correction | translation_review | conversation | vocabulary
    answer_language: str = "en"
    model_id: str = "nvidia/riva-translate-4b-instruct-v2"


class MathToolRequest(BaseModel):
    action: str  # symbolic | plot_1d | plot_2d | numerical
    operation: Optional[str] = "simplify"
    expression: str = "x^2 - 4"
    variable: str = "x"
    compare_expression: Optional[str] = None
    x_min: float = -6.0
    x_max: float = 6.0
    y_min: float = -4.0
    y_max: float = 4.0
    a: float = 0.0
    b: float = 3.0
    x0: float = 1.0
    x1: float = 2.0
    tol: float = 1e-6
    max_iter: int = 25
    steps: int = 8
    matrix_a: Optional[List[List[float]]] = None
    matrix_b: Optional[List[List[float]]] = None
    points_xy: Optional[List[List[float]]] = None


class AlgorithmToolRequest(BaseModel):
    mode: str = "algorithm"  # algorithm | data_structure | pseudocode
    algorithm: str = "bubble_sort"
    array: Optional[List[int]] = None
    target: Optional[int] = None
    graph: Optional[Dict[str, List[Dict[str, Any]]]] = None
    start_node: Optional[str] = None
    structure: str = "stack"
    operations: List[Dict[str, Any]] = Field(default_factory=list)
    code: str = ""
    language: str = "python"


class ElectronicsToolRequest(BaseModel):
    topology: str
    params: Dict[str, Any] = Field(default_factory=dict)


class CodeLabRequest(BaseModel):
    code: str
    stdin_data: str = ""
    test_cases: Optional[List[Dict[str, Any]]] = None
    timeout_seconds: float = 4.0


class NotebookPayload(BaseModel):
    title: str = Field(..., min_length=1)
    course: str = "General"
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    notes_markdown: str = ""
    formula_sheet: List[Dict[str, Any]] = Field(default_factory=list)
    mind_map: Dict[str, Any] = Field(default_factory=dict)
    sources: List[str] = Field(default_factory=list)
    saved_items: List[Dict[str, Any]] = Field(default_factory=list)


class PdfChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    model_id: str = "nvidia/nemotron-3-ultra-550b-a55b"
    document_ids: Optional[List[str]] = None


class CreateDeckRequest(BaseModel):
    title: str = Field(..., min_length=1)
    course: str = "General"
    notebook_id: Optional[str] = None
    cards: List[Dict[str, Any]] = Field(default_factory=list)


class ReviewCardRequest(BaseModel):
    card_id: str
    rating: str = "good"


class QuestionBankPayload(BaseModel):
    notebook_id: Optional[str] = None
    question_text: str = Field(..., min_length=1)
    question_type: str = "short_answer"
    options: List[str] = Field(default_factory=list)
    correct_answer: str = ""
    explanation: str = ""
    difficulty: str = "medium"
    topic: str = "General"
    tags: List[str] = Field(default_factory=list)
    source_ref: Optional[str] = None


class CreateExamRequest(BaseModel):
    title: str = Field(..., min_length=1)
    notebook_id: Optional[str] = None
    mode: str = "practice"
    time_limit_minutes: Optional[int] = 20
    questions: List[Dict[str, Any]] = Field(..., min_length=1)


class SubmitExamRequest(BaseModel):
    answers: Dict[str, str]
    elapsed_seconds: int = 0


class CreatePlanRequest(BaseModel):
    title: str = Field(..., min_length=1)
    exam_date: str
    daily_hours: float = 2.0
    courses: List[Dict[str, Any]] = Field(default_factory=list)
    weak_topics: Optional[List[str]] = None


class UpdatePlanSessionsRequest(BaseModel):
    sessions: List[Dict[str, Any]]


class LectureProcessRequest(BaseModel):
    transcript: str = Field(..., min_length=1)
    title: str = "Lecture Notes"
    model_id: str = "nvidia/nemotron-3.5-bolt-e4b"
    language: str = "en"


class PresentationGenerateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    subtitle: str = ""
    slides: List[Dict[str, Any]] = Field(..., min_length=1)


# --- Documents ---
@router.post("/documents/upload")
async def upload_study_document(
    file: UploadFile = File(...),
    notebook_id: Optional[str] = Form(default=None),
    db: AsyncSession = Depends(get_db),
):
    raw_bytes = await file.read()
    try:
        return await study_service.upload_study_document(
            db=db,
            filename=file.filename or "document.txt",
            raw_bytes=raw_bytes,
            content_type=file.content_type,
            notebook_id=notebook_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/documents")
async def list_study_documents(db: AsyncSession = Depends(get_db)):
    return await artifact_service.list_artifacts(db, origin_type="study_document", limit=100)


@router.get("/documents/{doc_id}")
async def get_study_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    rec = await artifact_service.get_record(db, doc_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return artifact_service.serialize(rec)


@router.put("/documents/{doc_id}/questions")
async def update_study_document_questions(
    doc_id: str,
    req: UpdateDocumentQuestionsRequest,
    db: AsyncSession = Depends(get_db),
):
    rec = await artifact_service.get_record(db, doc_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Document not found")
    meta = json.loads(rec.metadata_json or "{}")
    meta["questions"] = req.questions
    rec.metadata_json = json.dumps(meta, ensure_ascii=False)
    await db.commit()
    return artifact_service.serialize(rec)


@router.delete("/documents/{doc_id}", status_code=204)
async def delete_study_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await artifact_service.delete_artifact(db, doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return None


# --- Assignments & Homework Verifier ---
@router.get("/assignments")
async def list_assignments(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StudyAssignmentRecord).order_by(desc(StudyAssignmentRecord.updated_at)))
    return [study_service.serialize_assignment(a) for a in res.scalars().all()]


@router.post("/assignments", status_code=201)
async def create_assignment(req: CreateAssignmentRequest, db: AsyncSession = Depends(get_db)):
    questions = list(req.questions)
    if not questions and req.artifact_id:
        art = await artifact_service.get_record(db, req.artifact_id)
        if art is not None:
            meta = json.loads(art.metadata_json or "{}")
            questions = meta.get("questions") or []
    for idx, q in enumerate(questions):
        q.setdefault("id", f"q_{idx + 1}")
        q.setdefault("status", "pending")
        q.setdefault("included", True)

    rec = StudyAssignmentRecord(
        id=generate_uuid(),
        notebook_id=req.notebook_id,
        title=req.title.strip(),
        course=req.course.strip(),
        mode=req.mode,
        artifact_id=req.artifact_id,
        questions_json=json.dumps(questions, ensure_ascii=False),
    )
    db.add(rec)
    await db.commit()
    return study_service.serialize_assignment(rec)


@router.get("/assignments/{assignment_id}")
async def get_assignment(assignment_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StudyAssignmentRecord).where(StudyAssignmentRecord.id == assignment_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return study_service.serialize_assignment(rec)


@router.post("/assignments/{assignment_id}/solve")
async def solve_assignment(
    assignment_id: str,
    req: SolveAssignmentRequest,
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(StudyAssignmentRecord).where(StudyAssignmentRecord.id == assignment_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return await study_service.solve_assignment(
        db=db,
        assignment=rec,
        model_id=req.model_id,
        mode=req.mode,
        language=req.language,
        difficulty=req.difficulty,
        question_ids=req.question_ids,
    )


@router.post("/assignments/{assignment_id}/export")
async def export_assignment(
    assignment_id: str,
    fmt: str = Query(default="pdf"),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(StudyAssignmentRecord).where(StudyAssignmentRecord.id == assignment_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    data = study_service.serialize_assignment(rec)
    sections = [
        {
            "heading": f"{q.get('id')} ({q.get('source_ref', 'Question')})",
            "body": f"Question:\n{q.get('question_text', '')}\n\nSolution ({data['mode']}):\n{q.get('solution', 'Pending')}",
        }
        for q in data["questions"]
    ]
    rendered = export_service.generate(fmt=fmt, title=data["title"], sections=sections, json_payload=data)
    return await artifact_service.save_bytes(
        db=db,
        data=rendered["bytes"],
        filename=f"assignment_{rec.id[:8]}.{rendered['ext']}",
        media_type=rendered["media_type"],
        origin_type="study_export",
        origin_id=rec.id,
    )


@router.post("/assignments/verify-homework")
async def verify_homework(req: VerifyHomeworkRequest):
    return await study_service.verify_homework(
        question=req.question,
        student_solution=req.student_solution,
        expected_answer=req.expected_answer,
        rubric=req.rubric,
        model_id=req.model_id,
        language=req.language,
    )


# --- Tutor / Professor Mode & Language Tutor ---
@router.post("/tutor/respond")
async def tutor_respond(req: TutorRequest):
    mode_prompt = {
        "tutor": f"Act as a patient {req.level}-level tutor in {req.language}. Explain clearly with an analogy and a follow-up check question.",
        "clarify_step": f"Clarify the specific step the student highlighted at a {req.level} level in {req.language}.",
        "professor_practice": (
            f"Generate 3 original similar-style practice problems (without claiming they predict an instructor's private exam) "
            f"at {req.level} difficulty in {req.language} based on the provided material, plus worked hints."
        ),
    }.get(req.mode, "Explain step by step.")
    full_prompt = f"{mode_prompt}\n\n{f'Reference Context:{chr(10)}{req.context_text}{chr(10)}{chr(10)}' if req.context_text else ''}Student Request:\n{req.prompt}"
    res = await execution_engine.execute_model(
        model_id=req.model_id,
        prompt=full_prompt,
        system_prompt="You are a pedagogical tutor. Never fabricate citations.",
    )
    return {"status": res.status, "model_id": req.model_id, "response": res.response_text or res.error_message}


@router.post("/language-tutor")
async def language_tutor(req: LanguageTutorRequest):
    prompt = (
        f"Target Language: {req.target_language}\nCEFR Level: {req.learner_level}\n"
        f"Task: {req.task}\nExplanation Language: {req.answer_language}\n\n"
        f"Text:\n{req.text}\n\n"
        "Provide actionable corrections, natural alternatives, grammar notes, and a short contextual practice prompt."
    )
    res = await execution_engine.execute_model(
        model_id=req.model_id,
        prompt=prompt,
        system_prompt="You are an encouraging language tutor providing clear corrections and alternatives.",
    )
    return {"status": res.status, "model_id": req.model_id, "response": res.response_text or res.error_message}


# --- Interactive Deterministic Tools ---
@router.post("/tools/math")
async def math_tool(req: MathToolRequest):
    try:
        if req.action == "symbolic":
            return run_math_operation(
                operation=req.operation or "simplify",
                expression=req.expression,
                variable=req.variable,
                lower=req.a if req.operation == "integrate" and req.a != req.b else None,
                upper=req.b if req.operation == "integrate" and req.a != req.b else None,
                point=req.x0,
                matrix_a=req.matrix_a,
                matrix_b=req.matrix_b,
                compare_expression=req.compare_expression,
            )
        if req.action == "plot_1d":
            return sample_function_1d(req.expression, variable=req.variable, x_min=req.x_min, x_max=req.x_max)
        if req.action == "plot_2d":
            return sample_function_2d(req.expression, x_min=req.x_min, x_max=req.x_max, y_min=req.y_min, y_max=req.y_max)
        if req.action == "numerical":
            return run_numerical_method(
                method=req.operation or "bisection",
                expression=req.expression,
                a=req.a,
                b=req.b,
                x0=req.x0,
                x1=req.x1,
                tol=req.tol,
                max_iter=req.max_iter,
                steps=req.steps,
                points_xy=req.points_xy,
            )
        raise ValueError(f"Unsupported action '{req.action}'")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/tools/algorithms")
async def algorithms_tool(req: AlgorithmToolRequest):
    try:
        if req.mode == "algorithm":
            return run_algorithm_trace(
                algorithm=req.algorithm,
                array=req.array,
                target=req.target,
                graph=req.graph,
                start_node=req.start_node,
            )
        if req.mode == "data_structure":
            return run_data_structure_ops(req.structure, req.operations)
        if req.mode == "pseudocode":
            return generate_pseudocode(req.code, language=req.language)
        raise ValueError(f"Unsupported mode '{req.mode}'")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/tools/electronics")
async def electronics_tool(req: ElectronicsToolRequest):
    try:
        return solve_circuit(req.topology, req.params)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/tools/code-lab")
async def code_lab_tool(req: CodeLabRequest):
    return execute_python_sandbox(
        code=req.code,
        stdin_data=req.stdin_data,
        test_cases=req.test_cases,
        timeout_seconds=req.timeout_seconds,
    )


# --- Notebooks, PDF Chat, Research, Mind Maps, Formula Sheets ---
@router.get("/notebooks")
async def list_notebooks(q: Optional[str] = Query(default=None), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StudyNotebookRecord).order_by(desc(StudyNotebookRecord.updated_at)))
    items = [study_service.serialize_notebook(n) for n in res.scalars().all()]
    if q:
        ql = q.lower().strip()
        items = [n for n in items if ql in n["title"].lower() or ql in n["course"].lower() or ql in n["notes_markdown"].lower()]
    return items


@router.post("/notebooks", status_code=201)
async def create_notebook(req: NotebookPayload, db: AsyncSession = Depends(get_db)):
    rec = StudyNotebookRecord(
        id=generate_uuid(),
        title=req.title.strip(),
        course=req.course.strip(),
        description=req.description.strip(),
        tags_json=json.dumps(req.tags, ensure_ascii=False),
        notes_markdown=req.notes_markdown,
        formula_sheet_json=json.dumps(req.formula_sheet, ensure_ascii=False),
        mind_map_json=json.dumps(req.mind_map, ensure_ascii=False),
        sources_json=json.dumps(req.sources, ensure_ascii=False),
        saved_items_json=json.dumps(req.saved_items, ensure_ascii=False),
    )
    db.add(rec)
    await db.commit()
    return study_service.serialize_notebook(rec)


@router.get("/notebooks/{notebook_id}")
async def get_notebook(notebook_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StudyNotebookRecord).where(StudyNotebookRecord.id == notebook_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return study_service.serialize_notebook(rec)


@router.put("/notebooks/{notebook_id}")
async def update_notebook(notebook_id: str, req: NotebookPayload, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StudyNotebookRecord).where(StudyNotebookRecord.id == notebook_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Notebook not found")
    rec.title = req.title.strip()
    rec.course = req.course.strip()
    rec.description = req.description.strip()
    rec.tags_json = json.dumps(req.tags, ensure_ascii=False)
    rec.notes_markdown = req.notes_markdown
    rec.formula_sheet_json = json.dumps(req.formula_sheet, ensure_ascii=False)
    rec.mind_map_json = json.dumps(req.mind_map, ensure_ascii=False)
    rec.sources_json = json.dumps(req.sources, ensure_ascii=False)
    rec.saved_items_json = json.dumps(req.saved_items, ensure_ascii=False)
    rec.updated_at = get_utc_now()
    await db.commit()
    return study_service.serialize_notebook(rec)


@router.delete("/notebooks/{notebook_id}", status_code=204)
async def delete_notebook(notebook_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StudyNotebookRecord).where(StudyNotebookRecord.id == notebook_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Notebook not found")
    await db.delete(rec)
    await db.commit()
    return None


@router.post("/notebooks/{notebook_id}/pdf-chat")
async def notebook_pdf_chat(notebook_id: str, req: PdfChatRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StudyNotebookRecord).where(StudyNotebookRecord.id == notebook_id))
    nb = res.scalar_one_or_none()
    if nb is None:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return await study_service.pdf_chat(db, nb, req.question, req.model_id, document_ids=req.document_ids)


@router.post("/notebooks/{notebook_id}/research-compare")
async def notebook_research_compare(notebook_id: str, req: PdfChatRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StudyNotebookRecord).where(StudyNotebookRecord.id == notebook_id))
    nb = res.scalar_one_or_none()
    if nb is None:
        raise HTTPException(status_code=404, detail="Notebook not found")
    chat_res = await study_service.pdf_chat(
        db,
        nb,
        f"Compare claims, methodologies, agreements, and contradictions across sources regarding: {req.question}",
        req.model_id,
        document_ids=req.document_ids,
    )
    cit_check = validate_citations(chat_res.get("answer") or "")
    return {**chat_res, "citation_check": cit_check}


@router.post("/notebooks/{notebook_id}/formula-export")
async def export_notebook_formulas(
    notebook_id: str,
    fmt: str = Query(default="pdf"),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(StudyNotebookRecord).where(StudyNotebookRecord.id == notebook_id))
    nb = res.scalar_one_or_none()
    if nb is None:
        raise HTTPException(status_code=404, detail="Notebook not found")
    formulas = json.loads(nb.formula_sheet_json or "[]")
    sections = [
        {
            "heading": f.get("name", "Formula"),
            "body": f"Expression: {f.get('formula', '')}\nAssumptions: {f.get('assumptions', '')}\nUnits: {f.get('units', '')}\nExample: {f.get('example', '')}",
        }
        for f in formulas
    ] or [{"heading": "Notes", "body": nb.notes_markdown or "Empty formula sheet"}]
    rendered = export_service.generate(fmt=fmt, title=f"Formula Sheet: {nb.title}", sections=sections)
    return await artifact_service.save_bytes(
        db,
        data=rendered["bytes"],
        filename=f"formula_sheet_{nb.id[:8]}.{rendered['ext']}",
        media_type=rendered["media_type"],
        origin_type="study_export",
        origin_id=nb.id,
    )


# --- Flashcards & Question Bank ---
@router.get("/decks")
async def list_decks(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(FlashcardDeckRecord).order_by(desc(FlashcardDeckRecord.updated_at)))
    return [study_service.serialize_deck(d) for d in res.scalars().all()]


@router.post("/decks", status_code=201)
async def create_deck(req: CreateDeckRequest, db: AsyncSession = Depends(get_db)):
    cards = []
    seen_q = set()
    for c in req.cards:
        front = str(c.get("front", "")).strip()
        if not front or front.lower() in seen_q:
            continue
        seen_q.add(front.lower())
        cards.append({
            "id": c.get("id") or generate_uuid(),
            "front": front,
            "back": str(c.get("back", "")).strip(),
            "source_ref": c.get("source_ref", ""),
            "repetitions": int(c.get("repetitions", 0)),
            "interval_days": int(c.get("interval_days", 0)),
            "ease_factor": float(c.get("ease_factor", 2.5)),
            "due_at": c.get("due_at"),
        })
    rec = FlashcardDeckRecord(
        id=generate_uuid(),
        notebook_id=req.notebook_id,
        title=req.title.strip(),
        course=req.course.strip(),
        cards_json=json.dumps(cards, ensure_ascii=False),
    )
    db.add(rec)
    await db.commit()
    return study_service.serialize_deck(rec)


@router.post("/decks/{deck_id}/review")
async def review_deck_card(deck_id: str, req: ReviewCardRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(FlashcardDeckRecord).where(FlashcardDeckRecord.id == deck_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    cards = json.loads(rec.cards_json or "[]")
    updated = study_service.review_flashcard(cards, req.card_id, req.rating)
    rec.cards_json = json.dumps(updated, ensure_ascii=False)
    rec.updated_at = get_utc_now()
    await db.commit()
    return study_service.serialize_deck(rec)


@router.get("/decks/{deck_id}/export")
async def export_deck(deck_id: str, fmt: str = Query(default="csv"), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(FlashcardDeckRecord).where(FlashcardDeckRecord.id == deck_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    cards = json.loads(rec.cards_json or "[]")
    rows = [["Front", "Back", "Source", "IntervalDays", "EaseFactor"]] + [
        [c.get("front", ""), c.get("back", ""), c.get("source_ref", ""), c.get("interval_days", 0), c.get("ease_factor", 2.5)]
        for c in cards
    ]
    rendered = export_service.generate(fmt=fmt, title=rec.title, csv_rows=rows, json_payload=study_service.serialize_deck(rec))
    return await artifact_service.save_bytes(
        db,
        data=rendered["bytes"],
        filename=f"deck_{rec.id[:8]}.{rendered['ext']}",
        media_type=rendered["media_type"],
        origin_type="study_export",
        origin_id=rec.id,
    )


@router.get("/question-bank")
async def list_question_bank(
    topic: Optional[str] = Query(default=None),
    needs_practice: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(QuestionBankItemRecord).order_by(desc(QuestionBankItemRecord.created_at))
    if topic:
        stmt = stmt.where(QuestionBankItemRecord.topic == topic)
    if needs_practice is not None:
        stmt = stmt.where(QuestionBankItemRecord.needs_practice == needs_practice)
    res = await db.execute(stmt)
    return [
        {
            "id": q.id,
            "notebook_id": q.notebook_id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": json.loads(q.options_json or "[]"),
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "difficulty": q.difficulty,
            "topic": q.topic,
            "tags": json.loads(q.tags_json or "[]"),
            "source_ref": q.source_ref,
            "attempts_count": q.attempts_count,
            "correct_count": q.correct_count,
            "needs_practice": q.needs_practice,
        }
        for q in res.scalars().all()
    ]


@router.post("/question-bank", status_code=201)
async def add_question_bank_item(req: QuestionBankPayload, db: AsyncSession = Depends(get_db)):
    rec = QuestionBankItemRecord(
        id=generate_uuid(),
        notebook_id=req.notebook_id,
        question_text=req.question_text.strip(),
        question_type=req.question_type,
        options_json=json.dumps(req.options, ensure_ascii=False),
        correct_answer=req.correct_answer.strip(),
        explanation=req.explanation.strip(),
        difficulty=req.difficulty,
        topic=req.topic.strip(),
        tags_json=json.dumps(req.tags, ensure_ascii=False),
        source_ref=req.source_ref,
    )
    db.add(rec)
    await db.commit()
    return {"id": rec.id, "question_text": rec.question_text, "topic": rec.topic, "difficulty": rec.difficulty}


# --- Exams, Analytics & Weakness Detector ---
@router.get("/exams")
async def list_exams(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ExamRecord).order_by(desc(ExamRecord.updated_at)))
    return [study_service.serialize_exam(e) for e in res.scalars().all()]


@router.post("/exams", status_code=201)
async def create_exam(req: CreateExamRequest, db: AsyncSession = Depends(get_db)):
    questions = []
    for idx, q in enumerate(req.questions):
        item = dict(q)
        item.setdefault("id", f"eq_{idx + 1}")
        questions.append(item)
    rec = ExamRecord(
        id=generate_uuid(),
        notebook_id=req.notebook_id,
        title=req.title.strip(),
        mode=req.mode,
        time_limit_minutes=req.time_limit_minutes,
        questions_json=json.dumps(questions, ensure_ascii=False),
        attempts_json="[]",
    )
    db.add(rec)
    await db.commit()
    return study_service.serialize_exam(rec)


@router.post("/exams/{exam_id}/submit")
async def submit_exam(exam_id: str, req: SubmitExamRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ExamRecord).where(ExamRecord.id == exam_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    return await study_service.submit_exam(db, rec, req.answers, elapsed_seconds=req.elapsed_seconds)


@router.get("/analytics")
async def get_study_analytics(db: AsyncSession = Depends(get_db)):
    return await study_service.compute_analytics(db)


# --- Study Planner ---
@router.get("/planner")
async def list_study_plans(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StudyPlanRecord).order_by(desc(StudyPlanRecord.updated_at)))
    return [study_service.serialize_plan(p) for p in res.scalars().all()]


@router.post("/planner", status_code=201)
async def create_study_plan(req: CreatePlanRequest, db: AsyncSession = Depends(get_db)):
    sessions = study_service.build_study_sessions(
        exam_date_str=req.exam_date,
        daily_hours=req.daily_hours,
        courses=req.courses,
        weak_topics=req.weak_topics,
    )
    rec = StudyPlanRecord(
        id=generate_uuid(),
        title=req.title.strip(),
        exam_date=req.exam_date,
        daily_hours=req.daily_hours,
        courses_json=json.dumps(req.courses, ensure_ascii=False),
        sessions_json=json.dumps(sessions, ensure_ascii=False),
    )
    db.add(rec)
    await db.commit()
    return study_service.serialize_plan(rec)


@router.put("/planner/{plan_id}")
async def update_study_plan_sessions(plan_id: str, req: UpdatePlanSessionsRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StudyPlanRecord).where(StudyPlanRecord.id == plan_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Study plan not found")
    rec.sessions_json = json.dumps(req.sessions, ensure_ascii=False)
    rec.updated_at = get_utc_now()
    await db.commit()
    return study_service.serialize_plan(rec)


@router.post("/planner/{plan_id}/export-ics")
async def export_study_plan_ics(plan_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(StudyPlanRecord).where(StudyPlanRecord.id == plan_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Study plan not found")
    sessions = json.loads(rec.sessions_json or "[]")
    rendered = export_service.generate(fmt="ics", title=rec.title, ics_sessions=sessions)
    return await artifact_service.save_bytes(
        db,
        data=rendered["bytes"],
        filename=f"study_plan_{rec.id[:8]}.ics",
        media_type=rendered["media_type"],
        origin_type="study_export",
        origin_id=rec.id,
    )


# --- Lecture Assistant & Presentation Maker ---
@router.get("/lecture/status")
async def get_lecture_tooling_status():
    tooling = check_local_tooling()
    return {
        **tooling,
        "offline_audio_ready": tooling["faster_whisper"] or tooling["openai_whisper"],
        "consent_notice": "Recordings must comply with instructor and participant recording consent policies.",
    }


@router.post("/lecture/process")
async def process_lecture_transcript(req: LectureProcessRequest):
    prompt = (
        f"Lecture Title: {req.title}\nLanguage: {req.language}\n\n"
        f"Transcript:\n{req.transcript[:16000]}\n\n"
        "Create: (1) structured outline with timestamp links if present, "
        "(2) key terms & definitions, (3) 5 study flashcards, and (4) 3 self-test questions."
    )
    res = await execution_engine.execute_model(
        model_id=req.model_id,
        prompt=prompt,
        system_prompt="You are a lecture assistant. Preserve timestamp references accurately and note possible transcript typos.",
    )
    return {"status": res.status, "model_id": req.model_id, "notes": res.response_text or res.error_message}


@router.post("/presentations/generate")
async def generate_presentation_pptx(req: PresentationGenerateRequest, db: AsyncSession = Depends(get_db)):
    rendered = export_service.generate(
        fmt="pptx",
        title=req.title,
        slides=req.slides,
    )
    return await artifact_service.save_bytes(
        db,
        data=rendered["bytes"],
        filename=f"presentation_{generate_uuid()[:8]}.pptx",
        media_type=rendered["media_type"],
        origin_type="study_presentation",
        metadata={"slide_count": len(req.slides), "subtitle": req.subtitle},
    )
