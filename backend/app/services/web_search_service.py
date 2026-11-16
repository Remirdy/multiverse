import re
import asyncio
from typing import List, Tuple
from openai import AsyncOpenAI
from ddgs import DDGS
from app.core.config import settings
from app.schemas.search import WebSearchResultItem

class WebSearchService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings.NVIDIA_BASE_URL,
            api_key=settings.NVIDIA_API_KEY
        )
        self.fast_model = "nvidia/nemotron-3.5-bolt-e4b"

    async def generate_search_query(self, prompt: str) -> str:
        """
        Uses sub-second Nemotron Bolt to transform conversational user prompts
        into high-relevance search engine keywords (e.g., in English for global jobs).
        """
        try:
            res = await self.client.chat.completions.create(
                model=self.fast_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a search query optimizer. Given a user prompt, output ONLY a 3 to 6 word "
                            "precision search engine query (in English for job/tech queries) to find actual active listings, pages, or docs. "
                            "No quotes, no preamble, only the query words."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=25,
                temperature=0.1,
                timeout=4.0
            )
            query = res.choices[0].message.content or ""
            query = query.strip().strip('"').strip("'").strip()
            if query and len(query) > 3:
                return query
        except Exception as e:
            print("AI search query generation fallback:", e)

        # Fallback to keyword extraction
        noise = [
            r"\b(?:merhaba|selam|lütfen|bana|istiyorum|verir misin|bulur musun|arıyorum|öğrencisiyim|sınıf)\b",
            r"\b(?:2\.\s*sınıf|3\.\s*sınıf|4\.\s*sınıf|bilgisayar mühendisliği)\b",
            r"\b(?:ver|listele|sırala|yaz|göster|öner)\b",
            r"\b(?:son\s*\d+\s*(?:ay|gün|hafta)|güncel|çalışır|aktif)\b"
        ]
        cleaned = prompt
        for p in noise:
            cleaned = re.sub(p, " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"[?!.,;:\"'(){}\[\]]", " ", cleaned)
        words = [w.strip() for w in cleaned.split() if len(w.strip()) > 1]
        return " ".join(words[:5]) or prompt[:50]

    async def search(self, prompt: str, max_results: int = 6) -> Tuple[List[WebSearchResultItem], str]:
        """
        Generates an optimized search query, searches DuckDuckGo, and returns grounded context.
        """
        search_query = await self.generate_search_query(prompt)
        print(f"[WebSearch] Prompt: '{prompt[:40]}...' -> Search Query: '{search_query}'")

        def _do_search(q: str):
            items = []
            try:
                with DDGS() as ddgs:
                    raw = list(ddgs.text(q, max_results=max_results))
                    for r in raw:
                        title = r.get("title", "").strip()
                        link = r.get("href", "").strip()
                        snippet = r.get("body", "").strip()
                        if title and link:
                            items.append(WebSearchResultItem(
                                title=title,
                                link=link,
                                snippet=snippet
                            ))
            except Exception as e:
                print(f"[WebSearch] Error searching '{q}':", e)
            return items

        results = await asyncio.to_thread(_do_search, search_query)

        # If zero results, try fallback query with 'internship jobs'
        if not results:
            fallback_q = search_query + " jobs"
            results = await asyncio.to_thread(_do_search, fallback_q)

        if not results:
            return [], ""

        grounding_lines = [
            "🌐 [CANLI İNTERNET ARAMA SONUÇLARI - Gerçek Zamanlı Veri]:",
            f"Arama Sorgusu: '{search_query}'",
            "Aşağıdaki bağlantılar ve içerikler canlı internet aramasından güncel olarak çekilmiştir.",
            "Kullanıcının sorusuna doğrudan bu gerçek kaynakları kullanarak, çalışan ve tıklanabilir [Başlık](URL) linkleri vererek yanıt ver.",
            "Eğer kullanıcı tablo veya JSON formatı istediyse, bu gerçek linkleri ve başlıkları tablonun/JSON'un içine yerleştir.",
            "Asla 'veritabanına erişimim yok' veya 'arama sonuçları genel bilgi içeriyor' gibi bahaneler sunma; bu canlı ilan platformlarını ve açık pozisyonları doğrudan kullan:\n"
        ]
        for i, item in enumerate(results, 1):
            grounding_lines.append(f"{i}. Başlık: {item.title}")
            grounding_lines.append(f"   Link: {item.link}")
            grounding_lines.append(f"   Özet: {item.snippet}\n")

        grounding_text = "\n".join(grounding_lines)
        return results, grounding_text

web_search_service = WebSearchService()
