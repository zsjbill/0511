"""知识库搜索服务模块 — MySQL FULLTEXT 全文检索。

使用 jieba 分词对查询语句进行切词，
通过 MySQL FULLTEXT 索引执行全文检索。
"""

import logging
from sqlalchemy import text
from src.common.database import student_async_engine

logger = logging.getLogger(__name__)


async def search_kb(query: str, top_k: int = 5) -> list[dict]:
    """搜索知识库文档（kb_documents 表）。

    搜索流程：
    1. 使用 jieba 对查询语句进行分词
    2. 分词结果用空格拼接后作为全文搜索查询词
    3. 通过 MySQL MATCH ... AGAINST 执行全文检索
    4. 按相关性得分降序排列，返回 top_k 条结果

    返回字段：title（标题）、score（相关性得分）、content_snippet（内容摘要前200字）
    """
    try:
        import jieba
        tokens = list(jieba.cut(query))
        search_query = " ".join(tokens)
    except ImportError:
        search_query = query

    sql = text(
        "SELECT title, MATCH(title, content) AGAINST(:q IN NATURAL LANGUAGE MODE) AS score, "
        "SUBSTRING(content, 1, 200) AS content_snippet "
        "FROM kb_documents "
        "WHERE MATCH(title, content) AGAINST(:q IN NATURAL LANGUAGE MODE) "
        "ORDER BY score DESC LIMIT :limit"
    )

    async with student_async_engine.connect() as conn:
        result = await conn.execute(sql, {"q": search_query, "limit": top_k})
        rows = result.fetchall()
        return [
            {"title": row[0], "score": round(float(row[1] or 0), 4), "content_snippet": row[2]}
            for row in rows
        ]
