"""Interface for executing actions use case."""

import abc
from typing import List, Dict, Any
from dataclasses import dataclass

from ..interfaces.decision_use_case import DecisionAction

@dataclass
class ActionExecutionResult:
    """Result of executing a single action."""
    success: bool
    entity: str
    action: str
    error_message: str = None
    response_data: Dict[str, Any] = None


@dataclass
class ActionsExecutionResponse:
    """Response from executing multiple actions."""
    message: str
    results: List[ActionExecutionResult]
    total_actions: int
    successful_actions: int
    failed_actions: int
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_actions == 0:
            return 0.0
        return (self.successful_actions / self.total_actions) * 100.0


class DoActionsUseCase(abc.ABC):
    """Abstract base class for executing actions operations."""
    
    @abc.abstractmethod
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
        raise NotImplementedError
    
    @abc.abstractmethod
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
        raise NotImplementedError
    
    @abc.abstractmethod
    async def validate_action(self, action: DecisionAction) -> bool:
        """
        Validate if an action can be executed.
        
        Args:
            action: Action to validate
            
        Returns:
            True if action is valid, False otherwise
        """
        raise NotImplementedError
