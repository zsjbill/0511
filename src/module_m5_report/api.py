"""
M5: Report Module — API endpoints.
"""
from fastapi import APIRouter

from src.common.schemas import APIResponse, ReportRequest
from src.module_m5_report.service import report_service

router = APIRouter(prefix="/api/v1/reports", tags=["M5 - Reports"])


@router.post("/generate", response_model=APIResponse)
async def generate_report(request: ReportRequest) -> APIResponse:
    """Generate a report (daily/weekly/monthly)."""
    result = await report_service.generate(request)
    return APIResponse(data=result.model_dump())


@router.get("/", response_model=APIResponse)
async def list_reports(report_type: str = "daily", page: int = 1, page_size: int = 20) -> APIResponse:
    """List generated reports."""
    result = await report_service.list_reports(report_type, page, page_size)
    return APIResponse(data=result)


@router.get("/{report_id}", response_model=APIResponse)
async def get_report(report_id: int) -> APIResponse:
    """Get a specific report."""
    result = await report_service.get_report(report_id)
    return APIResponse(data=result)
