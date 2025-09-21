"""Unit tests for AI use case interface."""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from core.api.models.domain.ai import AIStatus, AIResponse, AIModel
from core.use_cases.interfaces.ai_use_case import AIUseCase
from core.use_cases.implementations.ai_use_case_impl import AIUseCaseImpl


class TestAIUseCaseInterface:
    """Test AI use case interface behavior."""

    @pytest.fixture
    def mock_ai_repository(self):
        """Create mock AI repository."""
        return AsyncMock()

    @pytest.fixture
    def ai_use_case(self, mock_ai_repository):
        """Create AI use case with mocked repository."""
        return AIUseCaseImpl(mock_ai_repository)

    @pytest.mark.asyncio
    async def test_send_message_success(self, ai_use_case, mock_ai_repository):
        """Test successful message sending."""
        # Arrange
        message = "Test message"
        model = "test-model"
        expected_response = AIResponse(
            message=message,
            response="Test response",
            model=model,
            response_time=1.5,
            timestamp=datetime.now()
        )
        mock_ai_repository.send_message.return_value = expected_response

        # Act
        result = await ai_use_case.send_message(message, model)

        # Assert
        assert result == expected_response
        mock_ai_repository.send_message.assert_called_once_with(message, model)

    @pytest.mark.asyncio
    async def test_send_message_without_model(self, ai_use_case, mock_ai_repository):
        """Test message sending without specifying model."""
        # Arrange
        message = "Test message"
        expected_response = AIResponse(
            message=message,
            response="Test response",
            model="default-model",
            response_time=1.5,
            timestamp=datetime.now()
        )
        mock_ai_repository.send_message.return_value = expected_response

        # Act
        result = await ai_use_case.send_message(message)

        # Assert
        assert result == expected_response
        mock_ai_repository.send_message.assert_called_once_with(message, None)

    @pytest.mark.asyncio
    async def test_send_message_repository_exception(self, ai_use_case, mock_ai_repository):
        """Test message sending when repository raises exception."""
        # Arrange
        message = "Test message"
        mock_ai_repository.send_message.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ai_use_case.send_message(message)

    @pytest.mark.asyncio
    async def test_get_status_success(self, ai_use_case, mock_ai_repository):
        """Test successful status retrieval."""
        # Arrange
        expected_status = AIStatus(
            status="ready",
            url="http://localhost:1234",
            model="test-model",
            available_models=["model1", "model2"],
            last_updated=datetime.now()
        )
        mock_ai_repository.get_status.return_value = expected_status

        # Act
        result = await ai_use_case.get_status()

        # Assert
        assert result == expected_status
        mock_ai_repository.get_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_status_repository_exception(self, ai_use_case, mock_ai_repository):
        """Test status retrieval when repository raises exception."""
        # Arrange
        mock_ai_repository.get_status.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ai_use_case.get_status()

    @pytest.mark.asyncio
    async def test_list_models_success(self, ai_use_case, mock_ai_repository):
        """Test successful model listing."""
        # Arrange
        models = [
            AIModel(name="model1"),
            AIModel(name="model2"),
            AIModel(name="model3")
        ]
        mock_ai_repository.list_models.return_value = models

        # Act
        result = await ai_use_case.list_models()

        # Assert
        assert result == ["model1", "model2", "model3"]
        mock_ai_repository.list_models.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_models_repository_exception(self, ai_use_case, mock_ai_repository):
        """Test model listing when repository raises exception."""
        # Arrange
        mock_ai_repository.list_models.side_effect = Exception("Repository error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            await ai_use_case.list_models()

    @pytest.mark.asyncio
    async def test_test_connection_success(self, ai_use_case, mock_ai_repository):
        """Test successful connection test."""
        # Arrange
        mock_ai_repository.test_connection.return_value = True

        # Act
        result = await ai_use_case.test_connection()

        # Assert
        assert result is True
        mock_ai_repository.test_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, ai_use_case, mock_ai_repository):
        """Test connection test failure."""
        # Arrange
        mock_ai_repository.test_connection.return_value = False

        # Act
        result = await ai_use_case.test_connection()

        # Assert
        assert result is False
        mock_ai_repository.test_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_repository_exception(self, ai_use_case, mock_ai_repository):
        """Test connection test when repository raises exception."""
        # Arrange
        mock_ai_repository.test_connection.side_effect = Exception("Repository error")

        # Act
        result = await ai_use_case.test_connection()

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_is_model_ready_success(self, ai_use_case, mock_ai_repository):
        """Test successful model ready check."""
        # Arrange
        mock_ai_repository.is_model_ready.return_value = True

        # Act
        result = await ai_use_case.is_model_ready()

        # Assert
        assert result is True
        mock_ai_repository.is_model_ready.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_model_ready_not_ready(self, ai_use_case, mock_ai_repository):
        """Test model not ready."""
        # Arrange
        mock_ai_repository.is_model_ready.return_value = False

        # Act
        result = await ai_use_case.is_model_ready()

        # Assert
        assert result is False
        mock_ai_repository.is_model_ready.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_model_ready_repository_exception(self, ai_use_case, mock_ai_repository):
        """Test model ready check when repository raises exception."""
        # Arrange
        mock_ai_repository.is_model_ready.side_effect = Exception("Repository error")

        # Act
        result = await ai_use_case.is_model_ready()

        # Assert
        assert result is False
