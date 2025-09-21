"""Home Assistant repository implementation."""

import logging
from typing import Any, Dict, List, Optional

from core.api.ha_client import HAClient
from core.api.models.domain.ha_entity import HAEntity, HAEntityState, HAEntitySummary, HAConfig
from core.repositories.interfaces.ha_repository import HARepository

_LOGGER = logging.getLogger(__name__)


class HARepositoryImpl(HARepository):
    """Home Assistant repository implementation."""

    def __init__(self, ha_client: HAClient) -> None:
        """Initialize the Home Assistant repository."""
        self._ha_client = ha_client

    async def get_all_entities(self) -> List[HAEntity]:
        """Get all entities from Home Assistant."""
        try:
            # Ensure client is connected
            if not self._ha_client._session:
                await self._ha_client.connect()
            
            # Get all states from client
            states_data = await self._ha_client.get_states()
            
            entities = []
            for state_data in states_data:
                try:
                    entity = HAEntity.from_dict(state_data)
                    entities.append(entity)
                except Exception as e:
                    _LOGGER.warning("Failed to parse entity %s: %s", state_data.get("entity_id", "unknown"), e)
                    continue
            
            _LOGGER.info("Retrieved %d entities from Home Assistant", len(entities))
            return entities
            
        except Exception as e:
            _LOGGER.error("Failed to get all entities: %s", e)
            raise

    async def get_entities_by_domain(self, domain: str) -> List[HAEntity]:
        """Get entities filtered by domain."""
        try:
            # Ensure client is connected
            if not self._ha_client._session:
                await self._ha_client.connect()
            
            # Get entities by domain from client
            states_data = await self._ha_client.get_entities_by_domain(domain)
            
            entities = []
            for state_data in states_data:
                try:
                    entity = HAEntity.from_dict(state_data)
                    entities.append(entity)
                except Exception as e:
                    _LOGGER.warning("Failed to parse entity %s: %s", state_data.get("entity_id", "unknown"), e)
                    continue
            
            _LOGGER.info("Retrieved %d entities for domain %s", len(entities), domain)
            return entities
            
        except Exception as e:
            _LOGGER.error("Failed to get entities by domain %s: %s", domain, e)
            raise

    async def get_entity_state(self, entity_id: str) -> Optional[HAEntity]:
        """Get state of a specific entity."""
        try:
            # Ensure client is connected
            if not self._ha_client._session:
                await self._ha_client.connect()
            
            # Get entity state from client
            state_data = await self._ha_client.get_entity_state(entity_id)
            
            if state_data:
                entity = HAEntity.from_dict(state_data)
                return entity
            else:
                return None
            
        except Exception as e:
            _LOGGER.error("Failed to get entity state for %s: %s", entity_id, e)
            raise

    async def get_entity_summary(self) -> HAEntitySummary:
        """Get summary of all entities."""
        try:
            # Get all entities
            entities = await self.get_all_entities()
            
            # Count entities by domain
            entities_by_domain = {}
            entities_by_state = {}
            entity_states = []
            
            for entity in entities:
                # Count by domain
                domain = entity.domain
                entities_by_domain[domain] = entities_by_domain.get(domain, 0) + 1
                
                # Count by state
                state = entity.state
                entities_by_state[state] = entities_by_state.get(state, 0) + 1
                
                # Create entity state summary
                entity_state = HAEntityState(
                    entity_id=entity.entity_id,
                    state=entity.state,
                    friendly_name=entity.friendly_name or entity.object_id,
                    domain=entity.domain,
                    last_updated=entity.last_updated,
                    unit_of_measurement=entity.unit_of_measurement,
                    device_class=entity.device_class,
                )
                entity_states.append(entity_state)
            
            summary = HAEntitySummary(
                total_entities=len(entities),
                entities_by_domain=entities_by_domain,
                entities_by_state=entities_by_state,
                last_updated=max([entity.last_updated for entity in entities]) if entities else None,
                entities=entity_states,
            )
            
            _LOGGER.info("Created entity summary with %d entities", len(entities))
            return summary
            
        except Exception as e:
            _LOGGER.error("Failed to get entity summary: %s", e)
            raise

    async def get_sensors(self) -> List[HAEntity]:
        """Get all sensor entities."""
        return await self.get_entities_by_domain("sensor")

    async def get_binary_sensors(self) -> List[HAEntity]:
        """Get all binary sensor entities."""
        return await self.get_entities_by_domain("binary_sensor")

    async def get_switches(self) -> List[HAEntity]:
        """Get all switch entities."""
        return await self.get_entities_by_domain("switch")

    async def get_lights(self) -> List[HAEntity]:
        """Get all light entities."""
        return await self.get_entities_by_domain("light")

    async def get_entity_history(self, entity_id: str, start_time: str = None, end_time: str = None) -> List[dict]:
        """Get history for a specific entity."""
        try:
            # Ensure client is connected
            if not self._ha_client._session:
                await self._ha_client.connect()
            
            # Get entity history from client
            history = await self._ha_client.get_entity_history(entity_id, start_time, end_time)
            
            _LOGGER.info("Retrieved history for entity %s", entity_id)
            return history
            
        except Exception as e:
            _LOGGER.error("Failed to get entity history for %s: %s", entity_id, e)
            raise

    async def get_services(self) -> dict:
        """Get available services from Home Assistant."""
        try:
            # Ensure client is connected
            if not self._ha_client._session:
                await self._ha_client.connect()
            
            # Get services from client
            services = await self._ha_client.get_services()
            
            _LOGGER.info("Retrieved services from Home Assistant")
            return services
            
        except Exception as e:
            _LOGGER.error("Failed to get services: %s", e)
            raise

    async def get_config(self) -> HAConfig:
        """Get Home Assistant configuration."""
        try:
            # Ensure client is connected
            if not self._ha_client._session:
                await self._ha_client.connect()
            
            # Get config from client
            config_data = await self._ha_client.get_config()
            
            config = HAConfig.from_dict(config_data)
            
            _LOGGER.info("Retrieved Home Assistant configuration")
            return config
            
        except Exception as e:
            _LOGGER.error("Failed to get config: %s", e)
            raise

    async def test_connection(self) -> bool:
        """Test connection to Home Assistant."""
        try:
            # Use the public test_connection method
            return await self._ha_client.test_connection()
            
        except Exception as e:
            _LOGGER.error("Failed to test Home Assistant connection: %s", e)
            return False

    async def get_complete_info(self) -> Dict[str, Any]:
        """Get complete information from Home Assistant."""
        try:
            # Ensure client is connected
            if not self._ha_client._session:
                await self._ha_client.connect()
            
            # Get complete information
            complete_info = await self._ha_client.get_complete_info()
            
            _LOGGER.info("Retrieved complete information from Home Assistant")
            return complete_info
            
        except Exception as e:
            _LOGGER.error("Failed to get complete information: %s", e)
            raise

    async def call_service(self, domain: str, service: str, entity_id: str = None, service_data: dict = None) -> dict:
        """Call a service on Home Assistant."""
        try:
            # Ensure client is connected
            if not self._ha_client._session:
                await self._ha_client.connect()
            
            # Use the HA client to call the service
            result = await self._ha_client.call_service(domain, service, entity_id, service_data)
            
            _LOGGER.info("Service call successful: %s.%s", domain, service)
            return result
                
        except Exception as e:
            _LOGGER.error("Failed to call service %s.%s: %s", domain, service, e)
            raise
