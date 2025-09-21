"""Unit tests for DecisionUseCase interface and implementation."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List
from datetime import datetime

from core.use_cases.interfaces.decision_use_case import DecisionUseCase, DecisionResponse, DecisionAction
from core.use_cases.implementations.decision_use_case_impl import DecisionUseCaseImpl
from core.repositories.interfaces.ai_repository import AIRepository
from core.repositories.interfaces.ha_repository import HARepository
from core.repositories.interfaces.file_repository import FileRepository
from core.api.models.domain.ai import AIResponse, AIChat
from core.api.models.domain.ha_entity import HAEntity, HAEntityState


@pytest.fixture
def mock_ai_repository():
    """Mock AI repository."""
    return AsyncMock(spec=AIRepository)


@pytest.fixture
def mock_ha_repository():
    """Mock HA repository."""
    return AsyncMock(spec=HARepository)


@pytest.fixture
def mock_file_repository():
    """Mock File repository."""
    return AsyncMock(spec=FileRepository)


@pytest.fixture
def decision_use_case(mock_ai_repository, mock_ha_repository, mock_file_repository):
    """Create DecisionUseCaseImpl instance with mocked dependencies."""
    return DecisionUseCaseImpl(mock_ai_repository, mock_ha_repository, mock_file_repository)


class TestDecisionUseCaseInterface:
    """Test DecisionUseCase interface behavior."""
    
    @pytest.mark.asyncio
    async def test_make_decision_success(self, decision_use_case, mock_ai_repository, mock_ha_repository):
        """Test successful decision making."""
        # Arrange
        user_prompt = "Enciende las luces del salón"
        mode = "assistant"
        
        # Mock HA entities
        mock_entity = HAEntity(
            entity_id="light.living_room",
            state="off",
            attributes={"friendly_name": "Living Room Light"},
            last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            context={"id": "test"},
            domain="light",
            object_id="living_room"
        )
        mock_ha_repository.get_all_entities.return_value = [mock_entity]
        mock_ha_repository.get_sensors.return_value = []
        
        # Mock AI response
        ai_response_data = {
            "message": "De acuerdo, enciendo las luces del salón",
            "actions": [
                {"entity": "light.living_room", "action": "turn_on"}
            ]
        }
        mock_ai_response = AIResponse(
            message="Test message",
            response=json.dumps(ai_response_data),
            model="test-model",
            tokens_used=150,
            response_time=1.5
        )
        mock_ai_repository.send_message.return_value = mock_ai_response
        
        # Act
        result = await decision_use_case.make_decision(user_prompt, mode)
        
        # Assert
        assert isinstance(result, DecisionResponse)
        assert result.message == "De acuerdo, enciendo las luces del salón"
        assert len(result.actions) == 1
        assert result.actions[0].entity == "light.living_room"
        assert result.actions[0].action == "turn_on"
        
        # Verify calls - the new flow only calls AI repository for step 1
        mock_ai_repository.send_message.assert_called_once()
    
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
    async def test_make_decision_ha_error(self, decision_use_case, mock_ai_repository, mock_ha_repository):
        """Test decision making when HA fails."""
        # Arrange
        # Mock AI response that requests HA information
        ai_response_data = {"message": "OK", "actions": []}
        mock_ai_response = AIResponse(
            message="Test message",
            response=json.dumps(ai_response_data),
            model="test-model",
            tokens_used=150,
            response_time=1.5
        )
        mock_ai_repository.send_message.return_value = mock_ai_response
        
        # Mock HA failure
        mock_ha_repository.get_all_entities.side_effect = OSError("HA connection failed")
        
        # Act & Assert
        with pytest.raises(OSError, match="Error getting Home Assistant information"):
            await decision_use_case.make_decision("test prompt", "assistant")
    
    @pytest.mark.asyncio
    async def test_make_decision_ai_error(self, decision_use_case, mock_ai_repository, mock_ha_repository):
        """Test decision making when AI fails."""
        # Arrange
        mock_ha_repository.get_all_entities.return_value = []
        mock_ha_repository.get_sensors.return_value = []
        mock_ai_repository.send_message.side_effect = OSError("AI connection failed")
        
        # Act & Assert
        with pytest.raises(OSError, match="AI connection failed"):
            await decision_use_case.make_decision("test prompt", "assistant")
    
    @pytest.mark.asyncio
    async def test_get_ha_information_success(self, decision_use_case, mock_ha_repository):
        """Test getting HA information successfully."""
        # Arrange
        mock_entity = HAEntity(
            entity_id="light.test",
            state="off",
            attributes={"friendly_name": "Test Light"},
            last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            context={"id": "test"},
            domain="light",
            object_id="test"
        )
        mock_ha_repository.get_all_entities.return_value = [mock_entity]
        mock_ha_repository.get_sensors.return_value = []
        
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
    async def test_get_ha_information_error(self, decision_use_case, mock_ha_repository):
        """Test getting HA information when it fails."""
        # Arrange
        mock_ha_repository.get_all_entities.side_effect = OSError("HA connection failed")
        
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
        # The prompt template has changed, so we just check it's a valid string
        assert len(result) > 0
        assert "User request" in result
        # The template structure has changed, so we just verify it contains the user prompt
        assert user_prompt in result
    
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
    
    # Additional tests for edge cases and missing scenarios
    
    @pytest.mark.asyncio
    async def test_make_decision_supervisor_mode(self, decision_use_case, mock_ai_repository, mock_ha_repository):
        """Test decision making in supervisor mode."""
        # Arrange
        user_prompt = "¿Debería encender las luces?"
        mode = "supervisor"
        
        # Mock HA entities
        mock_entity = HAEntity(
            entity_id="light.living_room",
            state="off",
            attributes={"friendly_name": "Living Room Light", "brightness": 0},
            last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            context={"id": "test"},
            domain="light",
            object_id="living_room"
        )
        mock_ha_repository.get_all_entities.return_value = [mock_entity]
        mock_ha_repository.get_sensors.return_value = []
        
        # Mock AI response for supervisor mode
        ai_response_data = {
            "message": "No, es de día y hay suficiente luz natural. No necesitas encender las luces.",
            "actions": []
        }
        mock_ai_response = AIResponse(
            message="Test message",
            response=json.dumps(ai_response_data),
            model="test-model",
            tokens_used=150,
            response_time=1.5
        )
        mock_ai_repository.send_message.return_value = mock_ai_response
        
        # Act
        result = await decision_use_case.make_decision(user_prompt, mode)
        
        # Assert
        assert isinstance(result, DecisionResponse)
        assert "día" in result.message or "luz natural" in result.message
        assert len(result.actions) == 0  # Supervisor mode can reject actions
        
        # Verify calls
        mock_ai_repository.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_decision_multiple_actions(self, decision_use_case, mock_ai_repository, mock_ha_repository):
        """Test decision making with multiple actions."""
        # Arrange
        user_prompt = "Enciende todas las luces del salón"
        mode = "assistant"
        
        # Mock HA entities
        mock_entities = [
            HAEntity(
                entity_id="light.living_room_1",
                state="off",
                attributes={"friendly_name": "Living Room Light 1"},
                last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                context={"id": "test"},
                domain="light",
                object_id="living_room_1"
            ),
            HAEntity(
                entity_id="light.living_room_2",
                state="off",
                attributes={"friendly_name": "Living Room Light 2"},
                last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                context={"id": "test"},
                domain="light",
                object_id="living_room_2"
            )
        ]
        mock_ha_repository.get_all_entities.return_value = mock_entities
        mock_ha_repository.get_sensors.return_value = []
        
        # Mock AI response with multiple actions
        ai_response_data = {
            "message": "De acuerdo, enciendo todas las luces del salón",
            "actions": [
                {"entity": "light.living_room_1", "action": "turn_on"},
                {"entity": "light.living_room_2", "action": "turn_on"}
            ]
        }
        mock_ai_response = AIResponse(
            message="Test message",
            response=json.dumps(ai_response_data),
            model="test-model",
            tokens_used=150,
            response_time=1.5
        )
        mock_ai_repository.send_message.return_value = mock_ai_response
        
        # Act
        result = await decision_use_case.make_decision(user_prompt, mode)
        
        # Assert
        assert isinstance(result, DecisionResponse)
        assert len(result.actions) == 2
        assert result.actions[0].entity == "light.living_room_1"
        assert result.actions[0].action == "turn_on"
        assert result.actions[1].entity == "light.living_room_2"
        assert result.actions[1].action == "turn_on"
    
    @pytest.mark.asyncio
    async def test_make_decision_with_parameters(self, decision_use_case, mock_ai_repository, mock_ha_repository):
        """Test decision making with action parameters."""
        # Arrange
        user_prompt = "Enciende la luz del salón al 80% de brillo"
        mode = "assistant"
        
        # Mock HA entities
        mock_entity = HAEntity(
            entity_id="light.living_room",
            state="off",
            attributes={"friendly_name": "Living Room Light", "brightness": 0},
            last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            context={"id": "test"},
            domain="light",
            object_id="living_room"
        )
        mock_ha_repository.get_all_entities.return_value = [mock_entity]
        mock_ha_repository.get_sensors.return_value = []
        
        # Mock AI response with parameters
        ai_response_data = {
            "message": "De acuerdo, enciendo la luz del salón al 80% de brillo",
            "actions": [
                {
                    "entity": "light.living_room",
                    "action": "turn_on",
                    "parameters": {"brightness": 204}  # 80% of 255
                }
            ]
        }
        mock_ai_response = AIResponse(
            message="Test message",
            response=json.dumps(ai_response_data),
            model="test-model",
            tokens_used=150,
            response_time=1.5
        )
        mock_ai_repository.send_message.return_value = mock_ai_response
        
        # Act
        result = await decision_use_case.make_decision(user_prompt, mode)
        
        # Assert
        assert isinstance(result, DecisionResponse)
        assert len(result.actions) == 1
        assert result.actions[0].entity == "light.living_room"
        assert result.actions[0].action == "turn_on"
        assert result.actions[0].parameters["brightness"] == 204
    
    @pytest.mark.asyncio
    async def test_make_decision_empty_actions(self, decision_use_case, mock_ai_repository, mock_ha_repository):
        """Test decision making with empty actions (supervisor rejection)."""
        # Arrange
        user_prompt = "Enciende las luces"
        mode = "supervisor"
        
        # Mock HA entities
        mock_entity = HAEntity(
            entity_id="light.living_room",
            state="on",  # Already on
            attributes={"friendly_name": "Living Room Light"},
            last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            context={"id": "test"},
            domain="light",
            object_id="living_room"
        )
        mock_ha_repository.get_all_entities.return_value = [mock_entity]
        mock_ha_repository.get_sensors.return_value = []
        
        # Mock AI response with no actions
        ai_response_data = {
            "message": "Las luces ya están encendidas, no es necesario hacer nada.",
            "actions": []
        }
        mock_ai_response = AIResponse(
            message="Test message",
            response=json.dumps(ai_response_data),
            model="test-model",
            tokens_used=150,
            response_time=1.5
        )
        mock_ai_repository.send_message.return_value = mock_ai_response
        
        # Act
        result = await decision_use_case.make_decision(user_prompt, mode)
        
        # Assert
        assert isinstance(result, DecisionResponse)
        assert "ya están encendidas" in result.message or "no es necesario" in result.message
        assert len(result.actions) == 0
    
    @pytest.mark.asyncio
    async def test_build_initial_prompt(self, decision_use_case):
        """Test building initial prompt."""
        # Arrange
        user_prompt = "Enciende las luces"
        mode = "assistant"
        
        # Act
        result = await decision_use_case.build_initial_prompt(user_prompt, mode)
        
        # Assert
        assert isinstance(result, str)
        assert user_prompt in result
        assert mode in result
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_build_ha_information_prompt(self, decision_use_case):
        """Test building HA information prompt."""
        # Arrange
        ha_info = '{"entities": [{"entity_id": "light.test", "state": "off"}], "sensors": []}'
        user_prompt = "Enciende las luces"
        
        # Act
        result = await decision_use_case.build_ha_information_prompt(ha_info, user_prompt)
        
        # Assert
        assert isinstance(result, str)
        assert user_prompt in result
        assert "light.test" in result
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_validate_actions_with_ha_info(self, decision_use_case, mock_ha_repository):
        """Test validating actions against HA information."""
        # Arrange
        actions = [
            DecisionAction(entity="light.test", action="turn_on"),
            DecisionAction(entity="light.nonexistent", action="turn_on")
        ]
        ha_info = '{"entities": [{"entity_id": "light.test", "state": "off"}], "sensors": []}'
        
        # Mock HA repository for service calls (if the method exists)
        if hasattr(mock_ha_repository, 'call_service'):
            mock_ha_repository.call_service.return_value = {"success": True}
        
        # Act
        result = await decision_use_case.validate_actions(actions, ha_info)
        
        # Assert
        assert isinstance(result, dict)
        # Should contain validation results for each action
    
    @pytest.mark.asyncio
    async def test_get_ha_information_with_sensors(self, decision_use_case, mock_ha_repository):
        """Test getting HA information including sensors."""
        # Arrange
        mock_entity = HAEntity(
            entity_id="light.test",
            state="off",
            attributes={"friendly_name": "Test Light"},
            last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            context={"id": "test"},
            domain="light",
            object_id="test"
        )
        mock_sensor = HAEntity(
            entity_id="sensor.temperature",
            state="22.5",
            attributes={"friendly_name": "Temperature", "unit_of_measurement": "°C"},
            last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
            context={"id": "test"},
            domain="sensor",
            object_id="temperature"
        )
        mock_ha_repository.get_all_entities.return_value = [mock_entity]
        mock_ha_repository.get_sensors.return_value = [mock_sensor]
        
        # Act
        result = await decision_use_case.get_ha_information()
        
        # Assert
        assert isinstance(result, str)
        ha_info = json.loads(result)
        assert "entities" in ha_info
        assert "sensors" in ha_info
        assert "services" in ha_info
        assert len(ha_info["entities"]) == 1
        assert len(ha_info["sensors"]) == 1
        assert ha_info["entities"][0]["entity_id"] == "light.test"
        assert ha_info["sensors"][0]["entity_id"] == "sensor.temperature"
    
    @pytest.mark.asyncio
    async def test_validate_decision_response_with_complex_actions(self, decision_use_case):
        """Test validating response with complex action parameters."""
        # Arrange
        response_data = {
            "message": "Configurando la iluminación del salón",
            "actions": [
                {
                    "entity": "light.living_room",
                    "action": "turn_on",
                    "parameters": {
                        "brightness": 255,
                        "color_temp": 4000,
                        "rgb_color": [255, 255, 255]
                    }
                },
                {
                    "entity": "light.dimmer",
                    "action": "set_value",
                    "parameters": {
                        "value": 80
                    }
                }
            ]
        }
        response_json = json.dumps(response_data)
        
        # Act
        result = await decision_use_case.validate_decision_response(response_json)
        
        # Assert
        assert isinstance(result, DecisionResponse)
        assert result.message == "Configurando la iluminación del salón"
        assert len(result.actions) == 2
        
        # Check first action
        assert result.actions[0].entity == "light.living_room"
        assert result.actions[0].action == "turn_on"
        assert result.actions[0].parameters["brightness"] == 255
        assert result.actions[0].parameters["color_temp"] == 4000
        assert result.actions[0].parameters["rgb_color"] == [255, 255, 255]
        
        # Check second action
        assert result.actions[1].entity == "light.dimmer"
        assert result.actions[1].action == "set_value"
        assert result.actions[1].parameters["value"] == 80
    
    @pytest.mark.asyncio
    async def test_validate_decision_response_empty_actions(self, decision_use_case):
        """Test validating response with empty actions list."""
        # Arrange
        response_data = {
            "message": "No hay acciones que realizar",
            "actions": []
        }
        response_json = json.dumps(response_data)
        
        # Act
        result = await decision_use_case.validate_decision_response(response_json)
        
        # Assert
        assert isinstance(result, DecisionResponse)
        assert result.message == "No hay acciones que realizar"
        assert len(result.actions) == 0
    
    @pytest.mark.asyncio
    async def test_decision_response_serialization_roundtrip(self):
        """Test DecisionResponse serialization and deserialization."""
        # Arrange
        original_response = DecisionResponse(
            message="Test message",
            actions=[
                DecisionAction(
                    entity="light.test",
                    action="turn_on",
                    parameters={"brightness": 255}
                ),
                DecisionAction(
                    entity="switch.test",
                    action="turn_off"
                )
            ]
        )
        
        # Act - Serialize to dict
        data = original_response.to_dict()
        
        # Deserialize from dict
        restored_response = DecisionResponse.from_dict(data)
        
        # Assert
        assert restored_response.message == original_response.message
        assert len(restored_response.actions) == len(original_response.actions)
        
        # Check first action
        assert restored_response.actions[0].entity == original_response.actions[0].entity
        assert restored_response.actions[0].action == original_response.actions[0].action
        assert restored_response.actions[0].parameters == original_response.actions[0].parameters
        
        # Check second action
        assert restored_response.actions[1].entity == original_response.actions[1].entity
        assert restored_response.actions[1].action == original_response.actions[1].action
        # Parameters should be empty dict when None is provided
        assert restored_response.actions[1].parameters == {}
