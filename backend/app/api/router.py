from fastapi import APIRouter
from app.schemas.router import RouteRequest, RouteResponse, EnhancePromptRequest, EnhancePromptResponse
from app.services.routing_service import routing_service
from app.services.prompt_service import prompt_service

router = APIRouter(prefix="/route", tags=["Routing"])

@router.post("", response_model=RouteResponse)
async def route_prompt(request: RouteRequest):
    """
    Automatic Model Routing:
    Analyzes prompt intent (programming, math, science, robotics, creative, etc.)
    and recommends the most suitable models.
    """
    return routing_service.classify(request.prompt)

@router.post("/enhance", response_model=EnhancePromptResponse)
async def enhance_prompt(request: EnhancePromptRequest):
    """
    Magic Prompt Enhancer:
    Uses sub-second NVIDIA Nemotron Bolt to transform a brief or rough prompt
    into an industry-grade, structured prompt for peak model output.
    """
    return await prompt_service.enhance(request.prompt, request.language or "tr")
