import time
from typing import List
from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.compare import ModelResponseSummary, SynthesizeResponse

class SynthesisService:
    def __init__(self):
        self._client = None
        self.primary_model = "nvidia/nemotron-3-ultra-550b-a55b"
        self.fallback_model = "nvidia/nemotron-3.5-super-vl-120b-a12b"

    @property
    def client(self):
        if self._client is None and settings.NVIDIA_API_KEY.strip():
            self._client = AsyncOpenAI(
                base_url=settings.NVIDIA_BASE_URL,
                api_key=settings.NVIDIA_API_KEY.strip()
            )
        return self._client

    async def synthesize(self, prompt: str, responses: List[ModelResponseSummary], language: str = "tr") -> SynthesizeResponse:
        start_time = time.perf_counter()

        system_instruction = (
            "Sen dünyanın en yetkin, tarafsız ve üst düzey yapay zekâ başhakemi ve başmimarısın. "
            "Kullanıcının tek bir sorusuna farklı yapay zekâ modelleri yarışarak yanıtlar vermiştir. "
            "Görevin modellerin yanıtlarını titizlikle incelemek ve mükemmel bir sentez üretmektir.\n\n"
            "Çıktı Formatı ve Yapısı (Kesinlikle bu yapıyı takip et):\n"
            "### ⚖️ 1. Modellerin Değerlendirmesi & Karşılaştırmalı Matris\n"
            "Modelleri bir Markdown tablosunda karşılaştır:\n"
            "| Model | Yaklaşım | Güçlü Yönler | Eksik / Hatalı Yönler | Puan (10 Üzerinden) |\n\n"
            "### 💡 2. Kritik Farklılıklar & Zayıf Noktalar\n"
            "Modellerin nerede ayrıştığını, hangi modelin hata yaptığını veya hangi modelin kritik bir güvenlik/performans detayını yakaladığını 2-3 maddede özetle.\n\n"
            "### 🏆 3. Nihai Altın Çözüm (The Golden Unified Solution)\n"
            "Tüm modellerin en doğru, en performanslı ve en temiz yönlerini birleştirerek, hiçbir eksik bırakmadan tek bir nihai, prodüksiyon kalitesinde kod ve açıklama sun.\n\n"
            "Kurallar:\n"
            "- Yanıt dilini kullanıcının sorduğu dile göre ayarla (Türkçe ise Türkçe, İngilizce ise İngilizce).\n"
            "- Tarafsız ol, teknik gerçeklere ve en iyi endüstri standartlarına (Clean Code, PEP 8, OWASP vb.) dayan."
        )

        formatted_responses = []
        for idx, r in enumerate(responses, 1):
            formatted_responses.append(
                f"--- [MODEL {idx}: {r.model_name} ({r.model_id})] ---\n{r.response_text}\n"
            )

        user_content = (
            f"KULLANICI SORUSU:\n{prompt}\n\n"
            f"MODELLERİN YANITLARI:\n\n" + "\n".join(formatted_responses) +
            "\nLütfen yukarıdaki talimata uygun olarak hakem değerlendirmeni ve Altın Çözümü (Golden Solution) sun."
        )

        target_model = self.primary_model
        try:
            res = await self.client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=2500,
                temperature=0.3
            )
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            msg = res.choices[0].message
            content = msg.content or getattr(msg, "reasoning_content", "") or ""

            return SynthesizeResponse(
                arbiter_model=target_model,
                synthesis_text=content.strip(),
                latency_ms=elapsed_ms
            )
        except Exception as e:
            # Fallback to 120B model if 550B encounters error/timeout
            try:
                target_model = self.fallback_model
                res = await self.client.chat.completions.create(
                    model=target_model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_content}
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                msg = res.choices[0].message
                content = msg.content or getattr(msg, "reasoning_content", "") or ""
                return SynthesizeResponse(
                    arbiter_model=target_model,
                    synthesis_text=content.strip(),
                    latency_ms=elapsed_ms
                )
            except Exception as e2:
                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return SynthesizeResponse(
                    arbiter_model="error",
                    synthesis_text=f"Hakem sentezi sırasında bir hata oluştu: {str(e2)}",
                    latency_ms=elapsed_ms
                )

synthesis_service = SynthesisService()
