import logging
from sqlalchemy import select, and_
from src.common.database import StudentSessionLocal
from src.common.models_student import Notification

logger = logging.getLogger(__name__)


async def create_notification(
    recipient_id: str, recipient_type: str, type: str,
    title: str, content: str, related_id: int = None,
) -> Notification:
    """Create a new notification and persist to DB."""
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
    """Get unread notifications for a recipient."""
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
    """Mark a notification as read."""
    async with StudentSessionLocal() as db:
        result = await db.execute(select(Notification).where(Notification.id == notification_id))
        notif = result.scalar_one_or_none()
        if notif:
            notif.is_read = 1
            await db.commit()
            return True
        return False
