#!/usr/bin/env python3
"""Neural CLI - Command Line Interface."""

import argparse
import asyncio
import logging
import sys
import os

# Add custom_components/neural to path
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "custom_components", "neural"))

from .commands.ai import AICommand
from .commands.ha import HACommand
from .utils.display import print_header, print_error, print_info
# Session manager removed - no longer needed for Neural AI

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Neural AI CLI - Command Line Interface for Neural AI integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # AI interaction
  neural ai message "hola, que tal?"
  neural ai status
  neural ai models

  # AI configuration
  neural ai config
  neural ai config --url https://openrouter.ai/api/v1
  neural ai config --model anthropic/claude-3.5-sonnet
  neural ai config --api-key sk-or-v1-your-api-key
  neural ai config --personality hal9000
  neural ai config --url https://openrouter.ai/api/v1 --model anthropic/claude-3.5-sonnet --api-key sk-or-v1-your-api-key --personality "Jarvis - Ironman"

  # AI decision making
  neural ai decide "Enciende las luces del salón"
  neural ai decide "Ajusta la temperatura a 22 grados" --mode supervisor
  neural ai decide "Optimiza el consumo energético" --mode autonomic

  # Home Assistant integration
  neural ha entities
  neural ha sensors
  neural ha summary
  neural ha entity sensor.temperature
  neural ha test
  neural ha complete
  
  # Home Assistant configuration
  neural ha config
  neural ha config --mode supervisor
  neural ha config --mode client
  neural ha config --mode standalone
  
  # Home Assistant with custom token
  neural ha --ha-token YOUR_TOKEN test

  # Home Assistant authentication
  neural auth status
  neural auth login
  neural auth login --token YOUR_TOKEN
  neural auth logout

  # Non-interactive mode (for scripts)
  neural ai message "Hello" --non-interactive
  neural ha entities --domain sensor
        """,
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Disable interactive prompts (for scripts)",
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )


    # AI command
    ai_parser = subparsers.add_parser("ai", help="AI interaction")
    ai_subparsers = ai_parser.add_subparsers(
        dest="action", help="AI actions"
    )

    message_parser = ai_subparsers.add_parser("message", help="Send message to AI")
    message_parser.add_argument("message", help="Message to send to AI")
    message_parser.add_argument("--model", help="AI model to use")

    status_ai_parser = ai_subparsers.add_parser(
        "status", help="Show AI status"
    )

    models_parser = ai_subparsers.add_parser(
        "models", help="List available AI models"
    )

    # AI config command
    config_ai_parser = ai_subparsers.add_parser("config", help="Manage AI configuration")
    config_ai_parser.add_argument("--url", help="Set LLM URL")
    config_ai_parser.add_argument("--model", help="Set LLM model")
    config_ai_parser.add_argument("--api-key", help="Set LLM API key")
    config_ai_parser.add_argument("--personality", 
                                 choices=["hal9000", "mother", "jarvis", "kitt"],
                                 help="Set AI personality")
    
    # AI decide command
    decide_parser = ai_subparsers.add_parser("decide", help="Make AI decisions based on Home Assistant state")
    decide_parser.add_argument("prompt", help="User prompt or instruction")
    decide_parser.add_argument("--mode", choices=["assistant", "supervisor", "autonomic"], 
                              default="assistant", help="Decision mode")

    # Home Assistant command
    ha_parser = subparsers.add_parser("ha", help="Home Assistant integration")
    ha_parser.add_argument("--ha-token", help="Home Assistant API token")
    ha_subparsers = ha_parser.add_subparsers(
        dest="action", help="Home Assistant actions"
    )

    entities_parser = ha_subparsers.add_parser("entities", help="Get all entities")
    entities_parser.add_argument("--domain", help="Filter by domain")

    ha_subparsers.add_parser("sensors", help="Get sensor entities")

    ha_subparsers.add_parser("summary", help="Get entity summary")

    entity_parser = ha_subparsers.add_parser("entity", help="Get specific entity")
    entity_parser.add_argument("entity_id", help="Entity ID")

    ha_subparsers.add_parser("test", help="Test connection to Home Assistant")
    
    ha_subparsers.add_parser("complete", help="Get complete Home Assistant information")
    
    ha_subparsers.add_parser("info", help="Show Home Assistant connection information")

    # HA config command
    config_ha_parser = ha_subparsers.add_parser("config", help="Manage HA configuration")
    config_ha_parser.add_argument("--mode", help="Set application mode (supervisor, client, standalone)")
    
    # HA update-home-info command
    update_home_info_parser = ha_subparsers.add_parser("update-home-info", help="Update home information")
    update_home_info_parser.add_argument("home_info", nargs="?", help="Home information in markdown format")

    # Authentication command
    auth_parser = subparsers.add_parser("auth", help="Home Assistant authentication")
    auth_subparsers = auth_parser.add_subparsers(
        dest="action", help="Authentication actions"
    )

    auth_subparsers.add_parser("status", help="Show authentication status")
    
    login_parser = auth_subparsers.add_parser("login", help="Login to Home Assistant")
    login_parser.add_argument("--token", help="Long-lived access token")
    
    auth_subparsers.add_parser("logout", help="Logout from Home Assistant")

    return parser


async def main():
    """Main function."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Show header
    print_header("NEURAL AI CLI")
    print_info("Command Line Interface for Neural AI integration")
    print()

    try:
        if args.command == "ai":
            command = AICommand()
            if args.action == "message":
                success = await command.execute(
                    args.action,
                    message=args.message,
                    model=args.model,
                    interactive=not args.non_interactive,
                )
            elif args.action == "status":
                success = await command.execute(
                    args.action,
                    interactive=not args.non_interactive,
                )
            elif args.action == "models":
                success = await command.execute(
                    args.action,
                    interactive=not args.non_interactive,
                )
            elif args.action == "config":
                success = await command.execute(
                    args.action,
                    url=getattr(args, 'url', None),
                    model=getattr(args, 'model', None),
                    api_key=getattr(args, 'api_key', None),
                    personality=getattr(args, 'personality', None),
                    interactive=not args.non_interactive,
                )
            elif args.action == "decide":
                success = await command.execute(
                    args.action,
                    prompt=args.prompt,
                    mode=args.mode,
                    interactive=not args.non_interactive,
                )
            else:
                success = False

        elif args.command == "ha":
            command = HACommand()
            # Pass HA connection parameters
            ha_params = {
                'ha_token': getattr(args, 'ha_token', None),
            }
            
            if args.action == "entities":
                success = await command.execute(
                    args.action,
                    domain=args.domain,
                    interactive=not args.non_interactive,
                    **ha_params
                )
            elif args.action == "sensors":
                success = await command.execute(
                    args.action,
                    interactive=not args.non_interactive,
                    **ha_params
                )
            elif args.action == "summary":
                success = await command.execute(
                    args.action,
                    interactive=not args.non_interactive,
                    **ha_params
                )
            elif args.action == "entity":
                success = await command.execute(
                    args.action,
                    entity_id=args.entity_id,
                    interactive=not args.non_interactive,
                    **ha_params
                )
            elif args.action == "test":
                success = await command.execute(
                    args.action,
                    interactive=not args.non_interactive,
                    **ha_params
                )
            elif args.action == "complete":
                success = await command.execute(
                    args.action,
                    interactive=not args.non_interactive,
                    **ha_params
                )
            elif args.action == "info":
                success = await command.execute(
                    args.action,
                    interactive=not args.non_interactive,
                    **ha_params
                )
            elif args.action == "config":
                success = await command.execute(
                    args.action,
                    mode=getattr(args, 'mode', None),
                    interactive=not args.non_interactive,
                    **ha_params
                )
            elif args.action == "update-home-info":
                success = await command.execute(
                    args.action,
                    home_info=getattr(args, 'home_info', None),
                    interactive=not args.non_interactive,
                    **ha_params
                )
            else:
                success = False

        elif args.command == "auth":
            from .commands.auth import AuthCommand
            command = AuthCommand()
            if args.action == "status":
                success = await command.execute(
                    args.action,
                    interactive=not args.non_interactive,
                )
            elif args.action == "login":
                success = await command.execute(
                    args.action,
                    token=getattr(args, 'token', None),
                    interactive=not args.non_interactive,
                )
            elif args.action == "logout":
                success = await command.execute(
                    args.action,
                    interactive=not args.non_interactive,
                )
            else:
                success = False

        else:
            parser.print_help()
            return 0

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n⏹️  Proceso interrumpido por el usuario")
        return 1

    except Exception as e:
        print_error(f"Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
