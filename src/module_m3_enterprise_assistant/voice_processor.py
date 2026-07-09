"""
M3: Voice Processor — Speech-to-text and structuring.
"""
import logging

logger = logging.getLogger(__name__)


class VoiceProcessor:
    """Convert voice input to structured text."""

    async def transcribe(self, audio_path: str) -> str:
        """Transcribe audio file to text."""
        # TODO: integrate ASR service (e.g., Whisper API)
        logger.info("Transcribing: %s", audio_path)
        return ""

    async def structure(self, raw_text: str) -> dict:
        """Extract structured intent/entities from transcribed text."""
        # TODO: use LLM to extract structured fields
        return {"raw": raw_text, "intent": "", "entities": {}}
