"""
M3: Command Executor — Parse and execute enterprise commands.
"""
import logging
from typing import Any

from src.common.llm_client import llm_client

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Recognize and execute commands like '同意张三请假'."""

    COMMAND_TYPES = ["请假审批", "报销审批", "信息查询", "任务分配", "会议安排"]

    async def parse(self, text: str) -> dict[str, Any]:
        """Parse natural language command into structured action."""
        prompt = f"""分析以下指令，提取关键信息：

指令类型：{', '.join(self.COMMAND_TYPES)}

输出JSON格式：
{{
  "command_type": "请假审批",
  "target_person": "张三",
  "action": "同意",
  "details": {{}}
}}"""
        result = await llm_client.chat_json([
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ])
        return result

    async def execute(self, parsed: dict[str, Any]) -> dict[str, Any]:
        """Execute the parsed command."""
        command_type = parsed.get("command_type", "")
        logger.info("Executing command: %s", command_type)
        # TODO: route to specific handler based on command_type
        return {"status": "executed", "command_type": command_type}
