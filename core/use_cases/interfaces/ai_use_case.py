"""AI use case interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from api.models.domain.ai import AIStatus, AIResponse, AIModel


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
