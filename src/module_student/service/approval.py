"""审批服务模块 — 学生申请的提交、审批流转、状态查询。

审批状态流转：
  - 学生提交 → approval_status = "待审批"（默认）
  - 教师通过 → "已通过"
  - 教师驳回 → "已驳回"
  - 教师转交 → "已转交"（同时通知新审批人）
"""

import logging
import datetime
from sqlalchemy import select
from src.common.database import StudentSessionLocal
from src.module_student.dbmodel.models import StudentAdminService
from src.module_student.service.notification import create_notification

logger = logging.getLogger(__name__)


async def submit_application(data) -> StudentAdminService:
    """提交申请：创建记录（状态=待审批）+ 通知老师。

    流程说明：
    1. 将申请数据写入 student_admin_services 表
    2. approval_status 默认值为 "待审批"
    3. 创建 type="new_application" 的通知推送给所有老师
    """
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

    # 通知所有老师有新申请
    await create_notification(
        recipient_id="teacher_all",
        recipient_type="teacher",
        type="new_application",
        title=f"新申请：{data.student_name} - {data.application_type}",
        content=f"{data.student_name} 提交了 {data.application_type} 申请：{data.application_content[:100]}",
        related_id=app.id,
    )
    return app


async def approve_application(application_id: int, action: str, approver: str,
                               comment: str = None, transfer_to: str = None) -> StudentAdminService:
    """审批申请：更新状态 + 通知学生（若转交则通知新审批人）。

    审批流程说明：
    1. 根据 action 参数将审批状态更新为"已通过"/"已驳回"/"已转交"
    2. 记录审批人和审批时间
    3. 如果有审批备注，追加到申请内容末尾
    4. 创建 type="approval_result" 的通知推送给学生
    5. 如果 action="转交" 且指定了 transfer_to，额外通知新审批人
    """
    async with StudentSessionLocal() as db:
        result = await db.execute(select(StudentAdminService).where(StudentAdminService.id == application_id))
        app = result.scalar_one_or_none()
        if not app:
            raise ValueError(f"Application {application_id} not found")

        # action -> approval_status 映射：通过→已通过, 驳回→已驳回, 转交→已转交
        status_map = {"通过": "已通过", "驳回": "已驳回", "转交": "已转交"}
        app.approval_status = status_map.get(action, action)
        app.approver = approver
        app.approved_at = datetime.datetime.now()

        if comment:
            current = app.application_content or ""
            app.application_content = current + f"\n[审批备注] {comment}"

        await db.commit()
        await db.refresh(app)

    # 通知学生审批结果
    await create_notification(
        recipient_id=app.student_id,
        recipient_type="student",
        type="approval_result",
        title=f"申请 {app.approval_status}",
        content=f"您的 {app.application_type} 申请已被 {approver} {app.approval_status}。"
                + (f" 备注：{comment}" if comment else ""),
        related_id=app.id,
    )

    # 如果是转交，通知新审批人
    if action == "转交" and transfer_to:
        await create_notification(
            recipient_id=transfer_to,
            recipient_type="teacher",
            type="new_application",
            title=f"转交申请：{app.student_name} - {app.application_type}",
            content=f"{approver} 将此申请转交给您处理。",
            related_id=app.id,
        )

    return app


async def get_application_status(application_id: int) -> StudentAdminService:
    """根据申请 ID 查询当前状态。

    返回 StudentAdminService 对象，包含完整记录信息。
    如果记录不存在则返回 None。
    """
    async with StudentSessionLocal() as db:
        result = await db.execute(select(StudentAdminService).where(StudentAdminService.id == application_id))
        return result.scalar_one_or_none()
