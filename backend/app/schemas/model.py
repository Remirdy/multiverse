from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ModelCapabilities(BaseModel):
    chat: bool = True
    vision: bool = False
    structured_output: bool = False
    tool_calling: bool = False
    streaming: bool = False
    context_length: int = 32000
    modalities: List[str] = Field(default_factory=lambda: ["text"])


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    provider_id: str = "nvidia"
    is_local: bool = False
    is_free_tier: bool = True
    description: str
    category: str
    context_length: int
    is_available: bool = True
    is_default: bool = False
    tags: List[str] = Field(default_factory=list)
    capabilities: Dict[str, Any] = Field(
        default_factory=lambda: {
            "chat": True,
            "vision": False,
            "structured_output": False,
            "tool_calling": False,
            "streaming": False,
            "context_length": 32000,
            "modalities": ["text"],
        }
    )


class ModelListResponse(BaseModel):
    models: List[ModelInfo]
    default_models: List[str]
    total: int


class ProviderConfigItem(BaseModel):
    provider_id: str
    name: str
    base_url: str
    is_local: bool = True
    is_enabled: bool = True
    status: str = "unknown"
    discovered_models: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class ProviderConfigureRequest(BaseModel):
    provider_id: str
    name: Optional[str] = None
    base_url: str
    api_key: Optional[str] = None
    is_local: bool = True
    is_enabled: bool = True


class ProviderTestRequest(BaseModel):
    provider_id: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None


class ExecutionPolicyUpdate(BaseModel):
    local_only: Optional[bool] = None
    free_only: Optional[bool] = None
    max_calls_per_run: Optional[int] = None
    max_parallel: Optional[int] = None
