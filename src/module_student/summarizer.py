import json, logging
from src.common.llm_client import llm_client

logger = logging.getLogger(__name__)

SUMMARY_PROMPT = """
Summarize the following student complaint into a concise work order summary (<=100 Chinese characters).
Output ONLY JSON:
{
  "complainant": "student name",
  "core_issue": "one-sentence description",
  "urgency": "low|medium|high",
  "suggested_handler": "department or role",
  "summary": "100-character Chinese summary"
}
"""


async def summarize_complaint(complaint_text: str) -> dict:
    messages = [
        {"role": "system", "content": SUMMARY_PROMPT},
        {"role": "user", "content": complaint_text},
    ]
    response = await llm_client.chat(messages, temperature=0.3, max_tokens=512)
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        return {"complainant": "unknown", "core_issue": "Parse error", "urgency": "medium", "suggested_handler": "N/A", "summary": response[:100]}
