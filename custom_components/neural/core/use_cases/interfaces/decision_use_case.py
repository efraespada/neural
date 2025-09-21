import abc
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class DecisionAction:
    """Represents an action to be executed in Home Assistant."""
    entity: str
    action: str
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class DecisionResponse:
    """Represents the response from the decision AI."""
    message: str
    actions: List[DecisionAction]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DecisionResponse to dictionary."""
        return {
            "message": self.message,
            "actions": [
                {
                    "entity": action.entity,
                    "action": action.action,
                    "parameters": action.parameters or {}
                }
                for action in self.actions
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecisionResponse":
        """Create DecisionResponse from dictionary."""
        actions = []
        for action_data in data.get("actions", []):
            action = DecisionAction(
                entity=action_data.get("entity", ""),
                action=action_data.get("action", ""),
                parameters=action_data.get("parameters")
            )
            actions.append(action)
        
        return cls(
            message=data.get("message", ""),
            actions=actions
        )


class DecisionUseCase(abc.ABC):
    """Abstract base class for decision-making operations."""
    
    @abc.abstractmethod
    async def make_decision(self, user_prompt: str, mode: str = "assistant") -> DecisionResponse:
        """
        Make a decision based on user prompt and Home Assistant state.
        
        Args:
            user_prompt: The user's request or instruction
            mode: The decision mode (assistant, supervisor, autonomic)
            
        Returns:
            DecisionResponse with message and actions to execute
            
        Raises:
            ValueError: If the prompt is empty or mode is invalid
            OSError: If there's an error accessing Home Assistant or AI services
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    async def get_ha_information(self) -> str:
        """
        Get comprehensive Home Assistant information in JSON format.
        
        Returns:
            JSON string with entities, sensors, and services information
            
        Raises:
            OSError: If there's an error accessing Home Assistant
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    async def build_decision_prompt(self, user_prompt: str, ha_info: str) -> str:
        """
        Build the complete prompt for the decision AI.
        
        Args:
            user_prompt: The original user request
            ha_info: Home Assistant information in JSON format
            
        Returns:
            Complete prompt string for the AI
            
        Raises:
            ValueError: If the prompt cannot be built
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    async def validate_decision_response(self, response: str) -> DecisionResponse:
        """
        Validate and parse the AI response.
        
        Args:
            response: Raw response from the AI
            
        Returns:
            Parsed DecisionResponse
            
        Raises:
            ValueError: If the response is not valid JSON or missing required fields
        """
        raise NotImplementedError
