import logging
from sqlalchemy import text
from src.common.database import student_async_engine

logger = logging.getLogger(__name__)


async def search_kb(query: str, top_k: int = 5) -> list[dict]:
    """Search kb_documents using MySQL FULLTEXT index with jieba tokenization."""
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
