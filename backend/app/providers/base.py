from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ProviderResponse(BaseModel):
    model_id: str
    model_name: str
    provider: str
    response_text: Optional[str] = None
    response_time_ms: Optional[float] = None
    status: str  # 'success', 'error', 'timeout', 'canceled'
    error_message: Optional[str] = None
    search_results: Optional[List[Dict[str, Any]]] = None
    usage: Optional[Dict[str, Any]] = None
    is_local: bool = False


class BaseProvider(ABC):
    provider_name: str = "BaseProvider"

    @abstractmethod
    async def generate(
        self,
        model_id: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 45.0,
        attachments: Optional[list] = None,
    ) -> ProviderResponse:
        """Generate response from a specific model with independent timeout and optional attachments."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Verify API health and key validity."""
        pass
