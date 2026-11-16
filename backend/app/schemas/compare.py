from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.search import WebSearchResultItem

class AttachmentItem(BaseModel):
    filename: str
    content_type: str
    file_type: str  # "image" or "document"
    size: int
    data_url: Optional[str] = None  # for images
    extracted_text: Optional[str] = None  # for documents
    preview: Optional[str] = None
    page_count: Optional[int] = None
    page_images: Optional[List[str]] = None  # Rendered PDF pages as images for Vision models

class CompareRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="User prompt to compare across models")
    model_ids: List[str] = Field(..., min_length=1, description="List of model IDs to query")
    conversation_id: Optional[str] = Field(None, description="Optional conversation UUID to associate with")
    system_prompt: Optional[str] = Field(None, description="Optional system instructions")
    timeout: Optional[float] = Field(None, description="Custom per-model timeout in seconds")
    attachments: Optional[List[AttachmentItem]] = Field(default=None, description="Uploaded files/images")
    web_search: Optional[bool] = Field(default=False, description="Enable live internet search grounding")

class ModelResult(BaseModel):
    model_id: str
    model_name: str
    provider: str
    response_text: Optional[str] = None
    response_time_ms: Optional[float] = None
    status: str  # 'success', 'error', 'timeout'
    error_message: Optional[str] = None

class CompareResponse(BaseModel):
    conversation_id: str
    turn_id: str
    prompt: str
    results: List[ModelResult]
    total_models: int
    successful_models: int
    failed_models: int
    attachments: Optional[List[AttachmentItem]] = None
    web_search_results: Optional[List[WebSearchResultItem]] = None

class RetryModelRequest(BaseModel):
    conversation_id: str
    turn_id: str
    model_id: str
    prompt: str
    system_prompt: Optional[str] = None
    timeout: Optional[float] = None
    attachments: Optional[List[AttachmentItem]] = None
    web_search: Optional[bool] = False

class ModelResponseSummary(BaseModel):
    model_id: str
    model_name: str
    response_text: str

class SynthesizeRequest(BaseModel):
    prompt: str
    responses: List[ModelResponseSummary]
    language: Optional[str] = "tr"

class SynthesizeResponse(BaseModel):
    arbiter_model: str
    synthesis_text: str
    latency_ms: float
