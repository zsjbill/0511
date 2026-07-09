"""
Pydantic schemas for request/response validation.
"""
import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class IntentType(str, Enum):
    COURSE_INQUIRY = "课程咨询"
    REGISTRATION = "报名意向"
    PRICE_INQUIRY = "价格询问"
    COMPLAINT = "投诉建议"
    CHITCHAT = "闲聊"
    COMPANY_INFO = "公司信息"
    OTHER = "其他"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ---------------------------------------------------------------------------
# Common
# ---------------------------------------------------------------------------
class Message(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


# ---------------------------------------------------------------------------
# Customer Judge (M1)
# ---------------------------------------------------------------------------
class CustomerJudgeRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    wechat: Optional[str] = None
    source: Optional[str] = None
    extra_info: Optional[dict[str, Any]] = None


class CustomerJudgeResponse(BaseModel):
    profile_score: int
    tags: list[str]
    recommended_service: Optional[str]
    match_reason: str


# ---------------------------------------------------------------------------
# Customer Agent (M2) - Chat
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    customer_id: Optional[int] = None
    message: str
    session_id: Optional[str] = None
    context: Optional[dict[str, Any]] = None


class ChatResponse(BaseModel):
    reply: str
    intent: IntentType
    confidence: float
    suggestions: list[str] = []
    actions: list[dict[str, Any]] = []


# ---------------------------------------------------------------------------
# Registration (M2)
# ---------------------------------------------------------------------------
class RegistrationRequest(BaseModel):
    customer_id: int
    activity_name: str
    notes: Optional[str] = None


class RegistrationResponse(BaseModel):
    registration_id: int
    status: str
    message: str


# ---------------------------------------------------------------------------
# Enterprise Assistant (M3) - NL2SQL
# ---------------------------------------------------------------------------
class NL2SQLRequest(BaseModel):
    query: str
    user_id: int
    context: Optional[dict[str, Any]] = None


class NL2SQLResponse(BaseModel):
    sql: str
    result: Optional[list[dict[str, Any]]] = None
    explanation: str


# ---------------------------------------------------------------------------
# Student Assistant (M4) - Risk
# ---------------------------------------------------------------------------
class RiskDetectionRequest(BaseModel):
    student_id: int
    conversation: list[Message]


class RiskDetectionResponse(BaseModel):
    risk_level: RiskLevel
    confidence: float
    key_signals: list[str]
    recommended_action: str


# ---------------------------------------------------------------------------
# Report (M5)
# ---------------------------------------------------------------------------
class ReportRequest(BaseModel):
    report_type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    date_range: Optional[tuple[datetime.date, datetime.date]] = None
    metrics: list[str] = []


class ReportResponse(BaseModel):
    report_id: int
    title: str
    content: str
    generated_at: datetime.datetime
