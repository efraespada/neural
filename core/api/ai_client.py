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

    def __init__(self, ai_url: str = "http://localhost:11434", ai_model: str = "llama3.2") -> None:
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
            async with self._session.get(f"{self._ai_url}/api/tags") as response:
                if response.status == 200:
                    return True
                else:
                    _LOGGER.error("AI service returned status %s", response.status)
                    return False
        except Exception as e:
            _LOGGER.error("Failed to test AI service connection: %s", e)
            return False

    async def send_message(self, message: str, model: Optional[str] = None) -> str:
        """Send a message to the AI and get response."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

        model_to_use = model or self._ai_model
        
        try:
            payload = {
                "model": model_to_use,
                "prompt": message,
                "stream": False
            }
            
            async with self._session.post(
                f"{self._ai_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
                else:
                    error_text = await response.text()
                    _LOGGER.error("AI service error: %s", error_text)
                    raise MyVerisureError(f"AI service error: {response.status}")
                    
        except Exception as e:
            _LOGGER.error("Failed to send message to AI: %s", e)
            raise MyVerisureError(f"Failed to send message to AI: {e}") from e

    async def get_status(self) -> Dict[str, Any]:
        """Get AI service status."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

        try:
            async with self._session.get(f"{self._ai_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "connected",
                        "url": self._ai_url,
                        "model": self._ai_model,
                        "available_models": [model.get("name", "") for model in data.get("models", [])]
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
            async with self._session.get(f"{self._ai_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return [model.get("name", "") for model in data.get("models", [])]
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
