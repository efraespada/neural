"""AI repository implementation."""

import logging
from datetime import datetime
from typing import List, Optional

from api.ai_client import AIClient
from api.models.domain.ai import AIStatus, AIResponse, AIModel
from repositories.interfaces.ai_repository import AIRepository

_LOGGER = logging.getLogger(__name__)


class AIRepositoryImpl(AIRepository):
    """AI repository implementation."""

    def __init__(self, ai_client: AIClient) -> None:
        """Initialize the AI repository."""
        self._ai_client = ai_client

    async def send_message(self, message: str, model: Optional[str] = None) -> AIResponse:
        """Send a message to AI and get response."""
        try:
            start_time = datetime.now()
            
            # Ensure client is connected
            if not self._ai_client._session:
                await self._ai_client.connect()
            
            # Send message to AI
            response_text = await self._ai_client.send_message(message, model)
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            return AIResponse(
                message=message,
                response=response_text,
                model=model or self._ai_client._ai_model,
                response_time=response_time,
                timestamp=end_time,
            )
            
        except Exception as e:
            _LOGGER.error("Failed to send message to AI: %s", e)
            raise

    async def get_status(self) -> AIStatus:
        """Get AI service status."""
        try:
            # Ensure client is connected
            if not self._ai_client._session:
                await self._ai_client.connect()
            
            # Get status from client
            status_data = await self._ai_client.get_status()
            
            return AIStatus(
                status=status_data.get("status", "unknown"),
                url=status_data.get("url", ""),
                model=status_data.get("model", ""),
                available_models=status_data.get("available_models", []),
                error=status_data.get("error"),
                last_updated=datetime.now(),
            )
            
        except Exception as e:
            _LOGGER.error("Failed to get AI status: %s", e)
            return AIStatus(
                status="error",
                url=self._ai_client._ai_url,
                model=self._ai_client._ai_model,
                available_models=[],
                error=str(e),
                last_updated=datetime.now(),
            )

    async def list_models(self) -> List[AIModel]:
        """List available AI models."""
        try:
            # Ensure client is connected
            if not self._ai_client._session:
                await self._ai_client.connect()
            
            # Get models from client
            model_names = await self._ai_client.list_models()
            
            return [AIModel(name=name) for name in model_names]
            
        except Exception as e:
            _LOGGER.error("Failed to list AI models: %s", e)
            return []

    async def test_connection(self) -> bool:
        """Test connection to AI service."""
        try:
            # Ensure client is connected
            if not self._ai_client._session:
                await self._ai_client.connect()
            
            # Test connection
            return await self._ai_client._test_connection()
            
        except Exception as e:
            _LOGGER.error("Failed to test AI connection: %s", e)
            return False
