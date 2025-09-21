"""Services for Neural AI integration."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, ServiceCall

from neural.const import DOMAIN, SERVICE_SEND_MESSAGE, SERVICE_GET_STATUS, SERVICE_UPDATE_CONFIG

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up Neural AI services."""
    
    async def send_message_service(call: ServiceCall) -> None:
        """Handle send message service."""
        try:
            message = call.data.get("message", "")
            if not message:
                _LOGGER.error("No message provided")
                return
            
            # Get coordinator from any entry
            coordinators = hass.data.get(DOMAIN, {})
            if not coordinators:
                _LOGGER.error("No Neural AI coordinator found")
                return
            
            # Use the first available coordinator
            coordinator = next(iter(coordinators.values()))
            
            # Process the message
            response = await coordinator.process_command(message)
            
            # Store response in coordinator data
            coordinator.last_response = response
            coordinator.last_command = message
            
            _LOGGER.info("Message processed: %s -> %s", message, response)
            
        except Exception as e:
            _LOGGER.error("Error in send_message service: %s", e)
    
    async def get_status_service(call: ServiceCall) -> None:
        """Handle get status service."""
        try:
            # Get coordinator from any entry
            coordinators = hass.data.get(DOMAIN, {})
            if not coordinators:
                _LOGGER.error("No Neural AI coordinator found")
                return
            
            # Use the first available coordinator
            coordinator = next(iter(coordinators.values()))
            
            # Get status
            status = await coordinator.get_status()
            
            _LOGGER.info("Neural AI Status: %s", status)
            
        except Exception as e:
            _LOGGER.error("Error in get_status service: %s", e)
    
    async def update_config_service(call: ServiceCall) -> None:
        """Handle update config service."""
        try:
            # Get coordinator from any entry
            coordinators = hass.data.get(DOMAIN, {})
            if not coordinators:
                _LOGGER.error("No Neural AI coordinator found")
                return
            
            # Use the first available coordinator
            coordinator = next(iter(coordinators.values()))
            
            # Update configuration
            new_config = call.data.get("config", {})
            if new_config:
                # Update coordinator configuration
                coordinator.entry.data.update(new_config)
                _LOGGER.info("Configuration updated: %s", new_config)
            
        except Exception as e:
            _LOGGER.error("Error in update_config service: %s", e)
    
    # Register services
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_MESSAGE,
        send_message_service,
        schema={
            "message": str,
        }
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_STATUS,
        get_status_service,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_CONFIG,
        update_config_service,
        schema={
            "config": dict,
        }
    )
    
    _LOGGER.info("Neural AI services registered")


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload Neural AI services."""
    try:
        hass.services.async_remove(DOMAIN, SERVICE_SEND_MESSAGE)
        hass.services.async_remove(DOMAIN, SERVICE_GET_STATUS)
        hass.services.async_remove(DOMAIN, SERVICE_UPDATE_CONFIG)
        
        _LOGGER.info("Neural AI services unloaded")
        
    except Exception as e:
        _LOGGER.error("Error unloading Neural AI services: %s", e)
