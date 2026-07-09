"""
M2: Customer Agent Module — API endpoints.
"""
from fastapi import APIRouter

from src.common.schemas import APIResponse, ChatRequest, ChatResponse, RegistrationRequest, RegistrationResponse
from src.module_m2_customer_agent.service import agent_service, registration_service

router = APIRouter(prefix="/api/v1/agent", tags=["M2 - Customer Agent"])


@router.post("/chat", response_model=APIResponse)
async def chat(request: ChatRequest) -> APIResponse:
    """Customer service chat endpoint."""
    result: ChatResponse = await agent_service.chat(request)
    return APIResponse(data=result.model_dump())


@router.post("/register", response_model=APIResponse)
async def register_activity(request: RegistrationRequest) -> APIResponse:
    """Activity registration endpoint."""
    result: RegistrationResponse = await registration_service.register(request)
    return APIResponse(data=result.model_dump())
