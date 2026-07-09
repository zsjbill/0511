"""
NLP utility functions — intent classification, text cleaning, etc.
"""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Remove extra whitespace and normalize text."""
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_keywords(text: str, top_n: int = 5) -> list[str]:
    """Simple keyword extraction based on frequency."""
    # Placeholder — in production, use jieba + TF-IDF or KeyBERT
    words = re.findall(r"[一-鿿]+|[a-zA-Z]+", text)
    from collections import Counter
    return [w for w, _ in Counter(words).most_common(top_n)]


def detect_language(text: str) -> str:
    """Detect whether text is primarily Chinese or English."""
    chinese_chars = len(re.findall(r"[一-鿿]", text))
    english_words = len(re.findall(r"[a-zA-Z]+", text))
    return "zh" if chinese_chars > english_words else "en"


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max_length characters, respecting word boundaries."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
