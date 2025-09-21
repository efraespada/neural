"""AI client for OpenRouter integration."""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from io import BytesIO

import aiohttp
import openai

from .base_client import BaseClient

_LOGGER = logging.getLogger(__name__)


class AIClient(BaseClient):
    """AI client for OpenRouter integration."""

    def __init__(self, ai_url: str, ai_model: str, api_key: str, stt_model: str, stt_api_key: str) -> None:
        """Initialize the AI client."""
        super().__init__()
        self._ai_url = ai_url
        self._ai_model = ai_model
        self._api_key = api_key
        self.stt_model = stt_model
        self._stt_api_key = stt_api_key
        self._whisper_client: Optional[openai.OpenAI] = None
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}" if api_key else None
        }

    async def connect(self) -> None:
        """Connect to the OpenRouter service."""
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            # Test connection to OpenRouter
            await self._test_connection()
            _LOGGER.info("Connected to OpenRouter at %s", self._ai_url)
            
        except Exception as e:
            _LOGGER.error("Failed to connect to OpenRouter: %s", e)
            raise Exception(f"Failed to connect to OpenRouter: {e}") from e

    async def _test_connection(self) -> bool:
        """Test connection to OpenRouter service."""
        try:
            if not self._api_key:
                _LOGGER.error("OpenRouter API key is required")
                return False
                
            async with self._session.get(
                f"{self._ai_url}/models",
                headers=self._headers
            ) as response:
                if response.status == 200:
                    return True
                elif response.status == 401:
                    _LOGGER.error("OpenRouter authentication failed - check API key")
                    return False
                else:
                    _LOGGER.error("OpenRouter service returned status %s", response.status)
                    return False
        except Exception as e:
            _LOGGER.error("Failed to test OpenRouter connection: %s", e)
            return False

    async def is_model_ready(self) -> bool:
        """Check if the AI model is available on OpenRouter."""
        if not self._session or not self._api_key:
            return False
            
        try:
            async with self._session.get(
                f"{self._ai_url}/models",
                headers=self._headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("data", [])
                    # Check if our model is available
                    model_names = [model.get("id", "") for model in models]
                    return self._ai_model in model_names
                else:
                    _LOGGER.error("OpenRouter models check failed with status %s", response.status)
                    return False
        except Exception as e:
            _LOGGER.error("Failed to check if model is ready: %s", e)
            return False

    async def send_message(self, message: str, model: Optional[str] = None) -> str:
        """Send a message to the AI and get response."""
        if not self._session:
            raise Exception("Client not connected")

        if not self._api_key:
            raise Exception("OpenRouter API key is required")

        model_to_use = model or self._ai_model
        
        # Check if model is available
        if not await self.is_model_ready():
            raise Exception(f"Model {model_to_use} is not available on OpenRouter")
        
        try:
            payload = {
                "model": model_to_use,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "stream": False,
                "temperature": 0.7,
                "max_tokens": 4000,  # Increased for better responses
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            _LOGGER.debug("Sending prompt to OpenRouter model %s: %s", model_to_use, message[:100] + "..." if len(message) > 100 else message)
            
            async with self._session.post(
                f"{self._ai_url}/chat/completions",
                json=payload,
                headers=self._headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    # Extract response from OpenAI-compatible format
                    choices = result.get("choices", [])
                    if choices and len(choices) > 0:
                        response_text = choices[0].get("message", {}).get("content", "")
                        _LOGGER.debug("OpenRouter response received: %s", response_text[:100] + "..." if len(response_text) > 100 else response_text)
                        return response_text
                    else:
                        _LOGGER.error("No response choices in OpenRouter result")
                        return ""
                else:
                    error_text = await response.text()
                    _LOGGER.error("OpenRouter service error: %s", error_text)
                    raise Exception(f"OpenRouter service error: {response.status}")
                    
        except Exception as e:
            _LOGGER.error("Failed to send message to OpenRouter: %s", e)
            raise Exception(f"Failed to send message to OpenRouter: {e}") from e

    async def analyze_prompt(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Send a prompt and analyze the response with additional metadata."""
        if not self._session:
            raise Exception("Client not connected")

        model_to_use = model or self._ai_model
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await self.send_message(prompt, model_to_use)
            end_time = asyncio.get_event_loop().time()
            
            return {
                "prompt": prompt,
                "response": response,
                "model": model_to_use,
                "processing_time": end_time - start_time,
                "status": "success",
                "provider": "OpenRouter"
            }
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            return {
                "prompt": prompt,
                "response": None,
                "model": model_to_use,
                "processing_time": end_time - start_time,
                "status": "error",
                "error": str(e),
                "provider": "OpenRouter"
            }

    async def get_status(self) -> Dict[str, Any]:
        """Get OpenRouter service status."""
        if not self._session:
            raise Exception("Client not connected")

        try:
            async with self._session.get(
                f"{self._ai_url}/models",
                headers=self._headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "connected",
                        "url": self._ai_url,
                        "model": self._ai_model,
                        "provider": "OpenRouter",
                        "available_models": [model.get("id", "") for model in data.get("data", [])],
                        "api_key_configured": bool(self._api_key)
                    }
                else:
                    return {
                        "status": "error",
                        "url": self._ai_url,
                        "model": self._ai_model,
                        "provider": "OpenRouter",
                        "error": f"HTTP {response.status}",
                        "api_key_configured": bool(self._api_key)
                    }
        except Exception as e:
            _LOGGER.error("Failed to get OpenRouter status: %s", e)
            return {
                "status": "error",
                "url": self._ai_url,
                "model": self._ai_model,
                "provider": "OpenRouter",
                "error": str(e),
                "api_key_configured": bool(self._api_key)
            }

    async def list_models(self) -> List[str]:
        """List available AI models on OpenRouter."""
        if not self._session:
            raise Exception("Client not connected")

        try:
            async with self._session.get(
                f"{self._ai_url}/models",
                headers=self._headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return [model.get("id", "") for model in data.get("data", [])]
                else:
                    _LOGGER.error("Failed to list OpenRouter models: HTTP %s", response.status)
                    return []
        except Exception as e:
            _LOGGER.error("Failed to list OpenRouter models: %s", e)
            return []

    def update_ai_config(self, ai_url: str = None, ai_model: str = None, api_key: str = None) -> None:
        """Update AI configuration."""
        if ai_url:
            self._ai_url = ai_url
        if ai_model:
            self._ai_model = ai_model
        if api_key:
            self._api_key = api_key
            self._headers["Authorization"] = f"Bearer {api_key}"
        _LOGGER.debug("OpenRouter client configuration updated")

    async def get_model_info(self, model_id: str = None) -> Dict[str, Any]:
        """Get detailed information about a specific model."""
        if not self._session:
            raise Exception("Client not connected")

        model_to_check = model_id or self._ai_model
        
        try:
            async with self._session.get(
                f"{self._ai_url}/models",
                headers=self._headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("data", [])
                    for model in models:
                        if model.get("id") == model_to_check:
                            return {
                                "id": model.get("id"),
                                "name": model.get("name"),
                                "description": model.get("description"),
                                "context_length": model.get("context_length"),
                                "pricing": model.get("pricing"),
                                "provider": model.get("provider", {}).get("id", "unknown")
                            }
                    return {"error": f"Model {model_to_check} not found"}
                else:
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            _LOGGER.error("Failed to get model info: %s", e)
            return {"error": str(e)}

    async def disconnect(self) -> None:
        """Disconnect from the OpenRouter service."""
        if self._session:
            await self._session.close()
            self._session = None
        if self._whisper_client:
            self._whisper_client = None
        _LOGGER.info("Disconnected from OpenRouter service")

    # Whisper methods
    async def transcribe_audio(self, audio_data: bytes, language: str = "es") -> str:
        """Transcribe audio using OpenAI Whisper."""
        try:
            if not self._whisper_client:
                if not self._stt_api_key:
                    raise ValueError("STT API key is required for audio transcription")
                self._whisper_client = openai.OpenAI(api_key=self._stt_api_key)
            
            _LOGGER.info("Transcribing audio with Whisper model: %s, language: %s", self.stt_model, language)
            
            # Create a file-like object from audio data
            audio_file = BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            # Transcribe using OpenAI Whisper
            transcription = self._whisper_client.audio.transcriptions.create(
                model=self.stt_model,
                file=audio_file,
                language=language,
                response_format="json"
            )
            
            result_text = transcription.text
            _LOGGER.info("Whisper transcription successful: %s", result_text[:50] + "..." if len(result_text) > 50 else result_text)
            
            return result_text
            
        except Exception as e:
            _LOGGER.error("Failed to transcribe audio with Whisper: %s", e)
            raise

    async def is_whisper_available(self) -> bool:
        """Check if Whisper service is available."""
        try:
            if not self._stt_api_key:
                return False
            
            if not self._whisper_client:
                self._whisper_client = openai.OpenAI(api_key=self._stt_api_key)
            
            return self._whisper_client is not None
            
        except Exception as e:
            _LOGGER.error("Whisper service not available: %s", e)
            return False

    async def get_whisper_supported_languages(self) -> List[str]:
        """Get list of supported languages for Whisper."""
        return [
            "es",  # Spanish
            "en",  # English
            "fr",  # French
            "de",  # German
            "it",  # Italian
            "pt",  # Portuguese
            "ru",  # Russian
            "ja",  # Japanese
            "ko",  # Korean
            "zh",  # Chinese
            "ar",  # Arabic
            "hi",  # Hindi
            "nl",  # Dutch
            "sv",  # Swedish
            "no",  # Norwegian
            "da",  # Danish
            "fi",  # Finnish
            "pl",  # Polish
            "tr",  # Turkish
            "he",  # Hebrew
        ]