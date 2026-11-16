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
        timeout: float = 45.0,
        attachments: Optional[list] = None
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

        # Process attachments
        doc_parts = []
        image_attachments = []
        if attachments:
            for item in attachments:
                # Support Pydantic model or dict
                ftype = getattr(item, "file_type", None) or (item.get("file_type") if isinstance(item, dict) else "")
                fname = getattr(item, "filename", None) or (item.get("filename") if isinstance(item, dict) else "Attachment")
                text = getattr(item, "extracted_text", None) or (item.get("extracted_text") if isinstance(item, dict) else "")
                durl = getattr(item, "data_url", None) or (item.get("data_url") if isinstance(item, dict) else "")
                pimages = getattr(item, "page_images", None) or (item.get("page_images") if isinstance(item, dict) else None)

                if ftype == "image" and durl:
                    image_attachments.append({"filename": fname, "data_url": durl})
                
                # If PDF has rendered page images, add them for vision models
                if pimages:
                    for p_idx, p_url in enumerate(pimages):
                        image_attachments.append({"filename": f"{fname} Sayfa {p_idx+1}", "data_url": p_url})

                if text:
                    doc_parts.append(f"📄 **[Ekli Belge: {fname}]**\n```\n{text[:35000]}\n```")

        doc_context = ("\n\n".join(doc_parts) + "\n\n---\n") if doc_parts else ""
        effective_prompt = f"{doc_context}{prompt}" if doc_context else prompt

        # Determine if this model is vision-capable
        is_vision = "vl" in model_id.lower() or "vision" in model_id.lower() or (
            model_info is not None and any(t in ["vision", "multimodal"] for t in model_info.tags)
        )

        # If user attached visual images / circuit drawings, but this model cannot see them,
        # return a clear, immediate notice rather than letting the text model hallucinate or apologize.
        if image_attachments and not is_vision:
            img_names = ", ".join([img["filename"] for img in image_attachments[:2]])
            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_name,
                response_text=(
                    f"⚠️ **Görsel / Şema Uyarısı ({model_name})**\n\n"
                    f"Bu model **saf metin ve kod** odaklıdır; yüklediğiniz görsel veya devre şemasını ({img_names}) doğrudan algılayamaz. Tahmin yürüterek uydurma devre formülleri üretmesi ve yanıltıcı değerler vermesi engellenmiştir.\n\n"
                    f"👉 **Doğru Çözüm İçin:** Devre şemalarını ve çizimleri piksel düzeyinde inceleyen **Nemotron Super VL 120B** veya **Llama 3.2 90B Vision** modelini kullanınız."
                ),
                response_time_ms=5.0,
                status="success",
                error_message=None
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if image_attachments and is_vision:
            content_blocks = [{"type": "text", "text": effective_prompt}]
            for img in image_attachments[:5]:  # send up to 5 visual diagrams/pages
                content_blocks.append({
                    "type": "image_url",
                    "image_url": {"url": img["data_url"]}
                })
            messages.append({"role": "user", "content": content_blocks})
        else:
            messages.append({"role": "user", "content": effective_prompt})

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
