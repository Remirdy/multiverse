import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.council.service import BUILTIN_ROLES, council_service
from app.database.models import CouncilPresetRecord, CouncilSessionRecord, generate_uuid
from app.database.session import get_db
from app.execution.engine import ExecutionBudget

router = APIRouter(prefix="/council", tags=["Council"])


class CouncilMemberConfig(BaseModel):
    role_id: str = "reviewer"
    model_id: str
    instructions: Optional[str] = None


class CouncilEstimateRequest(BaseModel):
    members: List[CouncilMemberConfig]
    review_rounds: int = 1
    enable_review: bool = True


class CreateCouncilPresetRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str = ""
    config: Dict[str, Any]


class CreateCouncilSessionRequest(BaseModel):
    title: Optional[str] = None
    prompt: str = Field(..., min_length=1)
    preset_id: Optional[str] = None
    members: List[CouncilMemberConfig] = Field(..., min_length=1)
    chair_model_id: str
    review_rounds: int = Field(default=1, ge=0, le=2)
    enable_review: bool = True
    enable_verification: bool = True
    instructions: Optional[str] = None
    attachments: Optional[list] = None
    budget: Optional[ExecutionBudget] = None
    pause_after_proposals: bool = False


class RetryMemberRequest(BaseModel):
    member_index: int = Field(..., ge=0)


class CouncilExportRequest(BaseModel):
    format: str = "pdf"
    include_full: bool = True


@router.get("/roles")
async def get_council_roles():
    return BUILTIN_ROLES


@router.get("/presets")
async def list_council_presets(db: AsyncSession = Depends(get_db)):
    return await council_service.ensure_builtin_presets(db)


@router.post("/presets", status_code=201)
async def create_council_preset(req: CreateCouncilPresetRequest, db: AsyncSession = Depends(get_db)):
    pid = generate_uuid()
    rec = CouncilPresetRecord(
        id=pid,
        name=req.name.strip(),
        description=req.description.strip(),
        config_json=json.dumps(req.config, ensure_ascii=False),
        is_builtin=False,
    )
    db.add(rec)
    await db.commit()
    return {
        "id": rec.id,
        "name": rec.name,
        "description": rec.description,
        "config": req.config,
        "is_builtin": False,
    }


@router.delete("/presets/{preset_id}", status_code=204)
async def delete_council_preset(preset_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CouncilPresetRecord).where(CouncilPresetRecord.id == preset_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Preset not found")
    if rec.is_builtin:
        raise HTTPException(status_code=400, detail="Built-in presets cannot be deleted")
    await db.delete(rec)
    await db.commit()
    return None


@router.post("/estimate")
async def estimate_council_run(req: CouncilEstimateRequest):
    return council_service.estimate_calls({
        "members": [m.model_dump() for m in req.members],
        "review_rounds": req.review_rounds,
        "enable_review": req.enable_review,
    })


@router.get("/sessions")
async def list_council_sessions(
    status: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(CouncilSessionRecord).order_by(desc(CouncilSessionRecord.updated_at)).limit(limit)
    if status:
        stmt = select(CouncilSessionRecord).where(CouncilSessionRecord.status == status).order_by(desc(CouncilSessionRecord.updated_at)).limit(limit)
    res = await db.execute(stmt)
    sessions = [council_service.serialize_session(s) for s in res.scalars().all()]
    if q:
        ql = q.lower().strip()
        sessions = [s for s in sessions if ql in s["title"].lower() or ql in s["prompt"].lower()]
    return sessions


@router.post("/sessions", status_code=201)
async def create_and_run_council_session(
    req: CreateCouncilSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await council_service.run_session(
            db=db,
            prompt=req.prompt,
            members=[m.model_dump() for m in req.members],
            chair_model_id=req.chair_model_id,
            title=req.title,
            preset_id=req.preset_id,
            review_rounds=req.review_rounds,
            enable_review=req.enable_review,
            enable_verification=req.enable_verification,
            instructions=req.instructions,
            attachments=req.attachments,
            budget=req.budget,
            pause_after_proposals=req.pause_after_proposals,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/sessions/{session_id}")
async def get_council_session(session_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CouncilSessionRecord).where(CouncilSessionRecord.id == session_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Council session not found")
    return council_service.serialize_session(rec)


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_council_session(session_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CouncilSessionRecord).where(CouncilSessionRecord.id == session_id))
    rec = res.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="Council session not found")
    await db.delete(rec)
    await db.commit()
    return None


@router.post("/sessions/{session_id}/resume")
async def resume_council_session(session_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await council_service.resume_session(db, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/sessions/{session_id}/retry-member")
async def retry_council_member(
    session_id: str,
    req: RetryMemberRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await council_service.retry_member(db, session_id, req.member_index)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/sessions/{session_id}/fork", status_code=201)
async def fork_council_session(session_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CouncilSessionRecord).where(CouncilSessionRecord.id == session_id))
    src = res.scalar_one_or_none()
    if src is None:
        raise HTTPException(status_code=404, detail="Council session not found")
    cfg = json.loads(src.config_json)
    return await council_service.run_session(
        db=db,
        prompt=src.prompt,
        members=cfg.get("members", []),
        chair_model_id=cfg.get("chair_model_id", "nvidia/nemotron-3-ultra-550b-a55b"),
        title=f"{src.title} (Fork)",
        preset_id=src.preset_id,
        review_rounds=cfg.get("review_rounds", 1),
        enable_review=cfg.get("enable_review", True),
        enable_verification=cfg.get("enable_verification", True),
        instructions=cfg.get("instructions"),
    )


@router.post("/sessions/{session_id}/export")
async def export_council_session(
    session_id: str,
    req: CouncilExportRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await council_service.export_session(
            db=db, session_id=session_id, fmt=req.format, include_full=req.include_full
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
