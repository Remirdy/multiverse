from typing import List
from pydantic import BaseModel

class RouteRequest(BaseModel):
    prompt: str

class RouteResponse(BaseModel):
    category: str
    category_label: str
    confidence: float
    reasoning: str
    recommended_model_ids: List[str]
