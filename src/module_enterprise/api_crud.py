"""
企业管理模块 CRUD API。

提供意向客户、员工日报、投诉反馈、学生成绩四张表的标准增删改查接口，
支持分页、模糊搜索、状态筛选和时间范围查询。
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.crud_base import CRUDBase
from src.common.database import get_enterprise_db
from src.common.models_enterprise import (
    ComplaintFeedback,
    EmployeeDailyReport,
    IntentCustomer,
    StudentScore,
)
from src.common.schemas_enterprise import (
    APIResponse,
    ComplaintFeedbackCreate,
    ComplaintFeedbackResponse,
    ComplaintFeedbackUpdate,
    EmployeeDailyReportCreate,
    EmployeeDailyReportResponse,
    EmployeeDailyReportUpdate,
    IntentCustomerCreate,
    IntentCustomerResponse,
    IntentCustomerUpdate,
    PaginatedData,
    StudentScoreCreate,
    StudentScoreResponse,
    StudentScoreUpdate,
)

router = APIRouter(prefix="/api/v1/enterprise", tags=["Enterprise Assistant"])

# ── CRUD instances 各表的 CRUD 操作实例 ─────────────────────────────────
customer_crud = CRUDBase(IntentCustomer, IntentCustomerCreate, IntentCustomerUpdate)
report_crud = CRUDBase(EmployeeDailyReport, EmployeeDailyReportCreate, EmployeeDailyReportUpdate)
complaint_crud = CRUDBase(ComplaintFeedback, ComplaintFeedbackCreate, ComplaintFeedbackUpdate)
score_crud = CRUDBase(StudentScore, StudentScoreCreate, StudentScoreUpdate)


# ── Helpers 辅助函数 ────────────────────────────────────────────────────

def paginated_response(items: list, total: int, page: int, page_size: int, total_pages: int) -> APIResponse:
    """封装分页查询结果为标准 API 响应。

    Args:
        items: 当前页数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页记录数
        total_pages: 总页数

    Returns:
        包含分页数据的 APIResponse 对象
    """
    return APIResponse(data=PaginatedData(
        items=items, total=total, page=page, page_size=page_size, total_pages=total_pages,
    ).model_dump())


async def _get_or_404(crud: CRUDBase, id: int, db: AsyncSession, response_schema: type):
    """根据 ID 查询单条记录，不存在时返回 404 响应。

    Args:
        crud: CRUD 操作实例
        id: 记录主键 ID
        db: 数据库会话
        response_schema: 响应模型类

    Returns:
        包含记录数据的 APIResponse，或 404 错误响应
    """
    obj = await crud.get(db, id)
    if obj is None:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=response_schema.model_validate(obj).model_dump())


async def _create_record(crud: CRUDBase, data, db: AsyncSession, response_schema: type):
    """创建一条新记录并返回。

    Args:
        crud: CRUD 操作实例
        data: 创建数据（Pydantic 模型）
        db: 数据库会话
        response_schema: 响应模型类

    Returns:
        包含新创建记录数据的 APIResponse
    """
    obj = await crud.create(db, data)
    return APIResponse(data=response_schema.model_validate(obj).model_dump())


async def _update_record(crud: CRUDBase, id: int, data, db: AsyncSession, response_schema: type):
    """更新一条记录，不存在时返回 404 响应。

    Args:
        crud: CRUD 操作实例
        id: 记录主键 ID
        data: 更新数据（Pydantic 模型）
        db: 数据库会话
        response_schema: 响应模型类

    Returns:
        包含更新后记录数据的 APIResponse，或 404 错误响应
    """
    obj = await crud.update(db, id, data)
    if obj is None:
        return APIResponse(code=404, message="Not found")
    return APIResponse(data=response_schema.model_validate(obj).model_dump())


async def _delete_record(crud: CRUDBase, id: int, db: AsyncSession):
    """删除一条记录，不存在时返回 404 响应。

    Args:
        crud: CRUD 操作实例
        id: 记录主键 ID
        db: 数据库会话

    Returns:
        成功删除或 404 的 APIResponse
    """
    deleted = await crud.delete(db, id)
    if not deleted:
        return APIResponse(code=404, message="Not found")
    return APIResponse(message="Deleted successfully")


# ── Customers 意向客户接口 ──────────────────────────────────────────────

@router.get("/customers", response_model=APIResponse, summary="获取意向客户列表", description="支持按姓名模糊搜索、状态筛选、时间范围查询，分页返回")
async def list_customers(
    page: int = Query(1, ge=1, description="当前页码，从 1 开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页记录数（1-100）"),
    customer_name: Optional[str] = Query(None, description="客户姓名（模糊匹配 LIKE）"),
    status: Optional[str] = Query(None, description="客户状态（精确匹配）"),
    start_date: Optional[str] = Query(None, description="创建时间范围（起始日期）"),
    end_date: Optional[str] = Query(None, description="创建时间范围（结束日期）"),
    db: AsyncSession = Depends(get_enterprise_db),
):
    """获取意向客户列表，支持多条件筛选和分页。

    - **customer_name**: 客户姓名（模糊匹配 LIKE）
    - **status**: 客户状态（精确匹配）
    - **start_date/end_date**: 创建时间范围
    """
    kwargs = {}
    if customer_name:
        kwargs["customer_name__like"] = customer_name
    if status:
        kwargs["status"] = status
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    result = await customer_crud.list(db, page=page, page_size=page_size, **kwargs)
    result["items"] = [IntentCustomerResponse.model_validate(item).model_dump() for item in result["items"]]
    return paginated_response(**result)


@router.get("/customers/{id}", response_model=APIResponse, summary="获取意向客户详情", description="根据 ID 获取单条意向客户记录")
async def get_customer(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    """获取单条意向客户记录。"""
    return await _get_or_404(customer_crud, id, db, IntentCustomerResponse)


@router.post("/customers", response_model=APIResponse, summary="创建意向客户", description="新增一条意向客户记录")
async def create_customer(data: IntentCustomerCreate, db: AsyncSession = Depends(get_enterprise_db)):
    """创建新的意向客户记录。"""
    return await _create_record(customer_crud, data, db, IntentCustomerResponse)


@router.put("/customers/{id}", response_model=APIResponse, summary="更新意向客户", description="根据 ID 更新意向客户信息")
async def update_customer(id: int, data: IntentCustomerUpdate, db: AsyncSession = Depends(get_enterprise_db)):
    """更新意向客户记录。"""
    return await _update_record(customer_crud, id, data, db, IntentCustomerResponse)


@router.delete("/customers/{id}", response_model=APIResponse, summary="删除意向客户", description="根据 ID 删除意向客户记录")
async def delete_customer(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    """删除意向客户记录。"""
    return await _delete_record(customer_crud, id, db)


# ── Reports 员工日报接口 ────────────────────────────────────────────────

@router.get("/reports", response_model=APIResponse, summary="获取员工日报列表", description="支持按部门筛选、员工姓名模糊搜索、提交时间范围查询，分页返回")
async def list_reports(
    page: int = Query(1, ge=1, description="当前页码，从 1 开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页记录数（1-100）"),
    department: Optional[str] = Query(None, description="所属部门（精确匹配）"),
    employee_name: Optional[str] = Query(None, description="员工姓名（模糊匹配 LIKE）"),
    start_date: Optional[str] = Query(None, description="提交时间范围（起始日期）"),
    end_date: Optional[str] = Query(None, description="提交时间范围（结束日期）"),
    db: AsyncSession = Depends(get_enterprise_db),
):
    """获取员工日报列表，支持多条件筛选和分页。

    - **department**: 所属部门（精确匹配）
    - **employee_name**: 员工姓名（模糊匹配 LIKE）
    - **start_date/end_date**: 提交时间范围
    """
    kwargs = {}
    if department:
        kwargs["department"] = department
    if employee_name:
        kwargs["employee_name__like"] = employee_name
    if start_date:
        kwargs["submitted_at__gte"] = start_date
    if end_date:
        kwargs["submitted_at__lte"] = end_date
    result = await report_crud.list(db, page=page, page_size=page_size, **kwargs)
    result["items"] = [EmployeeDailyReportResponse.model_validate(item).model_dump() for item in result["items"]]
    return paginated_response(**result)


@router.get("/reports/{id}", response_model=APIResponse, summary="获取日报详情", description="根据 ID 获取单条员工日报记录")
async def get_report(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    """获取单条员工日报记录。"""
    return await _get_or_404(report_crud, id, db, EmployeeDailyReportResponse)


@router.post("/reports", response_model=APIResponse, summary="创建员工日报", description="新增一条员工日报记录")
async def create_report(data: EmployeeDailyReportCreate, db: AsyncSession = Depends(get_enterprise_db)):
    """创建新的员工日报记录。"""
    return await _create_record(report_crud, data, db, EmployeeDailyReportResponse)


@router.put("/reports/{id}", response_model=APIResponse, summary="更新员工日报", description="根据 ID 更新员工日报信息")
async def update_report(id: int, data: EmployeeDailyReportUpdate, db: AsyncSession = Depends(get_enterprise_db)):
    """更新员工日报记录。"""
    return await _update_record(report_crud, id, data, db, EmployeeDailyReportResponse)


@router.delete("/reports/{id}", response_model=APIResponse, summary="删除员工日报", description="根据 ID 删除员工日报记录")
async def delete_report(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    """删除员工日报记录。"""
    return await _delete_record(report_crud, id, db)


# ── Complaints 投诉反馈接口 ─────────────────────────────────────────────

@router.get("/complaints", response_model=APIResponse, summary="获取投诉反馈列表", description="支持按状态、跟进人筛选，分页返回")
async def list_complaints(
    page: int = Query(1, ge=1, description="当前页码，从 1 开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页记录数（1-100）"),
    status: Optional[str] = Query(None, description="投诉状态（精确匹配）"),
    follower: Optional[str] = Query(None, description="跟进人（精确匹配）"),
    db: AsyncSession = Depends(get_enterprise_db),
):
    """获取投诉反馈列表，支持多条件筛选和分页。

    - **status**: 投诉状态（精确匹配）
    - **follower**: 跟进人（精确匹配）
    """
    kwargs = {}
    if status:
        kwargs["status"] = status
    if follower:
        kwargs["follower"] = follower
    result = await complaint_crud.list(db, page=page, page_size=page_size, **kwargs)
    result["items"] = [ComplaintFeedbackResponse.model_validate(item).model_dump() for item in result["items"]]
    return paginated_response(**result)


@router.get("/complaints/{id}", response_model=APIResponse, summary="获取投诉详情", description="根据 ID 获取单条投诉反馈记录")
async def get_complaint(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    """获取单条投诉反馈记录。"""
    return await _get_or_404(complaint_crud, id, db, ComplaintFeedbackResponse)


@router.post("/complaints", response_model=APIResponse, summary="创建投诉反馈", description="新增一条投诉反馈记录")
async def create_complaint(data: ComplaintFeedbackCreate, db: AsyncSession = Depends(get_enterprise_db)):
    """创建新的投诉反馈记录。"""
    return await _create_record(complaint_crud, data, db, ComplaintFeedbackResponse)


@router.put("/complaints/{id}", response_model=APIResponse, summary="更新投诉反馈", description="根据 ID 更新投诉反馈信息")
async def update_complaint(id: int, data: ComplaintFeedbackUpdate, db: AsyncSession = Depends(get_enterprise_db)):
    """更新投诉反馈记录。"""
    return await _update_record(complaint_crud, id, data, db, ComplaintFeedbackResponse)


@router.delete("/complaints/{id}", response_model=APIResponse, summary="删除投诉反馈", description="根据 ID 删除投诉反馈记录")
async def delete_complaint(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    """删除投诉反馈记录。"""
    return await _delete_record(complaint_crud, id, db)


# ── Scores 学生成绩接口 ─────────────────────────────────────────────────

@router.get("/scores", response_model=APIResponse, summary="获取学生成绩列表", description="支持按学号、姓名搜索，按分数范围筛选，分页返回")
async def list_scores(
    page: int = Query(1, ge=1, description="当前页码，从 1 开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页记录数（1-100）"),
    student_id: Optional[str] = Query(None, description="学号（精确匹配）"),
    student_name: Optional[str] = Query(None, description="学生姓名（模糊匹配 LIKE）"),
    min_score: Optional[float] = Query(None, description="最低分数阈值"),
    max_score: Optional[float] = Query(None, description="最高分数阈值"),
    db: AsyncSession = Depends(get_enterprise_db),
):
    """获取学生成绩列表，支持多条件筛选和分页。

    - **student_id**: 学号（精确匹配）
    - **student_name**: 学生姓名（模糊匹配 LIKE）
    - **min_score/max_score**: 分数范围筛选
    """
    kwargs = {}
    if student_id:
        kwargs["student_id"] = student_id
    if student_name:
        kwargs["student_name__like"] = student_name
    if min_score is not None:
        kwargs["min_score"] = min_score
    if max_score is not None:
        kwargs["max_score"] = max_score
    result = await score_crud.list(db, page=page, page_size=page_size, **kwargs)
    result["items"] = [StudentScoreResponse.model_validate(item).model_dump() for item in result["items"]]
    return paginated_response(**result)


@router.get("/scores/{id}", response_model=APIResponse, summary="获取成绩详情", description="根据 ID 获取单条学生成绩记录")
async def get_score(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    """获取单条学生成绩记录。"""
    return await _get_or_404(score_crud, id, db, StudentScoreResponse)


@router.post("/scores", response_model=APIResponse, summary="创建学生成绩", description="新增一条学生成绩记录")
async def create_score(data: StudentScoreCreate, db: AsyncSession = Depends(get_enterprise_db)):
    """创建新的学生成绩记录。"""
    return await _create_record(score_crud, data, db, StudentScoreResponse)


@router.put("/scores/{id}", response_model=APIResponse, summary="更新学生成绩", description="根据 ID 更新学生成绩信息")
async def update_score(id: int, data: StudentScoreUpdate, db: AsyncSession = Depends(get_enterprise_db)):
    """更新学生成绩记录。"""
    return await _update_record(score_crud, id, data, db, StudentScoreResponse)


@router.delete("/scores/{id}", response_model=APIResponse, summary="删除学生成绩", description="根据 ID 删除学生成绩记录")
async def delete_score(id: int, db: AsyncSession = Depends(get_enterprise_db)):
    """删除学生成绩记录。"""
    return await _delete_record(score_crud, id, db)
