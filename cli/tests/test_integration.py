"""Integration tests for CLI."""

import pytest
import sys
import os
from unittest.mock import patch, Mock, AsyncMock
from io import StringIO

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from cli.main import main, create_parser, setup_logging


class TestCLIIntegration:
    """Integration tests for CLI."""

    def setup_method(self):
        """Set up test fixtures."""
        self.original_argv = sys.argv.copy()

    def teardown_method(self):
        """Clean up test fixtures."""
        sys.argv = self.original_argv

    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()

        # Test that parser has expected subcommands
        subparsers = [
            action.dest
            for action in parser._actions
            if hasattr(action, "choices")
        ]
        assert len(subparsers) > 0

        # Test help
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            parser.print_help()
            help_output = mock_stdout.getvalue()
            assert "Neural AI CLI" in help_output
            assert "auth" in help_output
            assert "ai" in help_output
            assert "ha" in help_output

    def test_setup_logging(self):
        """Test logging setup."""
        with patch("logging.basicConfig") as mock_basic_config:
            setup_logging(verbose=True)
            mock_basic_config.assert_called_once()

    @pytest.mark.asyncio
    @patch("cli.main.AICommand")
    async def test_main_ai_message(self, mock_ai_command):
        """Test main function with AI message command."""
        sys.argv = ["neural", "ai", "message", "Hello, how are you?"]

        mock_command_instance = Mock()
        mock_command_instance.execute = AsyncMock(return_value=True)
        mock_ai_command.return_value = mock_command_instance

        with patch("cli.main.setup_logging"):
            result = await main()

        assert result == 0
        mock_command_instance.execute.assert_called_once()

    @pytest.mark.asyncio
    @patch("cli.main.HACommand")
    async def test_main_ha_entities(self, mock_ha_command):
        """Test main function with HA entities command."""
        sys.argv = ["neural", "ha", "entities"]

        mock_command_instance = Mock()
        mock_command_instance.execute = AsyncMock(return_value=True)
        mock_ha_command.return_value = mock_command_instance

        with patch("cli.main.setup_logging"):
            result = await main()

        assert result == 0
        mock_command_instance.execute.assert_called_once()

    @pytest.mark.asyncio
    @patch("cli.commands.auth.AuthCommand")
    async def test_main_auth_status(self, mock_auth_command):
        """Test main function with auth status command."""
        sys.argv = ["neural", "auth", "status"]

        mock_command_instance = Mock()
        mock_command_instance.execute = AsyncMock(return_value=True)
        mock_auth_command.return_value = mock_command_instance

        with patch("cli.main.setup_logging"):
            result = await main()

        assert result == 0
        mock_command_instance.execute.assert_called_once()

    def test_main_help(self):
        """Test main function with help command."""
        sys.argv = ["neural", "--help"]

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with pytest.raises(SystemExit):
                import asyncio
                asyncio.run(main())
            help_output = mock_stdout.getvalue()
            assert "Neural AI CLI" in help_output

    def test_main_unknown_command(self):
        """Test main function with unknown command."""
        sys.argv = ["neural", "unknown", "command"]

        with pytest.raises(SystemExit):
            import asyncio
            asyncio.run(main())


class TestCLIArgumentParsing:
    """Test CLI argument parsing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = create_parser()

    def test_ai_message_parsing(self):
        """Test AI message argument parsing."""
        args = self.parser.parse_args(["ai", "message", "Hello world"])
        assert args.command == "ai"
        assert args.action == "message"
        assert args.message == "Hello world"

    def test_ai_status_parsing(self):
        """Test AI status argument parsing."""
        args = self.parser.parse_args(["ai", "status"])
        assert args.command == "ai"
        assert args.action == "status"

    def test_ai_models_parsing(self):
        """Test AI models argument parsing."""
        args = self.parser.parse_args(["ai", "models"])
        assert args.command == "ai"
        assert args.action == "models"

    def test_ha_entities_parsing(self):
        """Test HA entities argument parsing."""
        args = self.parser.parse_args(["ha", "entities"])
        assert args.command == "ha"
        assert args.action == "entities"

    def test_ha_entities_with_domain_parsing(self):
        """Test HA entities with domain argument parsing."""
        args = self.parser.parse_args(["ha", "entities", "--domain", "sensor"])
        assert args.command == "ha"
        assert args.action == "entities"
        assert args.domain == "sensor"

    def test_ha_sensors_parsing(self):
        """Test HA sensors argument parsing."""
        args = self.parser.parse_args(["ha", "sensors"])
        assert args.command == "ha"
        assert args.action == "sensors"

    def test_ha_summary_parsing(self):
        """Test HA summary argument parsing."""
        args = self.parser.parse_args(["ha", "summary"])
        assert args.command == "ha"
        assert args.action == "summary"

    def test_auth_status_parsing(self):
        """Test auth status argument parsing."""
        args = self.parser.parse_args(["auth", "status"])
        assert args.command == "auth"
        assert args.action == "status"

    def test_auth_login_parsing(self):
        """Test auth login argument parsing."""
        args = self.parser.parse_args(["auth", "login"])
        assert args.command == "auth"
        assert args.action == "login"

    def test_auth_login_with_token_parsing(self):
        """Test auth login with token argument parsing."""
        args = self.parser.parse_args(["auth", "login", "--token", "test_token"])
        assert args.command == "auth"
        assert args.action == "login"
        assert args.token == "test_token"

    def test_auth_logout_parsing(self):
        """Test auth logout argument parsing."""
        args = self.parser.parse_args(["auth", "logout"])
        assert args.command == "auth"
        assert args.action == "logout"

    def test_verbose_flag_parsing(self):
        """Test verbose flag parsing."""
        args = self.parser.parse_args(["-v", "ai", "status"])
        assert args.verbose is True

    def test_non_interactive_flag_parsing(self):
        """Test non-interactive flag parsing."""
        args = self.parser.parse_args(["--non-interactive", "ai", "status"])
        assert args.non_interactive is True


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.original_argv = sys.argv.copy()

    def teardown_method(self):
        """Clean up test fixtures."""
        sys.argv = self.original_argv

    @pytest.mark.asyncio
    async def test_command_exception_handling(self):
        """Test command exception handling."""
        sys.argv = ["neural", "ai", "message", "test"]

        with patch("cli.main.AICommand") as mock_ai_command:
            mock_command_instance = Mock()
            mock_command_instance.execute = AsyncMock(side_effect=Exception("Test error"))
            mock_ai_command.return_value = mock_command_instance

            with patch("cli.main.setup_logging"):
                result = await main()

            assert result == 1

    def test_invalid_arguments_handling(self):
        """Test invalid arguments handling."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(["invalid", "command"])

    def test_missing_arguments_handling(self):
        """Test missing arguments handling."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(["ai", "message"])  # Missing message argument
