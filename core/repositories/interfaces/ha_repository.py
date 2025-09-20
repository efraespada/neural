"""Home Assistant repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from api.models.domain.ha_entity import HAEntity, HAEntityState, HAEntitySummary, HAConfig


class HARepository(ABC):
    """Interface for Home Assistant repository."""

    @abstractmethod
    async def get_all_entities(self) -> List[HAEntity]:
        """Get all entities from Home Assistant."""
        pass

    @abstractmethod
    async def get_entities_by_domain(self, domain: str) -> List[HAEntity]:
        """Get entities filtered by domain."""
        pass

    @abstractmethod
    async def get_entity_state(self, entity_id: str) -> Optional[HAEntity]:
        """Get state of a specific entity."""
        pass

    @abstractmethod
    async def get_entity_summary(self) -> HAEntitySummary:
        """Get summary of all entities."""
        pass

    @abstractmethod
    async def get_sensors(self) -> List[HAEntity]:
        """Get all sensor entities."""
        pass

    @abstractmethod
    async def get_binary_sensors(self) -> List[HAEntity]:
        """Get all binary sensor entities."""
        pass

    @abstractmethod
    async def get_switches(self) -> List[HAEntity]:
        """Get all switch entities."""
        pass

    @abstractmethod
    async def get_lights(self) -> List[HAEntity]:
        """Get all light entities."""
        pass

    @abstractmethod
    async def get_entity_history(self, entity_id: str, start_time: str = None, end_time: str = None) -> List[dict]:
        """Get history for a specific entity."""
        pass

    @abstractmethod
    async def get_services(self) -> dict:
        """Get available services from Home Assistant."""
        pass

    @abstractmethod
    async def get_config(self) -> HAConfig:
        """Get Home Assistant configuration."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to Home Assistant."""
        pass
