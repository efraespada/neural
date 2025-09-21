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

from .core.dependency_injection.providers import setup_dependencies, clear_dependencies, create_default_config
from .core import get_ai_use_case, get_ha_use_case
from .core.managers.config_manager import ConfigManager
from .core.repositories.implementations.file_repository_impl import FileRepositoryImpl
from .core.api.models.domain.config import AppConfig, LLMConfig, HAConfig, STTConfig
from .core.const import (
    DEFAULT_CONFIG_FILE_PATH,
    DEFAULT_WORK_MODE,
    DEFAULT_PERSONALITY,
    DEFAULT_HA_URL,
    DEFAULT_AI_URL,
    DEFAULT_AI_MODEL,
    DEFAULT_STT_MODEL,
    DEFAULT_MICROPHONE_ENABLED,
    DEFAULT_VOICE_LANGUAGE,
    DEFAULT_VOICE_TIMEOUT,
    WORK_MODES,
    PERSONALITIES,
)
from .const import (
    DOMAIN,
    CONF_HA_TOKEN,
    CONF_AI_API_KEY,
    CONF_WORK_MODE,
    CONF_PERSONALITY,
    CONF_AI_MODEL,
    CONF_AI_URL,
    CONF_HA_URL,
    CONF_STT_MODEL,
    CONF_STT_API_KEY,
    CONF_MICROPHONE_ENABLED,
    CONF_VOICE_LANGUAGE,
    CONF_VOICE_TIMEOUT,
    AI_MODELS, 
    STT_MODELS,
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
            ai_url = user_input[CONF_AI_URL].strip()
            ai_model = user_input[CONF_AI_MODEL].strip()
            ai_api_key = user_input[CONF_AI_API_KEY].strip()
            ha_url = user_input[CONF_HA_URL].strip()
            ha_token = user_input[CONF_HA_TOKEN].strip()
            stt_model = user_input[CONF_STT_MODEL].strip()
            stt_api_key = user_input[CONF_STT_API_KEY].strip()
            work_mode = user_input[CONF_WORK_MODE].strip()
            personality = user_input[CONF_PERSONALITY].strip()
            microphone_enabled = user_input[CONF_MICROPHONE_ENABLED]
            voice_language = user_input[CONF_VOICE_LANGUAGE].strip()
            voice_timeout = user_input[CONF_VOICE_TIMEOUT]
            
            if not ha_token:
                errors["base"] = "ha_token_required"
            elif not ai_api_key:
                errors["base"] = "ai_api_key_required"
            else:
                # Test tokens (basic validation)
                if await self._check_configuration(
                    ai_url,
                    ai_model,
                    ai_api_key,
                    ha_url,
                    ha_token,
                    stt_model,
                    stt_api_key,
                    work_mode,
                    personality,
                    microphone_enabled,
                    voice_language,
                    voice_timeout,
                ):
                    # Save configuration to config.json
                    await self._save_config_to_file(user_input)
                    
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
                    vol.Required(CONF_HA_URL, default=DEFAULT_HA_URL): str,
                    vol.Required(CONF_HA_TOKEN): str,
                    vol.Required(CONF_AI_URL, default=DEFAULT_AI_URL): str,
                    vol.Required(CONF_AI_MODEL, default=DEFAULT_AI_MODEL): vol.In(AI_MODELS),
                    vol.Required(CONF_AI_API_KEY): str,
                    vol.Required(CONF_STT_MODEL, default=DEFAULT_STT_MODEL): vol.In(STT_MODELS),
                    vol.Required(CONF_STT_API_KEY): str,
                    vol.Required(CONF_WORK_MODE, default=DEFAULT_WORK_MODE): vol.In(WORK_MODES),
                    vol.Required(CONF_PERSONALITY, default=DEFAULT_PERSONALITY): vol.In(PERSONALITIES),
                    vol.Required(CONF_MICROPHONE_ENABLED, default=DEFAULT_MICROPHONE_ENABLED): bool,
                    vol.Required(CONF_VOICE_LANGUAGE, default=DEFAULT_VOICE_LANGUAGE): str,
                    vol.Required(CONF_VOICE_TIMEOUT, default=DEFAULT_VOICE_TIMEOUT): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=30)
                    ),
                }
            ),
            errors=errors,
        )

    async def _check_configuration(self, ai_url: str, ai_model: str, ai_api_key: str, ha_url: str, ha_token: str, stt_model: str, stt_api_key: str, work_mode: str, personality: str, microphone_enabled: bool, voice_language: str, voice_timeout: int) -> bool:
        """Test if the provided tokens are valid using core use cases."""
        try:
            # Create temporary config
            config = AppConfig(
                llm=LLMConfig(
                    url=ai_url,
                    model=ai_model,
                    api_key=ai_api_key
                ),
                ha=HAConfig(
                    url=ha_url,
                    token=ha_token
                ),
                stt=STTConfig(
                    model=stt_model,
                    api_key=stt_api_key
                ),
                work_mode=work_mode,
                personality=personality,
                microphone_enabled=microphone_enabled,
                voice_language=voice_language,
                voice_timeout=voice_timeout
            )
            
            # Save temporary config
            file_repo = FileRepositoryImpl(base_path=".")
            config_manager = ConfigManager(file_repo, DEFAULT_CONFIG_FILE_PATH)
            await config_manager.save_config(config)
            
            # Setup dependencies with temporary config
            await setup_dependencies()
            
            # Test AI connection
            ai_use_case = get_ai_use_case()
            ai_connected = await ai_use_case.test_connection()
            
            # Test HA connection
            ha_use_case = get_ha_use_case()
            ha_entities = await ha_use_case.get_all_entities()
            ha_connected = len(ha_entities) >= 0  # If we can get entities, HA is connected
            
            # Test STT connection only if API key is provided
            stt_connected = True  # Default to True (STT is optional)
            if stt_api_key and stt_api_key.strip():
                try:
                    from .core.api.ai_client import AIClient
                    stt_client = AIClient(
                        ai_url=ai_url,
                        ai_model=ai_model,
                        api_key=ai_api_key,
                        stt_model=stt_model,
                        stt_api_key=stt_api_key
                    )
                    # Test STT connection by checking if Whisper is available
                    stt_connected = await stt_client.is_whisper_available()
                    _LOGGER.info("STT connection test: %s", stt_connected)
                except Exception as stt_e:
                    _LOGGER.warning("STT connection test failed: %s", stt_e)
                    stt_connected = False
            
            # Clean up dependencies
            clear_dependencies()
            
            return ai_connected and ha_connected and stt_connected
            
        except Exception as e:
            _LOGGER.error("Error testing tokens: %s", e)
            try:
                clear_dependencies()
            except:
                pass
            return False

    async def _save_config_to_file(self, user_input: dict[str, Any]) -> None:
        """Save configuration from config flow to config.json file."""
        try:
            # Create file repository and config manager
            file_repo = FileRepositoryImpl(base_path=".")
            config_manager = ConfigManager(file_repo, DEFAULT_CONFIG_FILE_PATH)
            
            # Create configuration from user input
            config = AppConfig(
                llm=LLMConfig(
                    url=user_input.get(CONF_AI_URL, DEFAULT_AI_URL),
                    model=user_input.get(CONF_AI_MODEL, DEFAULT_AI_MODEL),
                    api_key=user_input.get(CONF_AI_API_KEY, "")
                ),
                ha=HAConfig(
                    url=user_input.get(CONF_HA_URL, DEFAULT_HA_URL),
                    token=user_input.get(CONF_HA_TOKEN, "")
                ),
                stt=STTConfig(
                    model=user_input.get(CONF_STT_MODEL, DEFAULT_STT_MODEL),
                    api_key=user_input.get(CONF_STT_API_KEY, "")
                ),
                work_mode=user_input.get(CONF_WORK_MODE, DEFAULT_WORK_MODE),
                personality=user_input.get(CONF_PERSONALITY, DEFAULT_PERSONALITY),
                microphone_enabled=user_input.get(CONF_MICROPHONE_ENABLED, DEFAULT_MICROPHONE_ENABLED),
                voice_language=user_input.get(CONF_VOICE_LANGUAGE, DEFAULT_VOICE_LANGUAGE),
                voice_timeout=user_input.get(CONF_VOICE_TIMEOUT, DEFAULT_VOICE_TIMEOUT)
            )
            
            # Save configuration
            await config_manager.save_config(config)
            _LOGGER.info("Configuration saved to config.json")
            
        except Exception as e:
            _LOGGER.error("Error saving configuration: %s", e)
            raise


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
                    # Home Assistant Configuration
                    vol.Required(
                        CONF_HA_URL,
                        default=self.config_entry.data.get(CONF_HA_URL, DEFAULT_HA_URL),
                    ): str,
                    vol.Required(
                        CONF_HA_TOKEN,
                        default=self.config_entry.data.get(CONF_HA_TOKEN, ""),
                    ): str,
                    
                    # LLM/AI Configuration
                    vol.Required(
                        CONF_AI_URL,
                        default=self.config_entry.data.get(CONF_AI_URL, DEFAULT_AI_URL),
                    ): str,
                    vol.Required(
                        CONF_AI_MODEL,
                        default=self.config_entry.data.get(CONF_AI_MODEL, DEFAULT_AI_MODEL),
                    ): vol.In(AI_MODELS),
                    vol.Required(
                        CONF_AI_API_KEY,
                        default=self.config_entry.data.get(CONF_AI_API_KEY, ""),
                    ): str,
                    
                    # STT Configuration
                    vol.Required(
                        CONF_STT_MODEL,
                        default=self.config_entry.data.get(CONF_STT_MODEL, DEFAULT_STT_MODEL),
                    ): vol.In(STT_MODELS),
                    vol.Required(
                        CONF_STT_API_KEY,
                        default=self.config_entry.data.get(CONF_STT_API_KEY, ""),
                    ): str,
                    
                    # AI Behavior Configuration
                    vol.Required(
                        CONF_WORK_MODE,
                        default=self.config_entry.data.get(CONF_WORK_MODE, DEFAULT_WORK_MODE),
                    ): vol.In(WORK_MODES),
                    vol.Required(
                        CONF_PERSONALITY,
                        default=self.config_entry.data.get(CONF_PERSONALITY, DEFAULT_PERSONALITY),
                    ): vol.In(PERSONALITIES),
                    
                    # Voice Configuration
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
