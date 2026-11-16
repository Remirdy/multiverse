from fastapi import APIRouter
from app.providers.registry import model_registry
from app.providers.nvidia import nvidia_provider
from app.schemas.model import ModelListResponse

router = APIRouter(prefix="/models", tags=["Models"])

@router.get("", response_model=ModelListResponse)
async def list_models():
    """Retrieve all available models in the registry and their capabilities"""
    models = model_registry.list_all()
    default_ids = model_registry.get_default_model_ids()
    return ModelListResponse(
        models=models,
        default_models=default_ids,
        total=len(models)
    )

@router.get("/health")
async def check_models_health():
    """Verify provider connectivity and API key configuration status"""
    is_healthy = await nvidia_provider.check_health()
    return {
        "status": "configured" if is_healthy else "pending_key",
        "provider": "NVIDIA NIM",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_set": is_healthy
    }
