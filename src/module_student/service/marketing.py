"""营销文案生成模块 — 根据学生画像生成个性化营销文案。

基于学生的情绪标签、成绩、学习兴趣等信息，
生成三档风格（保守/适中/强力）的营销推送文案。
"""

import json, logging
from src.common.llm_client import llm_client

logger = logging.getLogger(__name__)

MARKETING_PROMPT = """
Generate 3 versions of marketing copy for a student based on their profile.
Output ONLY JSON:
{
  "conservative": "gentle suggestion, low pressure",
  "moderate": "balanced recommendation",
  "aggressive": "strong call to action"
}

Each version should be <=100 Chinese characters.
Tone should be warm, professional, not intrusive.
"""


async def generate_marketing(student_id: str, student_name: str, emotion_tags=None, scores=None, study_interest=None) -> dict:
    """根据学生画像生成三档风格的营销文案。

    参数：
        student_id: 学生学号
        student_name: 学生姓名
        emotion_tags: 情绪标签列表
        scores: 成绩数据
        study_interest: 学习兴趣标签

    返回三档文案：
        conservative: 温和建议、低压力
        moderate: 平衡推荐
        aggressive: 强行动号召

    每版文案不超过100个中文字符，语气温暖专业。
    """
    profile = f"Student: {student_name}\nEmotion tags: {emotion_tags}\nScores: {scores}\nInterest: {study_interest}"
    messages = [
        {"role": "system", "content": MARKETING_PROMPT},
        {"role": "user", "content": profile},
    ]
    # 调用大模型，较高温度（0.7）以增加文案创意多样性
    response = await llm_client.chat(messages, temperature=0.7, max_tokens=512)
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        return {"conservative": response[:100], "moderate": response[100:200], "aggressive": response[200:300]}
