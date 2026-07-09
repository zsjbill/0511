"""学生端知识库搜索 API 端点。

提供对 kb_documents 表的全文搜索接口，
支持 jieba 分词和 MySQL FULLTEXT 索引。
"""

from fastapi import APIRouter
from src.module_student.pdcmodel.schemas import APIResponse, KBSearchRequest
from src.module_student.service.kb import search_kb

router = APIRouter(prefix="/api/v1/student/kb", tags=["Student - Knowledge Base"])

@router.post("/search", response_model=APIResponse,
             summary="搜索知识库", description="对知识库文档进行全文搜索（使用 jieba 分词 + MySQL FULLTEXT 索引）。")
async def kb_search(request: KBSearchRequest):
    """搜索知识库文档。

    使用 jieba 分词对查询语句进行切词，
    然后通过 MySQL FULLTEXT 索引执行全文检索，
    返回匹配文档的标题、相关性得分和内容片段。
    """
    try:
        results = await search_kb(request.query, request.top_k)
        return APIResponse(data={"results": results, "query": request.query})
    except Exception as e:
        return APIResponse(code=500, message=str(e))
