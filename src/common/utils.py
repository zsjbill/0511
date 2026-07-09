"""
General utility functions.
"""
import hashlib
import time
import uuid
from typing import Any


def generate_id() -> str:
    """Generate a unique ID."""
    return uuid.uuid4().hex[:16]


def hash_text(text: str) -> str:
    """Return SHA-256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def timestamp() -> int:
    """Return current Unix timestamp in seconds."""
    return int(time.time())


def safe_get(d: dict, *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dicts."""
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d
