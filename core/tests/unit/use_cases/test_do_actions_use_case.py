"""Unit tests for DoActionsUseCase interface and implementation."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import List, Dict, Any

from core.use_cases.interfaces.do_actions_use_case import DoActionsUseCase, ActionExecutionResult, ActionsExecutionResponse
from core.use_cases.implementations.do_actions_use_case_impl import DoActionsUseCaseImpl
from core.use_cases.interfaces.decision_use_case import DecisionAction
from core.repositories.interfaces.ha_repository import HARepository
from core.api.models.domain.ha_entity import HAEntity
from datetime import datetime


@pytest.fixture
def mock_ha_repository():
    """Mock HA repository."""
    return AsyncMock(spec=HARepository)


@pytest.fixture
def do_actions_use_case(mock_ha_repository):
    """Create DoActionsUseCaseImpl instance with mocked dependencies."""
    return DoActionsUseCaseImpl(mock_ha_repository)


class TestDoActionsUseCaseInterface:
    """Test DoActionsUseCase interface behavior."""
    
    @pytest.mark.asyncio
    async def test_execute_actions_success(self, do_actions_use_case, mock_ha_repository):
        """Test successful execution of multiple actions."""
        # Arrange
        actions = [
            DecisionAction(entity="light.living_room", action="turn_on"),
            DecisionAction(entity="switch.kitchen", action="turn_off")
        ]
        
        # Mock HA repository responses
        mock_ha_repository.call_service.return_value = {"success": True}
        mock_ha_repository.get_all_entities.return_value = [
            HAEntity(
                entity_id="light.living_room",
                state="off",
                attributes={"friendly_name": "Living Room Light"},
                last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                context={"id": "test"},
                domain="light",
                object_id="living_room"
            ),
            HAEntity(
                entity_id="switch.kitchen",
                state="on",
                attributes={"friendly_name": "Kitchen Switch"},
                last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                context={"id": "test"},
                domain="switch",
                object_id="kitchen"
            )
        ]
        mock_ha_repository.get_services.return_value = {
            "available_services": [
                {"domain": "light", "services": {"turn_on": {}, "turn_off": {}}},
                {"domain": "switch", "services": {"turn_on": {}, "turn_off": {}}}
            ]
        }
        
        # Act
        result = await do_actions_use_case.execute_actions(actions)
        
        # Assert
        assert isinstance(result, ActionsExecutionResponse)
        assert result.total_actions == 2
        assert result.successful_actions == 2
        assert result.failed_actions == 0
        assert result.success_rate == 100.0
        assert len(result.results) == 2
        
        # Check individual results
        assert result.results[0].success is True
        assert result.results[0].entity == "light.living_room"
        assert result.results[0].action == "turn_on"
        
        assert result.results[1].success is True
        assert result.results[1].entity == "switch.kitchen"
        assert result.results[1].action == "turn_off"
        
        # Verify calls
        assert mock_ha_repository.call_service.call_count == 2
    
    @pytest.mark.asyncio
    async def test_execute_actions_partial_failure(self, do_actions_use_case, mock_ha_repository):
        """Test execution with some actions failing."""
        # Arrange
        actions = [
            DecisionAction(entity="light.living_room", action="turn_on"),
            DecisionAction(entity="light.nonexistent", action="turn_on")
        ]
        
        # Mock HA repository - first call succeeds, second fails
        def mock_call_service(domain, service, entity_id=None, service_data=None):
            if entity_id == "light.living_room":
                return {"success": True}
            else:
                raise Exception("Entity not found")
        
        mock_ha_repository.call_service.side_effect = mock_call_service
        mock_ha_repository.get_all_entities.return_value = [
            HAEntity(
                entity_id="light.living_room",
                state="off",
                attributes={"friendly_name": "Living Room Light"},
                last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                context={"id": "test"},
                domain="light",
                object_id="living_room"
            )
        ]
        mock_ha_repository.get_services.return_value = {
            "available_services": [{"domain": "light", "services": {"turn_on": {}}}]
        }
        
        # Act
        result = await do_actions_use_case.execute_actions(actions)
        
        # Assert
        assert isinstance(result, ActionsExecutionResponse)
        assert result.total_actions == 2
        assert result.successful_actions == 1
        assert result.failed_actions == 1
        assert result.success_rate == 50.0
        
        # Check results
        assert result.results[0].success is True
        assert result.results[1].success is False
        assert "Action validation failed" in result.results[1].error_message
    
    @pytest.mark.asyncio
    async def test_execute_actions_empty_list(self, do_actions_use_case):
        """Test execution with empty actions list."""
        # Act & Assert
        with pytest.raises(ValueError, match="Actions list cannot be empty"):
            await do_actions_use_case.execute_actions([])
    
    @pytest.mark.asyncio
    async def test_execute_actions_invalid_input(self, do_actions_use_case):
        """Test execution with invalid input type."""
        # Act & Assert
        with pytest.raises(ValueError, match="Actions must be a list"):
            await do_actions_use_case.execute_actions("not a list")
    
    @pytest.mark.asyncio
    async def test_execute_single_action_success(self, do_actions_use_case, mock_ha_repository):
        """Test successful execution of a single action."""
        # Arrange
        action = DecisionAction(entity="light.living_room", action="turn_on", parameters={"brightness": 255})
        
        mock_ha_repository.call_service.return_value = {"success": True}
        mock_ha_repository.get_all_entities.return_value = [
            HAEntity(
                entity_id="light.living_room",
                state="off",
                attributes={"friendly_name": "Living Room Light"},
                last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                context={"id": "test"},
                domain="light",
                object_id="living_room"
            )
        ]
        mock_ha_repository.get_services.return_value = {
            "available_services": [{"domain": "light", "services": {"turn_on": {}}}]
        }
        
        # Act
        result = await do_actions_use_case.execute_single_action(action)
        
        # Assert
        assert isinstance(result, ActionExecutionResult)
        assert result.success is True
        assert result.entity == "light.living_room"
        assert result.action == "turn_on"
        assert result.response_data == {"success": True}
        
        # Verify call
        mock_ha_repository.call_service.assert_called_once_with(
            domain="light",
            service="turn_on",
            entity_id="light.living_room",
            service_data={"brightness": 255}
        )
    
    @pytest.mark.asyncio
    async def test_execute_single_action_failure(self, do_actions_use_case, mock_ha_repository):
        """Test failed execution of a single action."""
        # Arrange
        action = DecisionAction(entity="light.nonexistent", action="turn_on")
        
        mock_ha_repository.call_service.side_effect = Exception("Entity not found")
        mock_ha_repository.get_all_entities.return_value = []
        mock_ha_repository.get_services.return_value = {"available_services": []}
        
        # Act
        result = await do_actions_use_case.execute_single_action(action)
        
        # Assert
        assert isinstance(result, ActionExecutionResult)
        assert result.success is False
        assert result.entity == "light.nonexistent"
        assert result.action == "turn_on"
        assert "Action validation failed" in result.error_message
    
    @pytest.mark.asyncio
    async def test_execute_single_action_invalid_entity(self, do_actions_use_case):
        """Test execution with invalid entity."""
        # Arrange
        action = DecisionAction(entity="", action="turn_on")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Action entity cannot be empty"):
            await do_actions_use_case.execute_single_action(action)
    
    @pytest.mark.asyncio
    async def test_execute_single_action_invalid_action(self, do_actions_use_case):
        """Test execution with invalid action."""
        # Arrange
        action = DecisionAction(entity="light.living_room", action="")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Action name cannot be empty"):
            await do_actions_use_case.execute_single_action(action)
    
    @pytest.mark.asyncio
    async def test_validate_action_success(self, do_actions_use_case, mock_ha_repository):
        """Test successful action validation."""
        # Arrange
        action = DecisionAction(entity="light.living_room", action="turn_on")
        
        mock_ha_repository.get_all_entities.return_value = [
            HAEntity(
                entity_id="light.living_room",
                state="off",
                attributes={"friendly_name": "Living Room Light"},
                last_changed=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                last_updated=datetime.fromisoformat("2023-01-01T00:00:00Z"),
                context={"id": "test"},
                domain="light",
                object_id="living_room"
            )
        ]
        mock_ha_repository.get_services.return_value = {
            "available_services": [{"domain": "light", "services": {"turn_on": {}}}]
        }
        
        # Act
        result = await do_actions_use_case.validate_action(action)
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_action_entity_not_found(self, do_actions_use_case, mock_ha_repository):
        """Test action validation with non-existent entity."""
        # Arrange
        action = DecisionAction(entity="light.nonexistent", action="turn_on")
        
        mock_ha_repository.get_all_entities.return_value = []
        mock_ha_repository.get_services.return_value = {"available_services": []}
        
        # Act
        result = await do_actions_use_case.validate_action(action)
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_action_invalid_entity_format(self, do_actions_use_case):
        """Test action validation with invalid entity format."""
        # Arrange
        action = DecisionAction(entity="invalid_entity", action="turn_on")
        
        # Act
        result = await do_actions_use_case.validate_action(action)
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_action_empty_entity(self, do_actions_use_case):
        """Test action validation with empty entity."""
        # Arrange
        action = DecisionAction(entity="", action="turn_on")
        
        # Act
        result = await do_actions_use_case.validate_action(action)
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_action_empty_action(self, do_actions_use_case):
        """Test action validation with empty action."""
        # Arrange
        action = DecisionAction(entity="light.living_room", action="")
        
        # Act
        result = await do_actions_use_case.validate_action(action)
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_action_ha_repository_error(self, do_actions_use_case, mock_ha_repository):
        """Test action validation when HA repository fails."""
        # Arrange
        action = DecisionAction(entity="light.living_room", action="turn_on")
        
        mock_ha_repository.get_all_entities.side_effect = Exception("HA connection failed")
        mock_ha_repository.get_services.return_value = {"available_services": []}
        
        # Act
        result = await do_actions_use_case.validate_action(action)
        
        # Assert
        # Should still return True as we continue validation even if HA checks fail
        assert result is True
    
    @pytest.mark.asyncio
    async def test_actions_execution_response_properties(self):
        """Test ActionsExecutionResponse properties."""
        # Arrange
        results = [
            ActionExecutionResult(success=True, entity="light.1", action="turn_on"),
            ActionExecutionResult(success=True, entity="light.2", action="turn_on"),
            ActionExecutionResult(success=False, entity="light.3", action="turn_on", error_message="Failed")
        ]
        
        response = ActionsExecutionResponse(
            message="Test execution",
            results=results,
            total_actions=3,
            successful_actions=2,
            failed_actions=1
        )
        
        # Assert
        assert response.success_rate == (2/3) * 100.0
        assert response.success_rate == pytest.approx(66.67, rel=1e-2)
    
    @pytest.mark.asyncio
    async def test_actions_execution_response_zero_actions(self):
        """Test ActionsExecutionResponse with zero actions."""
        # Arrange
        response = ActionsExecutionResponse(
            message="No actions",
            results=[],
            total_actions=0,
            successful_actions=0,
            failed_actions=0
        )
        
        # Assert
        assert response.success_rate == 0.0
    
    @pytest.mark.asyncio
    async def test_action_execution_result_creation(self):
        """Test ActionExecutionResult creation."""
        # Act
        result = ActionExecutionResult(
            success=True,
            entity="light.test",
            action="turn_on",
            response_data={"success": True}
        )
        
        # Assert
        assert result.success is True
        assert result.entity == "light.test"
        assert result.action == "turn_on"
        assert result.error_message is None
        assert result.response_data == {"success": True}
    
    @pytest.mark.asyncio
    async def test_action_execution_result_with_error(self):
        """Test ActionExecutionResult with error."""
        # Act
        result = ActionExecutionResult(
            success=False,
            entity="light.test",
            action="turn_on",
            error_message="Entity not found"
        )
        
        # Assert
        assert result.success is False
        assert result.entity == "light.test"
        assert result.action == "turn_on"
        assert result.error_message == "Entity not found"
        assert result.response_data is None
