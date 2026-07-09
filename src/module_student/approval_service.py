import logging
import datetime
from sqlalchemy import select
from src.common.database import StudentSessionLocal
from src.common.models_student import StudentAdminService
from src.module_student.notification_service import create_notification

logger = logging.getLogger(__name__)


async def submit_application(data) -> StudentAdminService:
    """Student submits an application. Creates DB record + notifies teachers."""
    async with StudentSessionLocal() as db:
        app = StudentAdminService(
            student_id=data.student_id,
            student_name=data.student_name,
            application_type=data.application_type,
            application_content=data.application_content,
            academic_related_data=data.academic_related_data,
        )
        db.add(app)
        await db.commit()
        await db.refresh(app)

    # Notify all teachers about new application
    await create_notification(
        recipient_id="teacher_all",
        recipient_type="teacher",
        type="new_application",
        title=f"New application: {data.student_name} - {data.application_type}",
        content=f"{data.student_name} submitted a {data.application_type} request: {data.application_content[:100]}",
        related_id=app.id,
    )
    return app


async def approve_application(application_id: int, action: str, approver: str,
                               comment: str = None, transfer_to: str = None) -> StudentAdminService:
    """Teacher approves/rejects/transfers an application. Updates record + notifies student."""
    async with StudentSessionLocal() as db:
        result = await db.execute(select(StudentAdminService).where(StudentAdminService.id == application_id))
        app = result.scalar_one_or_none()
        if not app:
            raise ValueError(f"Application {application_id} not found")

        status_map = {"通过": "已通过", "驳回": "已驳回", "转交": "已转交"}
        app.approval_status = status_map.get(action, action)
        app.approver = approver
        app.approved_at = datetime.datetime.now()

        if comment:
            current = app.application_content or ""
            app.application_content = current + f"\n[审批备注] {comment}"

        await db.commit()
        await db.refresh(app)

    # Notify student about result
    await create_notification(
        recipient_id=app.student_id,
        recipient_type="student",
        type="approval_result",
        title=f"Application {app.approval_status}",
        content=f"Your {app.application_type} request was {app.approval_status} by {approver}."
                + (f" Comment: {comment}" if comment else ""),
        related_id=app.id,
    )

    # If transferred, notify new approver
    if action == "转交" and transfer_to:
        await create_notification(
            recipient_id=transfer_to,
            recipient_type="teacher",
            type="new_application",
            title=f"Transferred: {app.student_name} - {app.application_type}",
            content=f"{approver} transferred this application to you for review.",
            related_id=app.id,
        )

    return app


async def get_application_status(application_id: int) -> StudentAdminService:
    """Get current status of an application."""
    async with StudentSessionLocal() as db:
        result = await db.execute(select(StudentAdminService).where(StudentAdminService.id == application_id))
        return result.scalar_one_or_none()
