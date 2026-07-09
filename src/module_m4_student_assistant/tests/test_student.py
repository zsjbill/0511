"""
M4: Unit tests for Student Assistant.
"""
import pytest
from src.module_m4_student_assistant.risk_monitor import RiskMonitor


class TestRiskMonitor:
    def setup_method(self) -> None:
        self.monitor = RiskMonitor()

    def test_load_prompt(self) -> None:
        assert self.monitor.prompt_template is not None
        assert len(self.monitor.prompt_template) > 0
