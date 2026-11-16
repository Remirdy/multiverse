import uuid
from typing import List, Optional
from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.database.models import Conversation, ComparisonTurn, ModelResponseRecord
from app.providers.nvidia import nvidia_provider
from app.providers.registry import model_registry
from app.schemas.compare import ModelResult, CompareResponse

class CompareService:
    async def compare_models(
        self,
        prompt: str,
        model_ids: List[str],
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        timeout: Optional[float] = None,
        db: Optional[AsyncSession] = None
    ) -> CompareResponse:
        # Enforce timeout & model limits
        effective_timeout = timeout or settings.DEFAULT_TIMEOUT_SECONDS
        sanitized_model_ids = [m for m in model_ids if model_registry.exists(m)][:settings.MAX_CONCURRENT_MODELS]
        if not sanitized_model_ids:
            sanitized_model_ids = model_registry.get_default_model_ids()[:3]

        # Dispatch async tasks concurrently
        tasks = [
            nvidia_provider.generate(
                model_id=mid,
                prompt=prompt,
                system_prompt=system_prompt,
                timeout=effective_timeout
            )
            for mid in sanitized_model_ids
        ]

        # Concurrency safety: asyncio.gather with return_exceptions=True
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        results: List[ModelResult] = []
        for mid, outcome in zip(sanitized_model_ids, raw_results):
            model_info = model_registry.get(mid)
            model_name = model_info.name if model_info else mid
            provider_name = model_info.provider if model_info else "NVIDIA NIM"

            if isinstance(outcome, Exception):
                results.append(ModelResult(
                    model_id=mid,
                    model_name=model_name,
                    provider=provider_name,
                    response_text=None,
                    response_time_ms=None,
                    status="error",
                    error_message=f"Request failed unexpectedly: {str(outcome)}"
                ))
            else:
                results.append(ModelResult(
                    model_id=outcome.model_id,
                    model_name=outcome.model_name,
                    provider=outcome.provider,
                    response_text=outcome.response_text,
                    response_time_ms=outcome.response_time_ms,
                    status=outcome.status,
                    error_message=outcome.error_message
                ))

        # Persistence handling
        turn_id = str(uuid.uuid4())
        if db is not None:
            conv_id = conversation_id
            if conv_id:
                stmt = select(Conversation).where(Conversation.id == conv_id)
                res = await db.execute(stmt)
                conv = res.scalar_one_or_none()
                if not conv:
                    conv = Conversation(
                        id=conv_id,
                        title=prompt[:45].strip() + ("..." if len(prompt) > 45 else "")
                    )
                    db.add(conv)
                else:
                    conv.updated_at = datetime.utcnow()
            else:
                conv_id = str(uuid.uuid4())
                conv = Conversation(
                    id=conv_id,
                    title=prompt[:45].strip() + ("..." if len(prompt) > 45 else "")
                )
                db.add(conv)

            turn = ComparisonTurn(
                id=turn_id,
                conversation_id=conv_id,
                prompt=prompt,
                system_prompt=system_prompt
            )
            db.add(turn)

            for r in results:
                db_resp = ModelResponseRecord(
                    turn_id=turn_id,
                    conversation_id=conv_id,
                    model_id=r.model_id,
                    model_name=r.model_name,
                    provider=r.provider,
                    response_text=r.response_text,
                    response_time_ms=r.response_time_ms,
                    status=r.status,
                    error_message=r.error_message
                )
                db.add(db_resp)

            await db.commit()
        else:
            conv_id = conversation_id or str(uuid.uuid4())

        successful_count = sum(1 for r in results if r.status == "success")
        failed_count = len(results) - successful_count

        return CompareResponse(
            conversation_id=conv_id,
            turn_id=turn_id,
            prompt=prompt,
            results=results,
            total_models=len(results),
            successful_models=successful_count,
            failed_models=failed_count
        )

    async def retry_single_model(
        self,
        conversation_id: str,
        turn_id: str,
        model_id: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: Optional[float] = None,
        db: Optional[AsyncSession] = None
    ) -> ModelResult:
        effective_timeout = timeout or settings.DEFAULT_TIMEOUT_SECONDS
        outcome = await nvidia_provider.generate(
            model_id=model_id,
            prompt=prompt,
            system_prompt=system_prompt,
            timeout=effective_timeout
        )

        model_info = model_registry.get(model_id)
        model_name = model_info.name if model_info else model_id

        result = ModelResult(
            model_id=outcome.model_id,
            model_name=outcome.model_name,
            provider=outcome.provider,
            response_text=outcome.response_text,
            response_time_ms=outcome.response_time_ms,
            status=outcome.status,
            error_message=outcome.error_message
        )

        if db is not None:
            # Update or insert record in DB
            stmt = select(ModelResponseRecord).where(
                ModelResponseRecord.turn_id == turn_id,
                ModelResponseRecord.model_id == model_id
            )
            res = await db.execute(stmt)
            existing = res.scalar_one_or_none()
            if existing:
                existing.response_text = result.response_text
                existing.response_time_ms = result.response_time_ms
                existing.status = result.status
                existing.error_message = result.error_message
                existing.created_at = datetime.utcnow()
            else:
                db_record = ModelResponseRecord(
                    turn_id=turn_id,
                    conversation_id=conversation_id,
                    model_id=result.model_id,
                    model_name=result.model_name,
                    provider=result.provider,
                    response_text=result.response_text,
                    response_time_ms=result.response_time_ms,
                    status=result.status,
                    error_message=result.error_message
                )
                db.add(db_record)
            await db.commit()

        return result

compare_service = CompareService()
