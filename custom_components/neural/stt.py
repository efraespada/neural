"""Neural AI Speech-to-Text engine using OpenRouter API."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioSampleRates,
    Provider,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
    async_register_provider,
    async_unregister_provider,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .core.dependency_injection.providers import setup_dependencies, clear_dependencies
from .core.dependency_injection.injector_container import get_audio_use_case

_LOGGER = logging.getLogger(__name__)


class NeuralSTTProvider(Provider):
    """Neural AI STT provider using OpenRouter API."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize Neural STT provider."""
        self.hass = hass
        self.config = config
        self._session: aiohttp.ClientSession | None = None
        _LOGGER.info("Neural STT provider initialized with config: %s", config)

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return ["es", "en", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"]

    @property
    def supported_formats(self) -> list[AudioFormats]:
        """Return a list of supported formats."""
        return [AudioFormats.WAV, AudioFormats.OGG, AudioFormats.MP3, AudioFormats.MP4]

    @property
    def supported_codecs(self) -> list[AudioCodecs]:
        """Return a list of supported codecs."""
        return [AudioCodecs.PCM, AudioCodecs.OGG_OPUS, AudioCodecs.MP3, AudioCodecs.AAC]

    @property
    def supported_bit_rates(self) -> list[AudioBitRates]:
        """Return a list of supported bit rates."""
        return [AudioBitRates.BITRATE_8, AudioBitRates.BITRATE_16, AudioBitRates.BITRATE_24]

    @property
    def supported_sample_rates(self) -> list[AudioSampleRates]:
        """Return a list of supported sample rates."""
        return [AudioSampleRates.SAMPLERATE_8000, AudioSampleRates.SAMPLERATE_16000, AudioSampleRates.SAMPLERATE_22050, AudioSampleRates.SAMPLERATE_44100, AudioSampleRates.SAMPLERATE_48000]

    @property
    def supported_channels(self) -> list[AudioChannels]:
        """Return a list of supported channels."""
        return [AudioChannels.CHANNEL_MONO, AudioChannels.CHANNEL_STEREO]

    async def async_process_audio(
        self, metadata: SpeechMetadata, stream: Any
    ) -> SpeechResult:
        """Process audio stream and return speech result."""
        try:
            _LOGGER.info("Processing audio with Neural STT")
            
            # Read audio data from stream
            audio_data = await self._read_audio_stream(stream)
            
            if not audio_data:
                _LOGGER.error("No audio data received")
                return SpeechResult("", SpeechResultState.ERROR)
            
            # Send audio to OpenRouter API
            text = await self._transcribe_audio(audio_data, metadata.language)
            
            if text:
                _LOGGER.info("Transcription successful: %s", text)
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
        try:
            while chunk := await stream.read(4096):
                audio_data += chunk
        except Exception as e:
            _LOGGER.error("Error reading audio stream: %s", e)
            return b""
        
        return audio_data

    async def _transcribe_audio(self, audio_data: bytes, language: str) -> str:
        """Transcribe audio using the audio use case."""
        try:
            # Setup dependencies
            await setup_dependencies()
            
            try:
                # Get audio use case
                audio_use_case = get_audio_use_case()
                
                # Transcribe audio using the use case
                transcription = await audio_use_case.transcribe_audio(audio_data, language)
                
                return transcription
                
            finally:
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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> bool:
    """Set up STT from a config entry."""
    stt_config = hass.data.get(DOMAIN, {}).get("stt_config", {})
    
    # Create and register the STT provider
    provider = await async_get_engine(hass, stt_config)
    async_register_provider(hass, provider)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload STT config entry."""
    # Unregister the STT provider
    async_unregister_provider(hass, DOMAIN)
    
    return True


async def async_get_engine(
    hass: HomeAssistant, config: dict[str, Any] | None = None
) -> NeuralSTTProvider:
    """Set up Neural STT provider."""
    if config is None:
        config = {}
    
    return NeuralSTTProvider(hass, config)
