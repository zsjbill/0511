"""
M4: Marketing Generator — Personalized marketing copy for value-added services.
"""
import logging

from src.common.llm_client import llm_client

logger = logging.getLogger(__name__)


class MarketingGenerator:
    """Generate personalized marketing copy for students."""

    async def generate(self, student_profile: dict) -> str:
        """Generate a marketing message based on student profile."""
        prompt = f"""基于以下学生画像，生成一段自然的增值服务推荐话术：

学生信息：
- 阶段：{student_profile.get('stage', '未知')}
- 兴趣方向：{student_profile.get('interests', ['通用'])}
- 已购服务：{student_profile.get('purchased', ['基础服务'])}

要求：语气温暖、非侵入式，不超过200字。"""

        copy = await llm_client.chat([
            {"role": "system", "content": "你是一个留学服务顾问，擅长用温和的方式推荐增值服务。"},
            {"role": "user", "content": prompt},
        ])
        return copy
