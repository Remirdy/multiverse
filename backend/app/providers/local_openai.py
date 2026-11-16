import ipaddress
import time
import asyncio
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import httpx
from openai import AsyncOpenAI

from app.core.config import settings
from app.providers.base import BaseProvider, ProviderResponse


DEFAULT_LOCAL_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "ollama": {
        "provider_id": "ollama",
        "name": "Ollama (Local)",
        "base_url": settings.OLLAMA_BASE_URL,
        "is_local": True,
        "is_enabled": True,
    },
    "lmstudio": {
        "provider_id": "lmstudio",
        "name": "LM Studio (Local)",
        "base_url": settings.LMSTUDIO_BASE_URL,
        "is_local": True,
        "is_enabled": True,
    },
    "llamacpp": {
        "provider_id": "llamacpp",
        "name": "llama.cpp Server (Local)",
        "base_url": settings.LLAMACPP_BASE_URL,
        "is_local": True,
        "is_enabled": True,
    },
    "mlx": {
        "provider_id": "mlx",
        "name": "MLX-LM Server (Apple Silicon)",
        "base_url": settings.MLX_BASE_URL,
        "is_local": True,
        "is_enabled": True,
    },
}


def validate_provider_url(url: str) -> str:
    """Validate an explicitly configured provider URL and block metadata hosts."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Provider URL must use http or https")
    if not parsed.hostname:
        raise ValueError("Provider URL must include a valid host")

    host_lower = parsed.hostname.lower()
    if host_lower in {"metadata.google.internal", "metadata", "169.254.169.254"}:
        raise ValueError("Cloud metadata hosts are forbidden")

    try:
        ip = ipaddress.ip_address(host_lower)
        if ip.is_link_local:
            raise ValueError("Link-local metadata addresses are forbidden")
    except ValueError as exc:
        if "forbidden" in str(exc):
            raise

    return url.rstrip("/")


class LocalOpenAIProvider(BaseProvider):
    provider_name: str = "Local OpenAI-Compatible"

    def __init__(self):
        self._configs: Dict[str, Dict[str, Any]] = {
            k: dict(v) for k, v in DEFAULT_LOCAL_PROVIDERS.items()
        }
        self._api_keys: Dict[str, str] = {}

    def list_configs(self) -> List[Dict[str, Any]]:
        return [dict(v) for v in self._configs.values()]

    def get_config(self, provider_id: str) -> Optional[Dict[str, Any]]:
        cfg = self._configs.get(provider_id)
        return dict(cfg) if cfg else None

    def configure_provider(
        self,
        provider_id: str,
        base_url: str,
        name: Optional[str] = None,
        api_key: Optional[str] = None,
        is_local: bool = True,
        is_enabled: bool = True,
    ) -> Dict[str, Any]:
        safe_url = validate_provider_url(base_url)
        existing = self._configs.get(provider_id, {})
        entry = {
            "provider_id": provider_id,
            "name": name or existing.get("name") or provider_id,
            "base_url": safe_url,
            "is_local": is_local,
            "is_enabled": is_enabled,
        }
        self._configs[provider_id] = entry
        if api_key is not None and api_key.strip():
            self._api_keys[provider_id] = api_key.strip()
        return dict(entry)

    async def test_and_discover(
        self,
        provider_id: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        cfg = self._configs.get(provider_id)
        target_url = base_url or (cfg["base_url"] if cfg else "")
        if not target_url:
            return {
                "provider_id": provider_id,
                "status": "not_configured",
                "discovered_models": [],
                "error": f"Provider '{provider_id}' is not configured.",
            }

        try:
            safe_url = validate_provider_url(target_url)
        except ValueError as exc:
            return {
                "provider_id": provider_id,
                "status": "invalid_url",
                "discovered_models": [],
                "error": str(exc),
            }

        headers: Dict[str, str] = {}
        effective_key = api_key or self._api_keys.get(provider_id)
        if effective_key:
            headers["Authorization"] = f"Bearer {effective_key}"

        models_url = f"{safe_url}/models"
        try:
            async with httpx.AsyncClient(timeout=3.5) as client:
                resp = await client.get(models_url, headers=headers)
            if resp.status_code != 200:
                return {
                    "provider_id": provider_id,
                    "status": "error",
                    "discovered_models": [],
                    "error": f"Endpoint returned HTTP {resp.status_code}. Ensure the local inference server is running.",
                }
            payload = resp.json()
            data = payload.get("data", []) if isinstance(payload, dict) else []
            discovered = [str(item.get("id")) for item in data if isinstance(item, dict) and item.get("id")]
            return {
                "provider_id": provider_id,
                "status": "connected",
                "discovered_models": discovered,
                "error": None,
            }
        except Exception as exc:
            return {
                "provider_id": provider_id,
                "status": "unreachable",
                "discovered_models": [],
                "error": f"Could not connect to {safe_url}: {type(exc).__name__}",
            }

    async def check_health(self) -> bool:
        return any(cfg.get("is_enabled", False) for cfg in self._configs.values())

    async def generate(
        self,
        model_id: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 45.0,
        attachments: Optional[list] = None,
        provider_id: str = "ollama",
    ) -> ProviderResponse:
        cfg = self._configs.get(provider_id)
        if not cfg or not cfg.get("is_enabled", True):
            return ProviderResponse(
                model_id=model_id,
                model_name=model_id,
                provider=provider_id,
                status="error",
                is_local=True,
                error_message=f"Local provider '{provider_id}' is not enabled or configured.",
            )

        raw_model_id = model_id
        if "::" in model_id:
            _, raw_model_id = model_id.split("::", 1)

        effective_prompt = prompt
        if attachments:
            doc_parts = []
            for item in attachments:
                fname = getattr(item, "filename", None) or (item.get("filename") if isinstance(item, dict) else "Attachment")
                text = getattr(item, "extracted_text", None) or (item.get("extracted_text") if isinstance(item, dict) else "")
                if text:
                    doc_parts.append(f"[Attached Document: {fname}]\n{text[:24000]}")
            if doc_parts:
                effective_prompt = "\n\n".join(doc_parts) + "\n\n---\n" + prompt

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": effective_prompt})

        api_key = self._api_keys.get(provider_id) or "local-no-key"
        effective_timeout = max(timeout or 60.0, 15.0)
        start_time = time.perf_counter()

        try:
            client = AsyncOpenAI(
                base_url=cfg["base_url"],
                api_key=api_key,
                timeout=effective_timeout,
            )
            completion = await asyncio.wait_for(
                client.chat.completions.create(
                    model=raw_model_id,
                    messages=messages,
                    temperature=0.4,
                    max_tokens=4096,
                ),
                timeout=effective_timeout,
            )
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            msg = completion.choices[0].message
            content = msg.content or ""
            usage_obj = getattr(completion, "usage", None)
            usage = None
            if usage_obj is not None:
                usage = {
                    "prompt_tokens": getattr(usage_obj, "prompt_tokens", None),
                    "completion_tokens": getattr(usage_obj, "completion_tokens", None),
                    "total_tokens": getattr(usage_obj, "total_tokens", None),
                }
            return ProviderResponse(
                model_id=model_id,
                model_name=raw_model_id,
                provider=cfg["name"],
                response_text=content,
                response_time_ms=elapsed_ms,
                status="success",
                usage=usage,
                is_local=bool(cfg.get("is_local", True)),
            )
        except asyncio.TimeoutError:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ProviderResponse(
                model_id=model_id,
                model_name=raw_model_id,
                provider=cfg["name"],
                response_time_ms=elapsed_ms,
                status="timeout",
                is_local=bool(cfg.get("is_local", True)),
                error_message=f"Local model timed out after {effective_timeout}s.",
            )
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ProviderResponse(
                model_id=model_id,
                model_name=raw_model_id,
                provider=cfg["name"],
                response_time_ms=elapsed_ms,
                status="error",
                is_local=bool(cfg.get("is_local", True)),
                error_message=f"Local provider error ({cfg['name']}): {str(exc)}",
            )


local_openai_provider = LocalOpenAIProvider()
