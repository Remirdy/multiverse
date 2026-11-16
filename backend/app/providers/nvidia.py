import time
import json
import asyncio
import urllib.parse
from typing import Optional, List, Dict, Any, Tuple
import requests
from lxml import html
from openai import AsyncOpenAI, APIError, AuthenticationError, RateLimitError
from ddgs import DDGS
from app.core.config import settings
from app.providers.base import BaseProvider, ProviderResponse
from app.providers.registry import model_registry

AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches the live internet for active job listings, internships, real-time facts, current news, official docs, or verified links. Call this whenever answering requires up-to-date or specific external web data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Targeted search keywords (in English or Turkish) optimized to find relevant listings or pages."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def _clean_url(href: str) -> str:
    if not href:
        return ""
    if "uddg=" in href:
        try:
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
            if "uddg" in parsed:
                return parsed["uddg"][0]
        except Exception:
            pass
    if href.startswith("//"):
        return "https:" + href
    return href

def _sync_web_search(query: str, max_results: int = 5) -> Tuple[str, List[Dict[str, str]]]:
    items: List[Dict[str, str]] = []
    
    # 1. Primary: Direct DDG HTML query (fast, bypasses bot challenges, returns direct job/career URLs)
    try:
        resp = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
            timeout=6
        )
        if resp.status_code == 200:
            tree = html.fromstring(resp.content)
            for r in tree.xpath('//div[contains(@class, "result__body")]'):
                title_elem = r.xpath('.//h2/a')
                snippet_elem = r.xpath('.//a[contains(@class, "result__snippet")]')
                if title_elem:
                    title = "".join(title_elem[0].xpath('.//text()')).strip()
                    href = _clean_url(title_elem[0].get("href", ""))
                    snippet = "".join(snippet_elem[0].xpath('.//text()')).strip() if snippet_elem else ""
                    if title and href and not href.startswith("https://duckduckgo.com"):
                        items.append({"title": title, "link": href, "snippet": snippet})
                        if len(items) >= max_results:
                            break
    except Exception as e:
        print(f"[_sync_web_search HTML search error for '{query}']: {e}")

    # 2. Fallback to ddgs library if HTML returned no results
    if not items:
        try:
            with DDGS() as ddgs:
                raw = list(ddgs.text(query, max_results=max_results))
                for r in raw:
                    t = r.get("title", "").strip()
                    l = _clean_url(r.get("href", "").strip())
                    s = r.get("body", "").strip()
                    if t and l:
                        items.append({"title": t, "link": l, "snippet": s})
        except Exception as e:
            print(f"[_sync_web_search ddgs fallback error for '{query}']: {e}")

    if not items:
        return "Canlı arama sonucu bulunamadı.", []

    lines = []
    for it in items:
        lines.append(f"- **Başlık**: {it['title']}\n  **Link**: {it['link']}\n  **Özet**: {it['snippet']}")
    return "\n\n".join(lines), items

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

        # Generous limits for multi-problem visual exam, deep reasoning, and long tables
        effective_max_tokens = 8192
        effective_timeout = max(timeout or 90.0, 120.0)

        start_time = time.perf_counter()

        try:
            # Autonomous Tool Capability: models decide entirely on their own when to call web_search
            tools_param = AVAILABLE_TOOLS if not is_vision else None
            tool_choice_param = "auto" if not is_vision else None

            completion_coroutine = client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=0.7,
                max_tokens=effective_max_tokens,
                timeout=effective_timeout,
                tools=tools_param,
                tool_choice=tool_choice_param
            )
            completion = await asyncio.wait_for(completion_coroutine, timeout=effective_timeout)
            
            msg = completion.choices[0].message

            # Autonomous Tool Execution (ReAct Loop)
            collected_search_items: List[Dict[str, str]] = []
            if msg.tool_calls:
                messages.append(msg)
                for tc in msg.tool_calls:
                    fn_name = tc.function.name
                    if fn_name == "web_search":
                        try:
                            args = json.loads(tc.function.arguments)
                            search_q = args.get("query", "")
                        except Exception:
                            search_q = str(tc.function.arguments)

                        search_obs, items = await asyncio.to_thread(_sync_web_search, search_q, 6)
                        if items:
                            collected_search_items.extend(items)

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": f"[Canlı Arama Sonuçları - '{search_q}']:\n{search_obs}"
                        })

                # Follow-up directive to ensure synthesis into grounded markdown response
                messages.append({
                    "role": "user",
                    "content": "Canlı arama tamamlandı. Lütfen yukarıdaki arama sonuçlarında yer alan çalışan doğrudan bağlantıları ([Başlık](URL) biçiminde) ve gerçek pozisyonları kullanarak kullanıcının sorusuna doğrudan, eksiksiz ve profesyonel Türkçe nihai cevabını yaz."
                })

                # Second turn: Generate final response grounded in live web findings
                second_coroutine = client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=effective_max_tokens,
                    timeout=effective_timeout
                )
                second_completion = await asyncio.wait_for(second_coroutine, timeout=effective_timeout)
                final_msg = second_completion.choices[0].message
                content = final_msg.content or getattr(final_msg, "reasoning_content", "") or ""
                if "<tool_call>" in content:
                    import re
                    content = re.sub(r"<tool_call>[\s\S]*?</tool_call>", "", content).strip()
            else:
                content = msg.content or getattr(msg, "reasoning_content", "") or ""

            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            return ProviderResponse(
                model_id=model_id,
                model_name=model_name,
                provider=provider_name,
                response_text=content,
                response_time_ms=elapsed_ms,
                status="success",
                error_message=None,
                search_results=collected_search_items if collected_search_items else None
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
