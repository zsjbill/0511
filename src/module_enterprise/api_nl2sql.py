"""
企业管理模块 - 自然语言转 SQL（NL2SQL）API。

接收用户自然语言查询，通过 LLM 转换为 SQL 语句并执行，
返回查询结果及生成的 SQL 语句。
"""
import logging
from fastapi import APIRouter
from src.common.schemas_enterprise import APIResponse, NL2SQLRequest
from src.module_enterprise.nl2sql_engine import NL2SQLEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/enterprise/nl2sql", tags=["Enterprise - NL2SQL"])
engine = NL2SQLEngine()


@router.post("/query", response_model=APIResponse, summary="自然语言查询转 SQL", description="接收用户自然语言描述，自动生成 SQL 查询语句并执行，返回查询结果及对应 SQL")
async def nl2sql_query(request: NL2SQLRequest):
    """执行自然语言转 SQL 查询。

    接收用户以自然语言描述的查询需求，通过 LLM 生成对应的 SQL SELECT 语句，
    经过安全性检查后执行查询，最后返回查询结果和生成的 SQL。

    Args:
        request: 包含用户自然语言查询的请求体

    Returns:
        包含 SQL 语句、查询结果和行数说明的 APIResponse

    Raises:
        ValueError: 当检测到非法 SQL 关键字或引用了不允许的表时抛出
    """
    try:
        result = await engine.query(request.query)
        return APIResponse(data=result)
    except ValueError as e:
        return APIResponse(code=400, message=str(e))
    except Exception as e:
        logger.exception("NL2SQL error")
        return APIResponse(code=500, message=f"Internal error: {str(e)}")
