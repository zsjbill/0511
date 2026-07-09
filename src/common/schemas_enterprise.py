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


# ---- IntentCustomer ----
class IntentCustomerCreate(BaseModel):
    customer_name: str = Field(..., max_length=50)
    age: Optional[int] = None
    gender: Optional[str] = None
    education: Optional[str] = None
    major: Optional[str] = None
    follow_up_record: Optional[str] = None
    status: str = "跟进中"


class IntentCustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    education: Optional[str] = None
    major: Optional[str] = None
    follow_up_record: Optional[str] = None
    status: Optional[str] = None


class IntentCustomerResponse(BaseModel):
    id: int
    customer_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    education: Optional[str] = None
    major: Optional[str] = None
    follow_up_record: Optional[str] = None
    status: str
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    model_config = {"from_attributes": True}


# ---- EmployeeDailyReport ----
class EmployeeDailyReportCreate(BaseModel):
    employee_id: str = Field(..., max_length=50)
    employee_name: str = Field(..., max_length=50)
    gender: Optional[str] = None
    report_content: str
    department: Optional[str] = None


class EmployeeDailyReportUpdate(BaseModel):
    employee_name: Optional[str] = None
    report_content: Optional[str] = None
    department: Optional[str] = None


class EmployeeDailyReportResponse(BaseModel):
    id: int
    employee_id: str
    employee_name: str
    gender: Optional[str] = None
    report_content: str
    submitted_at: Optional[datetime.datetime] = None
    department: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    model_config = {"from_attributes": True}


# ---- ComplaintFeedback ----
class ComplaintFeedbackCreate(BaseModel):
    student_id: str = Field(..., max_length=50)
    student_name: str = Field(..., max_length=50)
    complaint_detail: str
    status: str = "跟进中"
    follower: Optional[str] = None


class ComplaintFeedbackUpdate(BaseModel):
    student_name: Optional[str] = None
    complaint_detail: Optional[str] = None
    status: Optional[str] = None
    follower: Optional[str] = None


class ComplaintFeedbackResponse(BaseModel):
    id: int
    student_id: str
    student_name: str
    complaint_detail: str
    status: str
    follower: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    model_config = {"from_attributes": True}


# ---- StudentScore ----
class StudentScoreCreate(BaseModel):
    student_id: str = Field(..., max_length=50)
    student_name: str = Field(..., max_length=50)
    ielts_score: Optional[float] = None
    major_course_score: Optional[float] = None
    lab_score: Optional[float] = None


class StudentScoreUpdate(BaseModel):
    student_name: Optional[str] = None
    ielts_score: Optional[float] = None
    major_course_score: Optional[float] = None
    lab_score: Optional[float] = None


class StudentScoreResponse(BaseModel):
    id: int
    student_id: str
    student_name: str
    ielts_score: Optional[float] = None
    major_course_score: Optional[float] = None
    lab_score: Optional[float] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    model_config = {"from_attributes": True}


# ---- NL2SQL ----
class NL2SQLRequest(BaseModel):
    query: str


class NL2SQLResponse(BaseModel):
    sql: str
    result: Optional[list[dict]] = None
    explanation: str


# ---- Instruction ----
class InstructionRequest(BaseModel):
    instruction: str


class InstructionResponse(BaseModel):
    parsed: dict
    action: str
    result: str
