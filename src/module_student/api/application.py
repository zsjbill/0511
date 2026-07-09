"""学生端审批/通知 API 端点。

提供学生提交申请、教师审批、查询申请状态，
以及获取待办通知、标记已读等接口。
"""

from fastapi import APIRouter, Query
from src.module_student.pdcmodel.schemas import (
    APIResponse, ApplicationSubmitRequest, ApplicationApproveRequest,
    ApplicationStatusResponse, NotificationResponse,
)
from src.module_student.service.approval import submit_application, approve_application, get_application_status
from src.module_student.service.notification import get_pending_notifications, mark_as_read

router = APIRouter(prefix="/api/v1/student", tags=["Student - Approval"])


@router.post("/application/submit", response_model=APIResponse, status_code=201,
             summary="学生提交申请", description="提交请假/考务申请，写入行政服务表并通知老师端。")
async def submit(request: ApplicationSubmitRequest):
    """学生提交行政申请。

    申请写入 student_admin_services 表，状态初始为"待审批"，
    同时创建通知（type=new_application）推送给老师端。
    """
    try:
        app = await submit_application(request)
        return APIResponse(data=ApplicationStatusResponse.model_validate(app).model_dump(), message="Application submitted")
    except Exception as e:
        return APIResponse(code=500, message=str(e))


@router.post("/application/approve", response_model=APIResponse,
             summary="教师审批申请", description="教师通过/驳回/转交学生申请，更新状态并通知学生。")
async def approve(request: ApplicationApproveRequest):
    """教师审批学生申请。

    支持三种操作：通过（approval_status → 已通过）、
    驳回（→ 已驳回）、转交（→ 已转交，同时通知新审批人）。
    审批结果通过通知推送给学生。
    """
    try:
        app = await approve_application(
            request.application_id, request.action, request.approver,
            request.comment, request.transfer_to,
        )
        return APIResponse(data=ApplicationStatusResponse.model_validate(app).model_dump(), message=f"Application {request.action}")
    except ValueError as e:
        return APIResponse(code=404, message=str(e))
    except Exception as e:
        return APIResponse(code=500, message=str(e))


@router.get("/application/{application_id}/status", response_model=APIResponse,
            summary="查询申请状态", description="根据申请 ID 查询当前审批状态。")
async def status(application_id: int):
    """查询指定申请的当前审批状态。"""
    app = await get_application_status(application_id)
    if not app:
        return APIResponse(code=404, message="Application not found")
    return APIResponse(data=ApplicationStatusResponse.model_validate(app).model_dump())


@router.get("/notifications/pending", response_model=APIResponse,
            summary="获取待办通知", description="根据接收者 ID 和类型查询未读通知列表。")
async def pending_notifications(
    recipient_id: str = Query(..., description="接收者 ID（如学号或 teacher_all）"),
    recipient_type: str = Query(..., description="接收者类型（student / teacher）"),
):
    """查询指定接收者的待办（未读）通知列表。"""
    notifs = await get_pending_notifications(recipient_id, recipient_type)
    return APIResponse(data={
        "notifications": [NotificationResponse.model_validate(n).model_dump() for n in notifs],
        "count": len(notifs),
    })


@router.post("/notifications/{notification_id}/read", response_model=APIResponse,
             summary="标记通知已读", description="将指定通知标记为已读状态。")
async def read_notification(notification_id: int):
    """将指定通知标记为已读。"""
    ok = await mark_as_read(notification_id)
    if not ok:
        return APIResponse(code=404, message="Notification not found")
    return APIResponse(message="Marked as read")
