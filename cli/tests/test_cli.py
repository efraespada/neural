#!/usr/bin/env python3
"""Test script for Neural AI CLI."""

import sys
import os
from unittest.mock import patch
from io import StringIO

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from cli.main import create_parser, setup_logging


def test_cli():
    """Test the CLI functionality."""
    print("🧪 Testing Neural AI CLI...")
    print("=" * 50)

    # Test 1: Parser creation
    print("1. Testing parser creation...")
    parser = create_parser()
    assert parser is not None
    print("✅ Parser creation works")

    # Test 2: Help command
    print("\n2. Testing help command...")
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        parser.print_help()
        help_output = mock_stdout.getvalue()
        assert "Neural AI CLI" in help_output
        assert "auth" in help_output
        assert "ai" in help_output
        assert "ha" in help_output
    print("✅ Help command works")

    # Test 3: AI subcommand parsing
    print("\n3. Testing AI subcommand parsing...")
    args = parser.parse_args(["ai", "message", "Hello world"])
    assert args.command == "ai"
    assert args.action == "message"
    assert args.message == "Hello world"
    print("✅ AI subcommand parsing works")

    # Test 4: AI status subcommand parsing
    print("\n4. Testing AI status subcommand parsing...")
    args = parser.parse_args(["ai", "status"])
    assert args.command == "ai"
    assert args.action == "status"
    print("✅ AI status subcommand parsing works")

    # Test 5: HA entities subcommand parsing
    print("\n5. Testing HA entities subcommand parsing...")
    args = parser.parse_args(["ha", "entities"])
    assert args.command == "ha"
    assert args.action == "entities"
    print("✅ HA entities subcommand parsing works")

    # Test 6: HA entities with domain subcommand parsing
    print("\n6. Testing HA entities with domain subcommand parsing...")
    args = parser.parse_args(["ha", "entities", "--domain", "sensor"])
    assert args.command == "ha"
    assert args.action == "entities"
    assert args.domain == "sensor"
    print("✅ HA entities with domain subcommand parsing works")

    # Test 7: Auth status subcommand parsing
    print("\n7. Testing auth status subcommand parsing...")
    args = parser.parse_args(["auth", "status"])
    assert args.command == "auth"
    assert args.action == "status"
    print("✅ Auth status subcommand parsing works")

    # Test 8: Auth login with token subcommand parsing
    print("\n8. Testing auth login with token subcommand parsing...")
    args = parser.parse_args(["auth", "login", "--token", "test_token"])
    assert args.command == "auth"
    assert args.action == "login"
    assert args.token == "test_token"
    print("✅ Auth login with token subcommand parsing works")

    # Test 9: Logging setup
    print("\n9. Testing logging setup...")
    with patch("logging.basicConfig") as mock_basic_config:
        setup_logging(verbose=True)
        mock_basic_config.assert_called_once()
    print("✅ Logging setup works")

    print("\n" + "=" * 50)
    print("🎉 All CLI tests passed!")
    print("\nThe CLI is ready to use. You can now:")
    print("1. Run: neural ai message 'Hello, how are you?'")
    print("2. Run: neural ha entities")
    print("3. Run: neural auth status")
    print("4. Use other commands like: neural ai status")


if __name__ == "__main__":
    test_cli()
    sys.exit(0)
