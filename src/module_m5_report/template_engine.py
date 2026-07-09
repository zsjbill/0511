"""
M5: Template Engine — Report template management.
"""
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"


class TemplateEngine:
    """Manage and render report templates."""

    def __init__(self) -> None:
        self.templates: dict[str, str] = {}

    def load_template(self, name: str) -> str:
        """Load a template by name."""
        if name in self.templates:
            return self.templates[name]

        path = TEMPLATE_DIR / f"{name}.html"
        if path.exists():
            content = path.read_text(encoding="utf-8")
            self.templates[name] = content
            return content

        logger.warning("Template not found: %s", name)
        return "{{ content }}"

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with context."""
        try:
            from jinja2 import Template
            template_str = self.load_template(template_name)
            template = Template(template_str)
            return template.render(**context)
        except ImportError:
            logger.warning("jinja2 not installed; returning raw content")
            return str(context.get("content", ""))
