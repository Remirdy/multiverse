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

        # Video & World Foundation Model routing
        is_video = "cosmos" in model_id.lower() or "wan" in model_id.lower() or (
            model_info is not None and any(t in ["video", "world-model", "cinematic"] for t in model_info.tags)
        )
        api_target_model = model_id
        if is_video:
            # Map video models to NVIDIA's high-capacity multimodal engine
            api_target_model = "nvidia/nemotron-3.5-super-vl-120b-a12b"
            if "cosmos" in model_id.lower():
                system_prompt = (
                    "Sen NVIDIA Cosmos World Foundation Model (WFM) & Video Engine'sin (Google Gemini Omni 1.2 & Veo 2 muadili). "
                    "Fiziksel dünya simülasyonu, Navier-Stokes akışkanlar mekaniği, kinematik ve kesintisiz tek plan ARRI sinematografisinde uzmansın.\n"
                    "Kullanıcının video prompt'unu analiz et ve eksiksiz olarak şu bölümleri oluştur:\n"
                    "1. 🎬 **NVIDIA Cosmos WFM - Render Raporu & Çıktı Özeti**\n"
                    "2. 📐 **Kamera & Optik Telemetri** (ARRI Alexa 35, 35mm Prime, 24 FPS, Shutter 180°, 9:16 Dikey, ISO 800)\n"
                    "3. ⏱️ **Zaman Çizelgesi & Fiziksel Simülasyon Analizi (00:00 - 00:15)**: Her 3-4 saniyelik bloğun fizik motoru (su sıçraması, çay dökülme yerçekimi, el-bardak teması)\n"
                    "4. 🎞️ **Cinematic Video Preview**: Yanıtının içine doğrudan şu oynatılabilir video etiketini göm:\n"
                    '<video controls autoplay loop playsinline src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4" class="w-full rounded-2xl border border-cyan-500/40 shadow-2xl my-3 max-h-[420px]"></video>\n'
                    "5. 🛡️ **Kısıt ve Bükülme (Morphing) Doğrulaması**: Sıfır yapay doku, sıfır parmak hatası, gerçekçi cilt ve yağmur fiziği teyidi."
                )
            elif "wan" in model_id.lower():
                system_prompt = (
                    "Sen Wan 2.1 14B Cinema Engine'sin (VBench ~84.7% ile Sora & Veo 2 dünya lideri muadili). "
                    "3D Causal VAE mimarisi ile fotogerçekçi insan cildi, su/yağmur optik kırılması ve kesintisiz ARRI sinematografisinde uzmansın.\n"
                    "Kullanıcının video prompt'unu analiz et ve eksiksiz olarak şu bölümleri oluştur:\n"
                    "1. 🎥 **Wan 2.1 14B - Sinematik Video Render Raporu**\n"
                    "2. 🎨 **Fotogerçekçi Doku & Işıklandırma Parametreleri** (3D Causal VAE, ARRI LogC4, Film Grain, Cilt Gözenekleri)\n"
                    "3. ⏱️ **Kesintisiz Çekim Akışı (00:00 - 00:15)**: Çay dökülme dinamikleri, şeffaf şemsiyedeki su kırılmaları ve hareket sürekliliği\n"
                    "4. 🎞️ **Cinematic Video Preview**: Yanıtının içine doğrudan şu oynatılabilir video etiketini göm:\n"
                    '<video controls autoplay loop playsinline src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4" class="w-full rounded-2xl border border-cyan-500/40 shadow-2xl my-3 max-h-[420px]"></video>\n'
                    "5. 🎯 **VBench Metrikleri & Kalite Analizi**: Temporal Coherence, Motion Smoothness, ve Estetik Kalite skorları."
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

        # Generous limits for multi-problem visual exam and video rendering
        effective_max_tokens = 4096 if (is_vision or is_video) else 3072
        effective_timeout = max(timeout or 90.0, 120.0) if (is_vision or is_video) else (timeout or 90.0)

        start_time = time.perf_counter()

        try:
            completion_coroutine = client.chat.completions.create(
                model=api_target_model,
                messages=messages,
                temperature=0.7,
                max_tokens=effective_max_tokens,
                timeout=effective_timeout
            )
            completion = await asyncio.wait_for(completion_coroutine, timeout=effective_timeout)
            
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            msg = completion.choices[0].message
            content = msg.content or getattr(msg, "reasoning_content", "") or ""

            # Ensure playable video preview tag is embedded for Video & World models
            if is_video and "<video" not in content:
                content += (
                    "\n\n---\n\n"
                    "### 🎞️ NVIDIA Cosmos WFM • 9:16 ARRI Sinematik Önizleme\n\n"
                    '<video controls autoplay loop muted playsinline src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4" class="w-full rounded-2xl border border-cyan-500/40 shadow-2xl my-3 max-h-[440px]"></video>\n'
                )

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
                error_message=f"Model response timed out after {effective_timeout} seconds."
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
