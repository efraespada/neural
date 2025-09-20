"""Dependency injection providers for Neural AI integration using injector."""

import logging
from typing import Optional

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

_LOGGER = logging.getLogger(__name__)


async def setup_dependencies(ai_url: str = None, 
                       ai_model: str = None, 
                       ha_url: str = "http://homeassistant.local:8123", 
                       ha_token: Optional[str] = None) -> None:
    """Set up all dependencies for the Neural AI integration using injector."""
    _LOGGER.info("Setting up Neural AI dependencies with injector")

    # Load configuration from file if not provided
    if ai_url is None or ai_model is None:
        try:
            # Create file repository and config manager
            file_repo = FileRepositoryImpl(base_path=".")
            config_manager = ConfigManager(file_repo, "config.json")
            
            # Load configuration
            try:
                config_data = await config_manager.get_config()
            except ValueError:
                # Configuration not loaded, load it
                config_data = await config_manager.load_config()
            
            # Use configuration from file
            if ai_url is None:
                ai_url = config_data.llm.url
            if ai_model is None:
                ai_model = config_data.llm.model
            ai_api_key = config_data.llm.api_key
                
            _LOGGER.info("Using configuration from file: AI URL=%s, Model=%s", ai_url, ai_model)
            
        except Exception as e:
            _LOGGER.warning("Could not load configuration from file, using defaults: %s", e)
            if ai_url is None:
                ai_url = "https://openrouter.ai/api/v1"
            if ai_model is None:
                ai_model = "anthropic/claude-3.5-sonnet"
            ai_api_key = None

    # If no HA token provided, try to get it from credential manager
    if ha_token is None:
        try:
            credential_manager = CredentialManager()
            if credential_manager.has_credentials():
                stored_token = credential_manager.get_token()
                if stored_token:
                    ha_token = stored_token
                    _LOGGER.info("Using stored HA token from credential manager")
        except Exception as e:
            _LOGGER.debug("Could not load stored HA token: %s", e)

    # Create configuration
    config = Configuration(
        ai_url=ai_url,
        ai_model=ai_model,
        ai_api_key=ai_api_key,
        ha_url=ha_url,
        ha_token=ha_token
    )

    # Initialize the container with configuration
    initialize_container(config)
    _LOGGER.info("Neural AI dependencies setup completed with injector")


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
    'clear_dependencies',
    'get_ai_use_case',
    'get_ha_use_case', 
    'get_ai_client',
    'get_ha_client',
    'get_ai_repository',
    'get_ha_repository'
]
