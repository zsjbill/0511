"""
Student Assistant Module — 4表 CRUD API 端点。

提供行政服务、心理健康档案、心理预警、售后工单四个核心表的
增、删、改、查、列表分页接口。
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
@router.get("/admin-services", response_model=APIResponse, summary="行政服务列表（分页+筛选）", description="分页查询学生的行政服务记录，支持按学号、申请类型和审批状态过滤。")
async def list_admin_services(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数，最大100"),
    student_id: Optional[str] = Query(None, description="按学号精确筛选"),
    application_type: Optional[str] = Query(None, description="按申请类型筛选（如：请假、考务）"),
    approval_status: Optional[str] = Query(None, description="按审批状态筛选（待审批/已通过/已驳回/已转交）"),
    db: AsyncSession = Depends(get_student_db),
):
    """查询行政服务记录列表（分页）。

    支持按 student_id、application_type、approval_status 进行筛选，
    结果按创建时间倒序排列并分页返回。
    """
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


@router.get("/admin-services/{id}", response_model=APIResponse, summary="获取单个行政服务", description="根据 ID 查询单条行政服务记录的详细信息。")
async def get_admin_service(id: int, db: AsyncSession = Depends(get_student_db)):
    """根据 ID 查询单条行政服务记录。"""
    item = await admin_crud.get(db, id)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=StudentAdminServiceResponse.model_validate(item).model_dump())


@router.post("/admin-services", response_model=APIResponse, summary="创建行政服务", description="新增一条行政服务记录（请假/考务等）。")
async def create_admin_service(data: StudentAdminServiceCreate, db: AsyncSession = Depends(get_student_db)):
    """创建一条新的行政服务记录。"""
    item = await admin_crud.create(db, data)
    return APIResponse(data=StudentAdminServiceResponse.model_validate(item).model_dump())


@router.put("/admin-services/{id}", response_model=APIResponse, summary="更新行政服务", description="根据 ID 更新行政服务记录的内容。")
async def update_admin_service(id: int, data: StudentAdminServiceUpdate, db: AsyncSession = Depends(get_student_db)):
    """根据 ID 更新行政服务记录。"""
    item = await admin_crud.update(db, id, data)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=StudentAdminServiceResponse.model_validate(item).model_dump())


@router.delete("/admin-services/{id}", response_model=APIResponse, summary="删除行政服务", description="根据 ID 删除行政服务记录。")
async def delete_admin_service(id: int, db: AsyncSession = Depends(get_student_db)):
    """根据 ID 删除行政服务记录。"""
    success = await admin_crud.delete(db, id)
    if not success:
        return APIResponse(code=404, message="Not found")
    return APIResponse(message="Deleted successfully")


# ===================================================================
# Mental Health
# ===================================================================
@router.get("/mental-health", response_model=APIResponse, summary="心理健康档案列表（分页+筛选）", description="分页查询学生心理健康档案，支持按学号、日期范围筛选。")
async def list_mental_health(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数，最大100"),
    student_id: Optional[str] = Query(None, description="按学号精确筛选"),
    start_date: Optional[str] = Query(None, description="创建日期范围起点（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="创建日期范围终点（YYYY-MM-DD）"),
    db: AsyncSession = Depends(get_student_db),
):
    """查询心理健康档案列表（分页）。

    支持按 student_id、start_date、end_date 进行筛选，
    结果分页返回。
    """
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


@router.get("/mental-health/{id}", response_model=APIResponse, summary="获取单个心理健康档案", description="根据 ID 查询单条心理健康档案记录的详细信息。")
async def get_mental_health(id: int, db: AsyncSession = Depends(get_student_db)):
    """根据 ID 查询单条心理健康档案记录。"""
    item = await mental_crud.get(db, id)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=MentalHealthProfileResponse.model_validate(item).model_dump())


@router.post("/mental-health", response_model=APIResponse, summary="创建心理健康档案", description="新增一条学生心理健康档案记录。")
async def create_mental_health(data: MentalHealthProfileCreate, db: AsyncSession = Depends(get_student_db)):
    """创建一条新的心理健康档案记录。"""
    item = await mental_crud.create(db, data)
    return APIResponse(data=MentalHealthProfileResponse.model_validate(item).model_dump())


@router.put("/mental-health/{id}", response_model=APIResponse, summary="更新心理健康档案", description="根据 ID 更新心理健康档案记录的内容。")
async def update_mental_health(id: int, data: MentalHealthProfileUpdate, db: AsyncSession = Depends(get_student_db)):
    """根据 ID 更新心理健康档案记录。"""
    item = await mental_crud.update(db, id, data)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=MentalHealthProfileResponse.model_validate(item).model_dump())


@router.delete("/mental-health/{id}", response_model=APIResponse, summary="删除心理健康档案", description="根据 ID 删除心理健康档案记录。")
async def delete_mental_health(id: int, db: AsyncSession = Depends(get_student_db)):
    """根据 ID 删除心理健康档案记录。"""
    success = await mental_crud.delete(db, id)
    if not success:
        return APIResponse(code=404, message="Not found")
    return APIResponse(message="Deleted successfully")


# ===================================================================
# Alerts
# ===================================================================
@router.get("/alerts", response_model=APIResponse, summary="心理预警列表（分页+筛选）", description="分页查询心理预警记录，支持按风险等级、跟进状态、负责人筛选。")
async def list_alerts(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数，最大100"),
    risk_level: Optional[str] = Query(None, description="按风险等级筛选（low/medium/high）"),
    teacher_follow_up_status: Optional[str] = Query(None, description="按教师跟进状态筛选"),
    follower: Optional[str] = Query(None, description="按跟进负责人筛选"),
    db: AsyncSession = Depends(get_student_db),
):
    """查询心理预警记录列表（分页）。

    支持按 risk_level、teacher_follow_up_status、follower 进行筛选，
    结果分页返回。
    """
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


@router.get("/alerts/{id}", response_model=APIResponse, summary="获取单个心理预警", description="根据 ID 查询单条心理预警记录的详细信息。")
async def get_alert(id: int, db: AsyncSession = Depends(get_student_db)):
    """根据 ID 查询单条心理预警记录。"""
    item = await alert_crud.get(db, id)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=PsychologicalAlertResponse.model_validate(item).model_dump())


@router.post("/alerts", response_model=APIResponse, summary="创建心理预警", description="新增一条心理预警记录。")
async def create_alert(data: PsychologicalAlertCreate, db: AsyncSession = Depends(get_student_db)):
    """创建一条新的心理预警记录。"""
    item = await alert_crud.create(db, data)
    return APIResponse(data=PsychologicalAlertResponse.model_validate(item).model_dump())


@router.put("/alerts/{id}", response_model=APIResponse, summary="更新心理预警", description="根据 ID 更新心理预警记录的内容。")
async def update_alert(id: int, data: PsychologicalAlertUpdate, db: AsyncSession = Depends(get_student_db)):
    """根据 ID 更新心理预警记录。"""
    item = await alert_crud.update(db, id, data)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=PsychologicalAlertResponse.model_validate(item).model_dump())


@router.delete("/alerts/{id}", response_model=APIResponse, summary="删除心理预警", description="根据 ID 删除心理预警记录。")
async def delete_alert(id: int, db: AsyncSession = Depends(get_student_db)):
    """根据 ID 删除心理预警记录。"""
    success = await alert_crud.delete(db, id)
    if not success:
        return APIResponse(code=404, message="Not found")
    return APIResponse(message="Deleted successfully")


# ===================================================================
# Tickets
# ===================================================================
@router.get("/tickets", response_model=APIResponse, summary="售后工单列表（分页+筛选）", description="分页查询售后工单，支持按处理进度、学号、工单号筛选。")
async def list_tickets(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数，最大100"),
    processing_progress: Optional[str] = Query(None, description="按处理进度筛选"),
    student_id: Optional[str] = Query(None, description="按学号精确筛选"),
    ticket_no: Optional[str] = Query(None, description="按工单号精确筛选"),
    db: AsyncSession = Depends(get_student_db),
):
    """查询售后工单列表（分页）。

    支持按 processing_progress、student_id、ticket_no 进行筛选，
    结果分页返回。
    """
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


@router.get("/tickets/{id}", response_model=APIResponse, summary="获取单个售后工单", description="根据 ID 查询单条售后工单记录的详细信息。")
async def get_ticket(id: int, db: AsyncSession = Depends(get_student_db)):
    """根据 ID 查询单条售后工单记录。"""
    item = await ticket_crud.get(db, id)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=AfterSalesTicketResponse.model_validate(item).model_dump())


@router.post("/tickets", response_model=APIResponse, summary="创建售后工单", description="新增一条售后工单记录。")
async def create_ticket(data: AfterSalesTicketCreate, db: AsyncSession = Depends(get_student_db)):
    """创建一条新的售后工单记录。"""
    item = await ticket_crud.create(db, data)
    return APIResponse(data=AfterSalesTicketResponse.model_validate(item).model_dump())


@router.put("/tickets/{id}", response_model=APIResponse, summary="更新售后工单", description="根据 ID 更新售后工单记录的内容。")
async def update_ticket(id: int, data: AfterSalesTicketUpdate, db: AsyncSession = Depends(get_student_db)):
    """根据 ID 更新售后工单记录。"""
    item = await ticket_crud.update(db, id, data)
    if not item:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=AfterSalesTicketResponse.model_validate(item).model_dump())


@router.delete("/tickets/{id}", response_model=APIResponse, summary="删除售后工单", description="根据 ID 删除售后工单记录。")
async def delete_ticket(id: int, db: AsyncSession = Depends(get_student_db)):
    """根据 ID 删除售后工单记录。"""
    success = await ticket_crud.delete(db, id)
    if not success:
        return APIResponse(code=404, message="Not found")
    return APIResponse(message="Deleted successfully")
