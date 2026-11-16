import base64
import io
from fastapi import APIRouter, UploadFile, File, HTTPException
from pypdf import PdfReader

try:
    import pymupdf
except ImportError:
    pymupdf = None

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and parse documents (PDF, code, txt) or images for multi-model comparison.
    Uses pypdf as the primary PDF parser and optionally renders page previews if pymupdf is installed.
    """
    filename = file.filename or "uploaded_file"
    content_type = file.content_type or "application/octet-stream"

    contents = await file.read()
    size = len(contents)

    if size > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Dosya boyutu 25 MB limitini aşıyor.")

    lower_name = filename.lower()
    is_image = (
        content_type.startswith("image/")
        or any(lower_name.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"])
    )

    if is_image:
        mime = content_type if content_type.startswith("image/") else "image/png"
        b64 = base64.b64encode(contents).decode("utf-8")
        data_url = f"data:{mime};base64,{b64}"
        return {
            "filename": filename,
            "content_type": mime,
            "file_type": "image",
            "size": size,
            "data_url": data_url,
            "preview": f"Görsel ({filename}, {round(size/1024, 1)} KB)",
        }

    is_pdf = content_type == "application/pdf" or lower_name.endswith(".pdf")
    if is_pdf:
        try:
            reader = PdfReader(io.BytesIO(contents))
            pages_text = []
            page_images = []
            page_count = len(reader.pages)

            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(f"--- Sayfa {i + 1} ---\n{text.strip()}")

            if pymupdf is not None:
                doc = pymupdf.open(stream=contents, filetype="pdf")
                for i, page in enumerate(doc):
                    if i >= 4:
                        break
                    pix = page.get_pixmap(dpi=130)
                    png_bytes = pix.tobytes("png")
                    b64_page = base64.b64encode(png_bytes).decode("utf-8")
                    page_images.append(f"data:image/png;base64,{b64_page}")

            extracted_text = "\n\n".join(pages_text)
            if not extracted_text.strip():
                extracted_text = "[PDF görsel ve şemalardan oluşmaktadır. Görsel modeli şemaları doğrudan inceleyecektir]"

            preview = extracted_text[:200] + ("..." if len(extracted_text) > 200 else "")
            data_url = page_images[0] if page_images else None

            return {
                "filename": filename,
                "content_type": "application/pdf",
                "file_type": "document",
                "size": size,
                "extracted_text": extracted_text,
                "preview": preview,
                "page_count": page_count,
                "data_url": data_url,
                "page_images": page_images,
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF belgesi işlenemedi: {str(e)}")

    try:
        text_content = contents.decode("utf-8", errors="replace")
        preview = text_content[:200] + ("..." if len(text_content) > 200 else "")
        return {
            "filename": filename,
            "content_type": content_type or "text/plain",
            "file_type": "document",
            "size": size,
            "extracted_text": text_content,
            "preview": preview,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Belge okunamadı: {str(e)}")
