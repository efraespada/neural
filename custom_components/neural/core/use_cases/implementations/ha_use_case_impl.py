"""Home Assistant use case implementation."""

import logging
from typing import Any, Dict, List, Optional

from ...api.models.domain.ha_entity import HAEntity, HAEntitySummary, HAConfig
from ...repositories.interfaces.ha_repository import HARepository
from ..interfaces.ha_use_case import HAUseCase

_LOGGER = logging.getLogger(__name__)


class HAUseCaseImpl(HAUseCase):
    """Home Assistant use case implementation."""

    def __init__(self, ha_repository: HARepository) -> None:
        """Initialize the Home Assistant use case."""
        self._ha_repository = ha_repository

    async def get_all_entities(self) -> List[HAEntity]:
        """Get all entities from Home Assistant."""
        try:
            _LOGGER.info("Getting all entities from Home Assistant")
            
            # Get entities through repository
            entities = await self._ha_repository.get_all_entities()
            
            _LOGGER.info("Retrieved %d entities from Home Assistant", len(entities))
            return entities
            
        except Exception as e:
            _LOGGER.error("Failed to get all entities: %s", e)
            raise

    async def get_entities_by_domain(self, domain: str) -> List[HAEntity]:
        """Get entities filtered by domain."""
        try:
            _LOGGER.info("Getting entities for domain %s", domain)
            
            # Get entities through repository
            entities = await self._ha_repository.get_entities_by_domain(domain)
            
            _LOGGER.info("Retrieved %d entities for domain %s", len(entities), domain)
            return entities
            
        except Exception as e:
            _LOGGER.error("Failed to get entities by domain %s: %s", domain, e)
            raise

    async def get_entity_state(self, entity_id: str) -> Optional[HAEntity]:
        """Get state of a specific entity."""
        try:
            _LOGGER.info("Getting state for entity %s", entity_id)
            
            # Get entity state through repository
            entity = await self._ha_repository.get_entity_state(entity_id)
            
            if entity:
                _LOGGER.info("Retrieved state for entity %s: %s", entity_id, entity.state)
            else:
                _LOGGER.warning("Entity %s not found", entity_id)
            
            return entity
            
        except Exception as e:
            _LOGGER.error("Failed to get entity state for %s: %s", entity_id, e)
            raise

    async def get_entity_summary(self) -> HAEntitySummary:
        """Get summary of all entities."""
        try:
            _LOGGER.info("Getting entity summary from Home Assistant")
            
            # Get entity summary through repository
            summary = await self._ha_repository.get_entity_summary()
            
            _LOGGER.info("Retrieved entity summary: %d total entities, %d domains", 
                        summary.total_entities, len(summary.entities_by_domain))
            return summary
            
        except Exception as e:
            _LOGGER.error("Failed to get entity summary: %s", e)
            raise

    async def get_sensors(self) -> List[HAEntity]:
        """Get all sensor entities."""
        try:
            _LOGGER.info("Getting sensor entities from Home Assistant")
            
            # Get sensors through repository
            sensors = await self._ha_repository.get_sensors()
            
            _LOGGER.info("Retrieved %d sensor entities", len(sensors))
            return sensors
            
        except Exception as e:
            _LOGGER.error("Failed to get sensors: %s", e)
            raise

    async def get_binary_sensors(self) -> List[HAEntity]:
        """Get all binary sensor entities."""
        try:
            _LOGGER.info("Getting binary sensor entities from Home Assistant")
            
            # Get binary sensors through repository
            binary_sensors = await self._ha_repository.get_binary_sensors()
            
            _LOGGER.info("Retrieved %d binary sensor entities", len(binary_sensors))
            return binary_sensors
            
        except Exception as e:
            _LOGGER.error("Failed to get binary sensors: %s", e)
            raise

    async def get_switches(self) -> List[HAEntity]:
        """Get all switch entities."""
        try:
            _LOGGER.info("Getting switch entities from Home Assistant")
            
            # Get switches through repository
            switches = await self._ha_repository.get_switches()
            
            _LOGGER.info("Retrieved %d switch entities", len(switches))
            return switches
            
        except Exception as e:
            _LOGGER.error("Failed to get switches: %s", e)
            raise

    async def get_lights(self) -> List[HAEntity]:
        """Get all light entities."""
        try:
            _LOGGER.info("Getting light entities from Home Assistant")
            
            # Get lights through repository
            lights = await self._ha_repository.get_lights()
            
            _LOGGER.info("Retrieved %d light entities", len(lights))
            return lights
            
        except Exception as e:
            _LOGGER.error("Failed to get lights: %s", e)
            raise

    async def get_entity_history(self, entity_id: str, start_time: str = None, end_time: str = None) -> List[dict]:
        """Get history for a specific entity."""
        try:
            _LOGGER.info("Getting history for entity %s", entity_id)
            
            # Get entity history through repository
            history = await self._ha_repository.get_entity_history(entity_id, start_time, end_time)
            
            _LOGGER.info("Retrieved %d history entries for entity %s", len(history), entity_id)
            return history
            
        except Exception as e:
            _LOGGER.error("Failed to get entity history for %s: %s", entity_id, e)
            raise

    async def get_services(self) -> dict:
        """Get available services from Home Assistant."""
        try:
            _LOGGER.info("Getting services from Home Assistant")
            
            # Get services through repository
            services = await self._ha_repository.get_services()
            
            _LOGGER.info("Retrieved services from Home Assistant")
            return services
            
        except Exception as e:
            _LOGGER.error("Failed to get services: %s", e)
            raise

    async def get_config(self) -> HAConfig:
        """Get Home Assistant configuration."""
        try:
            _LOGGER.info("Getting Home Assistant configuration")
            
            # Get config through repository
            config = await self._ha_repository.get_config()
            
            _LOGGER.info("Retrieved Home Assistant configuration: %s", config.version)
            return config
            
        except Exception as e:
            _LOGGER.error("Failed to get config: %s", e)
            raise

    async def test_connection(self) -> bool:
        """Test connection to Home Assistant."""
        try:
            _LOGGER.info("Testing connection to Home Assistant")
            
            # Test connection through repository
            is_connected = await self._ha_repository.test_connection()
            
            _LOGGER.info("Home Assistant connection test: %s", "success" if is_connected else "failed")
            return is_connected
            
        except Exception as e:
            _LOGGER.error("Failed to test Home Assistant connection: %s", e)
            return False

    async def get_complete_info(self) -> Dict[str, Any]:
        """Get complete information from Home Assistant."""
        try:
            _LOGGER.info("Getting complete information from Home Assistant")
            
            # Get complete information through repository
            complete_info = await self._ha_repository.get_complete_info()
            
            _LOGGER.info("Retrieved complete information from Home Assistant")
            return complete_info
            
        except Exception as e:
            _LOGGER.error("Failed to get complete information: %s", e)
            raise
