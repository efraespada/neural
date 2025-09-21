"""Intent handler for Neural AI integration with Assist pipeline."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.intent import IntentHandler, IntentResponse
from homeassistant.helpers import intent

from .const import DOMAIN, INTENT_NEURAL_COMMAND

_LOGGER = logging.getLogger(__name__)


class NeuralIntentHandler(IntentHandler):
    """Intent handler for Neural AI commands."""

    def __init__(self, coordinator) -> None:
        """Initialize the intent handler."""
        super().__init__()
        self.coordinator = coordinator
        self.intent_type = INTENT_NEURAL_COMMAND

    async def async_handle(self, intent_obj: intent.Intent) -> IntentResponse:
        """Handle the intent."""
        try:
            _LOGGER.info("Processing Neural AI intent: %s", intent_obj.text)
            
            # Get the command from the intent
            command = intent_obj.text
            
            # Process the command using the coordinator
            response = await self.coordinator.process_command(command)
            
            # Create response
            intent_response = intent_obj.create_response()
            intent_response.async_set_speech(response)
            
            _LOGGER.info("Neural AI response: %s", response)
            return intent_response
            
        except Exception as e:
            _LOGGER.error("Error handling Neural AI intent: %s", e)
            intent_response = intent_obj.create_response()
            intent_response.async_set_speech(f"Error processing command: {str(e)}")
            return intent_response


async def async_setup_intents(hass: HomeAssistant, coordinator=None) -> None:
    """Set up Neural AI intents."""
    try:
        # Get coordinator from hass data if not provided
        if coordinator is None:
            from .const import DOMAIN
            if DOMAIN in hass.data and "coordinator" in hass.data[DOMAIN]:
                coordinator = hass.data[DOMAIN]["coordinator"]
            else:
                _LOGGER.warning("No coordinator available for Neural AI intents")
                return
        
        # Register the intent handler
        intent_handler = NeuralIntentHandler(coordinator)
        intent.async_register(hass, intent_handler)
        
        _LOGGER.info("Neural AI intents registered successfully")
        
    except Exception as e:
        _LOGGER.error("Error setting up Neural AI intents: %s", e)


async def async_unload_intents(hass: HomeAssistant) -> None:
    """Unload Neural AI intents."""
    try:
        # Unregister the intent handler
        intent.async_unregister(hass, INTENT_NEURAL_COMMAND)
        
        _LOGGER.info("Neural AI intents unloaded successfully")
        
    except Exception as e:
        _LOGGER.error("Error unloading Neural AI intents: %s", e)
