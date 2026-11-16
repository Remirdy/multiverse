from typing import List, Optional
from pydantic import BaseModel

class RouteRequest(BaseModel):
    prompt: str

class RouteResponse(BaseModel):
    category: str
    category_label: str
    confidence: float
    reasoning: str
    recommended_model_ids: List[str]

class EnhancePromptRequest(BaseModel):
    prompt: str
    language: Optional[str] = "tr"

class EnhancePromptResponse(BaseModel):
    original_prompt: str
    enhanced_prompt: str
    latency_ms: float
    model_used: str
