"""
M2: Course Matcher — Personalized course/program recommendation.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class CourseMatcher:
    """Match customers to courses based on profile and preferences."""

    def __init__(self) -> None:
        self.courses: list[dict[str, Any]] = self._load_courses()

    def _load_courses(self) -> list[dict[str, Any]]:
        # TODO: load from DB or config
        return [
            {"name": "澳洲八大冲刺班", "target": "澳洲名校申请", "price": "¥29,800"},
            {"name": "雅思保分班", "target": "雅思6.5+", "price": "¥12,800"},
            {"name": "艺术留学作品集", "target": "艺术设计专业", "price": "¥38,000"},
        ]

    async def match(self, profile: dict[str, Any], top_n: int = 3) -> list[dict[str, Any]]:
        """Return top-N matching courses for a customer profile."""
        # Simple scoring: keyword overlap
        scored = []
        interests = profile.get("interests", [])
        for course in self.courses:
            score = sum(1 for kw in interests if kw in course["target"])
            scored.append({**course, "score": score})

        scored.sort(key=lambda c: c["score"], reverse=True)
        return scored[:top_n]
