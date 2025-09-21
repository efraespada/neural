"""Audio repository implementation using AI client."""

import logging
from typing import List

from ...api.ai_client import AIClient
from ...repositories.interfaces.audio_repository import AudioRepository

_LOGGER = logging.getLogger(__name__)


class AudioRepositoryImpl(AudioRepository):
    """Audio repository implementation using AI client."""

    def __init__(self, ai_client: AIClient) -> None:
        """Initialize the audio repository."""
        self._ai_client = ai_client

    async def transcribe_audio(self, audio_data: bytes, language: str = "es") -> str:
        """Transcribe audio to text using AI client."""
        try:
            _LOGGER.info("Transcribing audio with language: %s", language)
            
            # Use AI client's Whisper functionality
            transcription = await self._ai_client.transcribe_audio(audio_data, language)
            
            _LOGGER.info("Audio transcription successful: %s", transcription[:50] + "..." if len(transcription) > 50 else transcription)
            return transcription
            
        except Exception as e:
            _LOGGER.error("Error transcribing audio: %s", e)
            return ""

    async def is_audio_supported(self) -> bool:
        """Check if audio processing is supported."""
        try:
            _LOGGER.info("Checking if audio processing is supported")
            
            # Check if Whisper is available through AI client
            is_supported = await self._ai_client.is_whisper_available()
            
            _LOGGER.info("Audio processing support: %s", "supported" if is_supported else "not supported")
            return is_supported
            
        except Exception as e:
            _LOGGER.error("Failed to check audio support: %s", e)
            return False

    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages for audio transcription."""
        try:
            _LOGGER.info("Getting supported languages for audio transcription")
            
            # Get supported languages from AI client
            supported_languages = await self._ai_client.get_whisper_supported_languages()
            
            _LOGGER.info("Supported languages: %s", supported_languages)
            return supported_languages
            
        except Exception as e:
            _LOGGER.error("Failed to get supported languages: %s", e)
            return ["es"]  # Default to Spanish

    async def test_audio_connection(self) -> bool:
        """Test connection to audio processing service."""
        try:
            _LOGGER.info("Testing audio processing service connection")
            
            # Test Whisper availability through AI client
            is_available = await self._ai_client.is_whisper_available()
            
            _LOGGER.info("Audio processing service connection test: %s", "success" if is_available else "failed")
            return is_available
            
        except Exception as e:
            _LOGGER.error("Failed to test audio connection: %s", e)
            return False
