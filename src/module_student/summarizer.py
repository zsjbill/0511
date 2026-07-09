"""投诉摘要生成模块 — 调用大模型提取投诉文本的关键信息。

从投诉文本中提取投诉人、核心问题、紧急程度、
建议处理部门和中文摘要（不超过100字）。
"""

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
    """生成投诉文本的摘要信息。

    调用大模型分析投诉内容，提取结构化摘要：
    - complainant：投诉人姓名
    - core_issue：核心问题一句话描述
    - urgency：紧急程度（low/medium/high）
    - suggested_handler：建议处理部门或角色
    - summary：不超过100字的中文摘要
    """
    messages = [
        {"role": "system", "content": SUMMARY_PROMPT},
        {"role": "user", "content": complaint_text},
    ]
    # 调用大模型，中等温度（0.3）在准确性和创造性之间取得平衡
    response = await llm_client.chat(messages, temperature=0.3, max_tokens=512)
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        # JSON 解析失败时返回默认结构
        return {"complainant": "unknown", "core_issue": "Parse error", "urgency": "medium", "suggested_handler": "N/A", "summary": response[:100]}
