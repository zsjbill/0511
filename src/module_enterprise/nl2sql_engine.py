import logging, re
from sqlalchemy import text
from src.common.llm_client import llm_client
from src.common.database import enterprise_async_engine

logger = logging.getLogger(__name__)

ALLOWED_TABLES = {"intent_customers", "employee_daily_reports", "complaint_feedback", "student_scores"}
FORBIDDEN_KEYWORDS = ["DELETE", "UPDATE", "DROP", "ALTER", "TRUNCATE", "INSERT", "CREATE", "GRANT", "REVOKE"]

DB_SCHEMA_PROMPT = """
You are a SQL generator. Given a natural language query, output ONLY a valid MySQL SELECT statement.

Available tables in enterprise_assistant database:
1. intent_customers(id, customer_name, age, gender, education, major, follow_up_record, status, created_at, updated_at)
2. employee_daily_reports(id, employee_id, employee_name, gender, report_content, submitted_at, department, created_at)
3. complaint_feedback(id, student_id, student_name, complaint_detail, status, follower, created_at, updated_at)
4. student_scores(id, student_id, student_name, ielts_score, major_course_score, lab_score, created_at, updated_at)

Rules:
- Only SELECT queries.
- Use LIKE for fuzzy search on name columns.
- For time ranges, use created_at or submitted_at columns.
- Default ORDER BY id DESC LIMIT 20.
- Output ONLY the SQL, no explanation.
"""


class NL2SQLEngine:

    async def query(self, natural_query: str) -> dict:
        sql = await self._generate_sql(natural_query)
        self._security_check(sql)
        result = await self._execute_sql(sql)
        return {"sql": sql, "result": result, "explanation": f"Query returned {len(result)} rows."}

    async def _generate_sql(self, query: str) -> str:
        messages = [
            {"role": "system", "content": DB_SCHEMA_PROMPT},
            {"role": "user", "content": query},
        ]
        sql = await llm_client.chat(messages, temperature=0.1, max_tokens=1024)
        sql = sql.strip().strip("```sql").strip("```").strip(";").strip()
        return sql

    def _security_check(self, sql: str) -> None:
        upper_sql = sql.upper()
        for kw in FORBIDDEN_KEYWORDS:
            if re.search(rf"\b{kw}\b", upper_sql):
                raise ValueError(f"Forbidden SQL keyword detected: {kw}. Only SELECT allowed.")
        mentioned_tables = {t.lower() for t in re.findall(r"FROM\s+(\w+)", upper_sql)} | {t.lower() for t in re.findall(r"JOIN\s+(\w+)", upper_sql)}
        unknown = mentioned_tables - ALLOWED_TABLES
        if unknown:
            raise ValueError(f"Query references disallowed table(s): {unknown}")
        if not upper_sql.strip().startswith("SELECT"):
            raise ValueError("Only SELECT queries are permitted.")

    async def _execute_sql(self, sql: str) -> list[dict]:
        async with enterprise_async_engine.connect() as conn:
            result = await conn.execute(text(sql))
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
