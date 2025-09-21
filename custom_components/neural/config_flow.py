"""Config flow for Neural AI integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

import os
import sys
import pathlib
import logging

_LOGGER = logging.getLogger(__name__)
_LOGGER.warning("PWD: %s", os.getcwd())
_LOGGER.warning("sys.path: %s", sys.path)
_LOGGER.warning("Package file: %s", pathlib.Path(__file__).resolve())

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback

from .core.dependency_injection.providers import setup_dependencies, clear_dependencies
from .core import get_ai_use_case, get_ha_use_case

from .const import (
    DOMAIN,
    CONF_HA_TOKEN,
    CONF_OPENROUTER_TOKEN,
    CONF_WORK_MODE,
    CONF_PERSONALITY,
    CONF_AI_MODEL,
    CONF_MICROPHONE_ENABLED,
    CONF_VOICE_LANGUAGE,
    CONF_VOICE_TIMEOUT,
    WORK_MODES,
    PERSONALITIES,
    AI_MODELS,
    DEFAULT_WORK_MODE,
    DEFAULT_PERSONALITY,
    DEFAULT_AI_MODEL,
    DEFAULT_MICROPHONE_ENABLED,
    DEFAULT_VOICE_LANGUAGE,
    DEFAULT_VOICE_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class NeuralConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Neural AI."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> NeuralOptionsFlowHandler:
        """Get the options flow for this handler."""
        return NeuralOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate tokens
            ha_token = user_input[CONF_HA_TOKEN].strip()
            openrouter_token = user_input[CONF_OPENROUTER_TOKEN].strip()
            
            if not ha_token:
                errors["base"] = "ha_token_required"
            elif not openrouter_token:
                errors["base"] = "openrouter_token_required"
            else:
                # Test tokens (basic validation)
                if await self._test_tokens(ha_token, openrouter_token):
                    return self.async_create_entry(
                        title="Neural AI",
                        data=user_input,
                    )
                else:
                    errors["base"] = "invalid_tokens"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HA_TOKEN): str,
                    vol.Required(CONF_OPENROUTER_TOKEN): str,
                    vol.Required(CONF_WORK_MODE, default=DEFAULT_WORK_MODE): vol.In(WORK_MODES),
                    vol.Required(CONF_PERSONALITY, default=DEFAULT_PERSONALITY): vol.In(PERSONALITIES),
                    vol.Required(CONF_AI_MODEL, default=DEFAULT_AI_MODEL): vol.In(AI_MODELS),
                    vol.Required(CONF_MICROPHONE_ENABLED, default=DEFAULT_MICROPHONE_ENABLED): bool,
                    vol.Required(CONF_VOICE_LANGUAGE, default=DEFAULT_VOICE_LANGUAGE): str,
                    vol.Required(CONF_VOICE_TIMEOUT, default=DEFAULT_VOICE_TIMEOUT): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=30)
                    ),
                }
            ),
            errors=errors,
        )

    async def _test_tokens(self, ha_token: str, openrouter_token: str) -> bool:
        """Test if the provided tokens are valid using core use cases."""
        try:
            # Setup dependencies with test tokens
            await setup_dependencies(
                ai_url="https://openrouter.ai/api/v1",
                ai_model="openai/gpt-4o-mini",  # Use a default model for testing
                ai_api_key=openrouter_token,
                ha_url="http://supervisor/core",
                ha_token=ha_token
            )
            
            # Test AI connection
            ai_use_case = get_ai_use_case()
            ai_connected = await ai_use_case.test_connection()
            
            # Test HA connection
            ha_use_case = get_ha_use_case()
            ha_entities = await ha_use_case.get_all_entities()
            ha_connected = len(ha_entities) >= 0  # If we can get entities, HA is connected
            
            # Clean up dependencies
            clear_dependencies()
            
            return ai_connected and ha_connected
            
        except Exception as e:
            _LOGGER.error("Error testing tokens: %s", e)
            try:
                clear_dependencies()
            except:
                pass
            return False


class NeuralOptionsFlowHandler(OptionsFlow):
    """Handle Neural AI options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_WORK_MODE,
                        default=self.config_entry.data.get(CONF_WORK_MODE, DEFAULT_WORK_MODE),
                    ): vol.In(WORK_MODES),
                    vol.Required(
                        CONF_PERSONALITY,
                        default=self.config_entry.data.get(CONF_PERSONALITY, DEFAULT_PERSONALITY),
                    ): vol.In(PERSONALITIES),
                    vol.Required(
                        CONF_AI_MODEL,
                        default=self.config_entry.data.get(CONF_AI_MODEL, DEFAULT_AI_MODEL),
                    ): vol.In(AI_MODELS),
                    vol.Required(
                        CONF_MICROPHONE_ENABLED,
                        default=self.config_entry.data.get(CONF_MICROPHONE_ENABLED, DEFAULT_MICROPHONE_ENABLED),
                    ): bool,
                    vol.Required(
                        CONF_VOICE_LANGUAGE,
                        default=self.config_entry.data.get(CONF_VOICE_LANGUAGE, DEFAULT_VOICE_LANGUAGE),
                    ): str,
                    vol.Required(
                        CONF_VOICE_TIMEOUT,
                        default=self.config_entry.data.get(CONF_VOICE_TIMEOUT, DEFAULT_VOICE_TIMEOUT),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=30)),
                }
            ),
        )
