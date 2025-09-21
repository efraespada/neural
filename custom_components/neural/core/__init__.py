"""Neural Core - Common library for Neural integration and CLI."""

__version__ = "1.0.0"
__author__ = "Neural Team"

from .dependency_injection.providers import setup_dependencies, clear_dependencies
from .dependency_injection.injector_container import (
    get_ai_use_case,
    get_ha_use_case,
    get_decision_use_case,
    get_do_actions_use_case,
    get_config_use_case,
    get_audio_use_case,
)

__all__ = [
    # Dependency Injection
    "setup_dependencies",
    "clear_dependencies",
    "get_ai_use_case",
    "get_ha_use_case",
    "get_decision_use_case",
    "get_do_actions_use_case",
    "get_config_use_case",
    "get_audio_use_case",
]
