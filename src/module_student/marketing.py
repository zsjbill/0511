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
    profile = f"Student: {student_name}\nEmotion tags: {emotion_tags}\nScores: {scores}\nInterest: {study_interest}"
    messages = [
        {"role": "system", "content": MARKETING_PROMPT},
        {"role": "user", "content": profile},
    ]
    response = await llm_client.chat(messages, temperature=0.7, max_tokens=512)
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        return {"conservative": response[:100], "moderate": response[100:200], "aggressive": response[200:300]}
