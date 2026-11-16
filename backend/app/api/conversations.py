from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.database.models import Conversation, ComparisonTurn, ModelResponseRecord
from app.schemas.conversation import (
    ConversationSummary,
    ConversationDetail,
    TurnDetail,
    CreateConversationRequest,
    UpdateConversationRequest
)
from app.schemas.compare import ModelResult

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.get("", response_model=List[ConversationSummary])
async def list_conversations(db: AsyncSession = Depends(get_db)):
    """List all saved conversations ordered by last updated"""
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.turns))
        .order_by(desc(Conversation.updated_at))
    )
    res = await db.execute(stmt)
    conversations = res.scalars().all()

    summaries = []
    for c in conversations:
        summaries.append(ConversationSummary(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            turns_count=len(c.turns)
        ))
    return summaries

@router.post("", response_model=ConversationSummary, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    req: CreateConversationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new comparison conversation"""
    title = (req.title or "New Comparison").strip()
    conv = Conversation(title=title)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return ConversationSummary(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        turns_count=0
    )

@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve full conversation history with all comparison turns and model responses"""
    stmt = (
        select(Conversation)
        .options(
            selectinload(Conversation.turns).selectinload(ComparisonTurn.responses)
        )
        .where(Conversation.id == conversation_id)
    )
    res = await db.execute(stmt)
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    turn_details = []
    for turn in conv.turns:
        resp_models = [
            ModelResult(
                model_id=r.model_id,
                model_name=r.model_name,
                provider=r.provider,
                response_text=r.response_text,
                response_time_ms=r.response_time_ms,
                status=r.status,
                error_message=r.error_message
            )
            for r in turn.responses
        ]
        turn_details.append(TurnDetail(
            id=turn.id,
            prompt=turn.prompt,
            system_prompt=turn.system_prompt,
            created_at=turn.created_at,
            responses=resp_models
        ))

    return ConversationDetail(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        turns=turn_details
    )

@router.patch("/{conversation_id}", response_model=ConversationSummary)
async def update_conversation(
    conversation_id: str,
    req: UpdateConversationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update conversation title"""
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    res = await db.execute(stmt)
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.title = req.title.strip()
    await db.commit()
    await db.refresh(conv)
    return ConversationSummary(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        turns_count=0
    )

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation and its turns"""
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    res = await db.execute(stmt)
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(conv)
    await db.commit()
    return None
