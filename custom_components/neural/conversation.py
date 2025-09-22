"""Conversation agent for Neural AI integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.components.conversation import (
    ConversationEntity,
    AbstractConversationAgent,
    ConversationResult,
    ConversationInput,
)
from homeassistant.util import ulid as ulid_util

from .const import DOMAIN
from .core.dependency_injection.providers import setup_dependencies
from .core.dependency_injection.injector_container import get_decision_use_case, get_do_actions_use_case
from .core.const import (
    SUPPORTED_LANGUAGES,
    DEFAULT_WORK_MODE,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Neural AI conversation entity."""
    async_add_entities(
        [
            NeuralConversationAgent(config_entry)
        ]
    )

class NeuralConversationAgent(
    ConversationEntity,
    AbstractConversationAgent
):
    """Conversation agent that processes all messages through Neural AI."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the conversation agent."""
        super().__init__()
        self._config_entry = config_entry
        self._attr_name = "Neural AI"
        self._attr_unique_id = f"{config_entry.entry_id}_conversation"
        self._supported_languages = list(SUPPORTED_LANGUAGES)

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return self._supported_languages

    async def async_process(
        self, user_input: ConversationInput
    ) -> ConversationResult:
        """Process a conversation turn."""
        conversation_id = user_input.conversation_id or ulid_util.ulid_now()
        try:
            _LOGGER.warning("Neural AI processing conversation: %s", user_input.text)
            
            # Get configuration from config entry
            work_mode = self._config_entry.data.get("work_mode", DEFAULT_WORK_MODE)
            _LOGGER.warning("Using work mode: %s", work_mode)
 
            # Setup dependencies and get use cases
            await setup_dependencies()
            decision_use_case = get_decision_use_case()
            do_actions_use_case = get_do_actions_use_case()
            
            # Step 1: Decision Use Case - Interpret the user request
            _LOGGER.warning("Step 1: Interpreting user request with Decision Use Case")
            decision_result = await decision_use_case.make_decision(user_input.text, work_mode)
            
            # Step 2: Do Actions Use Case - Execute necessary actions
            _LOGGER.warning("Step 2: Executing actions with Do Actions Use Case")
            actions_result = await do_actions_use_case.execute_actions(decision_result)
            
            # Step 3: Return the AI response message
            response = actions_result.get("message", "")
            
            _LOGGER.warning("Neural AI response: %s", response)
            return ConversationResult(
                response=response,
                conversation_id=conversation_id,
            )
            
        except Exception as e:
            _LOGGER.error("Error processing conversation: %s", e)
            return ConversationResult(
                response=f"Lo siento, hubo un error procesando tu solicitud: {str(e)}",
                conversation_id=conversation_id,
            )
