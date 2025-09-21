"""Dependency injection providers for Neural AI integration using injector."""

import logging
import os

from .injector_container import (
    initialize_container, 
    get_container, 
    Configuration,
    get_ai_use_case,
    get_ha_use_case,
    get_ai_client,
    get_ha_client,
    get_ai_repository,
    get_ha_repository
)

from ..auth.credential_manager import CredentialManager
from ..managers.config_manager import ConfigManager
from ..repositories.implementations.file_repository_impl import FileRepositoryImpl
from ..api.models.domain.config import AppConfig, LLMConfig, HAConfig, STTConfig

from ..const import (
    DEFAULT_AI_URL,
    DEFAULT_AI_MODEL,
    DEFAULT_STT_MODEL,
    DEFAULT_CONFIG_FILE_PATH,
    DEFAULT_WORK_MODE,
    DEFAULT_PERSONALITY,
    DEFAULT_MICROPHONE_ENABLED,
    DEFAULT_VOICE_LANGUAGE,
    DEFAULT_VOICE_TIMEOUT,
    DEFAULT_HA_URL,
)

_LOGGER = logging.getLogger(__name__)


async def setup_dependencies() -> None:
    """Set up all dependencies for the Neural AI integration using injector."""
    _LOGGER.info("Setting up Neural AI dependencies with injector")

    try:
        # Create file repository and config manager
        file_repo = FileRepositoryImpl(base_path=".")
        config_manager = ConfigManager(file_repo, DEFAULT_CONFIG_FILE_PATH)
        
        # Load configuration from file
        try:
            config_data = await config_manager.get_config()
        except ValueError:
            # Configuration not loaded, load it
            config_data = await config_manager.load_config()
            
        _LOGGER.info("Using configuration from file: AI URL=%s, Model=%s, STT Model=%s", 
                    config_data.llm.url, config_data.llm.model, config_data.stt.model)
        _LOGGER.info("STT API key configured: %s", "Yes" if config_data.stt.api_key else "No")

        # Get HA token
        ha_token = config_data.ha.token
        if not ha_token:
            # Try to get token from credential manager
            try:
                credential_manager = CredentialManager()
                if credential_manager.has_credentials():
                    stored_token = credential_manager.get_token()
                    if stored_token:
                        ha_token = stored_token
                        _LOGGER.info("Using stored HA token from credential manager")
            except Exception as e:
                _LOGGER.debug("Could not load stored HA token: %s", e)
        
        # Validate HA token only if required
        if not ha_token:
            raise ValueError("No HA token available. Please configure the integration first.")

        # Create configuration object
        config = Configuration(
            ai_url=config_data.llm.url,
            ai_model=config_data.llm.model,
            ai_api_key=config_data.llm.api_key,
            stt_model=config_data.stt.model,
            stt_api_key=config_data.stt.api_key,
            ha_url=config_data.ha.url,
            ha_token=ha_token
        )

        # Initialize the container with configuration
        initialize_container(config)
        _LOGGER.info("Neural AI dependencies setup completed with injector")
        
    except Exception as e:
        _LOGGER.error("Could not load configuration from file: %s", e)
        raise


async def create_default_config() -> None:
    """Create default configuration file if it doesn't exist."""
    try:
        # Create file repository and config manager
        file_repo = FileRepositoryImpl(base_path=".")
        config_manager = ConfigManager(file_repo, DEFAULT_CONFIG_FILE_PATH)
        
        # Check if config file exists physically
        if os.path.exists(DEFAULT_CONFIG_FILE_PATH):
            try:
                # Try to load the configuration
                await config_manager.load_config()
                _LOGGER.info("Configuration file already exists and is valid")
                return
            except Exception as e:
                _LOGGER.warning(f"Configuration file exists but is invalid: {e}")
                _LOGGER.info("Attempting to migrate existing configuration...")
                
                # Try to migrate existing config
                try:
                    await _migrate_existing_config(config_manager)
                    _LOGGER.info("Configuration migrated successfully")
                    return
                except Exception as migrate_error:
                    _LOGGER.warning(f"Could not migrate config: {migrate_error}")
                    _LOGGER.info("Will create new default configuration")
        else:
            _LOGGER.info("Configuration file does not exist, creating default")
        
        # Create default configuration using constants
        default_config = AppConfig(
            llm=LLMConfig(
                url=DEFAULT_AI_URL,
                model=DEFAULT_AI_MODEL,
                api_key=""
            ),
            ha=HAConfig(
                url=DEFAULT_HA_URL,
                token=""  # Will be set by config flow or credential manager
            ),
            stt=STTConfig(
                model=DEFAULT_STT_MODEL,
                api_key=""
            ),
            work_mode=DEFAULT_WORK_MODE,
            personality=DEFAULT_PERSONALITY,
            microphone_enabled=DEFAULT_MICROPHONE_ENABLED,
            voice_language=DEFAULT_VOICE_LANGUAGE,
            voice_timeout=DEFAULT_VOICE_TIMEOUT
        )
        
        # Save default configuration
        await config_manager.save_config(default_config)
        _LOGGER.info("Default configuration created at %s", DEFAULT_CONFIG_FILE_PATH)
        
    except Exception as e:
        _LOGGER.error("Error creating default configuration: %s", e)
        raise


async def _migrate_existing_config(config_manager: ConfigManager) -> None:
    """Migrate existing configuration to new format."""
    import json
    import os
    
    # Read raw JSON file
    with open(DEFAULT_CONFIG_FILE_PATH, 'r') as f:
        raw_config = json.load(f)
    
    # Fix personality field if it's an array
    if 'personality' in raw_config and isinstance(raw_config['personality'], list):
        # Take the first personality from the list
        raw_config['personality'] = raw_config['personality'][0] if raw_config['personality'] else "jarvis"
        _LOGGER.info(f"Migrated personality from array to string: {raw_config['personality']}")
    
    # Ensure all required fields exist
    if 'ha' not in raw_config:
        raw_config['ha'] = {
            "url": DEFAULT_HA_URL,
            "token": ""
        }

    if 'llm' not in raw_config:
        raw_config['llm'] = {
            "url": DEFAULT_AI_URL,
            "model": DEFAULT_AI_MODEL,
            "api_key": ""
        }

    if 'stt' not in raw_config:
        raw_config['stt'] = {
            "model": DEFAULT_STT_MODEL,
            "api_key": ""
        }

    if 'stt' not in raw_config:
        raw_config['stt'] = {
            "model": DEFAULT_STT_MODEL,
            "api_key": ""
        }
    
    if 'work_mode' not in raw_config:
        raw_config['work_mode'] = "assistant"
    
    if 'microphone_enabled' not in raw_config:
        raw_config['microphone_enabled'] = True
    
    if 'voice_language' not in raw_config:
        raw_config['voice_language'] = "es-ES"
    
    if 'voice_timeout' not in raw_config:
        raw_config['voice_timeout'] = 5
    
    # Create backup of original file
    backup_path = f"{DEFAULT_CONFIG_FILE_PATH}.backup"
    with open(backup_path, 'w') as f:
        json.dump(raw_config, f, indent=2)
    _LOGGER.info(f"Created backup at {backup_path}")
    
    # Write migrated config
    with open(DEFAULT_CONFIG_FILE_PATH, 'w') as f:
        json.dump(raw_config, f, indent=2)
    
    # Verify the migrated config can be loaded
    await config_manager.load_config()


def clear_dependencies() -> None:
    """Clear all registered dependencies."""
    try:
        container = get_container()
        container.clear()
        _LOGGER.info("Neural AI dependencies cleared")
    except Exception as e:
        _LOGGER.warning("Could not clear dependencies: %s", e)


# Re-export convenience functions from injector_container
__all__ = [
    'setup_dependencies',
    'create_default_config',
    'clear_dependencies',
    'get_ai_use_case',
    'get_ha_use_case', 
    'get_ai_client',
    'get_ha_client',
    'get_ai_repository',
    'get_ha_repository'
]
