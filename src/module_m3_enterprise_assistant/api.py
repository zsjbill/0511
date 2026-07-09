"""
M3: Enterprise Assistant Module — API endpoints.
"""
from fastapi import APIRouter

from src.common.schemas import APIResponse, NL2SQLRequest, NL2SQLResponse
from src.module_m3_enterprise_assistant.service import enterprise_service

router = APIRouter(prefix="/api/v1/enterprise", tags=["M3 - Enterprise Assistant"])


@router.post("/nl2sql", response_model=APIResponse)
async def nl2sql(request: NL2SQLRequest) -> APIResponse:
    """Natural language → SQL query."""
    result: NL2SQLResponse = await enterprise_service.nl2sql(request)
    return APIResponse(data=result.model_dump())


@router.post("/voice", response_model=APIResponse)
async def process_voice() -> APIResponse:
    """Process voice input → structured text."""
    # TODO: implement voice processing
    return APIResponse(message="Voice processing endpoint")


@router.get("/org/{employee_id}", response_model=APIResponse)
async def org_query(employee_id: int) -> APIResponse:
    """Query organization structure."""
    result = await enterprise_service.query_org(employee_id)
    return APIResponse(data=result)


@router.get("/onboard/{employee_id}", response_model=APIResponse)
async def onboard_guide(employee_id: int) -> APIResponse:
    """New employee onboarding guide."""
    result = await enterprise_service.get_onboard_guide(employee_id)
    return APIResponse(data=result)
