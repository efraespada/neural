"""Neural AI Speech-to-Text engine using OpenRouter API."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioSampleRates,
    SpeechToTextEntity,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .core.dependency_injection.providers import setup_dependencies, clear_dependencies
from .core.dependency_injection.injector_container import get_audio_use_case

_LOGGER = logging.getLogger(__name__)

from .const import (
    CONF_STT_MODEL,
    CONF_STT_API_KEY,
)

from .core.const import (
    DEFAULT_STT_MODEL,
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Neural STT entity."""
    model = config_entry.data.get(CONF_STT_MODEL, DEFAULT_STT_MODEL)
    api_key = config_entry.data.get(CONF_STT_API_KEY, "")

    stt_config = {
        CONF_STT_API_KEY: api_key,
        CONF_STT_MODEL: model,
    }

    _LOGGER.warning("Creating Neural STT entity with config: %s", stt_config)
    async_add_entities([NeuralSTTEntity(hass, stt_config)])

class NeuralSTTEntity(SpeechToTextEntity):
    """Neural AI STT entity using OpenAI Whisper."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize Neural STT entity."""
        self.hass = hass
        self.config = config
        self._session: aiohttp.ClientSession | None = None
        
        # Log configuration details (without sensitive data)
        safe_config = {k: v for k, v in config.items() if k != "stt_api_key"}
        safe_config["stt_api_key"] = "***" if config.get("stt_api_key") else "None"
        _LOGGER.info("Neural STT entity initialized with config: %s", safe_config)
        _LOGGER.info("STT Model: %s", config.get("stt_model", "whisper-1"))
        _LOGGER.info("AI URL: %s", config.get("ai_url", "https://openrouter.ai/api/v1"))
        _LOGGER.info("AI Model: %s", config.get("ai_model", "openai/gpt-oss-20b"))

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return "Neural AI STT"

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the entity."""
        return "neural_stt"

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return ["es", "en", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"]

    @property
    def supported_formats(self) -> list[AudioFormats]:
        """Return a list of supported formats."""
        return [AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[AudioCodecs]:
        """Return a list of supported codecs."""
        return [AudioCodecs.PCM]

    @property
    def supported_bit_rates(self) -> list[AudioBitRates]:
        """Return a list of supported bit rates."""
        return [AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[AudioSampleRates]:
        """Return a list of supported sample rates."""
        return [AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[AudioChannels]:
        """Return a list of supported channels."""
        return [AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(
        self, metadata: SpeechMetadata, stream: Any
    ) -> SpeechResult:
        """Process audio stream and return speech result."""
        try:
            _LOGGER.warning("Processing audio with Neural STT")
            _LOGGER.warning("Audio metadata - Language: %s, Format: %s, Codec: %s", 
                        metadata.language, metadata.format, metadata.codec)
            _LOGGER.warning("Audio metadata - Bit rate: %s, Sample rate: %s, Channels: %s", 
                        metadata.bit_rate, metadata.sample_rate, metadata.channel)
            
            # Read audio data from stream
            audio_data = await self._read_audio_stream(stream)
            _LOGGER.warning("Audio data size: %d bytes", len(audio_data))
            
            if not audio_data:
                _LOGGER.warning("No audio data received")
                return SpeechResult("", SpeechResultState.ERROR)
            
            # Send audio to transcription
            _LOGGER.warning("Starting audio transcription with language: %s", metadata.language)
            text = await self._transcribe_audio(audio_data, metadata.language)
            
            if text:
                _LOGGER.warning("Transcription successful: %s", text)
                return SpeechResult(text, SpeechResultState.SUCCESS)
            else:
                _LOGGER.error("No transcription result")
                return SpeechResult("", SpeechResultState.ERROR)
                
        except Exception as e:
            _LOGGER.error("Error processing audio: %s", e)
            return SpeechResult("", SpeechResultState.ERROR)

    async def _read_audio_stream(self, stream: Any) -> bytes:
        """Read audio data from stream."""
        audio_data = b""
        chunk_count = 0
        try:
            _LOGGER.warning("Starting to read audio stream")
            while chunk := await stream.read(4096):
                audio_data += chunk
                chunk_count += 1
                if chunk_count % 10 == 0:  # Log every 10 chunks
                    _LOGGER.warning("Read %d chunks, total size: %d bytes", chunk_count, len(audio_data))
        except Exception as e:
            _LOGGER.error("Error reading audio stream: %s", e)
            return b""
        
        _LOGGER.warning("Audio stream reading completed: %d chunks, %d bytes total", chunk_count, len(audio_data))
        return audio_data

    async def _transcribe_audio(self, audio_data: bytes, language: str) -> str:
        """Transcribe audio using the audio use case."""
        try:
            _LOGGER.warning("Setting up dependencies for audio transcription")
            # Setup dependencies
            await setup_dependencies()
            
            try:
                _LOGGER.warning("Getting audio use case")
                # Get audio use case
                audio_use_case = get_audio_use_case()
                
                _LOGGER.warning("Calling audio use case transcribe_audio with %d bytes, language: %s", 
                            len(audio_data), language)
                # Transcribe audio using the use case
                transcription = await audio_use_case.transcribe_audio(audio_data, language)
                
                _LOGGER.warning("Audio transcription completed: %s", transcription[:50] + "..." if len(transcription) > 50 else transcription)
                return transcription
                
            finally:
                _LOGGER.warning("Cleaning up dependencies")
                # Clean up dependencies
                clear_dependencies()
                        
        except Exception as e:
            _LOGGER.error("Error transcribing audio: %s", e)
            return ""

    async def async_cleanup(self) -> None:
        """Clean up resources."""
        if self._session:
            await self._session.close()
            self._session = None
