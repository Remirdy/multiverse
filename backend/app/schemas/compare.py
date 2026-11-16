from typing import List, Optional
from pydantic import BaseModel, Field

class CompareRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="User prompt to compare across models")
    model_ids: List[str] = Field(..., min_length=1, description="List of model IDs to query")
    conversation_id: Optional[str] = Field(None, description="Optional conversation UUID to associate with")
    system_prompt: Optional[str] = Field(None, description="Optional system instructions")
    timeout: Optional[float] = Field(None, description="Custom per-model timeout in seconds")

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

class RetryModelRequest(BaseModel):
    conversation_id: str
    turn_id: str
    model_id: str
    prompt: str
    system_prompt: Optional[str] = None
    timeout: Optional[float] = None
