"""
Enterprise Assistant CRUD API — 4 tables, 20 endpoints.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.crud_base import CRUDBase
from src.common.database import get_enterprise_db
from src.common.models_enterprise import (
    ComplaintFeedback,
    EmployeeDailyReport,
    IntentCustomer,
    StudentScore,
)
from src.common.schemas_enterprise import (
    APIResponse,
    ComplaintFeedbackCreate,
    ComplaintFeedbackResponse,
    ComplaintFeedbackUpdate,
    EmployeeDailyReportCreate,
    EmployeeDailyReportResponse,
    EmployeeDailyReportUpdate,
    IntentCustomerCreate,
    IntentCustomerResponse,
    IntentCustomerUpdate,
    PaginatedData,
    StudentScoreCreate,
    StudentScoreResponse,
    StudentScoreUpdate,
)

router = APIRouter(prefix="/api/v1/enterprise", tags=["Enterprise Assistant"])

# ── CRUD instances ────────────────────────────────────────────────────
customer_crud = CRUDBase(IntentCustomer, IntentCustomerCreate, IntentCustomerUpdate)
report_crud = CRUDBase(EmployeeDailyReport, EmployeeDailyReportCreate, EmployeeDailyReportUpdate)
complaint_crud = CRUDBase(ComplaintFeedback, ComplaintFeedbackCreate, ComplaintFeedbackUpdate)
score_crud = CRUDBase(StudentScore, StudentScoreCreate, StudentScoreUpdate)


# ── Helpers ────────────────────────────────────────────────────────────

def paginated_response(items: list, total: int, page: int, page_size: int, total_pages: int) -> APIResponse:
    """Wrap paginated result in a standard API response."""
    return APIResponse(data=PaginatedData(
        items=items, total=total, page=page, page_size=page_size, total_pages=total_pages,
    ).model_dump())


async def _get_or_404(crud: CRUDBase, id: int, db: AsyncSession, response_schema: type):
    """Fetch a single record or return a 404 response."""
    obj = await crud.get(db, id)
    if obj is None:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=response_schema.model_validate(obj).model_dump())


async def _create_record(crud: CRUDBase, data, db: AsyncSession, response_schema: type):
    """Create a record and return it."""
    obj = await crud.create(db, data)
    return APIResponse(data=response_schema.model_validate(obj).model_dump())


async def _update_record(crud: CRUDBase, id: int, data, db: AsyncSession, response_schema: type):
    """Update a record or return a 404."""
    obj = await crud.update(db, id, data)
    if obj is None:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=response_schema.model_validate(obj).model_dump())


async def _delete_record(crud: CRUDBase, id: int, db: AsyncSession):
    """Delete a record or return a 404."""
    deleted = await crud.delete(db, id)
    if not deleted:
        return APIResponse(code=404, message="Not found")
    return APIResponse(message="Deleted successfully")


# ── Customers ─────────────────────────────────────────────────────────

@router.get("/customers", response_model=APIResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    customer_name: Optional[str] = Query(None, description="Customer name (LIKE)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Created at start date"),
    end_date: Optional[str] = Query(None, description="Created at end date"),
    db: AsyncSession = Depends(get_enterprise_db),
):
    kwargs = {}
    if customer_name:
        kwargs["customer_name__like"] = customer_name
    if status:
        kwargs["status"] = status
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    result = await customer_crud.list(db, page=page, page_size=page_size, **kwargs)
    result["items"] = [IntentCustomerResponse.model_validate(item).model_dump() for item in result["items"]]
    return paginated_response(**result)


@router.get("/customers/{id}", response_model=APIResponse)
async def get_customer(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    return await _get_or_404(customer_crud, id, db, IntentCustomerResponse)


@router.post("/customers", response_model=APIResponse)
async def create_customer(data: IntentCustomerCreate, db: AsyncSession = Depends(get_enterprise_db)):
    return await _create_record(customer_crud, data, db, IntentCustomerResponse)


@router.put("/customers/{id}", response_model=APIResponse)
async def update_customer(id: int, data: IntentCustomerUpdate, db: AsyncSession = Depends(get_enterprise_db)):
    return await _update_record(customer_crud, id, data, db, IntentCustomerResponse)


@router.delete("/customers/{id}", response_model=APIResponse)
async def delete_customer(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    return await _delete_record(customer_crud, id, db)


# ── Reports ───────────────────────────────────────────────────────────

@router.get("/reports", response_model=APIResponse)
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    department: Optional[str] = Query(None, description="Filter by department"),
    employee_name: Optional[str] = Query(None, description="Employee name (LIKE)"),
    start_date: Optional[str] = Query(None, description="Submitted at start date"),
    end_date: Optional[str] = Query(None, description="Submitted at end date"),
    db: AsyncSession = Depends(get_enterprise_db),
):
    kwargs = {}
    if department:
        kwargs["department"] = department
    if employee_name:
        kwargs["employee_name__like"] = employee_name
    if start_date:
        kwargs["submitted_at__gte"] = start_date
    if end_date:
        kwargs["submitted_at__lte"] = end_date
    result = await report_crud.list(db, page=page, page_size=page_size, **kwargs)
    result["items"] = [EmployeeDailyReportResponse.model_validate(item).model_dump() for item in result["items"]]
    return paginated_response(**result)


@router.get("/reports/{id}", response_model=APIResponse)
async def get_report(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    return await _get_or_404(report_crud, id, db, EmployeeDailyReportResponse)


@router.post("/reports", response_model=APIResponse)
async def create_report(data: EmployeeDailyReportCreate, db: AsyncSession = Depends(get_enterprise_db)):
    return await _create_record(report_crud, data, db, EmployeeDailyReportResponse)


@router.put("/reports/{id}", response_model=APIResponse)
async def update_report(id: int, data: EmployeeDailyReportUpdate, db: AsyncSession = Depends(get_enterprise_db)):
    return await _update_record(report_crud, id, data, db, EmployeeDailyReportResponse)


@router.delete("/reports/{id}", response_model=APIResponse)
async def delete_report(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    return await _delete_record(report_crud, id, db)


# ── Complaints ────────────────────────────────────────────────────────

@router.get("/complaints", response_model=APIResponse)
async def list_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    follower: Optional[str] = Query(None, description="Filter by follower"),
    db: AsyncSession = Depends(get_enterprise_db),
):
    kwargs = {}
    if status:
        kwargs["status"] = status
    if follower:
        kwargs["follower"] = follower
    result = await complaint_crud.list(db, page=page, page_size=page_size, **kwargs)
    result["items"] = [ComplaintFeedbackResponse.model_validate(item).model_dump() for item in result["items"]]
    return paginated_response(**result)


@router.get("/complaints/{id}", response_model=APIResponse)
async def get_complaint(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    return await _get_or_404(complaint_crud, id, db, ComplaintFeedbackResponse)


@router.post("/complaints", response_model=APIResponse)
async def create_complaint(data: ComplaintFeedbackCreate, db: AsyncSession = Depends(get_enterprise_db)):
    return await _create_record(complaint_crud, data, db, ComplaintFeedbackResponse)


@router.put("/complaints/{id}", response_model=APIResponse)
async def update_complaint(id: int, data: ComplaintFeedbackUpdate, db: AsyncSession = Depends(get_enterprise_db)):
    return await _update_record(complaint_crud, id, data, db, ComplaintFeedbackResponse)


@router.delete("/complaints/{id}", response_model=APIResponse)
async def delete_complaint(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    return await _delete_record(complaint_crud, id, db)


# ── Scores ────────────────────────────────────────────────────────────

@router.get("/scores", response_model=APIResponse)
async def list_scores(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    student_id: Optional[str] = Query(None, description="Filter by student ID"),
    student_name: Optional[str] = Query(None, description="Student name (LIKE)"),
    min_score: Optional[float] = Query(None, description="Minimum score threshold"),
    max_score: Optional[float] = Query(None, description="Maximum score threshold"),
    db: AsyncSession = Depends(get_enterprise_db),
):
    kwargs = {}
    if student_id:
        kwargs["student_id"] = student_id
    if student_name:
        kwargs["student_name__like"] = student_name
    if min_score is not None:
        kwargs["min_score"] = min_score
    if max_score is not None:
        kwargs["max_score"] = max_score
    result = await score_crud.list(db, page=page, page_size=page_size, **kwargs)
    result["items"] = [StudentScoreResponse.model_validate(item).model_dump() for item in result["items"]]
    return paginated_response(**result)


@router.get("/scores/{id}", response_model=APIResponse)
async def get_score(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    return await _get_or_404(score_crud, id, db, StudentScoreResponse)


@router.post("/scores", response_model=APIResponse)
async def create_score(data: StudentScoreCreate, db: AsyncSession = Depends(get_enterprise_db)):
    return await _create_record(score_crud, data, db, StudentScoreResponse)


@router.put("/scores/{id}", response_model=APIResponse)
async def update_score(id: int, data: StudentScoreUpdate, db: AsyncSession = Depends(get_enterprise_db)):
    return await _update_record(score_crud, id, data, db, StudentScoreResponse)


@router.delete("/scores/{id}", response_model=APIResponse)
async def delete_score(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    return await _delete_record(score_crud, id, db)
