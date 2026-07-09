"""
M3: NL2SQL Engine — Natural language to SQL conversion.
"""
import logging

from src.common.llm_client import llm_client
from src.common.schemas import NL2SQLRequest, NL2SQLResponse

logger = logging.getLogger(__name__)

# Table schema for the LLM to reference
DB_SCHEMA = """
Tables:
- employees (id, name, department, position, email, status, created_at)
- customers (id, name, phone, wechat, source, tags, profile_score, created_at)
- conversations (id, customer_id, agent_id, intent, messages, status, created_at)
- registrations (id, customer_id, activity_name, status, registered_at)
- students (id, name, student_code, stage, target_country, risk_flags, created_at)
- reports (id, report_type, title, content, generated_at, created_by)
"""


class NL2SQLEngine:
    """Convert natural language queries to SQL and execute them."""

    async def execute(self, request: NL2SQLRequest) -> NL2SQLResponse:
        # Step 1: NL → SQL via LLM
        sql = await self._generate_sql(request.query)

        # Step 2: Execute SQL (TODO: actual DB execution)
        result = await self._execute_sql(sql)

        # Step 3: Explain result
        explanation = await self._explain(sql, result)

        return NL2SQLResponse(sql=sql, result=result, explanation=explanation)

    async def _generate_sql(self, query: str) -> str:
        prompt = f"""根据以下数据库 schema 将用户的自然语言查询转换为 SQL：

{DB_SCHEMA}

只输出 SQL，不要解释。"""
        sql = await llm_client.chat([
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ])
        return sql.strip().rstrip(";")

    async def _execute_sql(self, sql: str) -> list[dict]:
        # TODO: execute against real database with safety checks
        logger.info("Would execute SQL: %s", sql)
        return []

    async def _explain(self, sql: str, result: list[dict]) -> str:
        return f"查询执行完成，返回 {len(result)} 条结果。"
