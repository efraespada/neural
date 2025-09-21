"""Neural CLI - Command Line Interface for Neural integration."""

__version__ = "1.0.0"
__author__ = "Neural Team"

# Main CLI entry point
from .main import main, create_parser, setup_logging

# Command classes
from .commands.base import BaseCommand
from .commands.ai import AICommand
from .commands.ha import HACommand
from .commands.auth import AuthCommand

# Utility functions
from .utils.display import (
    print_header,
    print_success,
    print_error,
    print_info,
    print_warning,
    print_command_header,
)

# Public API
__all__ = [
    # Main functions
    "main",
    "create_parser", 
    "setup_logging",
    
    # Command classes
    "BaseCommand",
    "AICommand",
    "HACommand", 
    "AuthCommand",
    
    # Display utilities
    "print_header",
    "print_success",
    "print_error", 
    "print_info",
    "print_warning",
    "print_command_header",
]
