"""
M4: Risk Monitor — Psychological risk detection and alerting.
"""
import logging
import yaml
from pathlib import Path

from src.common.llm_client import llm_client
from src.common.schemas import RiskDetectionRequest, RiskDetectionResponse, RiskLevel

logger = logging.getLogger(__name__)


class RiskMonitor:
    """Detect psychological risk signals in student conversations."""

    def __init__(self) -> None:
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        prompt_path = Path(__file__).parent.parent.parent / "config/prompts/student_assistant/risk_detection.yaml"
        try:
            with open(prompt_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
            return config["risk_detection"]["prompt_template"]
        except Exception:
            logger.warning("Could not load risk detection prompt, using default")
            return "分析以下对话中的心理风险信号..."

    async def analyze(self, request: RiskDetectionRequest) -> RiskDetectionResponse:
        """Analyze conversation for risk signals."""
        conversation_text = "\n".join(
            f"{m.role}: {m.content}" for m in request.conversation
        )

        prompt = self.prompt_template.format(conversation=conversation_text)

        try:
            result = await llm_client.chat_json([
                {"role": "system", "content": "你是一个心理风险评估专家。"},
                {"role": "user", "content": prompt},
            ])

            risk_level = RiskLevel(result.get("risk_level", "low"))
            if risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH):
                await self._trigger_alert(request.student_id, risk_level, result)

            return RiskDetectionResponse(
                risk_level=risk_level,
                confidence=float(result.get("confidence", 0.5)),
                key_signals=result.get("key_signals", []),
                recommended_action=result.get("recommended_action", ""),
            )
        except Exception:
            logger.exception("Risk detection failed")
            return RiskDetectionResponse(
                risk_level=RiskLevel.LOW,
                confidence=0.0,
                key_signals=[],
                recommended_action="分析失败，请人工复核",
            )

    async def _trigger_alert(self, student_id: int, level: RiskLevel, details: dict) -> None:
        """Send alert to counselor when risk is detected."""
        logger.warning("Risk alert: student=%d level=%s", student_id, level)
        # TODO: send notification to counselor / trigger crisis workflow
