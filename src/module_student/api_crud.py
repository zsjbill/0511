"""
Student Assistant Module — 4-table CRUD API endpoints.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.crud_base import CRUDBase
from src.common.database import get_student_db
from src.common.models_student import (
    StudentAdminService,
    MentalHealthProfile,
    PsychologicalAlert,
    AfterSalesTicket,
)
from src.common.schemas_student import (
    APIResponse,
    PaginatedData,
    StudentAdminServiceCreate,
    StudentAdminServiceUpdate,
    StudentAdminServiceResponse,
    MentalHealthProfileCreate,
    MentalHealthProfileUpdate,
    MentalHealthProfileResponse,
    PsychologicalAlertCreate,
    PsychologicalAlertUpdate,
    PsychologicalAlertResponse,
    AfterSalesTicketCreate,
    AfterSalesTicketUpdate,
    AfterSalesTicketResponse,
)

router = APIRouter(prefix="/api/v1/student", tags=["Student Assistant"])

# ---- CRUD instances ----
admin_crud = CRUDBase(StudentAdminService, StudentAdminServiceCreate, StudentAdminServiceUpdate)
mental_crud = CRUDBase(MentalHealthProfile, MentalHealthProfileCreate, MentalHealthProfileUpdate)
alert_crud = CRUDBase(PsychologicalAlert, PsychologicalAlertCreate, PsychologicalAlertUpdate)
ticket_crud = CRUDBase(AfterSalesTicket, AfterSalesTicketCreate, AfterSalesTicketUpdate)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def paginated_response(items: list, total: int, page: int, page_size: int, total_pages: int) -> APIResponse:
    return APIResponse(data=PaginatedData(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    ).model_dump())


# ===================================================================
# Admin Services
# ===================================================================
@router.get("/admin-services", response_model=APIResponse)
async def list_admin_services(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    student_id: Optional[str] = None,
    application_type: Optional[str] = None,
    approval_status: Optional[str] = None,
    db: AsyncSession = Depends(get_student_db),
):
    kwargs = {}
    if student_id:
        kwargs["student_id"] = student_id
    if application_type:
        kwargs["application_type"] = application_type
    if approval_status:
        kwargs["approval_status"] = approval_status
    result = await admin_crud.list(db, page=page, page_size=page_size, **kwargs)
    result["items"] = [StudentAdminServiceResponse.model_validate(item).model_dump() for item in result["items"]]
    return paginated_response(**result)


@router.get("/admin-services/{id}", response_model=APIResponse)
async def get_admin_service(id: int, db: AsyncSession = Depends(get_student_db)):
    item = await admin_crud.get(db, id)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=StudentAdminServiceResponse.model_validate(item).model_dump())


@router.post("/admin-services", response_model=APIResponse)
async def create_admin_service(data: StudentAdminServiceCreate, db: AsyncSession = Depends(get_student_db)):
    item = await admin_crud.create(db, data)
    return APIResponse(data=StudentAdminServiceResponse.model_validate(item).model_dump())


@router.put("/admin-services/{id}", response_model=APIResponse)
async def update_admin_service(id: int, data: StudentAdminServiceUpdate, db: AsyncSession = Depends(get_student_db)):
    item = await admin_crud.update(db, id, data)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=StudentAdminServiceResponse.model_validate(item).model_dump())


@router.delete("/admin-services/{id}", response_model=APIResponse)
async def delete_admin_service(id: int, db: AsyncSession = Depends(get_student_db)):
    success = await admin_crud.delete(db, id)
    if not success:
        return APIResponse(code=404, message="Not found")
    return APIResponse(message="Deleted successfully")


# ===================================================================
# Mental Health
# ===================================================================
@router.get("/mental-health", response_model=APIResponse)
async def list_mental_health(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    student_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_student_db),
):
    kwargs = {}
    if student_id:
        kwargs["student_id"] = student_id
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    result = await mental_crud.list(db, page=page, page_size=page_size, **kwargs)
    result["items"] = [MentalHealthProfileResponse.model_validate(item).model_dump() for item in result["items"]]
    return paginated_response(**result)


@router.get("/mental-health/{id}", response_model=APIResponse)
async def get_mental_health(id: int, db: AsyncSession = Depends(get_student_db)):
    item = await mental_crud.get(db, id)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=MentalHealthProfileResponse.model_validate(item).model_dump())


@router.post("/mental-health", response_model=APIResponse)
async def create_mental_health(data: MentalHealthProfileCreate, db: AsyncSession = Depends(get_student_db)):
    item = await mental_crud.create(db, data)
    return APIResponse(data=MentalHealthProfileResponse.model_validate(item).model_dump())


@router.put("/mental-health/{id}", response_model=APIResponse)
async def update_mental_health(id: int, data: MentalHealthProfileUpdate, db: AsyncSession = Depends(get_student_db)):
    item = await mental_crud.update(db, id, data)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=MentalHealthProfileResponse.model_validate(item).model_dump())


@router.delete("/mental-health/{id}", response_model=APIResponse)
async def delete_mental_health(id: int, db: AsyncSession = Depends(get_student_db)):
    success = await mental_crud.delete(db, id)
    if not success:
        return APIResponse(code=404, message="Not found")
    return APIResponse(message="Deleted successfully")


# ===================================================================
# Alerts
# ===================================================================
@router.get("/alerts", response_model=APIResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    risk_level: Optional[str] = None,
    teacher_follow_up_status: Optional[str] = None,
    follower: Optional[str] = None,
    db: AsyncSession = Depends(get_student_db),
):
    kwargs = {}
    if risk_level:
        kwargs["risk_level"] = risk_level
    if teacher_follow_up_status:
        kwargs["teacher_follow_up_status"] = teacher_follow_up_status
    if follower:
        kwargs["follower"] = follower
    result = await alert_crud.list(db, page=page, page_size=page_size, **kwargs)
    result["items"] = [PsychologicalAlertResponse.model_validate(item).model_dump() for item in result["items"]]
    return paginated_response(**result)


@router.get("/alerts/{id}", response_model=APIResponse)
async def get_alert(id: int, db: AsyncSession = Depends(get_student_db)):
    item = await alert_crud.get(db, id)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=PsychologicalAlertResponse.model_validate(item).model_dump())


@router.post("/alerts", response_model=APIResponse)
async def create_alert(data: PsychologicalAlertCreate, db: AsyncSession = Depends(get_student_db)):
    item = await alert_crud.create(db, data)
    return APIResponse(data=PsychologicalAlertResponse.model_validate(item).model_dump())


@router.put("/alerts/{id}", response_model=APIResponse)
async def update_alert(id: int, data: PsychologicalAlertUpdate, db: AsyncSession = Depends(get_student_db)):
    item = await alert_crud.update(db, id, data)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=PsychologicalAlertResponse.model_validate(item).model_dump())


@router.delete("/alerts/{id}", response_model=APIResponse)
async def delete_alert(id: int, db: AsyncSession = Depends(get_student_db)):
    success = await alert_crud.delete(db, id)
    if not success:
        return APIResponse(code=404, message="Not found")
    return APIResponse(message="Deleted successfully")


# ===================================================================
# Tickets
# ===================================================================
@router.get("/tickets", response_model=APIResponse)
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    processing_progress: Optional[str] = None,
    student_id: Optional[str] = None,
    ticket_no: Optional[str] = None,
    db: AsyncSession = Depends(get_student_db),
):
    kwargs = {}
    if processing_progress:
        kwargs["processing_progress"] = processing_progress
    if student_id:
        kwargs["student_id"] = student_id
    if ticket_no:
        kwargs["ticket_no"] = ticket_no
    result = await ticket_crud.list(db, page=page, page_size=page_size, **kwargs)
    result["items"] = [AfterSalesTicketResponse.model_validate(item).model_dump() for item in result["items"]]
    return paginated_response(**result)


@router.get("/tickets/{id}", response_model=APIResponse)
async def get_ticket(id: int, db: AsyncSession = Depends(get_student_db)):
    item = await ticket_crud.get(db, id)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=AfterSalesTicketResponse.model_validate(item).model_dump())


@router.post("/tickets", response_model=APIResponse)
async def create_ticket(data: AfterSalesTicketCreate, db: AsyncSession = Depends(get_student_db)):
    item = await ticket_crud.create(db, data)
    return APIResponse(data=AfterSalesTicketResponse.model_validate(item).model_dump())


@router.put("/tickets/{id}", response_model=APIResponse)
async def update_ticket(id: int, data: AfterSalesTicketUpdate, db: AsyncSession = Depends(get_student_db)):
    item = await ticket_crud.update(db, id, data)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=AfterSalesTicketResponse.model_validate(item).model_dump())


@router.delete("/tickets/{id}", response_model=APIResponse)
async def delete_ticket(id: int, db: AsyncSession = Depends(get_student_db)):
    success = await ticket_crud.delete(db, id)
    if not success:
        return APIResponse(code=404, message="Not found")
    return APIResponse(message="Deleted successfully")
