from fastapi import APIRouter, Query
from src.common.schemas_student import (
    APIResponse, ApplicationSubmitRequest, ApplicationApproveRequest,
    ApplicationStatusResponse, NotificationResponse,
)
from src.module_student.approval_service import submit_application, approve_application, get_application_status
from src.module_student.notification_service import get_pending_notifications, mark_as_read

router = APIRouter(prefix="/api/v1/student", tags=["Student - Approval"])


@router.post("/application/submit", response_model=APIResponse, status_code=201)
async def submit(request: ApplicationSubmitRequest):
    try:
        app = await submit_application(request)
        return APIResponse(data=ApplicationStatusResponse.model_validate(app).model_dump(), message="Application submitted")
    except Exception as e:
        return APIResponse(code=500, message=str(e))


@router.post("/application/approve", response_model=APIResponse)
async def approve(request: ApplicationApproveRequest):
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


@router.get("/application/{application_id}/status", response_model=APIResponse)
async def status(application_id: int):
    app = await get_application_status(application_id)
    if not app:
        return APIResponse(code=404, message="Application not found")
    return APIResponse(data=ApplicationStatusResponse.model_validate(app).model_dump())


@router.get("/notifications/pending", response_model=APIResponse)
async def pending_notifications(
    recipient_id: str = Query(...), recipient_type: str = Query(...),
):
    notifs = await get_pending_notifications(recipient_id, recipient_type)
    return APIResponse(data={
        "notifications": [NotificationResponse.model_validate(n).model_dump() for n in notifs],
        "count": len(notifs),
    })


@router.post("/notifications/{notification_id}/read", response_model=APIResponse)
async def read_notification(notification_id: int):
    ok = await mark_as_read(notification_id)
    if not ok:
        return APIResponse(code=404, message="Notification not found")
    return APIResponse(message="Marked as read")
