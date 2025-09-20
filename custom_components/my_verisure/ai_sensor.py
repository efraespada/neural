"""Platform for Neural AI sensor."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER, ENTITY_NAMES
from .coordinator import MyVerisureDataUpdateCoordinator
from .device import get_device_info

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Neural AI sensor based on a config entry."""
    coordinator: MyVerisureDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    # Create AI sensor entity
    async_add_entities([NeuralAISensor(coordinator, config_entry)])


class NeuralAISensor(SensorEntity):
    """Representation of a Neural AI sensor."""

    def __init__(
        self, coordinator: MyVerisureDataUpdateCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the AI sensor."""
        self.coordinator = coordinator
        self.config_entry = config_entry
        self._attr_name = ENTITY_NAMES["ai_chat"]
        self._attr_unique_id = "neural_ai"
        self._attr_native_unit_of_measurement = None

        # Set device info
        self._attr_device_info = get_device_info(config_entry)

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "Unknown"

        ai_data = self.coordinator.data.get("ai_status", {})
        return ai_data.get("status", "Unknown")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        ai_data = self.coordinator.data.get("ai_status", {})
        
        attributes = {
            "ai_url": ai_data.get("url", "Unknown"),
            "ai_model": ai_data.get("model", "Unknown"),
            "available_models": ai_data.get("available_models", []),
            "last_updated": ai_data.get("last_updated"),
        }

        return attributes

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
