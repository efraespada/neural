"""AI use case implementation."""

import logging
from typing import List, Optional

from ...api.models.domain.ai import AIStatus, AIResponse
from core.repositories.interfaces.ai_repository import AIRepository
from core.use_cases.interfaces.ai_use_case import AIUseCase

_LOGGER = logging.getLogger(__name__)


class AIUseCaseImpl(AIUseCase):
    """AI use case implementation."""

    def __init__(self, ai_repository: AIRepository) -> None:
        """Initialize the AI use case."""
        self._ai_repository = ai_repository

    async def send_message(self, message: str, model: Optional[str] = None) -> AIResponse:
        """Send a message to AI and get response."""
        try:
            _LOGGER.info("Sending message to AI: %s", message[:50] + "..." if len(message) > 50 else message)
            
            # Send message through repository
            response = await self._ai_repository.send_message(message, model)
            
            _LOGGER.info("Received AI response: %s", response.response[:50] + "..." if len(response.response) > 50 else response.response)
            
            return response
            
        except Exception as e:
            _LOGGER.error("Failed to send message to AI: %s", e)
            raise

    async def get_status(self) -> AIStatus:
        """Get AI service status."""
        try:
            _LOGGER.info("Getting AI service status")
            
            # Get status through repository
            status = await self._ai_repository.get_status()
            
            _LOGGER.info("AI service status: %s", status.status)
            
            return status
            
        except Exception as e:
            _LOGGER.error("Failed to get AI status: %s", e)
            raise

    async def list_models(self) -> List[str]:
        """List available AI model names."""
        try:
            _LOGGER.info("Listing available AI models")
            
            # Get models through repository
            models = await self._ai_repository.list_models()
            
            model_names = [model.name for model in models]
            _LOGGER.info("Found %d AI models: %s", len(model_names), model_names)
            
            return model_names
            
        except Exception as e:
            _LOGGER.error("Failed to list AI models: %s", e)
            raise

    async def test_connection(self) -> bool:
        """Test connection to AI service."""
        try:
            _LOGGER.info("Testing AI service connection")
            
            # Test connection through repository
            is_connected = await self._ai_repository.test_connection()
            
            _LOGGER.info("AI service connection test: %s", "success" if is_connected else "failed")
            
            return is_connected
            
        except Exception as e:
            _LOGGER.error("Failed to test AI connection: %s", e)
            return False

    async def is_model_ready(self) -> bool:
        """Check if the AI model is ready for use."""
        try:
            _LOGGER.info("Checking if AI model is ready")
            
            # Check if model is ready through repository
            is_ready = await self._ai_repository.is_model_ready()
            
            _LOGGER.info("AI model ready status: %s", "ready" if is_ready else "not ready")
            
            return is_ready
            
        except Exception as e:
            _LOGGER.error("Failed to check if model is ready: %s", e)
            return False
