"""
All database table ORM models (unified management).

Tables:
  - User: 系统用户
  - Customer: 客户（访客）
  - Conversation: 对话记录
  - Registration: 活动报名
  - Student: 学生
  - Employee: 员工
  - Report: 报告
"""
import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.database import Base


# ---------------------------------------------------------------------------
# User / Auth
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(128))
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="agent")  # admin | agent | viewer
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


# ---------------------------------------------------------------------------
# Customer (访客／潜在客户)
# ---------------------------------------------------------------------------
class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[Optional[str]] = mapped_column(String(64))
    phone: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    wechat: Mapped[Optional[str]] = mapped_column(String(64))
    source: Mapped[Optional[str]] = mapped_column(String(64))  # 渠道来源
    tags: Mapped[Optional[str]] = mapped_column(Text)           # JSON string
    profile_score: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="customer")


# ---------------------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------------------
class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.id"), index=True)
    agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    intent: Mapped[Optional[str]] = mapped_column(String(64))
    messages: Mapped[str] = mapped_column(Text)                # JSON array of {role, content, time}
    status: Mapped[str] = mapped_column(String(32), default="active")  # active | closed
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    customer: Mapped[Optional["Customer"]] = relationship(back_populates="conversations")


# ---------------------------------------------------------------------------
# Registration (活动报名)
# ---------------------------------------------------------------------------
class Registration(Base):
    __tablename__ = "registrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.id"))
    activity_name: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending | confirmed | cancelled
    registered_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------
class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    student_code: Mapped[Optional[str]] = mapped_column(String(32), unique=True, index=True)
    stage: Mapped[Optional[str]] = mapped_column(String(64))    # 留学阶段
    target_country: Mapped[Optional[str]] = mapped_column(String(64))
    risk_flags: Mapped[Optional[str]] = mapped_column(Text)     # JSON
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------
class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    department: Mapped[Optional[str]] = mapped_column(String(128))
    position: Mapped[Optional[str]] = mapped_column(String(128))
    email: Mapped[Optional[str]] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_type: Mapped[str] = mapped_column(String(32))  # daily | weekly | monthly
    title: Mapped[str] = mapped_column(String(256))
    content: Mapped[str] = mapped_column(Text)
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))


# ---------------------------------------------------------------------------
# Composite indexes
# ---------------------------------------------------------------------------
Index("ix_conversations_customer_status", Conversation.customer_id, Conversation.status)
Index("ix_registrations_customer", Registration.customer_id, Registration.activity_name)
