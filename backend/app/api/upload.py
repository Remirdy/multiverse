import base64
import io
from fastapi import APIRouter, UploadFile, File, HTTPException
import pypdf

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and parse documents (PDF, code, txt) or images for multi-model comparison.
    """
    filename = file.filename or "uploaded_file"
    content_type = file.content_type or "application/octet-stream"
    
    contents = await file.read()
    size = len(contents)
    
    # 25 MB max limit
    if size > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Dosya boyutu 25 MB limitini aşıyor.")
        
    lower_name = filename.lower()
    is_image = (
        content_type.startswith("image/") or
        any(lower_name.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"])
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
            "preview": f"Görsel ({filename}, {round(size/1024, 1)} KB)"
        }
        
    is_pdf = content_type == "application/pdf" or lower_name.endswith(".pdf")
    if is_pdf:
        try:
            reader = pypdf.PdfReader(io.BytesIO(contents))
            pages_text = []
            for i, page in enumerate(reader.pages[:50]):  # up to 50 pages
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(f"--- Sayfa {i+1} ---\n{text.strip()}")
            extracted_text = "\n\n".join(pages_text)
            if not extracted_text.strip():
                extracted_text = "[PDF taranmış görsel veya metin içermeyen sayfalardan oluşuyor]"
            
            preview = extracted_text[:200] + ("..." if len(extracted_text) > 200 else "")
            return {
                "filename": filename,
                "content_type": "application/pdf",
                "file_type": "document",
                "size": size,
                "extracted_text": extracted_text,
                "preview": preview,
                "page_count": len(reader.pages)
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF belgesi işlenemedi: {str(e)}")
            
    # Text, markdown, code, csv, json files
    try:
        text_content = contents.decode("utf-8", errors="replace")
        preview = text_content[:200] + ("..." if len(text_content) > 200 else "")
        return {
            "filename": filename,
            "content_type": content_type or "text/plain",
            "file_type": "document",
            "size": size,
            "extracted_text": text_content,
            "preview": preview
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Belge okunamadı: {str(e)}")
