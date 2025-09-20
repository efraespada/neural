"""Unit tests for dependency injection container."""

import pytest
from unittest.mock import Mock, patch
from core.dependency_injection.injector_container import (
    Configuration, DependencyModule, DependencyContainer
)
from core.api.ai_client import AIClient
from core.api.ha_client import HAClient
from core.repositories.interfaces.ai_repository import AIRepository
from core.repositories.interfaces.ha_repository import HARepository
from core.use_cases.interfaces.ai_use_case import AIUseCase
from core.use_cases.interfaces.ha_use_case import HAUseCase


class TestConfiguration:
    """Test Configuration class."""

    def test_configuration_creation_with_defaults(self):
        """Test Configuration creation with default values."""
        # Act
        config = Configuration()
        
        # Assert
        assert config.ai_url == "http://localhost:1234"
        assert config.ai_model == "openai/gpt-oss-20b"
        assert config.ha_url == "http://homeassistant.local:8123"
        assert config.ha_token is None

    def test_configuration_creation_with_custom_values(self):
        """Test Configuration creation with custom values."""
        # Act
        config = Configuration(
            ai_url="http://custom-ai:8080",
            ai_model="custom-model",
            ha_url="http://custom-ha:8080",
            ha_token="custom-token"
        )
        
        # Assert
        assert config.ai_url == "http://custom-ai:8080"
        assert config.ai_model == "custom-model"
        assert config.ha_url == "http://custom-ha:8080"
        assert config.ha_token == "custom-token"


class TestDependencyModule:
    """Test DependencyModule class."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration(
            ai_url="http://test-ai:1234",
            ai_model="test-model",
            ha_url="http://test-ha:8123",
            ha_token="test-token"
        )

    @pytest.fixture
    def dependency_module(self, config):
        """Create dependency module."""
        return DependencyModule(config)

    def test_dependency_module_creation(self, dependency_module, config):
        """Test DependencyModule creation."""
        # Assert
        assert dependency_module.config == config

    @patch('core.dependency_injection.injector_container.AIClient')
    def test_provide_ai_client(self, mock_ai_client_class, dependency_module):
        """Test AI client provider."""
        # Arrange
        mock_ai_client = Mock()
        mock_ai_client_class.return_value = mock_ai_client
        
        # Act
        result = dependency_module.provide_ai_client()
        
        # Assert
        assert result == mock_ai_client
        mock_ai_client_class.assert_called_once_with(
            ai_url="http://test-ai:1234",
            ai_model="test-model"
        )

    @patch('core.dependency_injection.injector_container.HAClient')
    def test_provide_ha_client(self, mock_ha_client_class, dependency_module):
        """Test HA client provider."""
        # Arrange
        mock_ha_client = Mock()
        mock_ha_client_class.return_value = mock_ha_client
        
        # Act
        result = dependency_module.provide_ha_client()
        
        # Assert
        assert result == mock_ha_client
        mock_ha_client_class.assert_called_once_with(
            ha_url="http://test-ha:8123",
            ha_token="test-token"
        )

    @patch('core.dependency_injection.injector_container.AIRepositoryImpl')
    def test_provide_ai_repository(self, mock_ai_repo_class, dependency_module):
        """Test AI repository provider."""
        # Arrange
        mock_ai_client = Mock()
        mock_ai_repository = Mock()
        mock_ai_repo_class.return_value = mock_ai_repository
        
        # Act
        result = dependency_module.provide_ai_repository(mock_ai_client)
        
        # Assert
        assert result == mock_ai_repository
        mock_ai_repo_class.assert_called_once_with(mock_ai_client)

    @patch('core.dependency_injection.injector_container.HARepositoryImpl')
    def test_provide_ha_repository(self, mock_ha_repo_class, dependency_module):
        """Test HA repository provider."""
        # Arrange
        mock_ha_client = Mock()
        mock_ha_repository = Mock()
        mock_ha_repo_class.return_value = mock_ha_repository
        
        # Act
        result = dependency_module.provide_ha_repository(mock_ha_client)
        
        # Assert
        assert result == mock_ha_repository
        mock_ha_repo_class.assert_called_once_with(mock_ha_client)

    @patch('core.dependency_injection.injector_container.AIUseCaseImpl')
    def test_provide_ai_use_case(self, mock_ai_use_case_class, dependency_module):
        """Test AI use case provider."""
        # Arrange
        mock_ai_repository = Mock()
        mock_ai_use_case = Mock()
        mock_ai_use_case_class.return_value = mock_ai_use_case
        
        # Act
        result = dependency_module.provide_ai_use_case(mock_ai_repository)
        
        # Assert
        assert result == mock_ai_use_case
        mock_ai_use_case_class.assert_called_once_with(mock_ai_repository)

    @patch('core.dependency_injection.injector_container.HAUseCaseImpl')
    def test_provide_ha_use_case(self, mock_ha_use_case_class, dependency_module):
        """Test HA use case provider."""
        # Arrange
        mock_ha_repository = Mock()
        mock_ha_use_case = Mock()
        mock_ha_use_case_class.return_value = mock_ha_use_case
        
        # Act
        result = dependency_module.provide_ha_use_case(mock_ha_repository)
        
        # Assert
        assert result == mock_ha_use_case
        mock_ha_use_case_class.assert_called_once_with(mock_ha_repository)


class TestDependencyContainer:
    """Test DependencyContainer class."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration(
            ai_url="http://test-ai:1234",
            ai_model="test-model",
            ha_url="http://test-ha:8123",
            ha_token="test-token"
        )

    @pytest.fixture
    def container(self, config):
        """Create dependency container."""
        with patch('core.dependency_injection.injector_container.Injector') as mock_injector_class:
            mock_injector = Mock()
            mock_injector_class.return_value = mock_injector
            container = DependencyContainer(config)
            container._injector = mock_injector
            return container

    def test_container_creation(self, container, config):
        """Test DependencyContainer creation."""
        # Assert
        assert container._config == config
        assert hasattr(container, '_injector')

    def test_container_initialization(self, container):
        """Test container initialization with injector."""
        # Assert
        assert hasattr(container, '_injector')
        assert container._injector is not None

    def test_get_ai_use_case(self, container):
        """Test getting AI use case from container."""
        # Arrange
        mock_ai_use_case = Mock()
        container._injector.get.return_value = mock_ai_use_case
        
        # Act
        result = container.get(AIUseCase)
        
        # Assert
        assert result == mock_ai_use_case
        container._injector.get.assert_called_once_with(AIUseCase)

    def test_get_ha_use_case(self, container):
        """Test getting HA use case from container."""
        # Arrange
        mock_ha_use_case = Mock()
        container._injector.get.return_value = mock_ha_use_case
        
        # Act
        result = container.get(HAUseCase)
        
        # Assert
        assert result == mock_ha_use_case
        container._injector.get.assert_called_once_with(HAUseCase)

    def test_get_ai_repository(self, container):
        """Test getting AI repository from container."""
        # Arrange
        mock_ai_repository = Mock()
        container._injector.get.return_value = mock_ai_repository
        
        # Act
        result = container.get(AIRepository)
        
        # Assert
        assert result == mock_ai_repository
        container._injector.get.assert_called_once_with(AIRepository)

    def test_get_ha_repository(self, container):
        """Test getting HA repository from container."""
        # Arrange
        mock_ha_repository = Mock()
        container._injector.get.return_value = mock_ha_repository
        
        # Act
        result = container.get(HARepository)
        
        # Assert
        assert result == mock_ha_repository
        container._injector.get.assert_called_once_with(HARepository)

    def test_get_ai_client(self, container):
        """Test getting AI client from container."""
        # Arrange
        mock_ai_client = Mock()
        container._injector.get.return_value = mock_ai_client
        
        # Act
        result = container.get(AIClient)
        
        # Assert
        assert result == mock_ai_client
        container._injector.get.assert_called_once_with(AIClient)

    def test_get_ha_client(self, container):
        """Test getting HA client from container."""
        # Arrange
        mock_ha_client = Mock()
        container._injector.get.return_value = mock_ha_client
        
        # Act
        result = container.get(HAClient)
        
        # Assert
        assert result == mock_ha_client
        container._injector.get.assert_called_once_with(HAClient)

    def test_container_singleton_behavior(self, container):
        """Test that container returns same instance for singletons."""
        # Arrange
        mock_ai_use_case = Mock()
        container._injector.get.return_value = mock_ai_use_case
        
        # Act
        result1 = container.get(AIUseCase)
        result2 = container.get(AIUseCase)
        
        # Assert
        assert result1 == result2
        assert result1 == mock_ai_use_case
        # Should be called twice since we're getting the same instance
        assert container._injector.get.call_count == 2

    def test_container_dependency_resolution(self, container):
        """Test that container properly resolves dependencies."""
        # Arrange
        mock_ai_use_case = Mock()
        mock_ai_repository = Mock()
        mock_ai_client = Mock()
        
        # Configure the injector to return different mocks for different types
        def mock_get(interface):
            if interface == AIUseCase:
                return mock_ai_use_case
            elif interface == AIRepository:
                return mock_ai_repository
            elif interface == AIClient:
                return mock_ai_client
            return Mock()
        
        container._injector.get.side_effect = mock_get
        
        # Act
        ai_use_case = container.get(AIUseCase)
        ai_repository = container.get(AIRepository)
        ai_client = container.get(AIClient)
        
        # Assert
        assert ai_use_case == mock_ai_use_case
        assert ai_repository == mock_ai_repository
        assert ai_client == mock_ai_client

    def test_container_error_handling(self, container):
        """Test container error handling."""
        # Arrange
        container._injector.get.side_effect = Exception("Dependency resolution failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Dependency resolution failed"):
            container.get(AIUseCase)

    def test_container_configuration_access(self, container, config):
        """Test that container provides access to configuration."""
        # Assert
        assert container._config == config
        assert container._config.ai_url == "http://test-ai:1234"
        assert container._config.ai_model == "test-model"
        assert container._config.ha_url == "http://test-ha:8123"
        assert container._config.ha_token == "test-token"
