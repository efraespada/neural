"""Unit tests for AI repository interface."""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from api.models.domain.ai import AIStatus, AIResponse, AIModel
from repositories.interfaces.ai_repository import AIRepository
from repositories.implementations.ai_repository_impl import AIRepositoryImpl


class TestAIRepositoryInterface:
    """Test AI repository interface behavior."""

    @pytest.fixture
    def mock_ai_client(self):
        """Create mock AI client."""
        return AsyncMock()

    @pytest.fixture
    def ai_repository(self, mock_ai_client):
        """Create AI repository with mocked client."""
        return AIRepositoryImpl(mock_ai_client)

    @pytest.mark.asyncio
    async def test_send_message_success(self, ai_repository, mock_ai_client):
        """Test successful message sending."""
        # Arrange
        message = "Test message"
        model = "test-model"
        response_text = "Test response"
        mock_ai_client._session = Mock()  # Simulate connected session
        mock_ai_client._ai_model = "test-model"
        mock_ai_client.send_message.return_value = response_text

        # Act
        result = await ai_repository.send_message(message, model)

        # Assert
        assert isinstance(result, AIResponse)
        assert result.message == message
        assert result.response == response_text
        assert result.model == model
        assert result.response_time is not None
        assert result.timestamp is not None
        mock_ai_client.send_message.assert_called_once_with(message, model)

    @pytest.mark.asyncio
    async def test_send_message_auto_connects(self, ai_repository, mock_ai_client):
        """Test that repository auto-connects when session is None."""
        # Arrange
        message = "Test message"
        response_text = "Test response"
        mock_ai_client._session = None  # No session
        mock_ai_client._ai_model = "default-model"
        mock_ai_client.send_message.return_value = response_text

        # Act
        result = await ai_repository.send_message(message)

        # Assert
        mock_ai_client.connect.assert_called_once()
        mock_ai_client.send_message.assert_called_once_with(message, None)

    @pytest.mark.asyncio
    async def test_send_message_client_exception(self, ai_repository, mock_ai_client):
        """Test message sending when client raises exception."""
        # Arrange
        message = "Test message"
        mock_ai_client._session = Mock()
        mock_ai_client.send_message.side_effect = Exception("Client error")

        # Act & Assert
        with pytest.raises(Exception, match="Client error"):
            await ai_repository.send_message(message)

    @pytest.mark.asyncio
    async def test_get_status_success(self, ai_repository, mock_ai_client):
        """Test successful status retrieval."""
        # Arrange
        status_data = {
            "status": "ready",
            "url": "http://localhost:1234",
            "model": "test-model",
            "available_models": ["model1", "model2"]
        }
        mock_ai_client._session = Mock()
        mock_ai_client._ai_url = "http://localhost:1234"
        mock_ai_client._ai_model = "test-model"
        mock_ai_client.get_status.return_value = status_data

        # Act
        result = await ai_repository.get_status()

        # Assert
        assert isinstance(result, AIStatus)
        assert result.status == "ready"
        assert result.url == "http://localhost:1234"
        assert result.model == "test-model"
        assert result.available_models == ["model1", "model2"]
        assert result.error is None
        assert result.last_updated is not None
        mock_ai_client.get_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_status_auto_connects(self, ai_repository, mock_ai_client):
        """Test that repository auto-connects when session is None."""
        # Arrange
        status_data = {"status": "ready"}
        mock_ai_client._session = None
        mock_ai_client._ai_url = "http://localhost:1234"
        mock_ai_client._ai_model = "test-model"
        mock_ai_client.get_status.return_value = status_data

        # Act
        result = await ai_repository.get_status()

        # Assert
        mock_ai_client.connect.assert_called_once()
        assert result.status == "ready"

    @pytest.mark.asyncio
    async def test_get_status_client_exception(self, ai_repository, mock_ai_client):
        """Test status retrieval when client raises exception."""
        # Arrange
        mock_ai_client._session = Mock()
        mock_ai_client._ai_url = "http://localhost:1234"
        mock_ai_client._ai_model = "test-model"
        mock_ai_client.get_status.side_effect = Exception("Client error")

        # Act
        result = await ai_repository.get_status()

        # Assert
        assert isinstance(result, AIStatus)
        assert result.status == "error"
        assert result.error == "Client error"
        assert result.last_updated is not None

    @pytest.mark.asyncio
    async def test_list_models_success(self, ai_repository, mock_ai_client):
        """Test successful model listing."""
        # Arrange
        model_names = ["model1", "model2", "model3"]
        mock_ai_client._session = Mock()
        mock_ai_client.list_models.return_value = model_names

        # Act
        result = await ai_repository.list_models()

        # Assert
        assert len(result) == 3
        assert all(isinstance(model, AIModel) for model in result)
        assert [model.name for model in result] == model_names
        mock_ai_client.list_models.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_models_auto_connects(self, ai_repository, mock_ai_client):
        """Test that repository auto-connects when session is None."""
        # Arrange
        model_names = ["model1", "model2"]
        mock_ai_client._session = None
        mock_ai_client.list_models.return_value = model_names

        # Act
        result = await ai_repository.list_models()

        # Assert
        mock_ai_client.connect.assert_called_once()
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_list_models_client_exception(self, ai_repository, mock_ai_client):
        """Test model listing when client raises exception."""
        # Arrange
        mock_ai_client._session = Mock()
        mock_ai_client.list_models.side_effect = Exception("Client error")

        # Act
        result = await ai_repository.list_models()

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_test_connection_success(self, ai_repository, mock_ai_client):
        """Test successful connection test."""
        # Arrange
        mock_ai_client._session = Mock()
        mock_ai_client._test_connection.return_value = True

        # Act
        result = await ai_repository.test_connection()

        # Assert
        assert result is True
        mock_ai_client._test_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_auto_connects(self, ai_repository, mock_ai_client):
        """Test that repository auto-connects when session is None."""
        # Arrange
        mock_ai_client._session = None
        mock_ai_client._test_connection.return_value = True

        # Act
        result = await ai_repository.test_connection()

        # Assert
        mock_ai_client.connect.assert_called_once()
        assert result is True

    @pytest.mark.asyncio
    async def test_test_connection_client_exception(self, ai_repository, mock_ai_client):
        """Test connection test when client raises exception."""
        # Arrange
        mock_ai_client._session = Mock()
        mock_ai_client._test_connection.side_effect = Exception("Client error")

        # Act
        result = await ai_repository.test_connection()

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_is_model_ready_success(self, ai_repository, mock_ai_client):
        """Test successful model ready check."""
        # Arrange
        mock_ai_client._session = Mock()
        mock_ai_client.is_model_ready.return_value = True

        # Act
        result = await ai_repository.is_model_ready()

        # Assert
        assert result is True
        mock_ai_client.is_model_ready.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_model_ready_auto_connects(self, ai_repository, mock_ai_client):
        """Test that repository auto-connects when session is None."""
        # Arrange
        mock_ai_client._session = None
        mock_ai_client.is_model_ready.return_value = True

        # Act
        result = await ai_repository.is_model_ready()

        # Assert
        mock_ai_client.connect.assert_called_once()
        assert result is True

    @pytest.mark.asyncio
    async def test_is_model_ready_client_exception(self, ai_repository, mock_ai_client):
        """Test model ready check when client raises exception."""
        # Arrange
        mock_ai_client._session = Mock()
        mock_ai_client.is_model_ready.side_effect = Exception("Client error")

        # Act
        result = await ai_repository.is_model_ready()

        # Assert
        assert result is False
