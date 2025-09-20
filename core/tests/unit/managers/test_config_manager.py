"""
Tests unitarios para ConfigManager.
"""

import json
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from pathlib import Path

from managers.config_manager import ConfigManager
from repositories.interfaces.file_repository import FileRepository
from api.models.domain.config import AppConfig, LLMConfig, ConfigValidationResult


class TestConfigManager:
    """Tests para ConfigManager."""

    @pytest.fixture
    def mock_file_repository(self):
        """Fixture para mock del FileRepository."""
        return AsyncMock(spec=FileRepository)

    @pytest.fixture
    def config_manager(self, mock_file_repository):
        """Fixture para ConfigManager."""
        return ConfigManager(mock_file_repository, "test_config.json")

    @pytest.fixture
    def sample_config_data(self):
        """Fixture para datos de configuración de ejemplo."""
        return {
            "mode": "supervisor",
            "llm": {
                "ip": "192.168.11.89",
                "model": "openai/gpt-oss-20b"
            },
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }

    @pytest.fixture
    def sample_config(self, sample_config_data):
        """Fixture para AppConfig de ejemplo."""
        return AppConfig.from_dict(sample_config_data)

    @pytest.mark.asyncio
    async def test_config_manager_initialization(self, mock_file_repository):
        """Test inicialización del ConfigManager."""
        # Act
        manager = ConfigManager(mock_file_repository, "custom_config.json")
        
        # Assert
        assert manager._file_repository == mock_file_repository
        assert manager._config_file_path == "custom_config.json"
        assert manager._config is None
        assert not manager._is_loaded

    @pytest.mark.asyncio
    async def test_load_config_success(self, config_manager, mock_file_repository, sample_config_data):
        """Test carga exitosa de configuración."""
        # Arrange
        config_json = json.dumps(sample_config_data)
        mock_file_repository.get_file.return_value = config_json
        
        # Act
        result = await config_manager.load_config()
        
        # Assert
        assert result.mode == "supervisor"
        assert result.llm.ip == "192.168.11.89"
        assert result.llm.model == "openai/gpt-oss-20b"
        assert config_manager._is_loaded
        assert config_manager._config == result
        mock_file_repository.get_file.assert_called_once_with("test_config.json")

    @pytest.mark.asyncio
    async def test_load_config_file_not_found(self, config_manager, mock_file_repository):
        """Test carga cuando el archivo no existe."""
        # Arrange
        mock_file_repository.get_file.return_value = None
        
        # Act & Assert
        with pytest.raises(OSError, match="Error loading configuration"):
            await config_manager.load_config()

    @pytest.mark.asyncio
    async def test_load_config_invalid_json(self, config_manager, mock_file_repository):
        """Test carga con JSON inválido."""
        # Arrange
        mock_file_repository.get_file.return_value = "invalid json"
        
        # Act & Assert
        with pytest.raises(json.JSONDecodeError, match="Invalid JSON in configuration file"):
            await config_manager.load_config()

    @pytest.mark.asyncio
    async def test_save_config_success(self, config_manager, mock_file_repository, sample_config):
        """Test guardado exitoso de configuración."""
        # Arrange
        mock_file_repository.save_file.return_value = True
        
        # Act
        result = await config_manager.save_config(sample_config)
        
        # Assert
        assert result is True
        assert config_manager._config == sample_config
        assert config_manager._is_loaded
        mock_file_repository.save_file.assert_called_once()
        
        # Verificar que se guardó JSON válido
        call_args = mock_file_repository.save_file.call_args
        assert call_args[0][0] == "test_config.json"
        saved_content = call_args[0][1]
        json.loads(saved_content)  # Debe ser JSON válido

    @pytest.mark.asyncio
    async def test_save_config_no_config(self, config_manager, mock_file_repository):
        """Test guardado sin configuración."""
        # Act & Assert
        with pytest.raises(OSError, match="Error saving configuration"):
            await config_manager.save_config()

    @pytest.mark.asyncio
    async def test_get_config_success(self, config_manager, sample_config):
        """Test obtención de configuración cargada."""
        # Arrange
        config_manager._config = sample_config
        config_manager._is_loaded = True
        
        # Act
        result = await config_manager.get_config()
        
        # Assert
        assert result == sample_config

    @pytest.mark.asyncio
    async def test_get_config_not_loaded(self, config_manager):
        """Test obtención de configuración no cargada."""
        # Act & Assert
        with pytest.raises(ValueError, match="Configuration not loaded"):
            await config_manager.get_config()

    @pytest.mark.asyncio
    async def test_update_config_mode(self, config_manager, mock_file_repository, sample_config):
        """Test actualización de modo."""
        # Arrange
        config_manager._config = sample_config
        config_manager._is_loaded = True
        mock_file_repository.save_file.return_value = True
        
        # Act
        result = await config_manager.update_config(mode="client")
        
        # Assert
        assert result is True
        assert config_manager._config.mode == "client"
        mock_file_repository.save_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_config_llm(self, config_manager, mock_file_repository, sample_config):
        """Test actualización de configuración LLM."""
        # Arrange
        config_manager._config = sample_config
        config_manager._is_loaded = True
        mock_file_repository.save_file.return_value = True
        
        # Act
        result = await config_manager.update_config(llm_ip="192.168.1.100", llm_model="new-model")
        
        # Assert
        assert result is True
        assert config_manager._config.llm.ip == "192.168.1.100"
        assert config_manager._config.llm.model == "new-model"
        mock_file_repository.save_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_config_not_loaded(self, config_manager):
        """Test actualización sin configuración cargada."""
        # Act & Assert
        with pytest.raises(OSError, match="Error updating configuration"):
            await config_manager.update_config(mode="client")

    @pytest.mark.asyncio
    async def test_create_default_config(self, config_manager, mock_file_repository):
        """Test creación de configuración por defecto."""
        # Arrange
        mock_file_repository.save_file.return_value = True
        
        # Act
        result = await config_manager.create_default_config()
        
        # Assert
        assert result.mode == "supervisor"
        assert result.llm.ip == "192.168.11.89"
        assert result.llm.model == "openai/gpt-oss-20b"
        assert config_manager._config == result
        assert config_manager._is_loaded
        mock_file_repository.save_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_config_valid(self, config_manager, sample_config):
        """Test validación de configuración válida."""
        # Act
        result = await config_manager.validate_config(sample_config)
        
        # Assert
        assert result.is_valid is True
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_validate_config_invalid_mode(self, config_manager):
        """Test validación con modo inválido."""
        # Arrange
        invalid_config = AppConfig(
            mode="",  # Modo vacío
            llm=LLMConfig(ip="192.168.11.89", model="openai/gpt-oss-20b")
        )
        
        # Act
        result = await config_manager.validate_config(invalid_config)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "Mode cannot be empty" in result.errors

    @pytest.mark.asyncio
    async def test_validate_config_invalid_ip(self, config_manager):
        """Test validación con IP inválida."""
        # Arrange
        invalid_config = AppConfig(
            mode="supervisor",
            llm=LLMConfig(ip="invalid-ip", model="openai/gpt-oss-20b")
        )
        
        # Act
        result = await config_manager.validate_config(invalid_config)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "Invalid IP address" in result.errors[0]

    @pytest.mark.asyncio
    async def test_validate_config_empty_llm_model(self, config_manager):
        """Test validación con modelo LLM vacío."""
        # Arrange
        invalid_config = AppConfig(
            mode="supervisor",
            llm=LLMConfig(ip="192.168.11.89", model="")
        )
        
        # Act
        result = await config_manager.validate_config(invalid_config)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "LLM model cannot be empty" in result.errors

    @pytest.mark.asyncio
    async def test_validate_config_unknown_mode_warning(self, config_manager):
        """Test validación con modo desconocido (advertencia)."""
        # Arrange
        config_with_unknown_mode = AppConfig(
            mode="unknown_mode",
            llm=LLMConfig(ip="192.168.11.89", model="openai/gpt-oss-20b")
        )
        
        # Act
        result = await config_manager.validate_config(config_with_unknown_mode)
        
        # Assert
        assert result.is_valid is True  # Válido pero con advertencia
        assert len(result.warnings) > 0
        assert "Unknown mode" in result.warnings[0]

    @pytest.mark.asyncio
    async def test_reset_config(self, config_manager, mock_file_repository):
        """Test reset de configuración."""
        # Arrange
        mock_file_repository.save_file.return_value = True
        
        # Act
        result = await config_manager.reset_config()
        
        # Assert
        assert result.mode == "supervisor"
        assert result.llm.ip == "192.168.11.89"
        assert result.llm.model == "openai/gpt-oss-20b"
        assert config_manager._config == result
        assert config_manager._is_loaded

    @pytest.mark.asyncio
    async def test_backup_config_success(self, config_manager, mock_file_repository, sample_config):
        """Test backup exitoso de configuración."""
        # Arrange
        config_manager._config = sample_config
        config_manager._is_loaded = True
        mock_file_repository.save_file.return_value = True
        
        # Act
        result = await config_manager.backup_config("backup.json")
        
        # Assert
        assert result is True
        mock_file_repository.save_file.assert_called_once_with("backup.json", mock_file_repository.save_file.call_args[0][1])

    @pytest.mark.asyncio
    async def test_backup_config_not_loaded(self, config_manager):
        """Test backup sin configuración cargada."""
        # Act & Assert
        with pytest.raises(OSError, match="Error creating backup"):
            await config_manager.backup_config("backup.json")

    @pytest.mark.asyncio
    async def test_is_valid_ip_valid(self, config_manager):
        """Test validación de IP válida."""
        # Act & Assert
        assert config_manager._is_valid_ip("192.168.1.1") is True
        assert config_manager._is_valid_ip("10.0.0.1") is True
        assert config_manager._is_valid_ip("127.0.0.1") is True

    @pytest.mark.asyncio
    async def test_is_valid_ip_invalid(self, config_manager):
        """Test validación de IP inválida."""
        # Act & Assert
        assert config_manager._is_valid_ip("invalid") is False
        assert config_manager._is_valid_ip("192.168.1") is False
        assert config_manager._is_valid_ip("192.168.1.256") is False
        assert config_manager._is_valid_ip("") is False

    @pytest.mark.asyncio
    async def test_properties(self, config_manager):
        """Test propiedades del manager."""
        # Assert
        assert config_manager.is_loaded is False
        assert config_manager.config_file_path == "test_config.json"

    @pytest.mark.asyncio
    async def test_load_config_with_timestamps(self, config_manager, mock_file_repository):
        """Test carga de configuración con timestamps."""
        # Arrange
        config_data = {
            "mode": "supervisor",
            "llm": {
                "ip": "192.168.11.89",
                "model": "openai/gpt-oss-20b"
            },
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-02T15:30:00"
        }
        config_json = json.dumps(config_data)
        mock_file_repository.get_file.return_value = config_json
        
        # Act
        result = await config_manager.load_config()
        
        # Assert
        assert result.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert result.updated_at == datetime(2024, 1, 2, 15, 30, 0)

    @pytest.mark.asyncio
    async def test_save_config_with_current_config(self, config_manager, mock_file_repository, sample_config):
        """Test guardado usando configuración actual."""
        # Arrange
        config_manager._config = sample_config
        config_manager._is_loaded = True
        mock_file_repository.save_file.return_value = True
        
        # Act
        result = await config_manager.save_config()
        
        # Assert
        assert result is True
        mock_file_repository.save_file.assert_called_once()
