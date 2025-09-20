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

_LOGGER = logging.getLogger(__name__)


def setup_dependencies(ai_url: str = "http://localhost:1234", 
                       ai_model: str = "openai/gpt-oss-20b", 
                       ha_url: str = "http://homeassistant.local:8123", 
                       ha_token: Optional[str] = None) -> None:
    """Set up all dependencies for the Neural AI integration using injector."""
    _LOGGER.info("Setting up Neural AI dependencies with injector")

    # If no HA token provided, try to get it from credential manager
    if ha_token is None:
        try:
            from ..auth.credential_manager import CredentialManager
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
