"""
企业管理模块 - NL2SQL 引擎。

将用户自然语言查询转换为 SQL SELECT 语句并执行。
包含 SQL 生成、安全性检查（防注入）和查询执行功能。
"""
import logging, re
from sqlalchemy import text
from src.common.llm_client import llm_client
from src.common.database import enterprise_async_engine

logger = logging.getLogger(__name__)

# 允许查询的表名白名单
ALLOWED_TABLES = {"intent_customers", "employee_daily_reports", "complaint_feedback", "student_scores"}
# 禁止在生成的 SQL 中出现的关键字（防止注入攻击）
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
    """自然语言转 SQL 查询引擎。

    接收用户的自然语言描述，通过 LLM 生成对应的 SQL SELECT 查询语句，
    经过安全性校验后执行，返回结果及生成的 SQL。

    Usage:
        engine = NL2SQLEngine()
        result = await engine.query("查询所有意向客户")
    """

    async def query(self, natural_query: str) -> dict:
        """执行自然语言查询。

        将用户的自然语言查询转换为 SQL，执行安全性检查，然后查询数据库。

        Args:
            natural_query: 用户的自然语言查询字符串

        Returns:
            包含 sql（生成的 SQL 语句）、result（查询结果列表）和
            explanation（结果说明）的字典

        Raises:
            ValueError: 当 SQL 包含非法关键字或引用了不允许的表时抛出
        """
        sql = await self._generate_sql(natural_query)
        self._security_check(sql)
        result = await self._execute_sql(sql)
        return {"sql": sql, "result": result, "explanation": f"Query returned {len(result)} rows."}

    async def _generate_sql(self, query: str) -> str:
        """调用 LLM 从自然语言生成 SQL 语句。

        Args:
            query: 用户的自然语言查询

        Returns:
            生成的 SQL SELECT 语句字符串
        """
        messages = [
            {"role": "system", "content": DB_SCHEMA_PROMPT},
            {"role": "user", "content": query},
        ]
        sql = await llm_client.chat(messages, temperature=0.1, max_tokens=1024)
        sql = sql.strip().strip("```sql").strip("```").strip(";").strip()
        return sql

    def _security_check(self, sql: str) -> None:
        """对生成的 SQL 进行安全性检查。

        检查是否包含被禁止的关键字（DELETE、DROP 等）、
        是否引用了不在白名单中的表、是否以 SELECT 开头。

        Args:
            sql: 待检查的 SQL 语句

        Raises:
            ValueError: 当 SQL 未通过安全检测时抛出
        """
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
        """执行 SQL 查询并返回结果。

        Args:
            sql: 要执行的 SQL SELECT 语句

        Returns:
            查询结果列表，每条记录为一个字典
        """
        async with enterprise_async_engine.connect() as conn:
            result = await conn.execute(text(sql))
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
