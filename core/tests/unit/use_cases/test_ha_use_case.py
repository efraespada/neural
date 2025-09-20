"""Unit tests for Home Assistant use case interface."""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from core.api.models.domain.ha_entity import HAEntity, HAEntityState, HAEntitySummary, HAConfig
from core.use_cases.interfaces.ha_use_case import HAUseCase
from core.use_cases.implementations.ha_use_case_impl import HAUseCaseImpl


class TestHAUseCaseInterface:
    """Test Home Assistant use case interface behavior."""

    @pytest.fixture
    def mock_ha_repository(self):
        """Create mock HA repository."""
        return AsyncMock()

    @pytest.fixture
    def ha_use_case(self, mock_ha_repository):
        """Create HA use case with mocked repository."""
        return HAUseCaseImpl(mock_ha_repository)

    @pytest.fixture
    def sample_entity(self):
        """Create sample HA entity."""
        return HAEntity(
            entity_id="sensor.temperature",
            state="23.5",
            attributes={"unit_of_measurement": "°C", "friendly_name": "Temperature"},
            last_changed=datetime.now(),
            last_updated=datetime.now(),
            context={"id": "test"},
            domain="sensor",
            object_id="temperature",
            friendly_name="Temperature",
            unit_of_measurement="°C",
            device_class="temperature"
        )

    @pytest.fixture
    def sample_entities(self, sample_entity):
        """Create sample HA entities list."""
        entity2 = HAEntity(
            entity_id="light.living_room",
            state="on",
            attributes={"friendly_name": "Living Room Light"},
            last_changed=datetime.now(),
            last_updated=datetime.now(),
            context={"id": "test2"},
            domain="light",
            object_id="living_room",
            friendly_name="Living Room Light"
        )
        return [sample_entity, entity2]

    @pytest.mark.asyncio
    async def test_get_all_entities_success(self, ha_use_case, mock_ha_repository, sample_entities):
        """Test successful retrieval of all entities."""
        # Arrange
        mock_ha_repository.get_all_entities.return_value = sample_entities

        # Act
        result = await ha_use_case.get_all_entities()

        # Assert
        assert result == sample_entities
        assert len(result) == 2
        mock_ha_repository.get_all_entities.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_entities_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test get all entities when repository raises exception."""
        # Arrange
        mock_ha_repository.get_all_entities.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ha_use_case.get_all_entities()

    @pytest.mark.asyncio
    async def test_get_entities_by_domain_success(self, ha_use_case, mock_ha_repository, sample_entity):
        """Test successful retrieval of entities by domain."""
        # Arrange
        domain = "sensor"
        entities = [sample_entity]
        mock_ha_repository.get_entities_by_domain.return_value = entities

        # Act
        result = await ha_use_case.get_entities_by_domain(domain)

        # Assert
        assert result == entities
        assert len(result) == 1
        assert result[0].domain == domain
        mock_ha_repository.get_entities_by_domain.assert_called_once_with(domain)

    @pytest.mark.asyncio
    async def test_get_entities_by_domain_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test get entities by domain when repository raises exception."""
        # Arrange
        domain = "sensor"
        mock_ha_repository.get_entities_by_domain.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ha_use_case.get_entities_by_domain(domain)

    @pytest.mark.asyncio
    async def test_get_entity_state_success(self, ha_use_case, mock_ha_repository, sample_entity):
        """Test successful retrieval of entity state."""
        # Arrange
        entity_id = "sensor.temperature"
        mock_ha_repository.get_entity_state.return_value = sample_entity

        # Act
        result = await ha_use_case.get_entity_state(entity_id)

        # Assert
        assert result == sample_entity
        assert result.entity_id == entity_id
        mock_ha_repository.get_entity_state.assert_called_once_with(entity_id)

    @pytest.mark.asyncio
    async def test_get_entity_state_not_found(self, ha_use_case, mock_ha_repository):
        """Test entity state retrieval when entity not found."""
        # Arrange
        entity_id = "sensor.nonexistent"
        mock_ha_repository.get_entity_state.return_value = None

        # Act
        result = await ha_use_case.get_entity_state(entity_id)

        # Assert
        assert result is None
        mock_ha_repository.get_entity_state.assert_called_once_with(entity_id)

    @pytest.mark.asyncio
    async def test_get_entity_state_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test entity state retrieval when repository raises exception."""
        # Arrange
        entity_id = "sensor.temperature"
        mock_ha_repository.get_entity_state.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ha_use_case.get_entity_state(entity_id)

    @pytest.mark.asyncio
    async def test_get_entity_summary_success(self, ha_use_case, mock_ha_repository):
        """Test successful retrieval of entity summary."""
        # Arrange
        entity_states = [
            HAEntityState(
                entity_id="sensor.temperature",
                state="23.5",
                friendly_name="Temperature",
                domain="sensor",
                last_updated=datetime.now()
            )
        ]
        summary = HAEntitySummary(
            total_entities=1,
            entities_by_domain={"sensor": 1},
            entities_by_state={"23.5": 1},
            last_updated=datetime.now(),
            entities=entity_states
        )
        mock_ha_repository.get_entity_summary.return_value = summary

        # Act
        result = await ha_use_case.get_entity_summary()

        # Assert
        assert result == summary
        assert result.total_entities == 1
        mock_ha_repository.get_entity_summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_entity_summary_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test entity summary retrieval when repository raises exception."""
        # Arrange
        mock_ha_repository.get_entity_summary.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ha_use_case.get_entity_summary()

    @pytest.mark.asyncio
    async def test_get_sensors_success(self, ha_use_case, mock_ha_repository, sample_entity):
        """Test successful retrieval of sensors."""
        # Arrange
        sensors = [sample_entity]
        mock_ha_repository.get_sensors.return_value = sensors

        # Act
        result = await ha_use_case.get_sensors()

        # Assert
        assert result == sensors
        assert len(result) == 1
        assert result[0].domain == "sensor"
        mock_ha_repository.get_sensors.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_sensors_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test sensors retrieval when repository raises exception."""
        # Arrange
        mock_ha_repository.get_sensors.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ha_use_case.get_sensors()

    @pytest.mark.asyncio
    async def test_get_binary_sensors_success(self, ha_use_case, mock_ha_repository):
        """Test successful retrieval of binary sensors."""
        # Arrange
        binary_sensor = HAEntity(
            entity_id="binary_sensor.motion",
            state="on",
            attributes={"friendly_name": "Motion Sensor"},
            last_changed=datetime.now(),
            last_updated=datetime.now(),
            context={"id": "test"},
            domain="binary_sensor",
            object_id="motion",
            friendly_name="Motion Sensor"
        )
        binary_sensors = [binary_sensor]
        mock_ha_repository.get_binary_sensors.return_value = binary_sensors

        # Act
        result = await ha_use_case.get_binary_sensors()

        # Assert
        assert result == binary_sensors
        assert len(result) == 1
        assert result[0].domain == "binary_sensor"
        mock_ha_repository.get_binary_sensors.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_binary_sensors_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test binary sensors retrieval when repository raises exception."""
        # Arrange
        mock_ha_repository.get_binary_sensors.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ha_use_case.get_binary_sensors()

    @pytest.mark.asyncio
    async def test_get_switches_success(self, ha_use_case, mock_ha_repository):
        """Test successful retrieval of switches."""
        # Arrange
        switch = HAEntity(
            entity_id="switch.living_room",
            state="on",
            attributes={"friendly_name": "Living Room Switch"},
            last_changed=datetime.now(),
            last_updated=datetime.now(),
            context={"id": "test"},
            domain="switch",
            object_id="living_room",
            friendly_name="Living Room Switch"
        )
        switches = [switch]
        mock_ha_repository.get_switches.return_value = switches

        # Act
        result = await ha_use_case.get_switches()

        # Assert
        assert result == switches
        assert len(result) == 1
        assert result[0].domain == "switch"
        mock_ha_repository.get_switches.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_switches_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test switches retrieval when repository raises exception."""
        # Arrange
        mock_ha_repository.get_switches.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ha_use_case.get_switches()

    @pytest.mark.asyncio
    async def test_get_lights_success(self, ha_use_case, mock_ha_repository):
        """Test successful retrieval of lights."""
        # Arrange
        light = HAEntity(
            entity_id="light.living_room",
            state="on",
            attributes={"friendly_name": "Living Room Light"},
            last_changed=datetime.now(),
            last_updated=datetime.now(),
            context={"id": "test"},
            domain="light",
            object_id="living_room",
            friendly_name="Living Room Light"
        )
        lights = [light]
        mock_ha_repository.get_lights.return_value = lights

        # Act
        result = await ha_use_case.get_lights()

        # Assert
        assert result == lights
        assert len(result) == 1
        assert result[0].domain == "light"
        mock_ha_repository.get_lights.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_lights_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test lights retrieval when repository raises exception."""
        # Arrange
        mock_ha_repository.get_lights.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ha_use_case.get_lights()

    @pytest.mark.asyncio
    async def test_get_entity_history_success(self, ha_use_case, mock_ha_repository):
        """Test successful retrieval of entity history."""
        # Arrange
        entity_id = "sensor.temperature"
        start_time = "2023-01-01T00:00:00Z"
        end_time = "2023-01-01T23:59:59Z"
        history = [
            {"state": "23.5", "last_changed": "2023-01-01T12:00:00Z"},
            {"state": "24.0", "last_changed": "2023-01-01T13:00:00Z"}
        ]
        mock_ha_repository.get_entity_history.return_value = history

        # Act
        result = await ha_use_case.get_entity_history(entity_id, start_time, end_time)

        # Assert
        assert result == history
        assert len(result) == 2
        mock_ha_repository.get_entity_history.assert_called_once_with(entity_id, start_time, end_time)

    @pytest.mark.asyncio
    async def test_get_entity_history_without_times(self, ha_use_case, mock_ha_repository):
        """Test entity history retrieval without time parameters."""
        # Arrange
        entity_id = "sensor.temperature"
        history = [{"state": "23.5", "last_changed": "2023-01-01T12:00:00Z"}]
        mock_ha_repository.get_entity_history.return_value = history

        # Act
        result = await ha_use_case.get_entity_history(entity_id)

        # Assert
        assert result == history
        mock_ha_repository.get_entity_history.assert_called_once_with(entity_id, None, None)

    @pytest.mark.asyncio
    async def test_get_entity_history_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test entity history retrieval when repository raises exception."""
        # Arrange
        entity_id = "sensor.temperature"
        mock_ha_repository.get_entity_history.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ha_use_case.get_entity_history(entity_id)

    @pytest.mark.asyncio
    async def test_get_services_success(self, ha_use_case, mock_ha_repository):
        """Test successful retrieval of services."""
        # Arrange
        services = {
            "light": {
                "turn_on": {"description": "Turn on light"},
                "turn_off": {"description": "Turn off light"}
            },
            "switch": {
                "turn_on": {"description": "Turn on switch"},
                "turn_off": {"description": "Turn off switch"}
            }
        }
        mock_ha_repository.get_services.return_value = services

        # Act
        result = await ha_use_case.get_services()

        # Assert
        assert result == services
        assert "light" in result
        assert "switch" in result
        mock_ha_repository.get_services.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_services_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test services retrieval when repository raises exception."""
        # Arrange
        mock_ha_repository.get_services.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ha_use_case.get_services()

    @pytest.mark.asyncio
    async def test_get_config_success(self, ha_use_case, mock_ha_repository):
        """Test successful retrieval of configuration."""
        # Arrange
        config = HAConfig(
            version="2023.1.0",
            location_name="Home",
            time_zone="Europe/Madrid",
            unit_system={"length": "km", "mass": "kg"},
            components=["light", "sensor"],
            config_dir="/config",
            whitelist_external_dirs=[],
            allowlist_external_dirs=[],
            allowlist_external_urls=[],
            version_info={"version": "2023.1.0"}
        )
        mock_ha_repository.get_config.return_value = config

        # Act
        result = await ha_use_case.get_config()

        # Assert
        assert result == config
        assert result.version == "2023.1.0"
        mock_ha_repository.get_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_config_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test config retrieval when repository raises exception."""
        # Arrange
        mock_ha_repository.get_config.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ha_use_case.get_config()

    @pytest.mark.asyncio
    async def test_test_connection_success(self, ha_use_case, mock_ha_repository):
        """Test successful connection test."""
        # Arrange
        mock_ha_repository.test_connection.return_value = True

        # Act
        result = await ha_use_case.test_connection()

        # Assert
        assert result is True
        mock_ha_repository.test_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, ha_use_case, mock_ha_repository):
        """Test connection test failure."""
        # Arrange
        mock_ha_repository.test_connection.return_value = False

        # Act
        result = await ha_use_case.test_connection()

        # Assert
        assert result is False
        mock_ha_repository.test_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test connection test when repository raises exception."""
        # Arrange
        mock_ha_repository.test_connection.side_effect = Exception("Repository error")

        # Act
        result = await ha_use_case.test_connection()

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_get_complete_info_success(self, ha_use_case, mock_ha_repository):
        """Test successful retrieval of complete information."""
        # Arrange
        complete_info = {
            "entities": [{"entity_id": "sensor.temperature", "state": "23.5"}],
            "services": {"light": {"turn_on": {}}},
            "config": {"version": "2023.1.0"}
        }
        mock_ha_repository.get_complete_info.return_value = complete_info

        # Act
        result = await ha_use_case.get_complete_info()

        # Assert
        assert result == complete_info
        assert "entities" in result
        assert "services" in result
        assert "config" in result
        mock_ha_repository.get_complete_info.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_complete_info_repository_exception(self, ha_use_case, mock_ha_repository):
        """Test complete info retrieval when repository raises exception."""
        # Arrange
        mock_ha_repository.get_complete_info.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ha_use_case.get_complete_info()
