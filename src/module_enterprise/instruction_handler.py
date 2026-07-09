"""
企业管理模块 - 自然语言指令处理器。

解析用户输入的中文自然语言指令，将其映射为结构化的 CRUD 操作
（如更新投诉状态、更新客户状态），并在数据库中执行。
"""
import json
import logging
from sqlalchemy import select
from src.common.llm_client import llm_client
from src.common.database import EnterpriseSessionLocal
from src.common.models_enterprise import IntentCustomer, ComplaintFeedback

logger = logging.getLogger(__name__)

INSTRUCTION_PROMPT = """
Parse the following Chinese instruction into a JSON action. Available operations:
1. Update complaint status: {"target_table": "complaint_feedback", "action": "update", "identifiers": {"student_name": "..."}, "fields": {"status": "..."}}
2. Update customer status: {"target_table": "intent_customers", "action": "update", "identifiers": {"customer_name": "..."}, "fields": {"status": "..."}}

If the instruction cannot be mapped, return: {"action": "unknown", "reason": "..."}
Output ONLY the JSON.
"""


async def execute_instruction(instruction: str) -> dict:
    """执行自然语言指令。

    接收用户用中文描述的操作指令，通过 LLM 解析为结构化的 JSON action，
    然后根据 target_table 路由到对应的处理函数执行数据库操作。

    Args:
        instruction: 用户的中文自然语言指令（如"将张三的投诉状态改为已跟进"）

    Returns:
        包含解析结果（parsed）、操作类型（action）和执行结果（result）的字典
    """
    parsed = await _parse_instruction(instruction)
    if parsed.get("action") == "unknown":
        return {"parsed": parsed, "action": "unknown", "result": parsed.get("reason", "Unsupported operation")}

    target = parsed.get("target_table")
    if target == "complaint_feedback":
        return await _handle_complaint_update(parsed)
    elif target == "intent_customers":
        return await _handle_customer_update(parsed)

    return {"parsed": parsed, "action": "unknown", "result": "Unknown target table"}


async def _parse_instruction(instruction: str) -> dict:
    """调用 LLM 解析自然语言指令为结构化 JSON。

    Args:
        instruction: 用户的中文自然语言指令

    Returns:
        解析后的 JSON 字典，包含 action、target_table、identifiers、fields 等字段；
        解析失败时返回 {"action": "unknown", "reason": "..."}
    """
    messages = [
        {"role": "system", "content": INSTRUCTION_PROMPT},
        {"role": "user", "content": instruction},
    ]
    response = await llm_client.chat(messages, temperature=0.1, max_tokens=512)
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        return {"action": "unknown", "reason": f"Failed to parse: {response[:100]}"}


async def _handle_complaint_update(parsed: dict) -> dict:
    """处理投诉反馈状态更新操作。

    根据解析结果中的 identifiers（学生姓名）查找对应的投诉记录，
    并更新其指定字段（如 status）。

    Args:
        parsed: 解析后的指令字典，包含 identifiers 和 fields

    Returns:
        包含更新结果的字典
    """
    identifiers = parsed.get("identifiers", {})
    fields = parsed.get("fields", {})
    student_name = identifiers.get("student_name", "")
    async with EnterpriseSessionLocal() as db:
        result = await db.execute(select(ComplaintFeedback).where(ComplaintFeedback.student_name == student_name))
        obj = result.scalars().first()
        if not obj:
            return {"parsed": parsed, "action": "update", "result": f"No complaint found for: {student_name}"}
        for key, value in fields.items():
            setattr(obj, key, value)
        await db.commit()
        return {"parsed": parsed, "action": "update", "result": f"Updated complaint for {student_name}: {fields}"}


async def _handle_customer_update(parsed: dict) -> dict:
    """处理意向客户状态更新操作。

    根据解析结果中的 identifiers（客户姓名）查找对应的客户记录，
    并更新其指定字段（如 status）。

    Args:
        parsed: 解析后的指令字典，包含 identifiers 和 fields

    Returns:
        包含更新结果的字典
    """
    identifiers = parsed.get("identifiers", {})
    fields = parsed.get("fields", {})
    customer_name = identifiers.get("customer_name", "")
    async with EnterpriseSessionLocal() as db:
        result = await db.execute(select(IntentCustomer).where(IntentCustomer.customer_name == customer_name))
        obj = result.scalars().first()
        if not obj:
            return {"parsed": parsed, "action": "update", "result": f"No customer found for: {customer_name}"}
        for key, value in fields.items():
            setattr(obj, key, value)
        await db.commit()
        return {"parsed": parsed, "action": "update", "result": f"Updated customer {customer_name}: {fields}"}
