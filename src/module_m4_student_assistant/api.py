"""
M4: Student Assistant Module — API endpoints.
"""
from fastapi import APIRouter

from src.common.schemas import APIResponse, RiskDetectionRequest, RiskDetectionResponse
from src.module_m4_student_assistant.service import student_service

router = APIRouter(prefix="/api/v1/student", tags=["M4 - Student Assistant"])


@router.post("/risk", response_model=APIResponse)
async def detect_risk(request: RiskDetectionRequest) -> APIResponse:
    """Detect psychological risk in student conversations."""
    result: RiskDetectionResponse = await student_service.detect_risk(request)
    return APIResponse(data=result.model_dump())


@router.post("/leave", response_model=APIResponse)
async def leave_request() -> APIResponse:
    """Submit a leave request."""
    # TODO: implement
    return APIResponse(message="Leave request endpoint")


@router.get("/life/{student_id}", response_model=APIResponse)
async def life_knowledge(student_id: int, query: str = "") -> APIResponse:
    """Query overseas life knowledge base."""
    result = await student_service.query_life_knowledge(student_id, query)
    return APIResponse(data=result)


@router.post("/complaint/summarize", response_model=APIResponse)
async def summarize_complaint() -> APIResponse:
    """Summarize a student complaint."""
    # TODO: implement
    return APIResponse(message="Complaint summarization endpoint")


@router.post("/marketing/generate", response_model=APIResponse)
async def generate_marketing() -> APIResponse:
    """Generate marketing copy for value-added services."""
    # TODO: implement
    return APIResponse(message="Marketing generation endpoint")
