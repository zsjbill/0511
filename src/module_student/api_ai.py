from fastapi import APIRouter
from src.common.schemas_student import (
    APIResponse, RiskDetectRequest, SummarizeRequest, MarketingGenerateRequest,
)
from src.module_student.risk_monitor import detect_risk
from src.module_student.summarizer import summarize_complaint
from src.module_student.marketing import generate_marketing

router = APIRouter(prefix="/api/v1/student/ai", tags=["Student - AI"])

@router.post("/risk-detect", response_model=APIResponse)
async def risk_detect(request: RiskDetectRequest):
    try:
        result = await detect_risk(request.student_id, request.student_name, request.conversation_text)
        return APIResponse(data=result)
    except Exception as e:
        return APIResponse(code=500, message=str(e))

@router.post("/summarize", response_model=APIResponse)
async def summarize(request: SummarizeRequest):
    try:
        result = await summarize_complaint(request.complaint_text)
        return APIResponse(data=result)
    except Exception as e:
        return APIResponse(code=500, message=str(e))

@router.post("/marketing", response_model=APIResponse)
async def marketing(request: MarketingGenerateRequest):
    try:
        result = await generate_marketing(
            request.student_id, request.student_name,
            request.emotion_tags, request.scores, request.study_interest,
        )
        return APIResponse(data=result)
    except Exception as e:
        return APIResponse(code=500, message=str(e))
