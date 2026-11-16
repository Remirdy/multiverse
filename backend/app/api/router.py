from fastapi import APIRouter
from app.schemas.router import RouteRequest, RouteResponse
from app.services.routing_service import routing_service

router = APIRouter(prefix="/route", tags=["Routing"])

@router.post("", response_model=RouteResponse)
async def route_prompt(request: RouteRequest):
    """
    Automatic Model Routing:
    Analyzes prompt intent (programming, math, science, robotics, creative, etc.)
    and recommends the most suitable models.
    """
    return routing_service.classify(request.prompt)
