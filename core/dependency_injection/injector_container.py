"""Professional dependency injection container using injector library."""

import logging
from typing import Type, TypeVar, Optional, Any
from injector import Injector, inject, singleton, provider, Module

from ..api.ai_client import AIClient
from ..api.ha_client import HAClient
from ..repositories.interfaces.ai_repository import AIRepository
from ..repositories.interfaces.ha_repository import HARepository
from ..repositories.interfaces.file_repository import FileRepository
from ..repositories.implementations.ai_repository_impl import AIRepositoryImpl
from ..repositories.implementations.ha_repository_impl import HARepositoryImpl
from ..repositories.implementations.file_repository_impl import FileRepositoryImpl
from ..use_cases.interfaces.ai_use_case import AIUseCase
from ..use_cases.interfaces.ha_use_case import HAUseCase
from ..use_cases.implementations.ai_use_case_impl import AIUseCaseImpl
from ..use_cases.implementations.ha_use_case_impl import HAUseCaseImpl

T = TypeVar("T")
_LOGGER = logging.getLogger(__name__)


class Configuration:
    """Configuration class for dependency injection."""
    
    def __init__(self, 
                 ai_url: str = "http://localhost:1234",
                 ai_model: str = "openai/gpt-oss-20b",
                 ha_url: str = "http://homeassistant.local:8123",
                 ha_token: Optional[str] = None,
                 file_base_path: str = "."):
        """Initialize configuration."""
        self.ai_url = ai_url
        self.ai_model = ai_model
        self.ha_url = ha_url
        self.ha_token = ha_token
        self.file_base_path = file_base_path


class DependencyModule(Module):
    """Dependency injection module using injector."""
    
    def __init__(self, config: Configuration):
        """Initialize the module with configuration."""
        super().__init__()
        self.config = config
    
    @provider
    @singleton
    def provide_ai_client(self) -> AIClient:
        """Provide AI client as singleton."""
        _LOGGER.info("Creating AI client with URL: %s, Model: %s", 
                    self.config.ai_url, self.config.ai_model)
        return AIClient(ai_url=self.config.ai_url, ai_model=self.config.ai_model)
    
    @provider
    @singleton
    def provide_ha_client(self) -> HAClient:
        """Provide HA client as singleton."""
        _LOGGER.info("Creating HA client with URL: %s", self.config.ha_url)
        return HAClient(ha_url=self.config.ha_url, ha_token=self.config.ha_token)
    
    @provider
    @singleton
    def provide_ai_repository(self, ai_client: AIClient) -> AIRepository:
        """Provide AI repository as singleton."""
        _LOGGER.debug("Creating AI repository")
        return AIRepositoryImpl(ai_client)
    
    @provider
    @singleton
    def provide_ha_repository(self, ha_client: HAClient) -> HARepository:
        """Provide HA repository as singleton."""
        _LOGGER.debug("Creating HA repository")
        return HARepositoryImpl(ha_client)
    
    @provider
    @singleton
    def provide_ai_use_case(self, ai_repository: AIRepository) -> AIUseCase:
        """Provide AI use case as singleton."""
        _LOGGER.debug("Creating AI use case")
        return AIUseCaseImpl(ai_repository)
    
    @provider
    @singleton
    def provide_ha_use_case(self, ha_repository: HARepository) -> HAUseCase:
        """Provide HA use case as singleton."""
        _LOGGER.debug("Creating HA use case")
        return HAUseCaseImpl(ha_repository)
    
    @provider
    @singleton
    def provide_file_repository(self) -> FileRepository:
        """Provide File repository as singleton."""
        _LOGGER.debug("Creating File repository with base path: %s", self.config.file_base_path)
        return FileRepositoryImpl(base_path=self.config.file_base_path)


class DependencyContainer:
    """Professional dependency injection container using injector."""
    
    def __init__(self, config: Optional[Configuration] = None):
        """Initialize the container."""
        if config is None:
            config = Configuration()
        
        # Create module instance with config
        module = DependencyModule(config)
        self._injector = Injector([module])
        self._config = config
        _LOGGER.info("Dependency container initialized with injector")
    
    def get(self, interface: Type[T]) -> T:
        """Get a dependency by type."""
        try:
            return self._injector.get(interface)
        except Exception as e:
            _LOGGER.error("Failed to resolve dependency %s: %s", interface, e)
            raise
    
    def get_optional(self, interface: Type[T]) -> Optional[T]:
        """Get a dependency by type if available."""
        try:
            return self._injector.get(interface)
        except Exception:
            return None
    
    def create_child_injector(self, modules=None):
        """Create a child injector with additional modules."""
        if modules is None:
            modules = []
        return self._injector.create_child_injector(modules)
    
    def clear(self):
        """Clear the container (not supported by injector, but kept for compatibility)."""
        _LOGGER.warning("Clear operation not supported by injector - container remains active")


# Global container instance
_container: Optional[DependencyContainer] = None


def initialize_container(config: Optional[Configuration] = None) -> DependencyContainer:
    """Initialize the global dependency container."""
    global _container
    if _container is None:
        _container = DependencyContainer(config)
        _LOGGER.info("Global dependency container initialized")
    return _container


def get_container() -> DependencyContainer:
    """Get the global dependency container."""
    global _container
    if _container is None:
        _LOGGER.warning("Container not initialized, creating with default config")
        _container = DependencyContainer()
    return _container


def get(interface: Type[T]) -> T:
    """Get a dependency from the global container."""
    return get_container().get(interface)


def get_optional(interface: Type[T]) -> Optional[T]:
    """Get a dependency from the global container if available."""
    return get_container().get_optional(interface)


# Convenience functions for common dependencies
def get_ai_use_case() -> AIUseCase:
    """Get the AI use case."""
    return get(AIUseCase)


def get_ha_use_case() -> HAUseCase:
    """Get the Home Assistant use case."""
    return get(HAUseCase)


def get_ai_client() -> AIClient:
    """Get the AI client."""
    return get(AIClient)


def get_ha_client() -> HAClient:
    """Get the Home Assistant client."""
    return get(HAClient)


def get_ai_repository() -> AIRepository:
    """Get the AI repository."""
    return get(AIRepository)


def get_ha_repository() -> HARepository:
    """Get the HA repository."""
    return get(HARepository)


def get_file_repository() -> FileRepository:
    """Get the File repository."""
    return get(FileRepository)
