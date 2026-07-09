"""
M1: Unit tests for Customer Judge.
"""
import pytest
from src.module_m1_customer_judge.rule_engine import RuleEngine


class TestRuleEngine:
    def setup_method(self) -> None:
        self.engine = RuleEngine()

    def test_score_high_value_source(self) -> None:
        score = self.engine.calculate_score({"source": "朋友推荐", "has_phone": True})
        assert score >= 80

    def test_score_unknown_source(self) -> None:
        score = self.engine.calculate_score({"source": "unknown"})
        assert score == 30

    def test_tags_matching(self) -> None:
        tags = self.engine.match_tags({"source": "百度推广"})
        assert "高意向" in tags

    def test_recommend_high_score(self) -> None:
        rec = self.engine.recommend(85, ["高意向"])
        assert "VIP" in rec["service"]
