"""
Instruction handler — parses natural language instructions into CRUD actions
and executes them against the enterprise assistant database.
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
