"""Unit tests for Home Assistant repository interface."""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from core.api.models.domain.ha_entity import HAEntity, HAEntityState, HAEntitySummary, HAConfig
from core.repositories.interfaces.ha_repository import HARepository
from core.repositories.implementations.ha_repository_impl import HARepositoryImpl


class TestHARepositoryInterface:
    """Test Home Assistant repository interface behavior."""

    @pytest.fixture
    def mock_ha_client(self):
        """Create mock HA client."""
        return AsyncMock()

    @pytest.fixture
    def ha_repository(self, mock_ha_client):
        """Create HA repository with mocked client."""
        return HARepositoryImpl(mock_ha_client)

    @pytest.fixture
    def sample_entity_data(self):
        """Create sample entity data."""
        return {
            "entity_id": "sensor.temperature",
            "state": "23.5",
            "attributes": {
                "unit_of_measurement": "°C",
                "friendly_name": "Temperature",
                "device_class": "temperature"
            },
            "last_changed": "2023-01-01T12:00:00Z",
            "last_updated": "2023-01-01T12:00:00Z",
            "context": {"id": "test"}
        }

    @pytest.fixture
    def sample_entities_data(self, sample_entity_data):
        """Create sample entities data."""
        entity2_data = {
            "entity_id": "light.living_room",
            "state": "on",
            "attributes": {"friendly_name": "Living Room Light"},
            "last_changed": "2023-01-01T12:00:00Z",
            "last_updated": "2023-01-01T12:00:00Z",
            "context": {"id": "test2"}
        }
        return [sample_entity_data, entity2_data]

    @pytest.mark.asyncio
    async def test_get_all_entities_success(self, ha_repository, mock_ha_client, sample_entities_data):
        """Test successful retrieval of all entities."""
        # Arrange
        mock_ha_client.get_states.return_value = sample_entities_data

        # Act
        result = await ha_repository.get_all_entities()

        # Assert
        assert len(result) == 2
        assert all(isinstance(entity, HAEntity) for entity in result)
        assert result[0].entity_id == "sensor.temperature"
        assert result[1].entity_id == "light.living_room"
        mock_ha_client.get_states.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_entities_client_exception(self, ha_repository, mock_ha_client):
        """Test get all entities when client raises exception."""
        # Arrange
        mock_ha_client.get_states.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ha_repository.get_all_entities()

    @pytest.mark.asyncio
    async def test_get_entities_by_domain_success(self, ha_repository, mock_ha_client, sample_entity_data):
        """Test successful retrieval of entities by domain."""
        # Arrange
        domain = "sensor"
        entities_data = [sample_entity_data]
        mock_ha_client.get_entities_by_domain.return_value = entities_data

        # Act
        result = await ha_repository.get_entities_by_domain(domain)

        # Assert
        assert len(result) == 1
        assert result[0].domain == "sensor"
        assert result[0].entity_id == "sensor.temperature"
        mock_ha_client.get_entities_by_domain.assert_called_once_with(domain)

    @pytest.mark.asyncio
    async def test_get_entities_by_domain_client_exception(self, ha_repository, mock_ha_client):
        """Test get entities by domain when client raises exception."""
        # Arrange
        domain = "sensor"
        mock_ha_client.get_entities_by_domain.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ha_repository.get_entities_by_domain(domain)

    @pytest.mark.asyncio
    async def test_get_entity_state_success(self, ha_repository, mock_ha_client, sample_entity_data):
        """Test successful retrieval of entity state."""
        # Arrange
        entity_id = "sensor.temperature"
        mock_ha_client.get_entity_state.return_value = sample_entity_data

        # Act
        result = await ha_repository.get_entity_state(entity_id)

        # Assert
        assert isinstance(result, HAEntity)
        assert result.entity_id == entity_id
        assert result.state == "23.5"
        mock_ha_client.get_entity_state.assert_called_once_with(entity_id)

    @pytest.mark.asyncio
    async def test_get_entity_state_not_found(self, ha_repository, mock_ha_client):
        """Test entity state retrieval when entity not found."""
        # Arrange
        entity_id = "sensor.nonexistent"
        mock_ha_client.get_entity_state.return_value = None

        # Act
        result = await ha_repository.get_entity_state(entity_id)

        # Assert
        assert result is None
        mock_ha_client.get_entity_state.assert_called_once_with(entity_id)

    @pytest.mark.asyncio
    async def test_get_entity_state_client_exception(self, ha_repository, mock_ha_client):
        """Test entity state retrieval when client raises exception."""
        # Arrange
        entity_id = "sensor.temperature"
        mock_ha_client.get_entity_state.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ha_repository.get_entity_state(entity_id)

    @pytest.mark.asyncio
    async def test_get_entity_summary_success(self, ha_repository, mock_ha_client):
        """Test successful retrieval of entity summary."""
        # Arrange
        summary_data = {
            "total_entities": 2,
            "entities_by_domain": {"sensor": 1, "light": 1},
            "entities_by_state": {"23.5": 1, "on": 1},
            "last_updated": "2023-01-01T12:00:00Z",
            "entities": [
                {
                    "entity_id": "sensor.temperature",
                    "state": "23.5",
                    "friendly_name": "Temperature",
                    "domain": "sensor",
                    "last_updated": "2023-01-01T12:00:00Z"
                }
            ]
        }
        # get_entity_summary calls get_all_entities which calls get_states
        mock_ha_client.get_states.return_value = [
            {
                "entity_id": "sensor.temperature",
                "state": "23.5",
                "attributes": {"unit_of_measurement": "°C", "friendly_name": "Temperature"},
                "last_changed": "2023-01-01T12:00:00Z",
                "last_updated": "2023-01-01T12:00:00Z",
                "context": {"id": "test"}
            }
        ]

        # Act
        result = await ha_repository.get_entity_summary()

        # Assert
        assert isinstance(result, HAEntitySummary)
        assert result.total_entities == 1
        assert result.entities_by_domain == {"sensor": 1}
        assert len(result.entities) == 1
        mock_ha_client.get_states.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_entity_summary_client_exception(self, ha_repository, mock_ha_client):
        """Test entity summary retrieval when client raises exception."""
        # Arrange
        mock_ha_client.get_states.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ha_repository.get_entity_summary()

    @pytest.mark.asyncio
    async def test_get_sensors_success(self, ha_repository, mock_ha_client, sample_entity_data):
        """Test successful retrieval of sensors."""
        # Arrange
        sensors_data = [sample_entity_data]
        mock_ha_client.get_entities_by_domain.return_value = sensors_data

        # Act
        result = await ha_repository.get_sensors()

        # Assert
        assert len(result) == 1
        assert result[0].domain == "sensor"
        assert result[0].entity_id == "sensor.temperature"
        mock_ha_client.get_entities_by_domain.assert_called_once_with("sensor")

    @pytest.mark.asyncio
    async def test_get_sensors_client_exception(self, ha_repository, mock_ha_client):
        """Test sensors retrieval when client raises exception."""
        # Arrange
        mock_ha_client.get_entities_by_domain.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ha_repository.get_sensors()

    @pytest.mark.asyncio
    async def test_get_binary_sensors_success(self, ha_repository, mock_ha_client):
        """Test successful retrieval of binary sensors."""
        # Arrange
        binary_sensor_data = {
            "entity_id": "binary_sensor.motion",
            "state": "on",
            "attributes": {"friendly_name": "Motion Sensor"},
            "last_changed": "2023-01-01T12:00:00Z",
            "last_updated": "2023-01-01T12:00:00Z",
            "context": {"id": "test"}
        }
        binary_sensors_data = [binary_sensor_data]
        mock_ha_client.get_entities_by_domain.return_value = binary_sensors_data

        # Act
        result = await ha_repository.get_binary_sensors()

        # Assert
        assert len(result) == 1
        assert result[0].domain == "binary_sensor"
        assert result[0].entity_id == "binary_sensor.motion"
        mock_ha_client.get_entities_by_domain.assert_called_once_with("binary_sensor")

    @pytest.mark.asyncio
    async def test_get_binary_sensors_client_exception(self, ha_repository, mock_ha_client):
        """Test binary sensors retrieval when client raises exception."""
        # Arrange
        mock_ha_client.get_entities_by_domain.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ha_repository.get_binary_sensors()

    @pytest.mark.asyncio
    async def test_get_switches_success(self, ha_repository, mock_ha_client):
        """Test successful retrieval of switches."""
        # Arrange
        switch_data = {
            "entity_id": "switch.living_room",
            "state": "on",
            "attributes": {"friendly_name": "Living Room Switch"},
            "last_changed": "2023-01-01T12:00:00Z",
            "last_updated": "2023-01-01T12:00:00Z",
            "context": {"id": "test"}
        }
        switches_data = [switch_data]
        mock_ha_client.get_entities_by_domain.return_value = switches_data

        # Act
        result = await ha_repository.get_switches()

        # Assert
        assert len(result) == 1
        assert result[0].domain == "switch"
        assert result[0].entity_id == "switch.living_room"
        mock_ha_client.get_entities_by_domain.assert_called_once_with("switch")

    @pytest.mark.asyncio
    async def test_get_switches_client_exception(self, ha_repository, mock_ha_client):
        """Test switches retrieval when client raises exception."""
        # Arrange
        mock_ha_client.get_entities_by_domain.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ha_repository.get_switches()

    @pytest.mark.asyncio
    async def test_get_lights_success(self, ha_repository, mock_ha_client):
        """Test successful retrieval of lights."""
        # Arrange
        light_data = {
            "entity_id": "light.living_room",
            "state": "on",
            "attributes": {"friendly_name": "Living Room Light"},
            "last_changed": "2023-01-01T12:00:00Z",
            "last_updated": "2023-01-01T12:00:00Z",
            "context": {"id": "test"}
        }
        lights_data = [light_data]
        mock_ha_client.get_entities_by_domain.return_value = lights_data

        # Act
        result = await ha_repository.get_lights()

        # Assert
        assert len(result) == 1
        assert result[0].domain == "light"
        assert result[0].entity_id == "light.living_room"
        mock_ha_client.get_entities_by_domain.assert_called_once_with("light")

    @pytest.mark.asyncio
    async def test_get_lights_client_exception(self, ha_repository, mock_ha_client):
        """Test lights retrieval when client raises exception."""
        # Arrange
        mock_ha_client.get_entities_by_domain.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ha_repository.get_lights()

    @pytest.mark.asyncio
    async def test_get_entity_history_success(self, ha_repository, mock_ha_client):
        """Test successful retrieval of entity history."""
        # Arrange
        entity_id = "sensor.temperature"
        start_time = "2023-01-01T00:00:00Z"
        end_time = "2023-01-01T23:59:59Z"
        history_data = [
            {"state": "23.5", "last_changed": "2023-01-01T12:00:00Z"},
            {"state": "24.0", "last_changed": "2023-01-01T13:00:00Z"}
        ]
        mock_ha_client.get_entity_history.return_value = history_data

        # Act
        result = await ha_repository.get_entity_history(entity_id, start_time, end_time)

        # Assert
        assert result == history_data
        assert len(result) == 2
        mock_ha_client.get_entity_history.assert_called_once_with(entity_id, start_time, end_time)

    @pytest.mark.asyncio
    async def test_get_entity_history_without_times(self, ha_repository, mock_ha_client):
        """Test entity history retrieval without time parameters."""
        # Arrange
        entity_id = "sensor.temperature"
        history_data = [{"state": "23.5", "last_changed": "2023-01-01T12:00:00Z"}]
        mock_ha_client.get_entity_history.return_value = history_data

        # Act
        result = await ha_repository.get_entity_history(entity_id)

        # Assert
        assert result == history_data
        mock_ha_client.get_entity_history.assert_called_once_with(entity_id, None, None)

    @pytest.mark.asyncio
    async def test_get_entity_history_client_exception(self, ha_repository, mock_ha_client):
        """Test entity history retrieval when client raises exception."""
        # Arrange
        entity_id = "sensor.temperature"
        mock_ha_client.get_entity_history.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ha_repository.get_entity_history(entity_id)

    @pytest.mark.asyncio
    async def test_get_services_success(self, ha_repository, mock_ha_client):
        """Test successful retrieval of services."""
        # Arrange
        services_data = {
            "light": {
                "turn_on": {"description": "Turn on light"},
                "turn_off": {"description": "Turn off light"}
            },
            "switch": {
                "turn_on": {"description": "Turn on switch"},
                "turn_off": {"description": "Turn off switch"}
            }
        }
        mock_ha_client.get_services.return_value = services_data

        # Act
        result = await ha_repository.get_services()

        # Assert
        assert result == services_data
        assert "light" in result
        assert "switch" in result
        mock_ha_client.get_services.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_services_client_exception(self, ha_repository, mock_ha_client):
        """Test services retrieval when client raises exception."""
        # Arrange
        mock_ha_client.get_services.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ha_repository.get_services()

    @pytest.mark.asyncio
    async def test_get_config_success(self, ha_repository, mock_ha_client):
        """Test successful retrieval of configuration."""
        # Arrange
        config_data = {
            "version": "2023.1.0",
            "location_name": "Home",
            "time_zone": "Europe/Madrid",
            "unit_system": {"length": "km", "mass": "kg"},
            "components": ["light", "sensor"],
            "config_dir": "/config",
            "whitelist_external_dirs": [],
            "allowlist_external_dirs": [],
            "allowlist_external_urls": [],
            "version_info": {"version": "2023.1.0"}
        }
        mock_ha_client.get_config.return_value = config_data

        # Act
        result = await ha_repository.get_config()

        # Assert
        assert isinstance(result, HAConfig)
        assert result.version == "2023.1.0"
        assert result.location_name == "Home"
        assert result.time_zone == "Europe/Madrid"
        mock_ha_client.get_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_config_client_exception(self, ha_repository, mock_ha_client):
        """Test config retrieval when client raises exception."""
        # Arrange
        mock_ha_client.get_config.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ha_repository.get_config()

    @pytest.mark.asyncio
    async def test_test_connection_success(self, ha_repository, mock_ha_client):
        """Test successful connection test."""
        # Arrange
        mock_ha_client.test_connection.return_value = True

        # Act
        result = await ha_repository.test_connection()

        # Assert
        assert result is True
        mock_ha_client.test_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, ha_repository, mock_ha_client):
        """Test connection test failure."""
        # Arrange
        mock_ha_client.test_connection.return_value = False

        # Act
        result = await ha_repository.test_connection()

        # Assert
        assert result is False
        mock_ha_client.test_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_client_exception(self, ha_repository, mock_ha_client):
        """Test connection test when client raises exception."""
        # Arrange
        mock_ha_client.test_connection.side_effect = Exception("Client error")

        # Act
        result = await ha_repository.test_connection()

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_get_complete_info_success(self, ha_repository, mock_ha_client):
        """Test successful retrieval of complete information."""
        # Arrange
        complete_info_data = {
            "entities": [{"entity_id": "sensor.temperature", "state": "23.5"}],
            "services": {"light": {"turn_on": {}}},
            "config": {"version": "2023.1.0"}
        }
        mock_ha_client.get_complete_info.return_value = complete_info_data

        # Act
        result = await ha_repository.get_complete_info()

        # Assert
        assert result == complete_info_data
        assert "entities" in result
        assert "services" in result
        assert "config" in result
        mock_ha_client.get_complete_info.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_complete_info_client_exception(self, ha_repository, mock_ha_client):
        """Test complete info retrieval when client raises exception."""
        # Arrange
        mock_ha_client.get_complete_info.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ha_repository.get_complete_info()
