"""Audio use case interface."""

from abc import ABC, abstractmethod
from typing import List


class AudioUseCase(ABC):
    """Interface for audio use case."""

    @abstractmethod
    async def transcribe_audio(self, audio_data: bytes, language: str = "es") -> str:
        """Transcribe audio to text using AI service."""
        pass

    @abstractmethod
    async def is_audio_supported(self) -> bool:
        """Check if audio processing is supported."""
        pass

    @abstractmethod
    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages for audio transcription."""
        pass
