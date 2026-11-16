import time
import asyncio
from typing import Optional
from openai import AsyncOpenAI, APIError, AuthenticationError, RateLimitError
from app.core.config import settings
from app.providers.base import BaseProvider, ProviderResponse
from app.providers.registry import model_registry

class NvidiaProvider(BaseProvider):
    provider_name: str = "NVIDIA NIM"

    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None

    def _get_client(self) -> Optional[AsyncOpenAI]:
        """Lazy-initialize and reuse AsyncOpenAI client instance for NVIDIA NIM"""
        api_key = settings.NVIDIA_API_KEY.strip()
        if not api_key:
            return None
        if self._client is None:
            self._client = AsyncOpenAI(
                base_url=settings.NVIDIA_BASE_URL,
                api_key=api_key,
                timeout=settings.DEFAULT_TIMEOUT_SECONDS
            )
        return self._client

    def reload_client(self):
        self._client = None

    async def check_health(self) -> bool:
        return bool(settings.NVIDIA_API_KEY.strip())

    async def generate(
        self,
        model_id: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 45.0
    ) -> ProviderResponse:
        model_info = model_registry.get(model_id)
        model_name = model_info.name if model_info else model_id
        provider_name = model_info.provider if model_info else self.provider_name

        client = self._get_client()
        if client is None:
            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_name,
                response_text=None,
                response_time_ms=None,
                status="error",
                error_message="NVIDIA API Key not configured. Please set NVIDIA_API_KEY in backend/.env."
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start_time = time.perf_counter()

        try:
            completion_coroutine = client.chat.completions.create(
                model=model_id,
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
                provider=provider_name,
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
                provider=provider_name,
                response_text=None,
                response_time_ms=elapsed_ms,
                status="timeout",
                error_message=f"Model response timed out after {timeout} seconds."
            )

        except AuthenticationError:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_name,
                response_text=None,
                response_time_ms=elapsed_ms,
                status="error",
                error_message="Authentication failed: Invalid or expired NVIDIA API Key."
            )

        except RateLimitError as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_name,
                response_text=None,
                response_time_ms=elapsed_ms,
                status="error",
                error_message=f"Rate limit exceeded on NVIDIA NIM: {str(e)}"
            )

        except APIError as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_name,
                response_text=None,
                response_time_ms=elapsed_ms,
                status="error",
                error_message=f"NVIDIA API Error: {str(e)}"
            )

        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_name,
                response_text=None,
                response_time_ms=elapsed_ms,
                status="error",
                error_message=f"Unexpected error: {str(e)}"
            )

nvidia_provider = NvidiaProvider()
