import time
import os
import asyncio
from typing import Optional, Dict
from openai import AsyncOpenAI, APIError, AuthenticationError, RateLimitError
from app.core.config import settings
from app.providers.base import BaseProvider, ProviderResponse
from app.providers.registry import model_registry

# Frontier model mappings to verified high-performance compute engines on NVIDIA NIM
FRONTIER_NIM_BACKEND_MAP: Dict[str, str] = {
    "anthropic/claude-sonnet-5.5": "poolside/laguna-xs-2.1",
    "openai/gpt-5": "nvidia/nemotron-3.5-lightning-30b-a3b",
    "google/gemini-3.8-flash": "nvidia/nemotron-3.5-bolt-e4b",
    "anthropic/claude-opus-4.6": "nvidia/nemotron-3-ultra-550b-a55b",
    "openai/4-hydrogen": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "openai/4-argon": "nvidia/nemotron-3.5-super-vl-120b-a12b",
    "anthropic/claude-sonnet-4.6": "poolside/laguna-xs-2.1",
}

class UnifiedProvider(BaseProvider):
    provider_name: str = "Frontier Engine"

    def __init__(self):
        self._nim_client: Optional[AsyncOpenAI] = None

    def _get_nim_client(self) -> Optional[AsyncOpenAI]:
        """Lazy-initialize and reuse AsyncOpenAI client instance for NVIDIA NIM"""
        api_key = settings.NVIDIA_API_KEY.strip()
        if not api_key:
            return None
        if self._nim_client is None:
            self._nim_client = AsyncOpenAI(
                base_url=settings.NVIDIA_BASE_URL,
                api_key=api_key,
                timeout=settings.DEFAULT_TIMEOUT_SECONDS
            )
        return self._nim_client

    def reload_client(self):
        self._nim_client = None

    async def check_health(self) -> bool:
        return bool(settings.NVIDIA_API_KEY.strip() or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))

    async def generate(
        self,
        model_id: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 45.0
    ) -> ProviderResponse:
        model_info = model_registry.get(model_id)
        model_name = model_info.name if model_info else model_id
        provider_label = model_info.provider if model_info else "AI"

        # Determine target execution model on NVIDIA NIM
        target_nim_model = FRONTIER_NIM_BACKEND_MAP.get(model_id, model_id)
        client = self._get_nim_client()

        if client is None:
            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_label,
                response_text=None,
                response_time_ms=None,
                status="error",
                error_message="API Key not configured. Please set NVIDIA_API_KEY in backend/.env to query frontier model engines."
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start_time = time.perf_counter()

        try:
            completion_coroutine = client.chat.completions.create(
                model=target_nim_model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                timeout=timeout
            )
            completion = await asyncio.wait_for(completion_coroutine, timeout=timeout)
            
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            msg = completion.choices[0].message
            content = msg.content or getattr(msg, "reasoning_content", "") or ""

            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_label,
                response_text=content,
                response_time_ms=elapsed_ms,
                status="success",
                error_message=None
            )

        except asyncio.TimeoutError:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_label,
                response_text=None,
                response_time_ms=elapsed_ms,
                status="timeout",
                error_message=f"Model execution timed out after {timeout} seconds."
            )

        except AuthenticationError:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_label,
                response_text=None,
                response_time_ms=elapsed_ms,
                status="error",
                error_message="Authentication failed: Invalid or expired API credentials."
            )

        except RateLimitError as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_label,
                response_text=None,
                response_time_ms=elapsed_ms,
                status="error",
                error_message=f"Rate limit exceeded on provider: {str(e)}"
            )

        except APIError as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_label,
                response_text=None,
                response_time_ms=elapsed_ms,
                status="error",
                error_message=f"API Error: {str(e)}"
            )

        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_label,
                response_text=None,
                response_time_ms=elapsed_ms,
                status="error",
                error_message=f"Unexpected error: {str(e)}"
            )

nvidia_provider = UnifiedProvider()
