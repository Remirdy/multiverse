from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.compare import CompareRequest, CompareResponse, RetryModelRequest, ModelResult
from app.services.compare_service import compare_service

router = APIRouter(prefix="/compare", tags=["Comparison"])

@router.post("", response_model=CompareResponse)
async def compare_prompt(
    request: CompareRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a prompt concurrently to multiple AI models.
    Handles individual failures without aborting successful responses.
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    if not request.model_ids:
        raise HTTPException(status_code=400, detail="At least one model must be selected")

    return await compare_service.compare_models(
        prompt=request.prompt,
        model_ids=request.model_ids,
        conversation_id=request.conversation_id,
        system_prompt=request.system_prompt,
        timeout=request.timeout,
        db=db
    )

@router.post("/retry", response_model=ModelResult)
async def retry_model(
    request: RetryModelRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Retry a specific failed or timed-out model for a given turn.
    """
    return await compare_service.retry_single_model(
        conversation_id=request.conversation_id,
        turn_id=request.turn_id,
        model_id=request.model_id,
        prompt=request.prompt,
        system_prompt=request.system_prompt,
        timeout=request.timeout,
        db=db
    )
