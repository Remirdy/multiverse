from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.artifact_service import artifact_service

router = APIRouter(prefix="/artifacts", tags=["Artifacts"])


@router.get("")
async def list_artifacts(
    origin_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    return await artifact_service.list_artifacts(db, origin_type=origin_type, limit=limit)


@router.get("/{artifact_id}")
async def get_artifact_metadata(artifact_id: str, db: AsyncSession = Depends(get_db)):
    rec = await artifact_service.get_record(db, artifact_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact_service.serialize(rec)


@router.get("/{artifact_id}/download")
async def download_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    rec = await artifact_service.get_record(db, artifact_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    try:
        content = artifact_service.read_bytes(rec)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    headers = {"Content-Disposition": f'attachment; filename="{rec.filename}"'}
    return Response(content=content, media_type=rec.media_type, headers=headers)


@router.delete("/{artifact_id}", status_code=204)
async def delete_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await artifact_service.delete_artifact(db, artifact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return None
