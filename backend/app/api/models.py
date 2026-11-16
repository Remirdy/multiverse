from typing import List
from fastapi import APIRouter, HTTPException
from app.providers.registry import model_registry
from app.providers.nvidia import nvidia_provider
from app.providers.local_openai import local_openai_provider
from app.execution.engine import execution_engine
from app.schemas.model import (
    ModelListResponse,
    ProviderConfigItem,
    ProviderConfigureRequest,
    ProviderTestRequest,
    ExecutionPolicyUpdate,
)

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("", response_model=ModelListResponse)
async def list_models():
    """Retrieve all available models in the registry and their capabilities."""
    models = model_registry.list_all()
    default_ids = model_registry.get_default_model_ids()
    return ModelListResponse(
        models=models,
        default_models=default_ids,
        total=len(models),
    )


@router.get("/health")
async def check_models_health():
    """Verify provider connectivity and API key configuration status."""
    is_healthy = await nvidia_provider.check_health()
    return {
        "status": "configured" if is_healthy else "pending_key",
        "provider": "NVIDIA NIM",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_set": is_healthy,
    }


@router.get("/providers", response_model=List[ProviderConfigItem])
async def list_providers():
    """List configured cloud and local inference providers."""
    nvidia_ok = await nvidia_provider.check_health()
    items = [
        ProviderConfigItem(
            provider_id="nvidia",
            name="NVIDIA NIM",
            base_url="https://integrate.api.nvidia.com/v1",
            is_local=False,
            is_enabled=True,
            status="configured" if nvidia_ok else "pending_key",
            discovered_models=[m.id for m in model_registry.list_all() if m.provider_id == "nvidia"],
            error=None if nvidia_ok else "NVIDIA_API_KEY not set in backend/.env",
        )
    ]
    for cfg in local_openai_provider.list_configs():
        pid = cfg["provider_id"]
        discovered = [m.id.split("::", 1)[1] for m in model_registry.list_all() if m.provider_id == pid]
        items.append(
            ProviderConfigItem(
                provider_id=pid,
                name=cfg["name"],
                base_url=cfg["base_url"],
                is_local=bool(cfg.get("is_local", True)),
                is_enabled=bool(cfg.get("is_enabled", True)),
                status="ready" if discovered else "configured",
                discovered_models=discovered,
            )
        )
    return items


@router.post("/providers/configure", response_model=ProviderConfigItem)
async def configure_provider(req: ProviderConfigureRequest):
    """Configure or update an explicit OpenAI-compatible local or custom provider endpoint."""
    try:
        cfg = local_openai_provider.configure_provider(
            provider_id=req.provider_id.strip().lower(),
            base_url=req.base_url,
            name=req.name,
            api_key=req.api_key,
            is_local=req.is_local,
            is_enabled=req.is_enabled,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    test_res = await local_openai_provider.test_and_discover(
        provider_id=cfg["provider_id"],
        base_url=cfg["base_url"],
        api_key=req.api_key,
    )
    if test_res["discovered_models"]:
        model_registry.register_local_models(
            provider_id=cfg["provider_id"],
            provider_name=cfg["name"],
            model_ids=test_res["discovered_models"],
            is_local=bool(cfg["is_local"]),
        )
    return ProviderConfigItem(
        provider_id=cfg["provider_id"],
        name=cfg["name"],
        base_url=cfg["base_url"],
        is_local=bool(cfg["is_local"]),
        is_enabled=bool(cfg["is_enabled"]),
        status=test_res["status"],
        discovered_models=test_res["discovered_models"],
        error=test_res["error"],
    )


@router.post("/providers/test")
async def test_provider_connection(req: ProviderTestRequest):
    """Test connection and discover served models from a configured provider."""
    pid = req.provider_id.strip().lower()
    if pid == "nvidia":
        ok = await nvidia_provider.check_health()
        return {
            "provider_id": "nvidia",
            "status": "configured" if ok else "pending_key",
            "discovered_models": [m.id for m in model_registry.list_all() if m.provider_id == "nvidia"],
            "error": None if ok else "NVIDIA_API_KEY is not configured.",
        }

    res = await local_openai_provider.test_and_discover(
        provider_id=pid,
        base_url=req.base_url,
        api_key=req.api_key,
    )
    cfg = local_openai_provider.get_config(pid)
    if res["discovered_models"] and cfg:
        model_registry.register_local_models(
            provider_id=pid,
            provider_name=cfg["name"],
            model_ids=res["discovered_models"],
            is_local=bool(cfg.get("is_local", True)),
        )
    return res


@router.get("/policy")
async def get_execution_policy():
    return execution_engine.get_policy().model_dump()


@router.put("/policy")
async def update_execution_policy(req: ExecutionPolicyUpdate):
    policy = execution_engine.update_policy(
        local_only=req.local_only,
        free_only=req.free_only,
        max_calls_per_run=req.max_calls_per_run,
        max_parallel=req.max_parallel,
    )
    return policy.model_dump()
