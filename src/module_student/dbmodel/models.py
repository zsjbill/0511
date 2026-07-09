"""
Student assistant ORM models (7 tables).
"""
import datetime
from typing import Optional, Any
from sqlalchemy import DateTime, Integer, String, Text, Numeric, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from src.common.database import Base


class StudentAdminService(Base):
    __tablename__ = "student_admin_services"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    student_name: Mapped[str] = mapped_column(String(50), nullable=False)
    application_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    application_content: Mapped[str] = mapped_column(Text, nullable=False)
    approval_status: Mapped[str] = mapped_column(String(20), nullable=False, default="待审批", index=True)
    academic_related_data: Mapped[Optional[dict]] = mapped_column(JSON)
    approver: Mapped[Optional[str]] = mapped_column(String(50))
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class MentalHealthProfile(Base):
    __tablename__ = "mental_health_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    student_name: Mapped[str] = mapped_column(String(50), nullable=False)
    emotion_tags: Mapped[Optional[Any]] = mapped_column(JSON)
    emotion_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), index=True)
    historical_fluctuation: Mapped[Optional[Any]] = mapped_column(JSON)
    last_assessed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class PsychologicalAlert(Base):
    __tablename__ = "psychological_alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    student_name: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_reason: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    teacher_follow_up_status: Mapped[str] = mapped_column(String(20), nullable=False, default="未跟进", index=True)
    follower: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    followed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class AfterSalesTicket(Base):
    __tablename__ = "after_sales_tickets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    student_name: Mapped[str] = mapped_column(String(50), nullable=False)
    complaint_content: Mapped[str] = mapped_column(Text, nullable=False)
    processing_progress: Mapped[str] = mapped_column(String(20), nullable=False, default="待处理", index=True)
    handler: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    final_solution: Mapped[Optional[str]] = mapped_column(Text)
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    recipient_type: Mapped[str] = mapped_column(String(20), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[int] = mapped_column(Integer, default=0)
    related_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())


class SyncLog(Base):
    __tablename__ = "sync_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sync_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    records_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    finished_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class KBDocument(Base):
    __tablename__ = "kb_documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    source_file: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
