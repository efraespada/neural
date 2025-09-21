"""Sensor platform for Neural AI integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from neural.const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Neural AI sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        NeuralAIStatusSensor(coordinator, config_entry),
        NeuralAIResponseSensor(coordinator, config_entry),
    ]
    
    async_add_entities(entities)


class NeuralAIStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Neural AI status."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = "Neural AI Status"
        self._attr_unique_id = f"{config_entry.entry_id}_status"
        self._attr_icon = "mdi:brain"

    @property
    def native_value(self) -> str:
        """Return the status value."""
        return self.coordinator.data.get("status", "unknown")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "ai_model": self.coordinator.data.get("ai_model"),
            "personality": self.coordinator.data.get("personality"),
            "work_mode": self.coordinator.data.get("work_mode"),
            "is_processing": self.coordinator.data.get("is_processing", False),
            "last_update": self.coordinator.data.get("last_update"),
        }


class NeuralAIResponseSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Neural AI responses."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = "Neural AI Response"
        self._attr_unique_id = f"{config_entry.entry_id}_response"
        self._attr_icon = "mdi:message-text"

    @property
    def native_value(self) -> str:
        """Return the response value."""
        return self.coordinator.data.get("last_response", "")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "last_command": self.coordinator.data.get("last_command"),
            "status": self.coordinator.data.get("status"),
            "is_processing": self.coordinator.data.get("is_processing", False),
        }
