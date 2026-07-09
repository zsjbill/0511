import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class PaginatedData(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())


# ---- StudentAdminService ----
class StudentAdminServiceCreate(BaseModel):
    student_id: str = Field(..., max_length=50)
    student_name: str = Field(..., max_length=50)
    application_type: str = Field(..., max_length=50)
    application_content: str
    academic_related_data: Optional[dict] = None


class StudentAdminServiceUpdate(BaseModel):
    application_type: Optional[str] = None
    application_content: Optional[str] = None
    approval_status: Optional[str] = None
    approver: Optional[str] = None
    academic_related_data: Optional[dict] = None


class StudentAdminServiceResponse(BaseModel):
    id: int
    student_id: str
    student_name: str
    application_type: str
    application_content: str
    approval_status: str
    academic_related_data: Optional[dict] = None
    approver: Optional[str] = None
    approved_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    model_config = {"from_attributes": True}


# ---- MentalHealthProfile ----
class MentalHealthProfileCreate(BaseModel):
    student_id: str = Field(..., max_length=50)
    student_name: str = Field(..., max_length=50)
    emotion_tags: Optional[Any] = None
    emotion_score: Optional[float] = None
    historical_fluctuation: Optional[Any] = None
    last_assessed_at: Optional[datetime.datetime] = None


class MentalHealthProfileUpdate(BaseModel):
    emotion_tags: Optional[Any] = None
    emotion_score: Optional[float] = None
    historical_fluctuation: Optional[Any] = None
    last_assessed_at: Optional[datetime.datetime] = None


class MentalHealthProfileResponse(BaseModel):
    id: int
    student_id: str
    student_name: str
    emotion_tags: Optional[Any] = None
    emotion_score: Optional[float] = None
    historical_fluctuation: Optional[Any] = None
    last_assessed_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    model_config = {"from_attributes": True}


# ---- PsychologicalAlert ----
class PsychologicalAlertCreate(BaseModel):
    student_id: str = Field(..., max_length=50)
    student_name: str = Field(..., max_length=50)
    trigger_reason: str
    risk_level: str = "中"
    teacher_follow_up_status: str = "未跟进"
    follower: Optional[str] = None


class PsychologicalAlertUpdate(BaseModel):
    risk_level: Optional[str] = None
    teacher_follow_up_status: Optional[str] = None
    follower: Optional[str] = None
    trigger_reason: Optional[str] = None


class PsychologicalAlertResponse(BaseModel):
    id: int
    student_id: str
    student_name: str
    trigger_reason: str
    risk_level: str
    teacher_follow_up_status: str
    follower: Optional[str] = None
    followed_at: Optional[datetime.datetime] = None
    resolved_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    model_config = {"from_attributes": True}


# ---- AfterSalesTicket ----
class AfterSalesTicketCreate(BaseModel):
    ticket_no: str = Field(..., max_length=50)
    student_id: str = Field(..., max_length=50)
    student_name: str = Field(..., max_length=50)
    complaint_content: str
    handler: Optional[str] = None


class AfterSalesTicketUpdate(BaseModel):
    processing_progress: Optional[str] = None
    handler: Optional[str] = None
    final_solution: Optional[str] = None


class AfterSalesTicketResponse(BaseModel):
    id: int
    ticket_no: str
    student_id: str
    student_name: str
    complaint_content: str
    processing_progress: str
    handler: Optional[str] = None
    final_solution: Optional[str] = None
    resolved_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    model_config = {"from_attributes": True}


# ---- Notification ----
class NotificationResponse(BaseModel):
    id: int
    recipient_id: str
    recipient_type: str
    type: str
    title: str
    content: str
    is_read: int
    related_id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    model_config = {"from_attributes": True}


# ---- SyncLog ----
class SyncLogResponse(BaseModel):
    id: int
    sync_type: str
    status: str
    records_count: int
    error_message: Optional[str] = None
    started_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None
    model_config = {"from_attributes": True}


# ---- Approval-specific schemas ----
class ApplicationSubmitRequest(BaseModel):
    student_id: str = Field(..., max_length=50)
    student_name: str = Field(..., max_length=50)
    application_type: str = Field(..., max_length=50)
    application_content: str
    academic_related_data: Optional[dict] = None


class ApplicationApproveRequest(BaseModel):
    application_id: int
    action: str = Field(..., pattern="^(通过|驳回|转交)$")
    approver: str
    comment: Optional[str] = None
    transfer_to: Optional[str] = None


class ApplicationStatusResponse(BaseModel):
    id: int
    student_id: str
    student_name: str
    application_type: str
    approval_status: str
    approver: Optional[str] = None
    approved_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    model_config = {"from_attributes": True}


# ---- KB search ----
class KBSearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)


class KBSearchResult(BaseModel):
    title: str
    content_snippet: str
    score: float


# ---- AI capability schemas ----
class RiskDetectRequest(BaseModel):
    student_id: str
    student_name: str
    conversation_text: str


class RiskDetectResponse(BaseModel):
    risk_level: str
    confidence: float
    key_signals: list[str]
    recommended_action: str
    alert_created: bool = False


class SummarizeRequest(BaseModel):
    complaint_text: str = Field(..., min_length=200)


class SummarizeResponse(BaseModel):
    complainant: str
    core_issue: str
    urgency: str
    suggested_handler: str
    summary: str


class MarketingGenerateRequest(BaseModel):
    student_id: str
    student_name: str
    emotion_tags: Optional[Any] = None
    scores: Optional[dict] = None
    study_interest: Optional[str] = None


class MarketingGenerateResponse(BaseModel):
    conservative: str
    moderate: str
    aggressive: str
