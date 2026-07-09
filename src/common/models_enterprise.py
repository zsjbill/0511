"""
Enterprise assistant ORM models (4 tables).
"""
import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, String, Text, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column
from src.common.database import Base


class IntentCustomer(Base):
    __tablename__ = "intent_customers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    age: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    education: Mapped[Optional[str]] = mapped_column(String(50))
    major: Mapped[Optional[str]] = mapped_column(String(100))
    follow_up_record: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="跟进中", index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeDailyReport(Base):
    __tablename__ = "employee_daily_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    employee_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    report_content: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), index=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())


class ComplaintFeedback(Base):
    __tablename__ = "complaint_feedback"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    student_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    complaint_detail: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="跟进中", index=True)
    follower: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class StudentScore(Base):
    __tablename__ = "student_scores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    student_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    ielts_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), index=True)
    major_course_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    lab_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
