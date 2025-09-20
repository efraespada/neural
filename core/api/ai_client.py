"""AI client for local AI integration."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp

from .base_client import BaseClient
from .exceptions import (
    MyVerisureConnectionError,
    MyVerisureError,
)

_LOGGER = logging.getLogger(__name__)


class AIClient(BaseClient):
    """AI client for local AI integration."""

    def __init__(self, ai_url: str = "http://localhost:1234", ai_model: str = "openai/gpt-oss-20b") -> None:
        """Initialize the AI client."""
        super().__init__()
        self._ai_url = ai_url
        self._ai_model = ai_model

    async def connect(self) -> None:
        """Connect to the AI service."""
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            # Test connection to AI service
            await self._test_connection()
            _LOGGER.info("Connected to AI service at %s", self._ai_url)
            
        except Exception as e:
            _LOGGER.error("Failed to connect to AI service: %s", e)
            raise MyVerisureConnectionError(f"Failed to connect to AI service: {e}") from e

    async def _test_connection(self) -> bool:
        """Test connection to AI service."""
        try:
            async with self._session.get(f"{self._ai_url}/v1/models") as response:
                if response.status == 200:
                    return True
                else:
                    _LOGGER.error("AI service returned status %s", response.status)
                    return False
        except Exception as e:
            _LOGGER.error("Failed to test AI service connection: %s", e)
            return False

    async def is_model_ready(self) -> bool:
        """Check if the AI model is ready for use. Returns True if status is 200."""
        if not self._session:
            return False
            
        try:
            async with self._session.get(f"{self._ai_url}/v1/models") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("data", [])
                    # Check if our model is available
                    model_names = [model.get("id", "") for model in models]
                    return self._ai_model in model_names
                else:
                    _LOGGER.error("AI service health check failed with status %s", response.status)
                    return False
        except Exception as e:
            _LOGGER.error("Failed to check if model is ready: %s", e)
            return False

    async def send_message(self, message: str, model: Optional[str] = None) -> str:
        """Send a message to the AI and get response."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

        model_to_use = model or self._ai_model
        
        # Check if model is ready before sending
        if not await self.is_model_ready():
            raise MyVerisureError(f"Model {model_to_use} is not ready")
        
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
                "max_tokens": 1000
            }
            
            _LOGGER.debug("Sending prompt to AI model %s: %s", model_to_use, message[:100] + "..." if len(message) > 100 else message)
            
            async with self._session.post(
                f"{self._ai_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    # Extract response from OpenAI-compatible format
                    choices = result.get("choices", [])
                    if choices and len(choices) > 0:
                        response_text = choices[0].get("message", {}).get("content", "")
                        _LOGGER.debug("AI response received: %s", response_text[:100] + "..." if len(response_text) > 100 else response_text)
                        return response_text
                    else:
                        _LOGGER.error("No response choices in AI result")
                        return ""
                else:
                    error_text = await response.text()
                    _LOGGER.error("AI service error: %s", error_text)
                    raise MyVerisureError(f"AI service error: {response.status}")
                    
        except Exception as e:
            _LOGGER.error("Failed to send message to AI: %s", e)
            raise MyVerisureError(f"Failed to send message to AI: {e}") from e

    async def analyze_prompt(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Send a prompt and analyze the response with additional metadata."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

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
                "status": "success"
            }
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            return {
                "prompt": prompt,
                "response": None,
                "model": model_to_use,
                "processing_time": end_time - start_time,
                "status": "error",
                "error": str(e)
            }

    async def get_status(self) -> Dict[str, Any]:
        """Get AI service status."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

        try:
            async with self._session.get(f"{self._ai_url}/v1/models") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "connected",
                        "url": self._ai_url,
                        "model": self._ai_model,
                        "available_models": [model.get("id", "") for model in data.get("data", [])]
                    }
                else:
                    return {
                        "status": "error",
                        "url": self._ai_url,
                        "model": self._ai_model,
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            _LOGGER.error("Failed to get AI status: %s", e)
            return {
                "status": "error",
                "url": self._ai_url,
                "model": self._ai_model,
                "error": str(e)
            }

    async def list_models(self) -> List[str]:
        """List available AI models."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

        try:
            async with self._session.get(f"{self._ai_url}/v1/models") as response:
                if response.status == 200:
                    data = await response.json()
                    return [model.get("id", "") for model in data.get("data", [])]
                else:
                    _LOGGER.error("Failed to list models: HTTP %s", response.status)
                    return []
        except Exception as e:
            _LOGGER.error("Failed to list AI models: %s", e)
            return []

    def update_ai_config(self, ai_url: str = None, ai_model: str = None) -> None:
        """Update AI configuration."""
        if ai_url:
            self._ai_url = ai_url
        if ai_model:
            self._ai_model = ai_model
        _LOGGER.debug("AI client configuration updated")

    async def disconnect(self) -> None:
        """Disconnect from the AI service."""
        if self._session:
            await self._session.close()
            self._session = None
        _LOGGER.info("Disconnected from AI service")
