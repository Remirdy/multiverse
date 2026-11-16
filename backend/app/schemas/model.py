from typing import List, Optional
from pydantic import BaseModel

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    description: str
    category: str
    context_length: int
    is_available: bool = True
    is_default: bool = False
    tags: List[str] = []

class ModelListResponse(BaseModel):
    models: List[ModelInfo]
    default_models: List[str]
    total: int
