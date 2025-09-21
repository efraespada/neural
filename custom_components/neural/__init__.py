"""Neural AI integration for Home Assistant."""

from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import NeuralDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Neural AI from a config entry."""
    _LOGGER.info("Setting up Neural AI integration")

    # Create coordinator
    coordinator = NeuralDataUpdateCoordinator(hass, entry)
    
    # Load coordinator data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up all platforms for this entry
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Set up services (only once)
    if not hass.data[DOMAIN].get("services_setup"):
        from .services import async_setup_services
        await async_setup_services(hass)
        hass.data[DOMAIN]["services_setup"] = True

    # Set up intents (only once)
    if not hass.data[DOMAIN].get("intents_setup"):
        from .intent import async_setup_intents
        await async_setup_intents(hass, coordinator)
        hass.data[DOMAIN]["intents_setup"] = True

    # Set up STT engine (only once)
    if not hass.data[DOMAIN].get("stt_setup"):
        try:
            # Store STT configuration for later use
            stt_config = {
                "ai_url": entry.data.get("ai_url", "https://openrouter.ai/api/v1"),
                "ai_api_key": entry.data.get("ai_api_key", ""),
                "ai_model": entry.data.get("ai_model", "openai/gpt-oss-20b"),
                "stt_model": entry.data.get("stt_model", "whisper-1"),
                "stt_api_key": entry.data.get("stt_api_key", "")
            }
            hass.data[DOMAIN]["stt_config"] = stt_config
            hass.data[DOMAIN]["stt_setup"] = True
            _LOGGER.info("STT configuration stored successfully")
        except Exception as e:
            _LOGGER.error("Error setting up STT configuration: %s", e)
            # Continue without STT if setup fails

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Neural AI config entry."""
    _LOGGER.info("Unloading Neural AI integration")

    # Unload all platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    # Remove from data
    if entry.entry_id in hass.data[DOMAIN]:
        del hass.data[DOMAIN][entry.entry_id]

    # Unload services, intents and STT if no more entries
    if not hass.data[DOMAIN]:
        from .services import async_unload_services
        from .intent import async_unload_intents
        from homeassistant.components.stt import async_unregister_engine
        await async_unload_services(hass)
        await async_unload_intents(hass)
        await async_unregister_engine(hass, DOMAIN)
        del hass.data[DOMAIN]

    return True