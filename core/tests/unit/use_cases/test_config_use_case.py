"""
Tests unitarios para ConfigUseCase.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock

from core.use_cases.interfaces.config_use_case import ConfigUseCase
from core.use_cases.implementations.config_use_case_impl import ConfigUseCaseImpl
from core.managers.config_manager import ConfigManager
from core.api.models.domain.config import AppConfig, LLMConfig, ConfigValidationResult


class TestConfigUseCaseInterface:
    """Tests para la interfaz ConfigUseCase."""

    @pytest.fixture
    def mock_config_use_case(self):
        """Fixture para mock del ConfigUseCase."""
        return AsyncMock(spec=ConfigUseCase)

    @pytest.fixture
    def sample_config(self):
        """Fixture para AppConfig de ejemplo."""
        return AppConfig(
            mode="supervisor",
            llm=LLMConfig(url="https://openrouter.ai/api/v1", model="openai/gpt-oss-20b"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.mark.asyncio
    async def test_get_config_success(self, mock_config_use_case, sample_config):
        """Test get_config exitoso."""
        # Arrange
        mock_config_use_case.get_config.return_value = sample_config
        
        # Act
        result = await mock_config_use_case.get_config()
        
        # Assert
        assert result == sample_config
        mock_config_use_case.get_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_config_success(self, mock_config_use_case, sample_config):
        """Test load_config exitoso."""
        # Arrange
        mock_config_use_case.load_config.return_value = sample_config
        
        # Act
        result = await mock_config_use_case.load_config()
        
        # Assert
        assert result == sample_config
        mock_config_use_case.load_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_config_success(self, mock_config_use_case):
        """Test save_config exitoso."""
        # Arrange
        mock_config_use_case.save_config.return_value = True
        
        # Act
        result = await mock_config_use_case.save_config()
        
        # Assert
        assert result is True
        mock_config_use_case.save_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_mode_success(self, mock_config_use_case):
        """Test update_mode exitoso."""
        # Arrange
        mock_config_use_case.update_mode.return_value = True
        
        # Act
        result = await mock_config_use_case.update_mode("client")
        
        # Assert
        assert result is True
        mock_config_use_case.update_mode.assert_called_once_with("client")

    @pytest.mark.asyncio
    async def test_update_llm_url_success(self, mock_config_use_case):
        """Test update_llm_url exitoso."""
        # Arrange
        mock_config_use_case.update_llm_url.return_value = True
        
        # Act
        result = await mock_config_use_case.update_llm_url("192.168.1.100")
        
        # Assert
        assert result is True
        mock_config_use_case.update_llm_url.assert_called_once_with("192.168.1.100")

    @pytest.mark.asyncio
    async def test_update_llm_model_success(self, mock_config_use_case):
        """Test update_llm_model exitoso."""
        # Arrange
        mock_config_use_case.update_llm_model.return_value = True
        
        # Act
        result = await mock_config_use_case.update_llm_model("new-model")
        
        # Assert
        assert result is True
        mock_config_use_case.update_llm_model.assert_called_once_with("new-model")

    @pytest.mark.asyncio
    async def test_update_llm_config_success(self, mock_config_use_case):
        """Test update_llm_config exitoso."""
        # Arrange
        mock_config_use_case.update_llm_config.return_value = True
        
        # Act
        result = await mock_config_use_case.update_llm_config("192.168.1.100", "new-model")
        
        # Assert
        assert result is True
        mock_config_use_case.update_llm_config.assert_called_once_with("192.168.1.100", "new-model")

    @pytest.mark.asyncio
    async def test_validate_config_success(self, mock_config_use_case):
        """Test validate_config exitoso."""
        # Arrange
        validation_result = ConfigValidationResult(is_valid=True)
        mock_config_use_case.validate_config.return_value = validation_result
        
        # Act
        result = await mock_config_use_case.validate_config()
        
        # Assert
        assert result == validation_result
        mock_config_use_case.validate_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_default_config_success(self, mock_config_use_case, sample_config):
        """Test create_default_config exitoso."""
        # Arrange
        mock_config_use_case.create_default_config.return_value = sample_config
        
        # Act
        result = await mock_config_use_case.create_default_config()
        
        # Assert
        assert result == sample_config
        mock_config_use_case.create_default_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_config_success(self, mock_config_use_case, sample_config):
        """Test reset_config exitoso."""
        # Arrange
        mock_config_use_case.reset_config.return_value = sample_config
        
        # Act
        result = await mock_config_use_case.reset_config()
        
        # Assert
        assert result == sample_config
        mock_config_use_case.reset_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_backup_config_success(self, mock_config_use_case):
        """Test backup_config exitoso."""
        # Arrange
        mock_config_use_case.backup_config.return_value = True
        
        # Act
        result = await mock_config_use_case.backup_config("backup.json")
        
        # Assert
        assert result is True
        mock_config_use_case.backup_config.assert_called_once_with("backup.json")

    @pytest.mark.asyncio
    async def test_get_config_summary_success(self, mock_config_use_case):
        """Test get_config_summary exitoso."""
        # Arrange
        summary = {"mode": "supervisor", "llm": {"ip": "https://openrouter.ai/api/v1", "model": "openai/gpt-oss-20b"}}
        mock_config_use_case.get_config_summary.return_value = summary
        
        # Act
        result = await mock_config_use_case.get_config_summary()
        
        # Assert
        assert result == summary
        mock_config_use_case.get_config_summary.assert_called_once()


class TestConfigUseCaseImpl:
    """Tests para la implementación ConfigUseCaseImpl."""

    @pytest.fixture
    def mock_config_manager(self):
        """Fixture para mock del ConfigManager."""
        return AsyncMock(spec=ConfigManager)

    @pytest.fixture
    def config_use_case(self, mock_config_manager):
        """Fixture para ConfigUseCaseImpl."""
        return ConfigUseCaseImpl(mock_config_manager)

    @pytest.fixture
    def sample_config(self):
        """Fixture para AppConfig de ejemplo."""
        return AppConfig(
            mode="supervisor",
            llm=LLMConfig(url="https://openrouter.ai/api/v1", model="openai/gpt-oss-20b"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.mark.asyncio
    async def test_get_config_success(self, config_use_case, mock_config_manager, sample_config):
        """Test get_config exitoso."""
        # Arrange
        mock_config_manager.get_config.return_value = sample_config
        
        # Act
        result = await config_use_case.get_config()
        
        # Assert
        assert result == sample_config
        mock_config_manager.get_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_config_success(self, config_use_case, mock_config_manager, sample_config):
        """Test load_config exitoso."""
        # Arrange
        mock_config_manager.load_config.return_value = sample_config
        
        # Act
        result = await config_use_case.load_config()
        
        # Assert
        assert result == sample_config
        mock_config_manager.load_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_config_success(self, config_use_case, mock_config_manager, sample_config):
        """Test save_config exitoso."""
        # Arrange
        mock_config_manager.save_config.return_value = True
        
        # Act
        result = await config_use_case.save_config(sample_config)
        
        # Assert
        assert result is True
        mock_config_manager.save_config.assert_called_once_with(sample_config)

    @pytest.mark.asyncio
    async def test_update_mode_success(self, config_use_case, mock_config_manager):
        """Test update_mode exitoso."""
        # Arrange
        mock_config_manager.update_config.return_value = True
        
        # Act
        result = await config_use_case.update_mode("client")
        
        # Assert
        assert result is True
        mock_config_manager.update_config.assert_called_once_with(mode="client")

    @pytest.mark.asyncio
    async def test_update_mode_empty(self, config_use_case):
        """Test update_mode con modo vacío."""
        # Act & Assert
        with pytest.raises(ValueError, match="Mode cannot be empty"):
            await config_use_case.update_mode("")

    @pytest.mark.asyncio
    async def test_update_mode_whitespace(self, config_use_case):
        """Test update_mode con modo solo espacios."""
        # Act & Assert
        with pytest.raises(ValueError, match="Mode cannot be empty"):
            await config_use_case.update_mode("   ")

    @pytest.mark.asyncio
    async def test_update_llm_url_success(self, config_use_case, mock_config_manager):
        """Test update_llm_url exitoso."""
        # Arrange
        mock_config_manager.update_config.return_value = True
        
        # Act
        result = await config_use_case.update_llm_url("192.168.1.100")
        
        # Assert
        assert result is True
        mock_config_manager.update_config.assert_called_once_with(llm_url="192.168.1.100")

    @pytest.mark.asyncio
    async def test_update_llm_url_empty(self, config_use_case):
        """Test update_llm_url con IP vacía."""
        # Act & Assert
        with pytest.raises(ValueError, match="LLM URL cannot be empty"):
            await config_use_case.update_llm_url("")

    @pytest.mark.asyncio
    async def test_update_llm_model_success(self, config_use_case, mock_config_manager):
        """Test update_llm_model exitoso."""
        # Arrange
        mock_config_manager.update_config.return_value = True
        
        # Act
        result = await config_use_case.update_llm_model("new-model")
        
        # Assert
        assert result is True
        mock_config_manager.update_config.assert_called_once_with(llm_model="new-model")

    @pytest.mark.asyncio
    async def test_update_llm_model_empty(self, config_use_case):
        """Test update_llm_model con modelo vacío."""
        # Act & Assert
        with pytest.raises(ValueError, match="LLM model cannot be empty"):
            await config_use_case.update_llm_model("")

    @pytest.mark.asyncio
    async def test_update_llm_config_success(self, config_use_case, mock_config_manager):
        """Test update_llm_config exitoso."""
        # Arrange
        mock_config_manager.update_config.return_value = True
        
        # Act
        result = await config_use_case.update_llm_config("192.168.1.100", "new-model")
        
        # Assert
        assert result is True
        mock_config_manager.update_config.assert_called_once_with(llm_url="192.168.1.100", llm_model="new-model", llm_api_key=None, llm_personality=None)

    @pytest.mark.asyncio
    async def test_update_llm_config_empty_ip(self, config_use_case):
        """Test update_llm_config con IP vacía."""
        # Act & Assert
        with pytest.raises(ValueError, match="LLM URL cannot be empty"):
            await config_use_case.update_llm_config("", "new-model")

    @pytest.mark.asyncio
    async def test_update_llm_config_empty_model(self, config_use_case):
        """Test update_llm_config con modelo vacío."""
        # Act & Assert
        with pytest.raises(ValueError, match="LLM model cannot be empty"):
            await config_use_case.update_llm_config("192.168.1.100", "")

    @pytest.mark.asyncio
    async def test_validate_config_success(self, config_use_case, mock_config_manager):
        """Test validate_config exitoso."""
        # Arrange
        validation_result = ConfigValidationResult(is_valid=True)
        mock_config_manager.validate_config.return_value = validation_result
        
        # Act
        result = await config_use_case.validate_config()
        
        # Assert
        assert result == validation_result
        mock_config_manager.validate_config.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_create_default_config_success(self, config_use_case, mock_config_manager, sample_config):
        """Test create_default_config exitoso."""
        # Arrange
        mock_config_manager.create_default_config.return_value = sample_config
        
        # Act
        result = await config_use_case.create_default_config()
        
        # Assert
        assert result == sample_config
        mock_config_manager.create_default_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_config_success(self, config_use_case, mock_config_manager, sample_config):
        """Test reset_config exitoso."""
        # Arrange
        mock_config_manager.reset_config.return_value = sample_config
        
        # Act
        result = await config_use_case.reset_config()
        
        # Assert
        assert result == sample_config
        mock_config_manager.reset_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_backup_config_success(self, config_use_case, mock_config_manager):
        """Test backup_config exitoso."""
        # Arrange
        mock_config_manager.backup_config.return_value = True
        
        # Act
        result = await config_use_case.backup_config("backup.json")
        
        # Assert
        assert result is True
        mock_config_manager.backup_config.assert_called_once_with("backup.json")

    @pytest.mark.asyncio
    async def test_get_config_summary_success(self, config_use_case, mock_config_manager, sample_config):
        """Test get_config_summary exitoso."""
        # Arrange
        mock_config_manager.get_config.return_value = sample_config
        mock_config_manager.is_loaded = True
        mock_config_manager.config_file_path = "config.json"
        
        # Act
        result = await config_use_case.get_config_summary()
        
        # Assert
        assert result["mode"] == "supervisor"
        assert result["llm"]["url"] == "https://openrouter.ai/api/v1"
        assert result["llm"]["model"] == "openai/gpt-oss-20b"
        assert result["is_loaded"] is True
        assert result["config_file"] == "config.json"
        assert "created_at" in result
        assert "updated_at" in result

    @pytest.mark.asyncio
    async def test_trim_whitespace_in_updates(self, config_use_case, mock_config_manager):
        """Test que se eliminen espacios en blanco en las actualizaciones."""
        # Arrange
        mock_config_manager.update_config.return_value = True
        
        # Act
        await config_use_case.update_mode("  client  ")
        await config_use_case.update_llm_url("  192.168.1.100  ")
        await config_use_case.update_llm_model("  new-model  ")
        
        # Assert
        mock_config_manager.update_config.assert_any_call(mode="client")
        mock_config_manager.update_config.assert_any_call(llm_url="192.168.1.100")
        mock_config_manager.update_config.assert_any_call(llm_model="new-model")

    @pytest.mark.asyncio
    async def test_error_propagation(self, config_use_case, mock_config_manager):
        """Test que los errores se propaguen correctamente."""
        # Arrange
        mock_config_manager.get_config.side_effect = ValueError("Test error")
        mock_config_manager.load_config.side_effect = OSError("Load error")
        mock_config_manager.create_default_config.side_effect = OSError("Create error")
        
        # Act & Assert
        with pytest.raises(OSError, match="Create error"):
            await config_use_case.get_config()
