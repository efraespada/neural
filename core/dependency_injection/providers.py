"""Dependency injection providers for Neural AI integration."""

import logging
from typing import Dict, Any

from .container import register_singleton
from api.ai_client import AIClient
from api.ha_client import HAClient
from repositories.interfaces.ai_repository import AIRepository
from repositories.interfaces.ha_repository import HARepository
from repositories.implementations.ai_repository_impl import (
    AIRepositoryImpl,
)
from repositories.implementations.ha_repository_impl import (
    HARepositoryImpl,
)
from use_cases.interfaces.ai_use_case import AIUseCase
from use_cases.interfaces.ha_use_case import HAUseCase
from use_cases.implementations.ai_use_case_impl import AIUseCaseImpl
from use_cases.implementations.ha_use_case_impl import HAUseCaseImpl

_LOGGER = logging.getLogger(__name__)


def setup_dependencies(ai_url: str = "http://localhost:11434", ai_model: str = "llama3.2", 
                       ha_url: str = "http://homeassistant.local:8123", ha_token: str = None) -> None:
    """Set up all dependencies for the Neural AI integration."""
    _LOGGER.info("Setting up Neural AI dependencies")

    # If no HA token provided, try to get it from credential manager
    if ha_token is None:
        try:
            from auth.credential_manager import CredentialManager
            credential_manager = CredentialManager()
            if credential_manager.has_credentials():
                stored_token = credential_manager.get_token()
                if stored_token:
                    ha_token = stored_token
                    _LOGGER.info("Using stored HA token from credential manager")
        except Exception as e:
            _LOGGER.debug("Could not load stored HA token: %s", e)

    # Create specific clients for each domain
    ai_client = AIClient(ai_url=ai_url, ai_model=ai_model)
    ha_client = HAClient(ha_url=ha_url, ha_token=ha_token)

    # Register the specific clients as singletons
    def get_ai_client():
        return ai_client

    def get_ha_client():
        return ha_client

    register_singleton(AIClient, get_ai_client)
    register_singleton(HAClient, get_ha_client)

    # Register repositories as singletons, each using their specific client
    def create_ai_repository():
        return AIRepositoryImpl(ai_client)

    def create_ha_repository():
        return HARepositoryImpl(ha_client)

    register_singleton(AIRepository, create_ai_repository)
    register_singleton(HARepository, create_ha_repository)

    # Register use cases as singletons
    def create_ai_use_case():
        ai_repo = create_ai_repository()
        return AIUseCaseImpl(ai_repo)

    def create_ha_use_case():
        ha_repo = create_ha_repository()
        return HAUseCaseImpl(ha_repo)

    register_singleton(AIUseCase, create_ai_use_case)
    register_singleton(HAUseCase, create_ha_use_case)

    _LOGGER.info("Neural AI dependencies setup completed")


def get_ai_use_case() -> AIUseCase:
    """Get the AI use case."""
    from .container import resolve

    return resolve(AIUseCase)


def get_ha_use_case() -> HAUseCase:
    """Get the Home Assistant use case."""
    from .container import resolve

    return resolve(HAUseCase)


# Client getters for direct access if needed
def get_ai_client() -> AIClient:
    """Get the AI client."""
    from .container import resolve

    return resolve(AIClient)


def get_ha_client() -> HAClient:
    """Get the Home Assistant client."""
    from .container import resolve

    return resolve(HAClient)


def clear_dependencies() -> None:
    """Clear all registered dependencies."""
    from .container import get_container

    container = get_container()
    container.clear()
    _LOGGER.info("Neural AI dependencies cleared")
