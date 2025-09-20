"""
Manager para gestión de configuración de la aplicación.
"""

import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from repositories.interfaces.file_repository import FileRepository
from api.models.domain.config import AppConfig, LLMConfig, ConfigValidationResult

_LOGGER = logging.getLogger(__name__)


class ConfigManager:
    """Manager para gestión de configuración."""
    
    def __init__(self, file_repository: FileRepository, config_file_path: str = "config.json"):
        """
        Inicializar el manager de configuración.
        
        Args:
            file_repository: Repositorio de archivos para persistencia
            config_file_path: Ruta del archivo de configuración
        """
        self._file_repository = file_repository
        self._config_file_path = config_file_path
        self._config: Optional[AppConfig] = None
        self._is_loaded = False
    
    async def load_config(self) -> AppConfig:
        """
        Cargar configuración desde archivo.
        
        Returns:
            Configuración cargada
            
        Raises:
            FileNotFoundError: Si el archivo de configuración no existe
            json.JSONDecodeError: Si el archivo no es JSON válido
            OSError: Si hay error leyendo el archivo
        """
        try:
            _LOGGER.info("Loading configuration from: %s", self._config_file_path)
            
            # Leer contenido del archivo
            content = await self._file_repository.get_file(self._config_file_path)
            
            if content is None:
                raise FileNotFoundError(f"Configuration file not found: {self._config_file_path}")
            
            # Parsear JSON
            config_data = json.loads(content)
            
            # Crear objeto de configuración
            self._config = AppConfig.from_dict(config_data)
            self._is_loaded = True
            
            _LOGGER.info("Configuration loaded successfully")
            return self._config
            
        except json.JSONDecodeError as e:
            _LOGGER.error("Invalid JSON in configuration file: %s", e)
            raise json.JSONDecodeError("Invalid JSON in configuration file", e.doc, e.pos)
        except Exception as e:
            _LOGGER.error("Error loading configuration: %s", e)
            raise OSError(f"Error loading configuration: {e}")
    
    async def save_config(self, config: Optional[AppConfig] = None) -> bool:
        """
        Guardar configuración en archivo.
        
        Args:
            config: Configuración a guardar (si no se proporciona, usa la actual)
            
        Returns:
            True si se guardó correctamente
            
        Raises:
            ValueError: Si no hay configuración para guardar
            OSError: Si hay error escribiendo el archivo
        """
        try:
            config_to_save = config or self._config
            
            if config_to_save is None:
                raise ValueError("No configuration to save")
            
            _LOGGER.info("Saving configuration to: %s", self._config_file_path)
            
            # Convertir a JSON
            config_dict = config_to_save.to_dict()
            content = json.dumps(config_dict, indent=2, ensure_ascii=False)
            
            # Guardar archivo
            success = await self._file_repository.save_file(self._config_file_path, content)
            
            if success:
                self._config = config_to_save
                self._is_loaded = True
                _LOGGER.info("Configuration saved successfully")
            
            return success
            
        except Exception as e:
            _LOGGER.error("Error saving configuration: %s", e)
            raise OSError(f"Error saving configuration: {e}")
    
    async def get_config(self) -> AppConfig:
        """
        Obtener configuración actual.
        
        Returns:
            Configuración actual
            
        Raises:
            ValueError: Si la configuración no está cargada
        """
        if not self._is_loaded or self._config is None:
            raise ValueError("Configuration not loaded. Call load_config() first.")
        
        return self._config
    
    async def update_config(self, **kwargs) -> bool:
        """
        Actualizar configuración con nuevos valores.
        
        Args:
            **kwargs: Valores a actualizar (mode, llm_ip, llm_model)
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            if not self._is_loaded or self._config is None:
                raise ValueError("Configuration not loaded. Call load_config() first.")
            
            # Actualizar modo si se proporciona
            if "mode" in kwargs:
                self._config.update_mode(kwargs["mode"])
            
            # Actualizar LLM si se proporciona
            if "llm_ip" in kwargs or "llm_model" in kwargs:
                current_ip = self._config.llm.ip
                current_model = self._config.llm.model
                
                new_ip = kwargs.get("llm_ip", current_ip)
                new_model = kwargs.get("llm_model", current_model)
                
                self._config.update_llm(new_ip, new_model)
            
            # Guardar cambios
            return await self.save_config()
            
        except Exception as e:
            _LOGGER.error("Error updating configuration: %s", e)
            raise OSError(f"Error updating configuration: {e}")
    
    async def create_default_config(self) -> AppConfig:
        """
        Crear configuración por defecto.
        
        Returns:
            Configuración por defecto creada
        """
        _LOGGER.info("Creating default configuration")
        
        default_config = AppConfig(
            mode="supervisor",
            llm=LLMConfig(
                ip="192.168.11.89",
                model="openai/gpt-oss-20b"
            )
        )
        
        # Guardar configuración por defecto
        await self.save_config(default_config)
        
        return default_config
    
    async def validate_config(self, config: Optional[AppConfig] = None) -> ConfigValidationResult:
        """
        Validar configuración.
        
        Args:
            config: Configuración a validar (si no se proporciona, usa la actual)
            
        Returns:
            Resultado de validación
        """
        config_to_validate = config or self._config
        
        if config_to_validate is None:
            result = ConfigValidationResult(is_valid=False)
            result.add_error("No configuration to validate")
            return result
        
        result = ConfigValidationResult(is_valid=True)
        
        # Validar modo
        if not config_to_validate.mode:
            result.add_error("Mode cannot be empty")
        elif config_to_validate.mode not in ["supervisor", "client", "standalone"]:
            result.add_warning(f"Unknown mode: {config_to_validate.mode}")
        
        # Validar LLM IP
        if not config_to_validate.llm.ip:
            result.add_error("LLM IP cannot be empty")
        elif not self._is_valid_ip(config_to_validate.llm.ip):
            result.add_error(f"Invalid IP address: {config_to_validate.llm.ip}")
        
        # Validar LLM modelo
        if not config_to_validate.llm.model:
            result.add_error("LLM model cannot be empty")
        
        return result
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validar formato de IP."""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            
            for part in parts:
                if not part.isdigit():
                    return False
                num = int(part)
                if not 0 <= num <= 255:
                    return False
            
            return True
        except (ValueError, AttributeError):
            return False
    
    async def reset_config(self) -> AppConfig:
        """
        Resetear configuración a valores por defecto.
        
        Returns:
            Nueva configuración por defecto
        """
        _LOGGER.info("Resetting configuration to defaults")
        return await self.create_default_config()
    
    async def backup_config(self, backup_path: str) -> bool:
        """
        Crear backup de la configuración actual.
        
        Args:
            backup_path: Ruta del archivo de backup
            
        Returns:
            True si se creó el backup correctamente
        """
        try:
            if not self._is_loaded or self._config is None:
                raise ValueError("No configuration to backup")
            
            _LOGGER.info("Creating configuration backup: %s", backup_path)
            
            # Crear backup con timestamp
            backup_config = self._config
            backup_content = json.dumps(backup_config.to_dict(), indent=2, ensure_ascii=False)
            
            return await self._file_repository.save_file(backup_path, backup_content)
            
        except Exception as e:
            _LOGGER.error("Error creating backup: %s", e)
            raise OSError(f"Error creating backup: {e}")
    
    @property
    def is_loaded(self) -> bool:
        """Verificar si la configuración está cargada."""
        return self._is_loaded
    
    @property
    def config_file_path(self) -> str:
        """Obtener ruta del archivo de configuración."""
        return self._config_file_path
