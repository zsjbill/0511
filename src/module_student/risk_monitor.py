import json, logging
from src.common.llm_client import llm_client
from src.common.database import StudentSessionLocal
from src.common.models_student import PsychologicalAlert
from src.module_student.notification_service import create_notification

logger = logging.getLogger(__name__)

RISK_PROMPT = """
Analyze the following student conversation for psychological risk signals.
Output ONLY JSON:
{
  "risk_level": "low|medium|high",
  "confidence": 0.0-1.0,
  "key_signals": ["signal1", "signal2"],
  "recommended_action": "what the teacher should do"
}

Risk indicators:
- high: self-harm thoughts, suicidal ideation, extreme despair, threats to safety
- medium: frequent anxiety/depression, social withdrawal, significant academic decline
- low: mild stress, occasional negative emotions, normal adjustment issues
"""


async def detect_risk(student_id: str, student_name: str, conversation_text: str) -> dict:
    messages = [
        {"role": "system", "content": RISK_PROMPT},
        {"role": "user", "content": conversation_text},
    ]
    response = await llm_client.chat(messages, temperature=0.2, max_tokens=512)
    try:
        result = json.loads(response.strip())
    except json.JSONDecodeError:
        return {"risk_level": "low", "confidence": 0.0, "key_signals": [], "recommended_action": "Parse error", "alert_created": False}

    alert_created = False
    if result.get("risk_level") in ("medium", "high"):
        try:
            async with StudentSessionLocal() as db:
                alert = PsychologicalAlert(
                    student_id=student_id, student_name=student_name,
                    trigger_reason=conversation_text[:500],
                    risk_level=result["risk_level"],
                )
                db.add(alert)
                await db.commit()
                await db.refresh(alert)

            await create_notification(
                recipient_id="counselor_all", recipient_type="teacher",
                type="risk_alert",
                title=f"Risk Alert: {student_name} ({result['risk_level']})",
                content=f"Signals: {', '.join(result.get('key_signals', []))}\nAction: {result.get('recommended_action', '')}",
                related_id=alert.id,
            )
            alert_created = True
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")

    result["alert_created"] = alert_created
    return result
