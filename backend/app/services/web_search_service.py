import re
import asyncio
from typing import List, Tuple
from ddgs import DDGS
from app.schemas.search import WebSearchResultItem

class WebSearchService:
    @staticmethod
    def clean_search_query(raw_prompt: str) -> str:
        """
        Extract the core search terms from a conversational user prompt.
        e.g., '2. sınıf bilgisayar mühendisliği öğrencisiyim, yurt dışında ROS 2 ve otonom sistemler üzerine remote staj ilanları ver'
        -> 'ROS 2 autonomous systems remote internship'
        """
        # Remove common chat noise words
        noise = [
            r"\b(?:merhaba|selam|lütfen|bana|istiyorum|verir misin|bulur musun|arıyorum|öğrencisiyim|sınıf)\b",
            r"\b(?:2\.\s*sınıf|3\.\s*sınıf|4\.\s*sınıf|bilgisayar mühendisliği)\b",
            r"\b(?:ver|listele|sırala|yaz|göster|öner)\b",
            r"\b(?:son\s*\d+\s*(?:ay|gün|hafta)|güncel|çalışır|aktif)\b"
        ]
        cleaned = raw_prompt
        for p in noise:
            cleaned = re.sub(p, " ", cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r"[?!.,;:\"'(){}\[\]]", " ", cleaned)
        words = [w.strip() for w in cleaned.split() if len(w.strip()) > 1]
        
        # Keep top 6 informative keywords
        query = " ".join(words[:6])
        return query.strip() or raw_prompt[:50]

    async def search(self, prompt: str, max_results: int = 5) -> Tuple[List[WebSearchResultItem], str]:
        """
        Executes web search in a non-blocking thread and returns structured items + formatted grounding prompt.
        """
        query = self.clean_search_query(prompt)

        def _do_search():
            items = []
            try:
                with DDGS() as ddgs:
                    # First try cleaned query
                    raw = list(ddgs.text(query, max_results=max_results))
                    if not raw:
                        # Fallback to first 4 words of raw prompt
                        fallback_query = " ".join(prompt.split()[:4])
                        raw = list(ddgs.text(fallback_query, max_results=max_results))

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
                # If search throws, try safe fallback query
                try:
                    with DDGS() as ddgs:
                        raw = list(ddgs.text(prompt[:30], max_results=3))
                        for r in raw:
                            items.append(WebSearchResultItem(
                                title=r.get("title", ""),
                                link=r.get("href", ""),
                                snippet=r.get("body", "")
                            ))
                except Exception:
                    pass
            return items

        results = await asyncio.to_thread(_do_search)

        if not results:
            return [], ""

        grounding_lines = [
            "🌐 [CANLI İNTERNET ARAMA SONUÇLARI - Gerçek Zamanlı Veri]:",
            "Aşağıdaki bağlantılar ve içerikler canlı internet aramasından güncel olarak çekilmiştir.",
            "Kullanıcının sorusuna doğrudan bu gerçek kaynakları kullanarak, çalışan ve tıklanabilir [Başlık](URL) linkleri vererek yanıt ver.",
            "Asla 'veritabanına erişimim yok' deme; çünkü canlı web verisi sana sağlanmıştır:\n"
        ]
        for i, item in enumerate(results, 1):
            grounding_lines.append(f"{i}. Başlık: {item.title}")
            grounding_lines.append(f"   Link: {item.link}")
            grounding_lines.append(f"   Özet: {item.snippet}\n")

        grounding_text = "\n".join(grounding_lines)
        return results, grounding_text

web_search_service = WebSearchService()
