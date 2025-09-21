"""AI use case interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ...api.models.domain.ai import AIStatus


class AIUseCase(ABC):
    """Interface for AI use case."""

    @abstractmethod
    async def send_message(self, message: str, model: Optional[str] = None) -> str:
        """Send a message to AI and get response text."""
        pass

    @abstractmethod
    async def get_status(self) -> AIStatus:
        """Get AI service status."""
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available AI model names."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to AI service."""
        pass

    @abstractmethod
    async def is_model_ready(self) -> bool:
        """Check if the AI model is ready for use."""
        pass

    # Whisper methods
    @abstractmethod
    async def transcribe_audio(self, audio_data: bytes, language: str = "es") -> str:
        """Transcribe audio using Whisper."""
        pass

    @abstractmethod
    async def is_whisper_available(self) -> bool:
        """Check if Whisper is available."""
        pass

    @abstractmethod
    async def get_whisper_supported_languages(self) -> List[str]:
        """Get supported languages for Whisper."""
        pass
