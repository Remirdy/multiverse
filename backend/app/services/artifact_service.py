import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.models import ArtifactRecord, generate_uuid


def sanitize_filename(filename: str) -> str:
    """Strip path traversal and unsafe characters from filenames."""
    base = Path(filename or "artifact.bin").name
    cleaned = re.sub(r"[^a-zA-Z0-9._\-\u00c0-\u024f\u0400-\u04ff ]", "_", base).strip()
    cleaned = cleaned.lstrip(".") or "artifact.bin"
    return cleaned[:180]


class ArtifactService:
    """Manages content-hashed local artifact storage and metadata persistence."""

    def __init__(self, artifacts_dir: Optional[Path] = None):
        self.artifacts_dir = (artifacts_dir or settings.ARTIFACTS_DIR).resolve()
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def _safe_artifact_path(self, artifact_id: str, safe_name: str) -> Path:
        target = (self.artifacts_dir / f"{artifact_id}_{safe_name}").resolve()
        if not str(target).startswith(str(self.artifacts_dir)):
            raise ValueError("Resolved artifact path escapes storage root")
        return target

    async def save_bytes(
        self,
        db: AsyncSession,
        data: bytes,
        filename: str,
        media_type: str,
        origin_type: str = "upload",
        origin_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        artifact_id = generate_uuid()
        safe_name = sanitize_filename(filename)
        digest = hashlib.sha256(data).hexdigest()
        file_path = self._safe_artifact_path(artifact_id, safe_name)
        file_path.write_bytes(data)

        record = ArtifactRecord(
            id=artifact_id,
            filename=safe_name,
            media_type=media_type,
            size_bytes=len(data),
            content_hash=digest,
            storage_path=str(file_path),
            origin_type=origin_type,
            origin_id=origin_id,
            metadata_json=json.dumps(metadata or {}, ensure_ascii=False),
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return self.serialize(record)

    async def get_record(self, db: AsyncSession, artifact_id: str) -> Optional[ArtifactRecord]:
        res = await db.execute(select(ArtifactRecord).where(ArtifactRecord.id == artifact_id))
        return res.scalar_one_or_none()

    async def list_artifacts(
        self,
        db: AsyncSession,
        origin_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        stmt = select(ArtifactRecord).order_by(desc(ArtifactRecord.created_at)).limit(limit)
        if origin_type:
            stmt = select(ArtifactRecord).where(ArtifactRecord.origin_type == origin_type).order_by(desc(ArtifactRecord.created_at)).limit(limit)
        res = await db.execute(stmt)
        return [self.serialize(rec) for rec in res.scalars().all()]

    async def delete_artifact(self, db: AsyncSession, artifact_id: str) -> bool:
        rec = await self.get_record(db, artifact_id)
        if rec is None:
            return False
        path = Path(rec.storage_path).resolve()
        if str(path).startswith(str(self.artifacts_dir)) and path.exists():
            path.unlink()
        await db.delete(rec)
        await db.commit()
        return True

    def read_bytes(self, rec: ArtifactRecord) -> bytes:
        path = Path(rec.storage_path).resolve()
        if not str(path).startswith(str(self.artifacts_dir)) or not path.exists():
            raise FileNotFoundError("Artifact binary not found")
        return path.read_bytes()

    @staticmethod
    def serialize(rec: ArtifactRecord) -> Dict[str, Any]:
        return {
            "id": rec.id,
            "filename": rec.filename,
            "media_type": rec.media_type,
            "size_bytes": rec.size_bytes,
            "content_hash": rec.content_hash,
            "origin_type": rec.origin_type,
            "origin_id": rec.origin_id,
            "metadata": json.loads(rec.metadata_json) if rec.metadata_json else {},
            "download_url": f"/api/artifacts/{rec.id}/download",
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
        }


artifact_service = ArtifactService()
