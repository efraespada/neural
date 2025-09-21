"""Audio use case implementation."""

import logging
from typing import List

from ...repositories.interfaces.audio_repository import AudioRepository
from ..interfaces.audio_use_case import AudioUseCase

_LOGGER = logging.getLogger(__name__)


class AudioUseCaseImpl(AudioUseCase):
    """Audio use case implementation."""

    def __init__(self, audio_repository: AudioRepository) -> None:
        """Initialize the audio use case."""
        self._audio_repository = audio_repository

    async def transcribe_audio(self, audio_data: bytes, language: str = "es") -> str:
        """Transcribe audio to text using audio repository."""
        try:
            _LOGGER.info("Transcribing audio with language: %s", language)
            
            # Use the audio repository to transcribe the audio
            transcription = await self._audio_repository.transcribe_audio(audio_data, language)
            
            _LOGGER.info("Audio transcription completed: %s", transcription[:50] + "..." if len(transcription) > 50 else transcription)
            return transcription
            
        except Exception as e:
            _LOGGER.error("Failed to transcribe audio: %s", e)
            raise

    async def is_audio_supported(self) -> bool:
        """Check if audio processing is supported."""
        try:
            _LOGGER.info("Checking if audio processing is supported")
            
            # Check if audio processing is supported
            is_supported = await self._audio_repository.is_audio_supported()
            
            _LOGGER.info("Audio processing support: %s", "supported" if is_supported else "not supported")
            return is_supported
            
        except Exception as e:
            _LOGGER.error("Failed to check audio support: %s", e)
            return False

    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages for audio transcription."""
        try:
            _LOGGER.info("Getting supported languages for audio transcription")
            
            # Get supported languages from the audio repository
            supported_languages = await self._audio_repository.get_supported_languages()
            
            _LOGGER.info("Supported languages: %s", supported_languages)
            return supported_languages
            
        except Exception as e:
            _LOGGER.error("Failed to get supported languages: %s", e)
            return ["es"]  # Default to Spanish
