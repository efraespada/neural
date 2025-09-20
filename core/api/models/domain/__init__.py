"""Domain models for Neural AI API."""

from .ai import (
    AIStatus,
    AIResponse,
    AIModel,
)
from .ha_entity import (
    HAEntity,
    HAEntityState,
    HAEntitySummary,
    HAConfig,
)

__all__ = [
    "AIStatus",
    "AIResponse",
    "AIModel",
    "HAEntity",
    "HAEntityState",
    "HAEntitySummary",
    "HAConfig",
]
