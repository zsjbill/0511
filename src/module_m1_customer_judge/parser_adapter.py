"""
M1: Parser Adapter — Multipurpose format parsing via common/file_parser.
"""
from src.common.file_parser import parse_file


async def parse_uploaded_file(file_path: str) -> str:
    """Parse an uploaded file and return its text content."""
    return parse_file(file_path)
