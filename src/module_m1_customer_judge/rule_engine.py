"""
M1: Rule Engine — Dynamic rule loading and matching.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class RuleEngine:
    """Dynamic rule engine for customer profile matching."""

    def __init__(self) -> None:
        self.rules: list[dict[str, Any]] = self._load_rules()

    def _load_rules(self) -> list[dict[str, Any]]:
        """Load rules from config file or database."""
        # TODO: load from data/user_profile_rules/rules_v1.xlsx
        return [
            {"source": "百度推广", "base_score": 70, "tags": ["搜索广告", "高意向"]},
            {"source": "微信朋友圈", "base_score": 50, "tags": ["社交广告", "中意向"]},
            {"source": "朋友推荐", "base_score": 80, "tags": ["口碑推荐", "高意向"]},
        ]

    def calculate_score(self, features: dict[str, Any]) -> int:
        """Calculate customer score based on matching rules."""
        source = features.get("source", "")
        for rule in self.rules:
            if rule.get("source") == source:
                score = rule["base_score"]
                if features.get("has_phone"):
                    score += 10
                if features.get("has_wechat"):
                    score += 10
                return min(score, 100)
        return 30  # default for unknown source

    def match_tags(self, features: dict[str, Any]) -> list[str]:
        """Match tags for a customer."""
        source = features.get("source", "")
        for rule in self.rules:
            if rule.get("source") == source:
                return list(rule.get("tags", []))
        return ["未知渠道"]

    def recommend(self, score: int, tags: list[str]) -> dict[str, Any]:
        """Recommend a service based on score and tags."""
        if score >= 80:
            return {"service": "VIP一对一咨询", "reason": "高意向客户，建议资深顾问跟进"}
        elif score >= 50:
            return {"service": "标准留学方案", "reason": "中等意向，推荐标准服务套餐"}
        else:
            return {"service": "免费资料包", "reason": "低意向，先提供免费资料培养兴趣"}
