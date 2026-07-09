"""通知服务模块 — 通知的创建、查询、标记已读。

支持向学生/教师发送各类通知（新申请、审批结果、风险预警等），
提供待办通知查询和已读标记功能。
"""

import logging
from sqlalchemy import select, and_
from src.common.database import StudentSessionLocal
from src.common.models_student import Notification

logger = logging.getLogger(__name__)


async def create_notification(
    recipient_id: str, recipient_type: str, type: str,
    title: str, content: str, related_id: int = None,
) -> Notification:
    """创建一条新通知并持久化到数据库。

    参数：
        recipient_id: 接收者标识（学号/teacher_all/具体教师ID）
        recipient_type: 接收者类型（student/teacher）
        type: 通知类型（new_application/approval_result/risk_alert）
        title: 通知标题
        content: 通知正文内容
        related_id: 关联的业务记录ID
    """
    async with StudentSessionLocal() as db:
        notif = Notification(
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            type=type,
            title=title,
            content=content,
            related_id=related_id,
        )
        db.add(notif)
        await db.commit()
        await db.refresh(notif)
        logger.info(f"Notification created: id={notif.id}, type={type}, recipient={recipient_id}")
        return notif


async def get_pending_notifications(recipient_id: str, recipient_type: str, limit: int = 20):
    """查询指定接收者的未读通知列表。

    按创建时间倒序排列，默认最多返回20条。
    只返回 is_read=0（未读）的通知记录。
    """
    async with StudentSessionLocal() as db:
        result = await db.execute(
            select(Notification)
            .where(
                and_(
                    Notification.recipient_id == recipient_id,
                    Notification.recipient_type == recipient_type,
                    Notification.is_read == 0,
                )
            )
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


async def mark_as_read(notification_id: int) -> bool:
    """将指定通知标记为已读。

    将通知的 is_read 字段设置为 1。
    如果通知不存在则返回 False，否则返回 True。
    """
    async with StudentSessionLocal() as db:
        result = await db.execute(select(Notification).where(Notification.id == notification_id))
        notif = result.scalar_one_or_none()
        if notif:
            notif.is_read = 1
            await db.commit()
            return True
        return False
