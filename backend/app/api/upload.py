import base64
from fastapi import APIRouter, UploadFile, File, HTTPException
import pymupdf

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and parse documents (PDF with visual schematics, code, txt) or images for multi-model comparison.
    Renders PDF pages as images so Vision models can see circuit diagrams and schematics.
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
            doc = pymupdf.open(stream=contents, filetype="pdf")
            pages_text = []
            page_images = []
            
            for i, page in enumerate(doc):
                text = page.get_text() or ""
                if text.strip():
                    pages_text.append(f"--- Sayfa {i+1} ---\n{text.strip()}")
                
                # Render the first 4 pages as high-resolution images for Vision models (circuit diagrams, charts)
                if i < 4:
                    pix = page.get_pixmap(dpi=130)
                    png_bytes = pix.tobytes("png")
                    b64_page = base64.b64encode(png_bytes).decode("utf-8")
                    page_images.append(f"data:image/png;base64,{b64_page}")
            
            extracted_text = "\n\n".join(pages_text)
            if not extracted_text.strip():
                extracted_text = "[PDF görsel ve şemalardan oluşmaktadır. Görsel modeli şemaları doğrudan inceleyecektir]"
            
            preview = extracted_text[:200] + ("..." if len(extracted_text) > 200 else "")
            
            # Thumbnail for first page
            data_url = page_images[0] if page_images else None
            
            return {
                "filename": filename,
                "content_type": "application/pdf",
                "file_type": "document",
                "size": size,
                "extracted_text": extracted_text,
                "preview": preview,
                "page_count": len(doc),
                "data_url": data_url,
                "page_images": page_images
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
