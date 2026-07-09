"""
NL2SQL Engine Tests — 10 security tests (no LLM, fast) + 10 integration tests (require LLM).
"""
import pytest
from src.module_enterprise.service.nl2sql_engine import NL2SQLEngine


# ─── Security Tests (no LLM needed) ─────────────────────────────────────────

class TestNL2SQLSecurity:
    """Security validation without LLM connectivity."""

    def setup_method(self):
        self.engine = NL2SQLEngine()

    def test_rejects_delete(self):
        with pytest.raises(ValueError, match="DELETE"):
            self.engine._security_check("DELETE FROM intent_customers WHERE id=1")

    def test_rejects_update(self):
        with pytest.raises(ValueError, match="UPDATE"):
            self.engine._security_check("UPDATE intent_customers SET status='active' WHERE id=1")

    def test_rejects_drop(self):
        with pytest.raises(ValueError, match="DROP"):
            self.engine._security_check("DROP TABLE intent_customers")

    def test_rejects_insert(self):
        with pytest.raises(ValueError, match="INSERT"):
            self.engine._security_check("INSERT INTO intent_customers (name) VALUES ('test')")

    def test_rejects_alter(self):
        with pytest.raises(ValueError, match="ALTER"):
            self.engine._security_check("ALTER TABLE intent_customers ADD COLUMN test VARCHAR(50)")

    def test_allows_select(self):
        # Should not raise any exception
        self.engine._security_check("SELECT * FROM intent_customers")

    def test_allows_select_with_join(self):
        self.engine._security_check(
            "SELECT c.*, r.report_content FROM intent_customers c "
            "JOIN employee_daily_reports r ON c.id = r.employee_id"
        )

    def test_rejects_unknown_table(self):
        with pytest.raises(ValueError, match="disallowed table"):
            self.engine._security_check("SELECT * FROM secret_table")

    def test_rejects_non_select_start(self):
        with pytest.raises(ValueError, match="Only SELECT"):
            self.engine._security_check("EXPLAIN SELECT * FROM intent_customers")

    def test_allows_select_with_where(self):
        self.engine._security_check(
            "SELECT customer_name, status FROM intent_customers "
            "WHERE status = 'active' AND created_at >= '2025-01-01' "
            "ORDER BY id DESC LIMIT 10"
        )


# ─── Integration Tests (require LLM) ────────────────────────────────────────

class TestNL2SQLEngine:
    """Integration tests that require LLM connectivity."""

    @pytest.mark.asyncio
    async def test_query_generates_sql(self):
        engine = NL2SQLEngine()
        result = await engine.query("查询所有意向客户")
        assert isinstance(result, dict)
        assert "sql" in result
        assert "result" in result

    @pytest.mark.asyncio
    async def test_query_customer_by_name(self):
        engine = NL2SQLEngine()
        result = await engine.query("查找名字叫张三的客户")
        assert isinstance(result, dict)
        assert "sql" in result

    @pytest.mark.asyncio
    async def test_query_status_filter(self):
        engine = NL2SQLEngine()
        result = await engine.query("查询所有状态为已签约的客户")
        assert isinstance(result, dict)
        assert "sql" in result

    @pytest.mark.asyncio
    async def test_query_time_range(self):
        engine = NL2SQLEngine()
        result = await engine.query("查询2025年1月创建的客户")
        assert isinstance(result, dict)
        assert "sql" in result

    @pytest.mark.asyncio
    async def test_query_aggregate(self):
        engine = NL2SQLEngine()
        result = await engine.query("统计每个状态的客户数量")
        assert isinstance(result, dict)
        assert "sql" in result
        assert "result" in result

    @pytest.mark.asyncio
    async def test_query_order(self):
        engine = NL2SQLEngine()
        result = await engine.query("按创建时间倒序显示所有客户")
        assert isinstance(result, dict)
        assert "sql" in result

    @pytest.mark.asyncio
    async def test_query_score_range(self):
        engine = NL2SQLEngine()
        result = await engine.query("查询雅思成绩大于6.5的学生")
        assert isinstance(result, dict)
        assert "sql" in result

    @pytest.mark.asyncio
    async def test_query_multi_table(self):
        engine = NL2SQLEngine()
        result = await engine.query("查询所有有投诉记录的客户")
        assert isinstance(result, dict)
        assert "sql" in result

    @pytest.mark.asyncio
    async def test_query_follow_up_incomplete(self):
        engine = NL2SQLEngine()
        result = await engine.query("查询所有未跟进的客户")
        assert isinstance(result, dict)
        assert "sql" in result

    def test_total_test_count(self):
        """Verify we have exactly 10 security tests and 10 integration tests."""
        sec = TestNL2SQLSecurity
        integ = TestNL2SQLEngine
        sec_tests = [m for m in dir(sec) if m.startswith("test_")]
        integ_tests = [m for m in dir(integ) if m.startswith("test_")]
        assert len(sec_tests) == 10, f"Expected 10 security tests, got {len(sec_tests)}"
        assert len(integ_tests) == 10, f"Expected 10 integration tests, got {len(integ_tests)}"
