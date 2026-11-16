import time
from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.router import EnhancePromptResponse

class PromptEnhancementService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings.NVIDIA_BASE_URL,
            api_key=settings.NVIDIA_API_KEY
        )
        # Nemotron Bolt is sub-second (under 1s) and provides exceptional instruction following
        self.model = "nvidia/nemotron-3.5-bolt-e4b"

    async def enhance(self, prompt: str, language: str = "tr") -> EnhancePromptResponse:
        start_time = time.perf_counter()

        system_instruction = (
            "Sen dünyanın en yetenekli yapay zekâ prompt mühendisisin. "
            "Kullanıcının yazdığı kısa, sade veya eksik soruyu/istemi; yapay zekalardan (kodlama, mantık, matematik, mimari) "
            "en detaylı, profesyonel, hatasız ve prodüksiyon seviyesinde yanıt alabilmesi için mükemmel bir prompt'a dönüştür.\n\n"
            "Önemli Kurallar:\n"
            "1. Kullanıcının dilini aynen koru (Türkçe ise Türkçe, İngilizce ise İngilizce).\n"
            "2. Gerekli teknik kütüphaneleri, mimari desenleri, hata yönetimini, güvenlik kriterlerini ve beklenen çıktı formatını netleştir.\n"
            "3. Asla giriş/çıkış selamlaması ('İşte geliştirilmiş prompt:' vb.) yapma.\n"
            "4. YALNIZCA ve DOĞRUDAN geliştirilmiş prompt metnini tırnak işareti olmadan döndür."
        )

        try:
            res = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            content = res.choices[0].message.content or getattr(res.choices[0].message, "reasoning_content", "") or prompt
            enhanced_text = content.strip().strip('"').strip("'")

            return EnhancePromptResponse(
                original_prompt=prompt,
                enhanced_prompt=enhanced_text,
                latency_ms=elapsed_ms,
                model_used=self.model
            )
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            # Fallback to original prompt if error
            return EnhancePromptResponse(
                original_prompt=prompt,
                enhanced_prompt=prompt,
                latency_ms=elapsed_ms,
                model_used="fallback"
            )

prompt_service = PromptEnhancementService()
