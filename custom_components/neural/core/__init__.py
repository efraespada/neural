"""Neural Core - Common library for Neural integration and CLI."""

__version__ = "1.0.0"
__author__ = "Neural Team"

# Import main components
from .api import AIClient, HAClient, BaseClient
from .auth import CredentialManager
from .use_cases import (
    AIUseCase,
    HAUseCase,
    ConfigUseCase,
    DecisionUseCase,
    DecisionResponse,
    DecisionAction,
    DoActionsUseCase,
    ActionExecutionResult,
    ActionsExecutionResponse,
    UpdateHomeInfoUseCase,
)
from .dependency_injection import setup_dependencies, clear_dependencies
from .dependency_injection.injector_container import (
    get_ai_use_case,
    get_ha_use_case,
    get_decision_use_case,
    get_do_actions_use_case,
    get_config_use_case,
)

__all__ = [
    # API Clients
    "AIClient",
    "HAClient", 
    "BaseClient",
    # Auth
    "CredentialManager",
    # Use Cases
    "AIUseCase",
    "HAUseCase",
    "ConfigUseCase",
    "DecisionUseCase",
    "DecisionResponse",
    "DecisionAction",
    "DoActionsUseCase",
    "ActionExecutionResult",
    "ActionsExecutionResponse",
    "UpdateHomeInfoUseCase",
    # Dependency Injection
    "setup_dependencies",
    "clear_dependencies",
    "get_ai_use_case",
    "get_ha_use_case",
    "get_decision_use_case",
    "get_do_actions_use_case",
    "get_config_use_case",
]
