"""Services for the Neural AI integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN, LOGGER

# Service schemas
SERVICE_SEND_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("message"): cv.string,
    vol.Optional("model"): cv.string,
})

SERVICE_GET_STATUS_SCHEMA = vol.Schema({})

SERVICE_LIST_MODELS_SCHEMA = vol.Schema({})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Neural AI."""
    
    async def async_send_message_service(call: ServiceCall) -> None:
        """Service to send a message to AI."""
        message = call.data["message"]
        model = call.data.get("model")
        
        # Find the coordinator
        for entry_id, coordinator in hass.data[DOMAIN].items():
            if entry_id != "services_setup":  # Skip the services setup flag
                try:
                    response = await coordinator.async_send_message(message, model)
                    if response:
                        LOGGER.info("AI response received via service: %s", response[:100] + "..." if len(response) > 100 else response)
                    else:
                        LOGGER.error("No response from AI via service")
                except Exception as e:
                    LOGGER.error("Error sending message to AI via service: %s", e)
                break

    async def async_get_status_service(call: ServiceCall) -> None:
        """Service to get AI status."""
        # Find the coordinator
        for entry_id, coordinator in hass.data[DOMAIN].items():
            if entry_id != "services_setup":  # Skip the services setup flag
                try:
                    status = await coordinator.async_get_ai_status()
                    LOGGER.info("AI status via service: %s", status)
                except Exception as e:
                    LOGGER.error("Error getting AI status via service: %s", e)
                break

    async def async_list_models_service(call: ServiceCall) -> None:
        """Service to list available AI models."""
        # Find the coordinator
        for entry_id, coordinator in hass.data[DOMAIN].items():
            if entry_id != "services_setup":  # Skip the services setup flag
                try:
                    models = await coordinator.async_list_models()
                    LOGGER.info("Available AI models via service: %s", models)
                except Exception as e:
                    LOGGER.error("Error listing AI models via service: %s", e)
                break

    # Register services
    hass.services.async_register(
        DOMAIN,
        "send_message",
        async_send_message_service,
        schema=SERVICE_SEND_MESSAGE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "get_status",
        async_get_status_service,
        schema=SERVICE_GET_STATUS_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "list_models",
        async_list_models_service,
        schema=SERVICE_LIST_MODELS_SCHEMA,
    )

    LOGGER.info("Neural AI services registered")


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services for Neural AI."""
    hass.services.async_remove(DOMAIN, "send_message")
    hass.services.async_remove(DOMAIN, "get_status")
    hass.services.async_remove(DOMAIN, "list_models")
    
    LOGGER.info("Neural AI services unloaded")