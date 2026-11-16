from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.compare import ModelResult

class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    turns_count: int = 0

class TurnDetail(BaseModel):
    id: str
    prompt: str
    system_prompt: Optional[str] = None
    created_at: datetime
    responses: List[ModelResult] = []

class ConversationDetail(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    turns: List[TurnDetail] = []

class CreateConversationRequest(BaseModel):
    title: Optional[str] = None

class UpdateConversationRequest(BaseModel):
    title: str
