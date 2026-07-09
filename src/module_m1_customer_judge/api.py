"""
M1: Customer Judge Module — API endpoints.
"""
from fastapi import APIRouter, UploadFile

from src.common.schemas import APIResponse, CustomerJudgeRequest, CustomerJudgeResponse
from src.module_m1_customer_judge.service import judge_customer

router = APIRouter(prefix="/api/v1/judge", tags=["M1 - Customer Judge"])


@router.post("/", response_model=APIResponse)
async def judge(request: CustomerJudgeRequest) -> APIResponse:
    """Judge a customer: profile scoring + recommendation."""
    result: CustomerJudgeResponse = await judge_customer(request)
    return APIResponse(data=result.model_dump())


@router.post("/upload", response_model=APIResponse)
async def upload_file(file: UploadFile) -> APIResponse:
    """Upload a file for batch customer analysis."""
    # TODO: implement batch parsing and judging
    return APIResponse(message=f"File '{file.filename}' received, processing queued")
