import asyncio
import json
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.models import JobRecord, JobEventRecord, generate_uuid, get_utc_now
from app.database.session import AsyncSessionLocal
from app.providers.base import ProviderResponse
from app.providers.nvidia import nvidia_provider
from app.providers.local_openai import local_openai_provider
from app.providers.registry import model_registry


FakeModelCallable = Callable[
    [str, str, Optional[str], float, Optional[list]],
    Awaitable[ProviderResponse] | ProviderResponse,
]

_test_provider_fake: Optional[FakeModelCallable] = None


def set_test_provider_fake(fake_fn: Optional[FakeModelCallable]) -> None:
    """Register or clear an explicit test-only fake model runner."""
    global _test_provider_fake
    _test_provider_fake = fake_fn


class ExecutionBudget(BaseModel):
    max_calls: int = Field(default=settings.DEFAULT_MAX_CALLS_PER_RUN, ge=1, le=100)
    max_tokens: Optional[int] = Field(default=None, ge=64)
    max_duration_seconds: float = Field(default=180.0, ge=5.0, le=900.0)
    max_parallel: int = Field(default=settings.MAX_CONCURRENT_MODELS, ge=1, le=12)
    local_only: bool = Field(default=settings.LOCAL_ONLY_DEFAULT)
    free_only: bool = Field(default=settings.FREE_ONLY_DEFAULT)


class ExecutionPolicy(BaseModel):
    local_only: bool = settings.LOCAL_ONLY_DEFAULT
    free_only: bool = settings.FREE_ONLY_DEFAULT
    max_calls_per_run: int = settings.DEFAULT_MAX_CALLS_PER_RUN
    max_parallel: int = settings.MAX_CONCURRENT_MODELS


class JobManager:
    """Manages durable background/long-running jobs and ordered execution events."""

    def __init__(self):
        self._cancel_flags: Dict[str, bool] = {}

    def is_canceled(self, job_id: Optional[str]) -> bool:
        if not job_id:
            return False
        return self._cancel_flags.get(job_id, False)

    async def create_job(
        self,
        job_type: str,
        budget: Optional[ExecutionBudget] = None,
        db: Optional[AsyncSession] = None,
    ) -> str:
        job_id = generate_uuid()
        self._cancel_flags[job_id] = False
        budget_json = budget.model_dump_json() if budget else None

        async def _persist(session: AsyncSession):
            rec = JobRecord(
                id=job_id,
                job_type=job_type,
                status="queued",
                progress_phase="queued",
                budget_json=budget_json,
                usage_json=json.dumps({"calls": 0, "tokens": 0}),
            )
            session.add(rec)
            await session.commit()

        if db is not None:
            await _persist(db)
        else:
            async with AsyncSessionLocal() as session:
                await _persist(session)
        return job_id

    async def append_event(
        self,
        job_id: str,
        event_type: str,
        payload: Dict[str, Any],
        status: Optional[str] = None,
        progress_phase: Optional[str] = None,
        usage: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> int:
        async def _persist(session: AsyncSession) -> int:
            res = await session.execute(select(JobRecord).where(JobRecord.id == job_id))
            job = res.scalar_one_or_none()
            if job is None:
                return 0
            if status is not None:
                job.status = status
            if progress_phase is not None:
                job.progress_phase = progress_phase
            if usage is not None:
                job.usage_json = json.dumps(usage, ensure_ascii=False)
            if result is not None:
                job.result_json = json.dumps(result, ensure_ascii=False)
            if error_message is not None:
                job.error_message = error_message
            job.updated_at = get_utc_now()

            seq_res = await session.execute(
                select(JobEventRecord.sequence)
                .where(JobEventRecord.job_id == job_id)
                .order_by(desc(JobEventRecord.sequence))
                .limit(1)
            )
            last_seq = seq_res.scalar_one_or_none() or 0
            next_seq = last_seq + 1
            session.add(
                JobEventRecord(
                    job_id=job_id,
                    sequence=next_seq,
                    event_type=event_type,
                    payload_json=json.dumps(payload, ensure_ascii=False),
                )
            )
            await session.commit()
            return next_seq

        if db is not None:
            return await _persist(db)
        async with AsyncSessionLocal() as session:
            return await _persist(session)

    async def request_cancel(self, job_id: str, db: AsyncSession) -> Optional[Dict[str, Any]]:
        self._cancel_flags[job_id] = True
        res = await db.execute(select(JobRecord).where(JobRecord.id == job_id))
        job = res.scalar_one_or_none()
        if job is None:
            return None
        job.cancel_requested = True
        if job.status in {"queued", "running", "waiting_for_approval"}:
            job.status = "canceled"
            job.progress_phase = "canceled"
        await db.commit()
        await self.append_event(
            job_id,
            "job_canceled",
            {"job_id": job_id, "status": job.status},
            status=job.status,
            progress_phase=job.progress_phase,
            db=db,
        )
        return self.serialize_job(job)

    async def check_canceled(self, job_id: Optional[str], db: Optional[AsyncSession] = None) -> bool:
        if not job_id:
            return False
        if self._cancel_flags.get(job_id):
            return True
        if db is not None:
            res = await db.execute(select(JobRecord.cancel_requested).where(JobRecord.id == job_id))
            val = res.scalar_one_or_none()
            if val:
                self._cancel_flags[job_id] = True
                return True
        return False

    @staticmethod
    def serialize_job(job: JobRecord) -> Dict[str, Any]:
        return {
            "id": job.id,
            "job_type": job.job_type,
            "status": job.status,
            "progress_phase": job.progress_phase,
            "budget": json.loads(job.budget_json) if job.budget_json else None,
            "usage": json.loads(job.usage_json) if job.usage_json else {},
            "result": json.loads(job.result_json) if job.result_json else None,
            "error_message": job.error_message,
            "cancel_requested": job.cancel_requested,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }


class ExecutionEngine:
    """Shared model execution engine enforcing capability routing, budgets, and policies."""

    def __init__(self):
        self.policy = ExecutionPolicy()
        self._semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_MODELS)

    def get_policy(self) -> ExecutionPolicy:
        return self.policy

    def update_policy(
        self,
        local_only: Optional[bool] = None,
        free_only: Optional[bool] = None,
        max_calls_per_run: Optional[int] = None,
        max_parallel: Optional[int] = None,
    ) -> ExecutionPolicy:
        if local_only is not None:
            self.policy.local_only = local_only
        if free_only is not None:
            self.policy.free_only = free_only
        if max_calls_per_run is not None:
            self.policy.max_calls_per_run = max(1, min(max_calls_per_run, 100))
        if max_parallel is not None:
            self.policy.max_parallel = max(1, min(max_parallel, 12))
            self._semaphore = asyncio.Semaphore(self.policy.max_parallel)
        return self.policy

    def resolve_budget(self, budget: Optional[ExecutionBudget] = None) -> ExecutionBudget:
        if budget is None:
            return ExecutionBudget(
                max_calls=self.policy.max_calls_per_run,
                max_parallel=self.policy.max_parallel,
                local_only=self.policy.local_only,
                free_only=self.policy.free_only,
            )
        return ExecutionBudget(
            max_calls=min(budget.max_calls, self.policy.max_calls_per_run),
            max_tokens=budget.max_tokens,
            max_duration_seconds=budget.max_duration_seconds,
            max_parallel=min(budget.max_parallel, self.policy.max_parallel),
            local_only=budget.local_only or self.policy.local_only,
            free_only=budget.free_only or self.policy.free_only,
        )

    def check_model_policy(
        self,
        model_id: str,
        budget: Optional[ExecutionBudget] = None,
        require_vision: bool = False,
    ) -> Optional[str]:
        """Return an error reason if model execution violates active policies or capabilities."""
        effective = self.resolve_budget(budget)
        info = model_registry.get(model_id)
        is_local = info.is_local if info else ("::" in model_id and not model_id.startswith("nvidia::"))
        is_free_tier = info.is_free_tier if info else is_local

        if effective.local_only and not is_local:
            provider_label = info.provider if info else "external provider"
            return (
                f"Local-only policy is active; non-local provider '{provider_label}' "
                f"for model '{model_id}' is blocked. Configure a local model (Ollama, LM Studio, llama.cpp) or disable local-only mode."
            )

        if effective.free_only and not is_free_tier:
            return f"Free-only policy is active; model '{model_id}' is not classified as free/local."

        if require_vision and info is not None and not info.capabilities.get("vision", False):
            return f"Model '{info.name}' does not advertise vision capability."

        return None

    async def execute_model(
        self,
        model_id: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 60.0,
        attachments: Optional[list] = None,
        budget: Optional[ExecutionBudget] = None,
        call_counter: Optional[Dict[str, int]] = None,
        job_id: Optional[str] = None,
        require_vision: bool = False,
    ) -> ProviderResponse:
        effective = self.resolve_budget(budget)

        if await job_manager.check_canceled(job_id):
            return ProviderResponse(
                model_id=model_id,
                model_name=model_id,
                provider="System",
                status="canceled",
                error_message="Execution canceled by user.",
            )

        policy_error = self.check_model_policy(model_id, effective, require_vision=require_vision)
        if policy_error:
            info = model_registry.get(model_id)
            return ProviderResponse(
                model_id=model_id,
                model_name=info.name if info else model_id,
                provider=info.provider if info else "Policy",
                status="error",
                error_message=policy_error,
            )

        if call_counter is not None:
            current_calls = call_counter.get("calls", 0)
            if current_calls >= effective.max_calls:
                return ProviderResponse(
                    model_id=model_id,
                    model_name=model_id,
                    provider="Budget",
                    status="error",
                    error_message=f"Run call budget exceeded ({effective.max_calls} calls max).",
                )
            if effective.max_tokens and call_counter.get("tokens", 0) >= effective.max_tokens:
                return ProviderResponse(
                    model_id=model_id,
                    model_name=model_id,
                    provider="Budget",
                    status="error",
                    error_message=f"Run token budget exceeded ({effective.max_tokens} tokens max).",
                )
            call_counter["calls"] = current_calls + 1

        if _test_provider_fake is not None:
            start = time.perf_counter()
            maybe_coro = _test_provider_fake(model_id, prompt, system_prompt, timeout, attachments)
            if asyncio.iscoroutine(maybe_coro):
                res = await maybe_coro
            else:
                res = maybe_coro
            if res.response_time_ms is None:
                res.response_time_ms = round((time.perf_counter() - start) * 1000, 2)
            if call_counter is not None and res.usage and res.usage.get("total_tokens"):
                call_counter["tokens"] = call_counter.get("tokens", 0) + int(res.usage["total_tokens"])
            return res

        info = model_registry.get(model_id)
        async with self._semaphore:
            if "::" in model_id:
                provider_id = info.provider_id if info else model_id.split("::", 1)[0]
                res = await local_openai_provider.generate(
                    model_id=model_id,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    timeout=timeout,
                    attachments=attachments,
                    provider_id=provider_id,
                )
            else:
                res = await nvidia_provider.generate(
                    model_id=model_id,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    timeout=timeout,
                    attachments=attachments,
                )
            if call_counter is not None and res.usage and res.usage.get("total_tokens"):
                call_counter["tokens"] = call_counter.get("tokens", 0) + int(res.usage["total_tokens"])
            return res

    async def execute_batch(
        self,
        requests: List[Dict[str, Any]],
        budget: Optional[ExecutionBudget] = None,
        call_counter: Optional[Dict[str, int]] = None,
        job_id: Optional[str] = None,
    ) -> List[ProviderResponse]:
        effective = self.resolve_budget(budget)
        batch_sem = asyncio.Semaphore(effective.max_parallel)

        async def _run_one(item: Dict[str, Any]) -> ProviderResponse:
            async with batch_sem:
                return await self.execute_model(
                    model_id=item["model_id"],
                    prompt=item["prompt"],
                    system_prompt=item.get("system_prompt"),
                    timeout=item.get("timeout", 60.0),
                    attachments=item.get("attachments"),
                    budget=effective,
                    call_counter=call_counter,
                    job_id=job_id,
                    require_vision=bool(item.get("require_vision", False)),
                )

        return await asyncio.gather(*[_run_one(req) for req in requests])


job_manager = JobManager()
execution_engine = ExecutionEngine()
