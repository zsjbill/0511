"""
File parser — unified entry for PDF, Excel, TXT, DOCX parsing.
"""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FileParser:
    """Parse various file formats into plain text."""

    @staticmethod
    def parse(file_path: str | Path) -> str:
        """Auto-detect extension and parse."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        if ext == ".pdf":
            return FileParser._parse_pdf(path)
        elif ext in (".xlsx", ".xls"):
            return FileParser._parse_excel(path)
        elif ext == ".docx":
            return FileParser._parse_docx(path)
        elif ext in (".txt", ".md", ".yaml", ".yml", ".json", ".py", ".csv"):
            return path.read_text(encoding="utf-8")
        else:
            logger.warning("Unknown file type: %s, trying as text", ext)
            return path.read_text(encoding="utf-8")

    @staticmethod
    def _parse_pdf(path: Path) -> str:
        try:
            import pymupdf  # PyMuPDF
            doc = pymupdf.open(str(path))
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            return text
        except ImportError:
            logger.error("pymupdf not installed")
            return ""

    @staticmethod
    def _parse_excel(path: Path) -> str:
        try:
            import pandas as pd
            df = pd.read_excel(path)
            return df.to_string(index=False)
        except ImportError:
            logger.error("pandas not installed")
            return ""

    @staticmethod
    def _parse_docx(path: Path) -> str:
        try:
            from docx import Document
            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            logger.error("python-docx not installed")
            return ""


# Shortcut
parse_file = FileParser.parse
