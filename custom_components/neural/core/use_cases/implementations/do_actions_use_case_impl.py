"""Implementation of do actions use case."""

import logging
from typing import List

from ..interfaces.do_actions_use_case import DoActionsUseCase, ActionExecutionResult, ActionsExecutionResponse
from ..interfaces.decision_use_case import DecisionAction
from ...repositories.interfaces.ha_repository import HARepository

_LOGGER = logging.getLogger(__name__)


class DoActionsUseCaseImpl(DoActionsUseCase):
    """
    Implementation of do actions use case.
    Executes actions on Home Assistant through the HA repository.
    """
    
    def __init__(self, ha_repository: HARepository):
        """
        Initialize the DoActionsUseCaseImpl.
        
        Args:
            ha_repository: Home Assistant repository for executing actions
        """
        self._ha_repository = ha_repository
    
    async def execute_actions(self, actions: List[DecisionAction]) -> ActionsExecutionResponse:
        """
        Execute a list of actions on Home Assistant.
        
        Args:
            actions: List of actions to execute
            
        Returns:
            ActionsExecutionResponse with execution results
            
        Raises:
            ValueError: If actions list is empty or invalid
            OSError: If there's an error executing actions
        """
        try:
            _LOGGER.debug("Executing %d actions", len(actions))
            
            # Validate inputs
            if not actions:
                raise ValueError("Actions list cannot be empty")
            
            if not isinstance(actions, list):
                raise ValueError("Actions must be a list")
            
            # Execute each action
            results = []
            successful_count = 0
            failed_count = 0
            
            for i, action in enumerate(actions):
                _LOGGER.debug("Executing action %d/%d: %s.%s", i + 1, len(actions), action.entity, action.action)
                
                try:
                    result = await self.execute_single_action(action)
                    results.append(result)
                    
                    if result.success:
                        successful_count += 1
                        _LOGGER.info("Action %d/%d executed successfully: %s.%s", 
                                   i + 1, len(actions), action.entity, action.action)
                    else:
                        failed_count += 1
                        _LOGGER.warning("Action %d/%d failed: %s.%s - %s", 
                                      i + 1, len(actions), action.entity, action.action, result.error_message)
                        
                except Exception as e:
                    _LOGGER.error("Error executing action %d/%d: %s", i + 1, len(actions), e)
                    failed_count += 1
                    results.append(ActionExecutionResult(
                        success=False,
                        entity=action.entity,
                        action=action.action,
                        error_message=str(e)
                    ))
            
            # Create response
            response = ActionsExecutionResponse(
                message=f"Executed {len(actions)} actions: {successful_count} successful, {failed_count} failed",
                results=results,
                total_actions=len(actions),
                successful_actions=successful_count,
                failed_actions=failed_count
            )
            
            _LOGGER.info("Actions execution completed: %d/%d successful (%.1f%%)", 
                        successful_count, len(actions), response.success_rate)
            
            return response
            
        except ValueError as e:
            _LOGGER.error("Error executing actions: %s", e)
            raise
        except Exception as e:
            _LOGGER.error("Error executing actions: %s", e)
            raise OSError(f"Error executing actions: {e}")
    
    async def execute_single_action(self, action: DecisionAction) -> ActionExecutionResult:
        """
        Execute a single action on Home Assistant.
        
        Args:
            action: Action to execute
            
        Returns:
            ActionExecutionResult with execution result
            
        Raises:
            ValueError: If action is invalid
            OSError: If there's an error executing the action
        """
        try:
            _LOGGER.debug("Executing single action: %s.%s", action.entity, action.action)
            
            # Validate action
            if not action.entity or not action.entity.strip():
                raise ValueError("Action entity cannot be empty")
            
            if not action.action or not action.action.strip():
                raise ValueError("Action name cannot be empty")
            
            # Validate action before execution
            is_valid = await self.validate_action(action)
            if not is_valid:
                return ActionExecutionResult(
                    success=False,
                    entity=action.entity,
                    action=action.action,
                    error_message="Action validation failed"
                )
            
            # Execute the action through HA repository
            try:
                response_data = await self._ha_repository.call_service(
                    domain=action.entity.split('.')[0],
                    service=action.action,
                    entity_id=action.entity,
                    service_data=action.parameters or {}
                )
                
                _LOGGER.info("Action executed successfully: %s.%s", action.entity, action.action)
                
                return ActionExecutionResult(
                    success=True,
                    entity=action.entity,
                    action=action.action,
                    response_data=response_data
                )
                
            except Exception as e:
                _LOGGER.error("Error calling HA service for %s.%s: %s", action.entity, action.action, e)
                return ActionExecutionResult(
                    success=False,
                    entity=action.entity,
                    action=action.action,
                    error_message=str(e)
                )
                
        except ValueError as e:
            _LOGGER.error("Error executing single action: %s", e)
            raise
        except Exception as e:
            _LOGGER.error("Error executing single action: %s", e)
            raise OSError(f"Error executing single action: {e}")
    
    async def validate_action(self, action: DecisionAction) -> bool:
        """
        Validate if an action can be executed.
        
        Args:
            action: Action to validate
            
        Returns:
            True if action is valid, False otherwise
        """
        try:
            _LOGGER.debug("Validating action: %s.%s", action.entity, action.action)
            
            # Basic validation
            if not action.entity or not action.entity.strip():
                _LOGGER.warning("Action entity is empty")
                return False
            
            if not action.action or not action.action.strip():
                _LOGGER.warning("Action name is empty")
                return False
            
            # Extract domain from entity
            if '.' not in action.entity:
                _LOGGER.warning("Invalid entity format: %s", action.entity)
                return False
            
            domain = action.entity.split('.')[0]
            entity_id = action.entity.split('.')[1]
            
            if not domain or not entity_id:
                _LOGGER.warning("Invalid entity format: %s", action.entity)
                return False
            
            # Check if entity exists
            try:
                entities = await self._ha_repository.get_all_entities()
                entity_exists = any(entity.entity_id == action.entity for entity in entities)
                
                if not entity_exists:
                    _LOGGER.warning("Entity does not exist: %s", action.entity)
                    return False
                
            except Exception as e:
                _LOGGER.warning("Error checking entity existence: %s", e)
                # Continue validation even if we can't check entity existence
                pass
            
            # Check if service exists for the domain
            try:
                services = await self._ha_repository.get_services()
                # This is a basic check - in a real implementation you'd validate
                # that the specific service exists for the domain
                if not services:
                    _LOGGER.warning("No services available")
                    return False
                
            except Exception as e:
                _LOGGER.warning("Error checking services: %s", e)
                # Continue validation even if we can't check services
                pass
            
            _LOGGER.debug("Action validation passed: %s.%s", action.entity, action.action)
            return True
            
        except Exception as e:
            _LOGGER.error("Error validating action: %s", e)
            return False
