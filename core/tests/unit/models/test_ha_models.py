"""Unit tests for Home Assistant domain models."""

import pytest
from datetime import datetime
from core.api.models.domain.ha_entity import (
    HAEntity, HASensor, HASummary, HAEntityState, 
    HAEntitySummary, HAConfig
)


class TestHAEntity:
    """Test HAEntity model."""

    def test_ha_entity_creation(self):
        """Test HAEntity creation with all fields."""
        # Arrange
        now = datetime.now()
        
        # Act
        entity = HAEntity(
            entity_id="sensor.temperature",
            state="23.5",
            attributes={"unit_of_measurement": "°C", "friendly_name": "Temperature"},
            last_changed=now,
            last_updated=now,
            context={"id": "test"},
            domain="sensor",
            object_id="temperature",
            friendly_name="Temperature",
            unit_of_measurement="°C",
            device_class="temperature",
            icon="mdi:thermometer"
        )
        
        # Assert
        assert entity.entity_id == "sensor.temperature"
        assert entity.state == "23.5"
        assert entity.attributes == {"unit_of_measurement": "°C", "friendly_name": "Temperature"}
        assert entity.last_changed == now
        assert entity.last_updated == now
        assert entity.context == {"id": "test"}
        assert entity.domain == "sensor"
        assert entity.object_id == "temperature"
        assert entity.friendly_name == "Temperature"
        assert entity.unit_of_measurement == "°C"
        assert entity.device_class == "temperature"
        assert entity.icon == "mdi:thermometer"

    def test_ha_entity_creation_minimal(self):
        """Test HAEntity creation with minimal fields."""
        # Arrange
        now = datetime.now()
        
        # Act
        entity = HAEntity(
            entity_id="sensor.temperature",
            state="23.5",
            attributes={},
            last_changed=now,
            last_updated=now,
            context={},
            domain="sensor",
            object_id="temperature"
        )
        
        # Assert
        assert entity.entity_id == "sensor.temperature"
        assert entity.state == "23.5"
        assert entity.domain == "sensor"
        assert entity.object_id == "temperature"
        assert entity.friendly_name is None
        assert entity.unit_of_measurement is None
        assert entity.device_class is None
        assert entity.icon is None

    def test_ha_entity_to_dict(self):
        """Test HAEntity to_dict method."""
        # Arrange
        now = datetime.now()
        entity = HAEntity(
            entity_id="sensor.temperature",
            state="23.5",
            attributes={"unit_of_measurement": "°C"},
            last_changed=now,
            last_updated=now,
            context={"id": "test"},
            domain="sensor",
            object_id="temperature",
            friendly_name="Temperature",
            unit_of_measurement="°C",
            device_class="temperature",
            icon="mdi:thermometer"
        )
        
        # Act
        result = entity.to_dict()
        
        # Assert
        assert result["entity_id"] == "sensor.temperature"
        assert result["state"] == "23.5"
        assert result["attributes"] == {"unit_of_measurement": "°C"}
        assert result["last_changed"] == now.isoformat()
        assert result["last_updated"] == now.isoformat()
        assert result["context"] == {"id": "test"}
        assert result["domain"] == "sensor"
        assert result["object_id"] == "temperature"
        assert result["friendly_name"] == "Temperature"
        assert result["unit_of_measurement"] == "°C"
        assert result["device_class"] == "temperature"
        assert result["icon"] == "mdi:thermometer"

    def test_ha_entity_from_dict(self):
        """Test HAEntity from_dict method."""
        # Arrange
        now = datetime.now()
        data = {
            "entity_id": "sensor.temperature",
            "state": "23.5",
            "attributes": {
                "unit_of_measurement": "°C", 
                "friendly_name": "Temperature",
                "device_class": "temperature",
                "icon": "mdi:thermometer"
            },
            "last_changed": now.isoformat(),
            "last_updated": now.isoformat(),
            "context": {"id": "test"}
        }
        
        # Act
        entity = HAEntity.from_dict(data)
        
        # Assert
        assert entity.entity_id == "sensor.temperature"
        assert entity.state == "23.5"
        assert entity.attributes == {
            "unit_of_measurement": "°C", 
            "friendly_name": "Temperature",
            "device_class": "temperature",
            "icon": "mdi:thermometer"
        }
        assert entity.last_changed == now
        assert entity.last_updated == now
        assert entity.context == {"id": "test"}
        assert entity.domain == "sensor"
        assert entity.object_id == "temperature"
        assert entity.friendly_name == "Temperature"
        assert entity.unit_of_measurement == "°C"
        assert entity.device_class == "temperature"
        assert entity.icon == "mdi:thermometer"

    def test_ha_entity_from_dict_with_z_suffix(self):
        """Test HAEntity from_dict with Z suffix in timestamps."""
        # Arrange
        data = {
            "entity_id": "sensor.temperature",
            "state": "23.5",
            "attributes": {"unit_of_measurement": "°C"},
            "last_changed": "2023-01-01T12:00:00Z",
            "last_updated": "2023-01-01T12:00:00Z",
            "context": {"id": "test"}
        }
        
        # Act
        entity = HAEntity.from_dict(data)
        
        # Assert
        assert entity.entity_id == "sensor.temperature"
        assert entity.state == "23.5"
        assert isinstance(entity.last_changed, datetime)
        assert isinstance(entity.last_updated, datetime)

    def test_ha_entity_from_dict_with_missing_fields(self):
        """Test HAEntity from_dict with missing fields."""
        # Arrange
        data = {
            "entity_id": "sensor.temperature",
            "state": "23.5",
            "attributes": {},
            "last_changed": "2023-01-01T12:00:00Z",
            "last_updated": "2023-01-01T12:00:00Z",
            "context": {}
        }
        
        # Act
        entity = HAEntity.from_dict(data)
        
        # Assert
        assert entity.entity_id == "sensor.temperature"
        assert entity.state == "23.5"
        assert entity.domain == "sensor"
        assert entity.object_id == "temperature"
        assert entity.friendly_name is None
        assert entity.unit_of_measurement is None
        assert entity.device_class is None
        assert entity.icon is None


class TestHASensor:
    """Test HASensor model."""

    def test_ha_sensor_creation(self):
        """Test HASensor creation with all fields."""
        # Arrange
        now = datetime.now()
        
        # Act
        sensor = HASensor(
            entity_id="sensor.temperature",
            state="23.5",
            unit_of_measurement="°C",
            device_class="temperature",
            friendly_name="Temperature",
            last_updated=now
        )
        
        # Assert
        assert sensor.entity_id == "sensor.temperature"
        assert sensor.state == "23.5"
        assert sensor.unit_of_measurement == "°C"
        assert sensor.device_class == "temperature"
        assert sensor.friendly_name == "Temperature"
        assert sensor.last_updated == now

    def test_ha_sensor_creation_minimal(self):
        """Test HASensor creation with minimal fields."""
        # Act
        sensor = HASensor(
            entity_id="sensor.temperature",
            state="23.5"
        )
        
        # Assert
        assert sensor.entity_id == "sensor.temperature"
        assert sensor.state == "23.5"
        assert sensor.unit_of_measurement is None
        assert sensor.device_class is None
        assert sensor.friendly_name is None
        assert sensor.last_updated is None

    def test_ha_sensor_to_dict(self):
        """Test HASensor to_dict method."""
        # Arrange
        now = datetime.now()
        sensor = HASensor(
            entity_id="sensor.temperature",
            state="23.5",
            unit_of_measurement="°C",
            device_class="temperature",
            friendly_name="Temperature",
            last_updated=now
        )
        
        # Act
        result = sensor.to_dict()
        
        # Assert
        assert result["entity_id"] == "sensor.temperature"
        assert result["state"] == "23.5"
        assert result["unit_of_measurement"] == "°C"
        assert result["device_class"] == "temperature"
        assert result["friendly_name"] == "Temperature"
        assert result["last_updated"] == now.isoformat()

    def test_ha_sensor_from_dict(self):
        """Test HASensor from_dict method."""
        # Arrange
        now = datetime.now()
        data = {
            "entity_id": "sensor.temperature",
            "state": "23.5",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "friendly_name": "Temperature",
            "last_updated": now.isoformat()
        }
        
        # Act
        sensor = HASensor.from_dict(data)
        
        # Assert
        assert sensor.entity_id == "sensor.temperature"
        assert sensor.state == "23.5"
        assert sensor.unit_of_measurement == "°C"
        assert sensor.device_class == "temperature"
        assert sensor.friendly_name == "Temperature"
        assert sensor.last_updated == now


class TestHASummary:
    """Test HASummary model."""

    def test_ha_summary_creation(self):
        """Test HASummary creation."""
        # Arrange
        now = datetime.now()
        
        # Act
        summary = HASummary(
            total_entities=10,
            entities_by_domain={"sensor": 5, "light": 3, "switch": 2},
            entities_by_state={"on": 8, "off": 2},
            last_updated=now
        )
        
        # Assert
        assert summary.total_entities == 10
        assert summary.entities_by_domain == {"sensor": 5, "light": 3, "switch": 2}
        assert summary.entities_by_state == {"on": 8, "off": 2}
        assert summary.last_updated == now

    def test_ha_summary_to_dict(self):
        """Test HASummary to_dict method."""
        # Arrange
        now = datetime.now()
        summary = HASummary(
            total_entities=10,
            entities_by_domain={"sensor": 5, "light": 3, "switch": 2},
            entities_by_state={"on": 8, "off": 2},
            last_updated=now
        )
        
        # Act
        result = summary.to_dict()
        
        # Assert
        assert result["total_entities"] == 10
        assert result["entities_by_domain"] == {"sensor": 5, "light": 3, "switch": 2}
        assert result["entities_by_state"] == {"on": 8, "off": 2}
        assert result["last_updated"] == now.isoformat()

    def test_ha_summary_from_dict(self):
        """Test HASummary from_dict method."""
        # Arrange
        now = datetime.now()
        data = {
            "total_entities": 10,
            "entities_by_domain": {"sensor": 5, "light": 3, "switch": 2},
            "entities_by_state": {"on": 8, "off": 2},
            "last_updated": now.isoformat()
        }
        
        # Act
        summary = HASummary.from_dict(data)
        
        # Assert
        assert summary.total_entities == 10
        assert summary.entities_by_domain == {"sensor": 5, "light": 3, "switch": 2}
        assert summary.entities_by_state == {"on": 8, "off": 2}
        assert summary.last_updated == now


class TestHAEntityState:
    """Test HAEntityState model."""

    def test_ha_entity_state_creation(self):
        """Test HAEntityState creation with all fields."""
        # Arrange
        now = datetime.now()
        
        # Act
        entity_state = HAEntityState(
            entity_id="sensor.temperature",
            state="23.5",
            friendly_name="Temperature",
            domain="sensor",
            last_updated=now,
            unit_of_measurement="°C",
            device_class="temperature"
        )
        
        # Assert
        assert entity_state.entity_id == "sensor.temperature"
        assert entity_state.state == "23.5"
        assert entity_state.friendly_name == "Temperature"
        assert entity_state.domain == "sensor"
        assert entity_state.last_updated == now
        assert entity_state.unit_of_measurement == "°C"
        assert entity_state.device_class == "temperature"

    def test_ha_entity_state_creation_minimal(self):
        """Test HAEntityState creation with minimal fields."""
        # Arrange
        now = datetime.now()
        
        # Act
        entity_state = HAEntityState(
            entity_id="sensor.temperature",
            state="23.5",
            friendly_name="Temperature",
            domain="sensor",
            last_updated=now
        )
        
        # Assert
        assert entity_state.entity_id == "sensor.temperature"
        assert entity_state.state == "23.5"
        assert entity_state.friendly_name == "Temperature"
        assert entity_state.domain == "sensor"
        assert entity_state.last_updated == now
        assert entity_state.unit_of_measurement is None
        assert entity_state.device_class is None

    def test_ha_entity_state_to_dict(self):
        """Test HAEntityState to_dict method."""
        # Arrange
        now = datetime.now()
        entity_state = HAEntityState(
            entity_id="sensor.temperature",
            state="23.5",
            friendly_name="Temperature",
            domain="sensor",
            last_updated=now,
            unit_of_measurement="°C",
            device_class="temperature"
        )
        
        # Act
        result = entity_state.to_dict()
        
        # Assert
        assert result["entity_id"] == "sensor.temperature"
        assert result["state"] == "23.5"
        assert result["friendly_name"] == "Temperature"
        assert result["domain"] == "sensor"
        assert result["last_updated"] == now.isoformat()
        assert result["unit_of_measurement"] == "°C"
        assert result["device_class"] == "temperature"

    def test_ha_entity_state_from_dict(self):
        """Test HAEntityState from_dict method."""
        # Arrange
        now = datetime.now()
        data = {
            "entity_id": "sensor.temperature",
            "state": "23.5",
            "friendly_name": "Temperature",
            "domain": "sensor",
            "last_updated": now.isoformat(),
            "unit_of_measurement": "°C",
            "device_class": "temperature"
        }
        
        # Act
        entity_state = HAEntityState.from_dict(data)
        
        # Assert
        assert entity_state.entity_id == "sensor.temperature"
        assert entity_state.state == "23.5"
        assert entity_state.friendly_name == "Temperature"
        assert entity_state.domain == "sensor"
        assert entity_state.last_updated == now
        assert entity_state.unit_of_measurement == "°C"
        assert entity_state.device_class == "temperature"

    def test_ha_entity_state_from_dict_with_z_suffix(self):
        """Test HAEntityState from_dict with Z suffix in timestamp."""
        # Arrange
        data = {
            "entity_id": "sensor.temperature",
            "state": "23.5",
            "friendly_name": "Temperature",
            "domain": "sensor",
            "last_updated": "2023-01-01T12:00:00Z"
        }
        
        # Act
        entity_state = HAEntityState.from_dict(data)
        
        # Assert
        assert entity_state.entity_id == "sensor.temperature"
        assert entity_state.state == "23.5"
        assert isinstance(entity_state.last_updated, datetime)


class TestHAEntitySummary:
    """Test HAEntitySummary model."""

    def test_ha_entity_summary_creation(self):
        """Test HAEntitySummary creation."""
        # Arrange
        now = datetime.now()
        entity_states = [
            HAEntityState(
                entity_id="sensor.temperature",
                state="23.5",
                friendly_name="Temperature",
                domain="sensor",
                last_updated=now
            )
        ]
        
        # Act
        summary = HAEntitySummary(
            total_entities=1,
            entities_by_domain={"sensor": 1},
            entities_by_state={"23.5": 1},
            last_updated=now,
            entities=entity_states
        )
        
        # Assert
        assert summary.total_entities == 1
        assert summary.entities_by_domain == {"sensor": 1}
        assert summary.entities_by_state == {"23.5": 1}
        assert summary.last_updated == now
        assert len(summary.entities) == 1
        assert summary.entities[0].entity_id == "sensor.temperature"

    def test_ha_entity_summary_to_dict(self):
        """Test HAEntitySummary to_dict method."""
        # Arrange
        now = datetime.now()
        entity_states = [
            HAEntityState(
                entity_id="sensor.temperature",
                state="23.5",
                friendly_name="Temperature",
                domain="sensor",
                last_updated=now
            )
        ]
        summary = HAEntitySummary(
            total_entities=1,
            entities_by_domain={"sensor": 1},
            entities_by_state={"23.5": 1},
            last_updated=now,
            entities=entity_states
        )
        
        # Act
        result = summary.to_dict()
        
        # Assert
        assert result["total_entities"] == 1
        assert result["entities_by_domain"] == {"sensor": 1}
        assert result["entities_by_state"] == {"23.5": 1}
        assert result["last_updated"] == now.isoformat()
        assert len(result["entities"]) == 1
        assert result["entities"][0]["entity_id"] == "sensor.temperature"

    def test_ha_entity_summary_from_dict(self):
        """Test HAEntitySummary from_dict method."""
        # Arrange
        now = datetime.now()
        data = {
            "total_entities": 1,
            "entities_by_domain": {"sensor": 1},
            "entities_by_state": {"23.5": 1},
            "last_updated": now.isoformat(),
            "entities": [
                {
                    "entity_id": "sensor.temperature",
                    "state": "23.5",
                    "friendly_name": "Temperature",
                    "domain": "sensor",
                    "last_updated": now.isoformat()
                }
            ]
        }
        
        # Act
        summary = HAEntitySummary.from_dict(data)
        
        # Assert
        assert summary.total_entities == 1
        assert summary.entities_by_domain == {"sensor": 1}
        assert summary.entities_by_state == {"23.5": 1}
        assert summary.last_updated == now
        assert len(summary.entities) == 1
        assert summary.entities[0].entity_id == "sensor.temperature"


class TestHAConfig:
    """Test HAConfig model."""

    def test_ha_config_creation(self):
        """Test HAConfig creation."""
        # Act
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
        
        # Assert
        assert config.version == "2023.1.0"
        assert config.location_name == "Home"
        assert config.time_zone == "Europe/Madrid"
        assert config.unit_system == {"length": "km", "mass": "kg"}
        assert config.components == ["light", "sensor"]
        assert config.config_dir == "/config"
        assert config.whitelist_external_dirs == []
        assert config.allowlist_external_dirs == []
        assert config.allowlist_external_urls == []
        assert config.version_info == {"version": "2023.1.0"}

    def test_ha_config_to_dict(self):
        """Test HAConfig to_dict method."""
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
        
        # Act
        result = config.to_dict()
        
        # Assert
        assert result["version"] == "2023.1.0"
        assert result["location_name"] == "Home"
        assert result["time_zone"] == "Europe/Madrid"
        assert result["unit_system"] == {"length": "km", "mass": "kg"}
        assert result["components"] == ["light", "sensor"]
        assert result["config_dir"] == "/config"
        assert result["whitelist_external_dirs"] == []
        assert result["allowlist_external_dirs"] == []
        assert result["allowlist_external_urls"] == []
        assert result["version_info"] == {"version": "2023.1.0"}

    def test_ha_config_from_dict(self):
        """Test HAConfig from_dict method."""
        # Arrange
        data = {
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
        
        # Act
        config = HAConfig.from_dict(data)
        
        # Assert
        assert config.version == "2023.1.0"
        assert config.location_name == "Home"
        assert config.time_zone == "Europe/Madrid"
        assert config.unit_system == {"length": "km", "mass": "kg"}
        assert config.components == ["light", "sensor"]
        assert config.config_dir == "/config"
        assert config.whitelist_external_dirs == []
        assert config.allowlist_external_dirs == []
        assert config.allowlist_external_urls == []
        assert config.version_info == {"version": "2023.1.0"}

    def test_ha_config_from_dict_with_missing_fields(self):
        """Test HAConfig from_dict with missing fields."""
        # Arrange
        data = {
            "version": "2023.1.0",
            "location_name": "Home"
        }
        
        # Act
        config = HAConfig.from_dict(data)
        
        # Assert
        assert config.version == "2023.1.0"
        assert config.location_name == "Home"
        assert config.time_zone == ""
        assert config.unit_system == {}
        assert config.components == []
        assert config.config_dir == ""
        assert config.whitelist_external_dirs == []
        assert config.allowlist_external_dirs == []
        assert config.allowlist_external_urls == []
        assert config.version_info == {}
