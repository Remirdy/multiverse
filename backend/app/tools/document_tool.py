import io
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image
from pypdf import PdfReader
from docx import Document as DocxDocument
from pptx import Presentation

from app.core.config import settings


MAX_ARCHIVE_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
MAX_PDF_PAGES = 200


def check_local_tooling() -> Dict[str, Any]:
    """Report actual availability of optional local binaries and engines."""
    tesseract_path = shutil.which("tesseract")
    ngspice_path = shutil.which("ngspice")
    faster_whisper_installed = False
    whisper_installed = False
    try:
        import faster_whisper  # type: ignore  # noqa: F401
        faster_whisper_installed = True
    except ImportError:
        pass
    try:
        import whisper  # type: ignore  # noqa: F401
        whisper_installed = True
    except ImportError:
        pass

    return {
        "tesseract_ocr": bool(tesseract_path),
        "tesseract_path": tesseract_path,
        "ngspice": bool(ngspice_path),
        "faster_whisper": faster_whisper_installed,
        "openai_whisper": whisper_installed,
    }


def _validate_zip_archive(raw_bytes: bytes) -> None:
    """Protect against zip traversal and decompression bombs in DOCX/PPTX files."""
    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
        total_uncompressed = 0
        for info in zf.infolist():
            name = info.filename
            if name.startswith("/") or ".." in Path(name).parts:
                raise ValueError(f"Unsafe archive entry path detected: {name}")
            total_uncompressed += info.file_size
            if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                raise ValueError("Archive uncompressed size exceeds safety limit (100 MB).")


def extract_questions_from_text(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract numbered or labeled assignment questions from page-grounded text chunks."""
    questions: List[Dict[str, Any]] = []
    seen_texts = set()
    q_pattern = re.compile(
        r"(?:^|\n)\s*((?:Q(?:uestion)?\s*\d+|Soru\s*\d+|\d{1,2}[.)])\s+[^\n]+(?:\n(?!\s*(?:Q(?:uestion)?\s*\d+|Soru\s*\d+|\d{1,2}[.)])\s+)[^\n]+)*)",
        re.IGNORECASE,
    )
    for chunk in chunks:
        page_num = chunk.get("page", 1)
        text = chunk.get("text", "")
        for match in q_pattern.finditer(text):
            q_text = re.sub(r"\s+", " ", match.group(1)).strip()
            if len(q_text) < 8:
                continue
            norm = q_text.lower()
            if norm not in seen_texts:
                seen_texts.add(norm)
                questions.append({
                    "id": f"q_{len(questions) + 1}",
                    "question_text": q_text,
                    "page": page_num,
                    "source_ref": f"Page {page_num}",
                    "status": "pending",
                    "included": True,
                })
    return questions


def chunk_text_records(chunks: List[Dict[str, Any]], max_chars: int = 1200) -> List[Dict[str, Any]]:
    """Split extracted pages/slides into bounded retrieval chunks preserving page references."""
    out: List[Dict[str, Any]] = []
    for ch in chunks:
        page = ch.get("page", 1)
        text = (ch.get("text") or "").strip()
        if not text:
            continue
        start = 0
        while start < len(text):
            piece = text[start : start + max_chars].strip()
            if piece:
                out.append({"page": page, "chunk_index": len(out) + 1, "text": piece})
            start += max_chars
    return out


def parse_document_bytes(filename: str, raw_bytes: bytes, content_type: Optional[str] = None) -> Dict[str, Any]:
    """Parse PDF, DOCX, PPTX, TXT, MD, or PNG/JPG into structured page-grounded text and questions."""
    if not raw_bytes:
        raise ValueError("Uploaded file is empty.")
    if len(raw_bytes) > settings.MAX_UPLOAD_BYTES:
        raise ValueError("Uploaded file exceeds 25 MB limit.")

    ext = Path(filename or "").suffix.lower()
    mime = (content_type or "").lower()
    tooling = check_local_tooling()

    chunks: List[Dict[str, Any]] = []
    headings: List[str] = []
    tables: List[List[List[str]]] = []
    warnings: List[str] = []
    detected_type = "text"

    if ext == ".pdf" or mime == "application/pdf":
        if not raw_bytes.startswith(b"%PDF"):
            raise ValueError("File header does not match a valid PDF document.")
        detected_type = "pdf"
        reader = PdfReader(io.BytesIO(raw_bytes))
        if reader.is_encrypted:
            raise ValueError("Encrypted PDF documents require unlocking before intake.")
        if len(reader.pages) > MAX_PDF_PAGES:
            raise ValueError(f"PDF exceeds maximum supported page count ({MAX_PDF_PAGES} pages).")

        low_text_pages = 0
        for idx, page in enumerate(reader.pages, 1):
            text = (page.extract_text() or "").strip()
            if len(text) < 20:
                low_text_pages += 1
            if text:
                chunks.append({"page": idx, "text": text})
                for line in text.splitlines()[:4]:
                    if 4 <= len(line.strip()) <= 90 and line.strip().endswith((":", "")) and line.strip().istitle():
                        headings.append(line.strip())
        if low_text_pages > 0 and not tooling["tesseract_ocr"]:
            warnings.append(
                f"{low_text_pages} page(s) had sparse extractable text (possibly scanned images); "
                "local Tesseract OCR is not installed on this host."
            )

    elif ext == ".docx" or "wordprocessingml" in mime:
        _validate_zip_archive(raw_bytes)
        detected_type = "docx"
        doc = DocxDocument(io.BytesIO(raw_bytes))
        paras = []
        for p in doc.paragraphs:
            txt = p.text.strip()
            if not txt:
                continue
            paras.append(txt)
            if p.style and "heading" in (p.style.name or "").lower():
                headings.append(txt)
        for tbl in doc.tables:
            t_rows = [[cell.text.strip() for cell in row.cells] for row in tbl.rows]
            if t_rows:
                tables.append(t_rows)
                paras.append("\n".join(" | ".join(r) for r in t_rows))
        chunks.append({"page": 1, "text": "\n\n".join(paras)})

    elif ext == ".pptx" or "presentationml" in mime:
        _validate_zip_archive(raw_bytes)
        detected_type = "pptx"
        prs = Presentation(io.BytesIO(raw_bytes))
        for idx, slide in enumerate(prs.slides, 1):
            slide_texts = []
            if slide.shapes.title and slide.shapes.title.text.strip():
                headings.append(slide.shapes.title.text.strip())
            for shape in slide.shapes:
                if getattr(shape, "has_text_frame", False) and shape.text_frame:
                    t = shape.text_frame.text.strip()
                    if t:
                        slide_texts.append(t)
                if getattr(shape, "has_table", False) and shape.table:
                    t_rows = [[c.text.strip() for c in r.cells] for r in shape.table.rows]
                    tables.append(t_rows)
                    slide_texts.append("\n".join(" | ".join(r) for r in t_rows))
            if slide_texts:
                chunks.append({"page": idx, "text": "\n".join(slide_texts)})

    elif ext in {".png", ".jpg", ".jpeg"} or mime in {"image/png", "image/jpeg"}:
        detected_type = "image"
        with Image.open(io.BytesIO(raw_bytes)) as img:
            width, height = img.size
            fmt = img.format
        ocr_text = ""
        if tooling["tesseract_ocr"] and tooling["tesseract_path"]:
            with tempfile.NamedTemporaryFile(suffix=ext or ".png", delete=True) as tmp:
                tmp.write(raw_bytes)
                tmp.flush()
                try:
                    proc = subprocess.run(
                        [tooling["tesseract_path"], tmp.name, "stdout"],
                        capture_output=True,
                        text=True,
                        timeout=12,
                    )
                    if proc.returncode == 0:
                        ocr_text = proc.stdout.strip()
                except Exception as exc:
                    warnings.append(f"OCR execution failed: {exc}")
        else:
            warnings.append("Image uploaded; local Tesseract OCR binary is not installed, so image text extraction is unavailable without a vision model.")
        chunks.append({
            "page": 1,
            "text": ocr_text or f"[Image {fmt} {width}x{height}px uploaded; verify with vision model or manual text input]",
        })

    elif ext in {".txt", ".md", ".markdown", ".csv", ".json", ".py", ".js", ".ts"} or mime.startswith("text/"):
        detected_type = "markdown" if ext in {".md", ".markdown"} else "text"
        text = raw_bytes.decode("utf-8", errors="replace").strip()
        for line in text.splitlines():
            if line.startswith("#"):
                headings.append(line.lstrip("#").strip())
        chunks.append({"page": 1, "text": text})

    else:
        raise ValueError(f"Unsupported file format '{ext or mime}'. Supported formats: PDF, DOCX, PPTX, TXT, MD, PNG, JPG.")

    full_text = "\n\n".join(f"[Page {c['page']}]\n{c['text']}" for c in chunks)
    bounded_chunks = chunk_text_records(chunks)
    questions = extract_questions_from_text(chunks)

    return {
        "file_type": detected_type,
        "page_count": max(1, len(chunks)),
        "headings": headings[:40],
        "tables_count": len(tables),
        "tables": tables[:15],
        "chunks": bounded_chunks,
        "extracted_text": full_text,
        "questions": questions,
        "warnings": warnings,
        "tooling": tooling,
    }


def validate_citations(text: str, source_chunks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Validate DOI/URL syntax locally and cross-check inline references against uploaded sources."""
    doi_pattern = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b")
    url_pattern = re.compile(r"https?://[^\s)\]\"'>]+")
    page_ref_pattern = re.compile(r"\[(?:Page|Sayfa)\s+(\d+)\]", re.IGNORECASE)

    dois = sorted(set(doi_pattern.findall(text or "")))
    urls = sorted(set(url_pattern.findall(text or "")))
    cited_pages = sorted({int(p) for p in page_ref_pattern.findall(text or "")})

    available_pages = {int(ch.get("page", 0)) for ch in (source_chunks or []) if ch.get("page")}
    matched_pages = [p for p in cited_pages if p in available_pages]
    missing_pages = [p for p in cited_pages if available_pages and p not in available_pages]

    doi_checks = [
        {
            "doi": d,
            "syntax_valid": bool(doi_pattern.fullmatch(d)),
            "verification_status": "syntax_checked_only",
            "note": "Online DOI resolution is disabled; syntax validated locally.",
        }
        for d in dois
    ]
    return {
        "dois": doi_checks,
        "urls": urls,
        "cited_pages": cited_pages,
        "matched_source_pages": matched_pages,
        "missing_source_pages": missing_pages,
    }
