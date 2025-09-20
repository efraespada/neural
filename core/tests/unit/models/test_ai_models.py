"""Unit tests for AI domain models."""

import pytest
from datetime import datetime
from core.api.models.domain.ai import AIStatus, AIChat, AIResponse, AIModel


class TestAIStatus:
    """Test AIStatus model."""

    def test_ai_status_creation(self):
        """Test AIStatus creation with all fields."""
        # Arrange
        now = datetime.now()
        
        # Act
        status = AIStatus(
            status="ready",
            url="http://localhost:1234",
            model="test-model",
            available_models=["model1", "model2"],
            error=None,
            last_updated=now
        )
        
        # Assert
        assert status.status == "ready"
        assert status.url == "http://localhost:1234"
        assert status.model == "test-model"
        assert status.available_models == ["model1", "model2"]
        assert status.error is None
        assert status.last_updated == now

    def test_ai_status_creation_with_error(self):
        """Test AIStatus creation with error."""
        # Arrange
        now = datetime.now()
        
        # Act
        status = AIStatus(
            status="error",
            url="http://localhost:1234",
            model="test-model",
            available_models=[],
            error="Connection failed",
            last_updated=now
        )
        
        # Assert
        assert status.status == "error"
        assert status.error == "Connection failed"

    def test_ai_status_to_dict(self):
        """Test AIStatus to_dict method."""
        # Arrange
        now = datetime.now()
        status = AIStatus(
            status="ready",
            url="http://localhost:1234",
            model="test-model",
            available_models=["model1", "model2"],
            error=None,
            last_updated=now
        )
        
        # Act
        result = status.to_dict()
        
        # Assert
        assert result["status"] == "ready"
        assert result["url"] == "http://localhost:1234"
        assert result["model"] == "test-model"
        assert result["available_models"] == ["model1", "model2"]
        assert result["error"] is None
        assert result["last_updated"] == now.isoformat()

    def test_ai_status_from_dict(self):
        """Test AIStatus from_dict method."""
        # Arrange
        now = datetime.now()
        data = {
            "status": "ready",
            "url": "http://localhost:1234",
            "model": "test-model",
            "available_models": ["model1", "model2"],
            "error": None,
            "last_updated": now.isoformat()
        }
        
        # Act
        status = AIStatus.from_dict(data)
        
        # Assert
        assert status.status == "ready"
        assert status.url == "http://localhost:1234"
        assert status.model == "test-model"
        assert status.available_models == ["model1", "model2"]
        assert status.error is None
        assert status.last_updated == now

    def test_ai_status_from_dict_with_missing_fields(self):
        """Test AIStatus from_dict with missing fields."""
        # Arrange
        data = {
            "status": "ready",
            "url": "http://localhost:1234"
        }
        
        # Act
        status = AIStatus.from_dict(data)
        
        # Assert
        assert status.status == "ready"
        assert status.url == "http://localhost:1234"
        assert status.model == ""
        assert status.available_models == []
        assert status.error is None
        assert status.last_updated is None


class TestAIChat:
    """Test AIChat model."""

    def test_ai_chat_creation(self):
        """Test AIChat creation with all fields."""
        # Arrange
        now = datetime.now()
        
        # Act
        chat = AIChat(
            message="Hello",
            response="Hi there!",
            model="test-model",
            timestamp=now,
            tokens_used=100,
            response_time=1.5
        )
        
        # Assert
        assert chat.message == "Hello"
        assert chat.response == "Hi there!"
        assert chat.model == "test-model"
        assert chat.timestamp == now
        assert chat.tokens_used == 100
        assert chat.response_time == 1.5

    def test_ai_chat_creation_minimal(self):
        """Test AIChat creation with minimal fields."""
        # Arrange
        now = datetime.now()
        
        # Act
        chat = AIChat(
            message="Hello",
            response="Hi there!",
            model="test-model",
            timestamp=now
        )
        
        # Assert
        assert chat.message == "Hello"
        assert chat.response == "Hi there!"
        assert chat.model == "test-model"
        assert chat.timestamp == now
        assert chat.tokens_used is None
        assert chat.response_time is None

    def test_ai_chat_to_dict(self):
        """Test AIChat to_dict method."""
        # Arrange
        now = datetime.now()
        chat = AIChat(
            message="Hello",
            response="Hi there!",
            model="test-model",
            timestamp=now,
            tokens_used=100,
            response_time=1.5
        )
        
        # Act
        result = chat.to_dict()
        
        # Assert
        assert result["message"] == "Hello"
        assert result["response"] == "Hi there!"
        assert result["model"] == "test-model"
        assert result["timestamp"] == now.isoformat()
        assert result["tokens_used"] == 100
        assert result["response_time"] == 1.5

    def test_ai_chat_from_dict(self):
        """Test AIChat from_dict method."""
        # Arrange
        now = datetime.now()
        data = {
            "message": "Hello",
            "response": "Hi there!",
            "model": "test-model",
            "timestamp": now.isoformat(),
            "tokens_used": 100,
            "response_time": 1.5
        }
        
        # Act
        chat = AIChat.from_dict(data)
        
        # Assert
        assert chat.message == "Hello"
        assert chat.response == "Hi there!"
        assert chat.model == "test-model"
        assert chat.timestamp == now
        assert chat.tokens_used == 100
        assert chat.response_time == 1.5

    def test_ai_chat_from_dict_with_missing_timestamp(self):
        """Test AIChat from_dict with missing timestamp."""
        # Arrange
        data = {
            "message": "Hello",
            "response": "Hi there!",
            "model": "test-model"
        }
        
        # Act
        chat = AIChat.from_dict(data)
        
        # Assert
        assert chat.message == "Hello"
        assert chat.response == "Hi there!"
        assert chat.model == "test-model"
        assert isinstance(chat.timestamp, datetime)


class TestAIResponse:
    """Test AIResponse model."""

    def test_ai_response_creation(self):
        """Test AIResponse creation with all fields."""
        # Arrange
        now = datetime.now()
        
        # Act
        response = AIResponse(
            message="Hello",
            response="Hi there!",
            model="test-model",
            tokens_used=100,
            response_time=1.5,
            timestamp=now
        )
        
        # Assert
        assert response.message == "Hello"
        assert response.response == "Hi there!"
        assert response.model == "test-model"
        assert response.tokens_used == 100
        assert response.response_time == 1.5
        assert response.timestamp == now

    def test_ai_response_creation_minimal(self):
        """Test AIResponse creation with minimal fields."""
        # Act
        response = AIResponse(
            message="Hello",
            response="Hi there!",
            model="test-model"
        )
        
        # Assert
        assert response.message == "Hello"
        assert response.response == "Hi there!"
        assert response.model == "test-model"
        assert response.tokens_used is None
        assert response.response_time is None
        assert response.timestamp is None

    def test_ai_response_to_dict(self):
        """Test AIResponse to_dict method."""
        # Arrange
        now = datetime.now()
        response = AIResponse(
            message="Hello",
            response="Hi there!",
            model="test-model",
            tokens_used=100,
            response_time=1.5,
            timestamp=now
        )
        
        # Act
        result = response.to_dict()
        
        # Assert
        assert result["message"] == "Hello"
        assert result["response"] == "Hi there!"
        assert result["model"] == "test-model"
        assert result["tokens_used"] == 100
        assert result["response_time"] == 1.5
        assert result["timestamp"] == now.isoformat()

    def test_ai_response_to_dict_with_none_timestamp(self):
        """Test AIResponse to_dict with None timestamp."""
        # Arrange
        response = AIResponse(
            message="Hello",
            response="Hi there!",
            model="test-model"
        )
        
        # Act
        result = response.to_dict()
        
        # Assert
        assert result["timestamp"] is None

    def test_ai_response_from_dict(self):
        """Test AIResponse from_dict method."""
        # Arrange
        now = datetime.now()
        data = {
            "message": "Hello",
            "response": "Hi there!",
            "model": "test-model",
            "tokens_used": 100,
            "response_time": 1.5,
            "timestamp": now.isoformat()
        }
        
        # Act
        response = AIResponse.from_dict(data)
        
        # Assert
        assert response.message == "Hello"
        assert response.response == "Hi there!"
        assert response.model == "test-model"
        assert response.tokens_used == 100
        assert response.response_time == 1.5
        assert response.timestamp == now

    def test_ai_response_from_dict_with_missing_fields(self):
        """Test AIResponse from_dict with missing fields."""
        # Arrange
        data = {
            "message": "Hello",
            "response": "Hi there!"
        }
        
        # Act
        response = AIResponse.from_dict(data)
        
        # Assert
        assert response.message == "Hello"
        assert response.response == "Hi there!"
        assert response.model == ""
        assert response.tokens_used is None
        assert response.response_time is None
        assert response.timestamp is None


class TestAIModel:
    """Test AIModel model."""

    def test_ai_model_creation(self):
        """Test AIModel creation with all fields."""
        # Arrange
        now = datetime.now()
        
        # Act
        model = AIModel(
            name="test-model",
            size=1000000,
            modified_at=now,
            digest="abc123"
        )
        
        # Assert
        assert model.name == "test-model"
        assert model.size == 1000000
        assert model.modified_at == now
        assert model.digest == "abc123"

    def test_ai_model_creation_minimal(self):
        """Test AIModel creation with minimal fields."""
        # Act
        model = AIModel(name="test-model")
        
        # Assert
        assert model.name == "test-model"
        assert model.size is None
        assert model.modified_at is None
        assert model.digest is None

    def test_ai_model_to_dict(self):
        """Test AIModel to_dict method."""
        # Arrange
        now = datetime.now()
        model = AIModel(
            name="test-model",
            size=1000000,
            modified_at=now,
            digest="abc123"
        )
        
        # Act
        result = model.to_dict()
        
        # Assert
        assert result["name"] == "test-model"
        assert result["size"] == 1000000
        assert result["modified_at"] == now.isoformat()
        assert result["digest"] == "abc123"

    def test_ai_model_to_dict_with_none_modified_at(self):
        """Test AIModel to_dict with None modified_at."""
        # Arrange
        model = AIModel(name="test-model")
        
        # Act
        result = model.to_dict()
        
        # Assert
        assert result["modified_at"] is None

    def test_ai_model_from_dict(self):
        """Test AIModel from_dict method."""
        # Arrange
        now = datetime.now()
        data = {
            "name": "test-model",
            "size": 1000000,
            "modified_at": now.isoformat(),
            "digest": "abc123"
        }
        
        # Act
        model = AIModel.from_dict(data)
        
        # Assert
        assert model.name == "test-model"
        assert model.size == 1000000
        assert model.modified_at == now
        assert model.digest == "abc123"

    def test_ai_model_from_dict_with_missing_fields(self):
        """Test AIModel from_dict with missing fields."""
        # Arrange
        data = {"name": "test-model"}
        
        # Act
        model = AIModel.from_dict(data)
        
        # Assert
        assert model.name == "test-model"
        assert model.size is None
        assert model.modified_at is None
        assert model.digest is None
