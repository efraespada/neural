"""Unit tests for DecisionUseCase interface and implementation."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List

from core.use_cases.interfaces.decision_use_case import DecisionUseCase, DecisionResponse, DecisionAction
from core.use_cases.implementations.decision_use_case_impl import DecisionUseCaseImpl
from core.use_cases.interfaces.ai_use_case import AIUseCase
from core.use_cases.interfaces.ha_use_case import HAUseCase
from core.api.models.domain.ai import AIResponse, AIChat
from core.api.models.domain.ha_entity import HAEntity, HAEntityState


@pytest.fixture
def mock_ai_use_case():
    """Mock AI use case."""
    return AsyncMock(spec=AIUseCase)


@pytest.fixture
def mock_ha_use_case():
    """Mock HA use case."""
    return AsyncMock(spec=HAUseCase)


@pytest.fixture
def decision_use_case(mock_ai_use_case, mock_ha_use_case):
    """Create DecisionUseCaseImpl instance with mocked dependencies."""
    return DecisionUseCaseImpl(mock_ai_use_case, mock_ha_use_case)


class TestDecisionUseCaseInterface:
    """Test DecisionUseCase interface behavior."""
    
    @pytest.mark.asyncio
    async def test_make_decision_success(self, decision_use_case, mock_ai_use_case, mock_ha_use_case):
        """Test successful decision making."""
        # Arrange
        user_prompt = "Enciende las luces del salón"
        mode = "assistant"
        
        # Mock HA entities
        mock_entity = HAEntity(
            entity_id="light.living_room",
            state="off",
            attributes={"friendly_name": "Living Room Light"},
            last_changed="2023-01-01T00:00:00Z",
            last_updated="2023-01-01T00:00:00Z",
            context={"id": "test"}
        )
        mock_ha_use_case.get_all_entities.return_value = [mock_entity]
        mock_ha_use_case.get_sensors.return_value = []
        
        # Mock AI response
        ai_response_data = {
            "message": "De acuerdo, enciendo las luces del salón",
            "actions": [
                {"entity": "light.living_room", "action": "turn_on"}
            ]
        }
        mock_ai_response = AIResponse(
            content=json.dumps(ai_response_data),
            model="test-model",
            usage={"prompt_tokens": 100, "completion_tokens": 50}
        )
        mock_ai_use_case.send_message.return_value = mock_ai_response
        
        # Act
        result = await decision_use_case.make_decision(user_prompt, mode)
        
        # Assert
        assert isinstance(result, DecisionResponse)
        assert result.message == "De acuerdo, enciendo las luces del salón"
        assert len(result.actions) == 1
        assert result.actions[0].entity == "light.living_room"
        assert result.actions[0].action == "turn_on"
        
        # Verify calls
        mock_ha_use_case.get_all_entities.assert_called_once()
        mock_ha_use_case.get_sensors.assert_called_once()
        mock_ai_use_case.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_decision_empty_prompt(self, decision_use_case):
        """Test decision making with empty prompt."""
        # Act & Assert
        with pytest.raises(ValueError, match="User prompt cannot be empty"):
            await decision_use_case.make_decision("", "assistant")
    
    @pytest.mark.asyncio
    async def test_make_decision_invalid_mode(self, decision_use_case):
        """Test decision making with invalid mode."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid mode"):
            await decision_use_case.make_decision("test prompt", "invalid_mode")
    
    @pytest.mark.asyncio
    async def test_make_decision_ha_error(self, decision_use_case, mock_ha_use_case):
        """Test decision making when HA fails."""
        # Arrange
        mock_ha_use_case.get_all_entities.side_effect = OSError("HA connection failed")
        
        # Act & Assert
        with pytest.raises(OSError, match="Error getting Home Assistant information"):
            await decision_use_case.make_decision("test prompt", "assistant")
    
    @pytest.mark.asyncio
    async def test_make_decision_ai_error(self, decision_use_case, mock_ai_use_case, mock_ha_use_case):
        """Test decision making when AI fails."""
        # Arrange
        mock_ha_use_case.get_all_entities.return_value = []
        mock_ha_use_case.get_sensors.return_value = []
        mock_ai_use_case.send_message.side_effect = OSError("AI connection failed")
        
        # Act & Assert
        with pytest.raises(OSError, match="AI connection failed"):
            await decision_use_case.make_decision("test prompt", "assistant")
    
    @pytest.mark.asyncio
    async def test_get_ha_information_success(self, decision_use_case, mock_ha_use_case):
        """Test getting HA information successfully."""
        # Arrange
        mock_entity = HAEntity(
            entity_id="light.test",
            state="off",
            attributes={"friendly_name": "Test Light"},
            last_changed="2023-01-01T00:00:00Z",
            last_updated="2023-01-01T00:00:00Z",
            context={"id": "test"}
        )
        mock_ha_use_case.get_all_entities.return_value = [mock_entity]
        mock_ha_use_case.get_sensors.return_value = []
        
        # Act
        result = await decision_use_case.get_ha_information()
        
        # Assert
        assert isinstance(result, str)
        ha_info = json.loads(result)
        assert "entities" in ha_info
        assert "sensors" in ha_info
        assert "services" in ha_info
        assert len(ha_info["entities"]) == 1
        assert ha_info["entities"][0]["entity_id"] == "light.test"
    
    @pytest.mark.asyncio
    async def test_get_ha_information_error(self, decision_use_case, mock_ha_use_case):
        """Test getting HA information when it fails."""
        # Arrange
        mock_ha_use_case.get_all_entities.side_effect = OSError("HA connection failed")
        
        # Act & Assert
        with pytest.raises(OSError, match="Error getting Home Assistant information"):
            await decision_use_case.get_ha_information()
    
    @pytest.mark.asyncio
    async def test_build_decision_prompt(self, decision_use_case):
        """Test building decision prompt."""
        # Arrange
        user_prompt = "Enciende las luces"
        ha_info = '{"entities": [], "sensors": []}'
        
        # Act
        result = await decision_use_case.build_decision_prompt(user_prompt, ha_info)
        
        # Assert
        assert isinstance(result, str)
        assert user_prompt in result
        assert ha_info in result
        assert "User request" in result
        assert "Home Assistant information" in result
    
    @pytest.mark.asyncio
    async def test_validate_decision_response_success(self, decision_use_case):
        """Test validating valid decision response."""
        # Arrange
        response_data = {
            "message": "Test message",
            "actions": [
                {"entity": "light.test", "action": "turn_on"}
            ]
        }
        response_json = json.dumps(response_data)
        
        # Act
        result = await decision_use_case.validate_decision_response(response_json)
        
        # Assert
        assert isinstance(result, DecisionResponse)
        assert result.message == "Test message"
        assert len(result.actions) == 1
        assert result.actions[0].entity == "light.test"
        assert result.actions[0].action == "turn_on"
    
    @pytest.mark.asyncio
    async def test_validate_decision_response_with_markdown(self, decision_use_case):
        """Test validating response with markdown formatting."""
        # Arrange
        response_data = {
            "message": "Test message",
            "actions": [
                {"entity": "light.test", "action": "turn_on"}
            ]
        }
        response_with_markdown = f"```json\n{json.dumps(response_data)}\n```"
        
        # Act
        result = await decision_use_case.validate_decision_response(response_with_markdown)
        
        # Assert
        assert isinstance(result, DecisionResponse)
        assert result.message == "Test message"
        assert len(result.actions) == 1
    
    @pytest.mark.asyncio
    async def test_validate_decision_response_invalid_json(self, decision_use_case):
        """Test validating invalid JSON response."""
        # Arrange
        invalid_json = "invalid json"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid JSON in AI response"):
            await decision_use_case.validate_decision_response(invalid_json)
    
    @pytest.mark.asyncio
    async def test_validate_decision_response_missing_fields(self, decision_use_case):
        """Test validating response with missing required fields."""
        # Arrange
        incomplete_response = {"message": "Test message"}  # Missing actions
        
        # Act & Assert
        with pytest.raises(ValueError, match="AI response missing 'actions' field"):
            await decision_use_case.validate_decision_response(json.dumps(incomplete_response))
    
    @pytest.mark.asyncio
    async def test_validate_decision_response_invalid_actions(self, decision_use_case):
        """Test validating response with invalid actions."""
        # Arrange
        invalid_response = {
            "message": "Test message",
            "actions": "not a list"  # Should be a list
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="AI response 'actions' field must be a list"):
            await decision_use_case.validate_decision_response(json.dumps(invalid_response))
    
    @pytest.mark.asyncio
    async def test_validate_decision_response_action_missing_fields(self, decision_use_case):
        """Test validating response with actions missing required fields."""
        # Arrange
        invalid_response = {
            "message": "Test message",
            "actions": [
                {"entity": "light.test"}  # Missing action field
            ]
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Action 0 missing 'action' field"):
            await decision_use_case.validate_decision_response(json.dumps(invalid_response))
    
    @pytest.mark.asyncio
    async def test_decision_response_to_dict(self):
        """Test DecisionResponse to_dict method."""
        # Arrange
        actions = [
            DecisionAction(entity="light.test", action="turn_on", parameters={"brightness": 255})
        ]
        response = DecisionResponse(message="Test message", actions=actions)
        
        # Act
        result = response.to_dict()
        
        # Assert
        assert result["message"] == "Test message"
        assert len(result["actions"]) == 1
        assert result["actions"][0]["entity"] == "light.test"
        assert result["actions"][0]["action"] == "turn_on"
        assert result["actions"][0]["parameters"]["brightness"] == 255
    
    @pytest.mark.asyncio
    async def test_decision_response_from_dict(self):
        """Test DecisionResponse from_dict method."""
        # Arrange
        data = {
            "message": "Test message",
            "actions": [
                {
                    "entity": "light.test",
                    "action": "turn_on",
                    "parameters": {"brightness": 255}
                }
            ]
        }
        
        # Act
        result = DecisionResponse.from_dict(data)
        
        # Assert
        assert result.message == "Test message"
        assert len(result.actions) == 1
        assert result.actions[0].entity == "light.test"
        assert result.actions[0].action == "turn_on"
        assert result.actions[0].parameters["brightness"] == 255
    
    @pytest.mark.asyncio
    async def test_decision_action_creation(self):
        """Test DecisionAction creation."""
        # Act
        action = DecisionAction(
            entity="light.test",
            action="turn_on",
            parameters={"brightness": 255}
        )
        
        # Assert
        assert action.entity == "light.test"
        assert action.action == "turn_on"
        assert action.parameters["brightness"] == 255
    
    @pytest.mark.asyncio
    async def test_decision_action_without_parameters(self):
        """Test DecisionAction creation without parameters."""
        # Act
        action = DecisionAction(entity="light.test", action="turn_on")
        
        # Assert
        assert action.entity == "light.test"
        assert action.action == "turn_on"
        assert action.parameters is None
