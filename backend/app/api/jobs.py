import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db, AsyncSessionLocal
from app.database.models import JobRecord, JobEventRecord
from app.execution.engine import job_manager

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("")
async def list_jobs(limit: int = Query(default=30, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(JobRecord).order_by(desc(JobRecord.created_at)).limit(limit))
    return [job_manager.serialize_job(job) for job in res.scalars().all()]


@router.get("/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(JobRecord).where(JobRecord.id == job_id))
    job = res.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    events_res = await db.execute(
        select(JobEventRecord)
        .where(JobEventRecord.job_id == job_id)
        .order_by(JobEventRecord.sequence)
    )
    events = [
        {
            "sequence": ev.sequence,
            "event_type": ev.event_type,
            "payload": json.loads(ev.payload_json) if ev.payload_json else {},
            "created_at": ev.created_at.isoformat() if ev.created_at else None,
        }
        for ev in events_res.scalars().all()
    ]
    data = job_manager.serialize_job(job)
    data["events"] = events
    return data


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await job_manager.request_cancel(job_id, db)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@router.get("/{job_id}/events")
async def stream_job_events(job_id: str, since: int = Query(default=0, ge=0)):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(JobRecord).where(JobRecord.id == job_id))
        if res.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Job not found")

    async def event_stream():
        last_seq = since
        terminal = {"succeeded", "partially_succeeded", "failed", "canceled"}
        for _ in range(120):
            async with AsyncSessionLocal() as session:
                ev_res = await session.execute(
                    select(JobEventRecord)
                    .where(JobEventRecord.job_id == job_id, JobEventRecord.sequence > last_seq)
                    .order_by(JobEventRecord.sequence)
                )
                for ev in ev_res.scalars().all():
                    last_seq = ev.sequence
                    payload = {
                        "sequence": ev.sequence,
                        "event_type": ev.event_type,
                        "payload": json.loads(ev.payload_json) if ev.payload_json else {},
                        "created_at": ev.created_at.isoformat() if ev.created_at else None,
                    }
                    yield f"id: {ev.sequence}\nevent: {ev.event_type}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

                job_res = await session.execute(select(JobRecord.status).where(JobRecord.id == job_id))
                status = job_res.scalar_one_or_none()
                if status in terminal or status is None:
                    yield f"event: end\ndata: {json.dumps({'job_id': job_id, 'status': status})}\n\n"
                    break
            await asyncio.sleep(0.25)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
