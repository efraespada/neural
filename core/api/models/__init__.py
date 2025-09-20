"""Models for Neural AI API."""

from .dto.ai_dto import AIChatDTO, AIStatusDTO, AIModelDTO
from .dto.ha_dto import HAEntityDTO, HASensorDTO, HASummaryDTO

from .domain.ai import AIChat, AIStatus, AIModel
from .domain.ha_entity import HAEntity, HASensor, HASummary

__all__ = [
    # DTOs
    "AIChatDTO",
    "AIStatusDTO", 
    "AIModelDTO",
    "HAEntityDTO",
    "HASensorDTO",
    "HASummaryDTO",
    # Domain Models
    "AIChat",
    "AIStatus",
    "AIModel",
    "HAEntity",
    "HASensor",
    "HASummary",
]
