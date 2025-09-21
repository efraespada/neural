"""
Implementación del caso de uso de configuración.
"""

import logging
from typing import Optional, Dict, Any

from use_cases.interfaces.config_use_case import ConfigUseCase
from managers.config_manager import ConfigManager
from api.models.domain.config import AppConfig, ConfigValidationResult

_LOGGER = logging.getLogger(__name__)


class ConfigUseCaseImpl(ConfigUseCase):
    """Implementación del caso de uso de configuración."""

    def __init__(self, config_manager: ConfigManager):
        """
        Inicializar el caso de uso de configuración.
        
        Args:
            config_manager: Manager de configuración
        """
        self._config_manager = config_manager

    async def get_config(self) -> AppConfig:
        """
        Obtener configuración actual.
        
        Returns:
            Configuración actual
            
        Raises:
            ValueError: Si la configuración no está cargada
            OSError: Si hay error accediendo a la configuración
        """
        try:
            _LOGGER.debug("Getting current configuration")
            try:
                config = await self._config_manager.get_config()
                return config
            except ValueError:
                # Configuration not loaded, load it
                _LOGGER.debug("Configuration not loaded, loading it...")
                try:
                    config = await self._config_manager.load_config()
                    return config
                except (FileNotFoundError, OSError):
                    # Configuration file doesn't exist, create default
                    _LOGGER.debug("Configuration file not found, creating default...")
                    config = await self._config_manager.create_default_config()
                    return config
        except Exception as e:
            _LOGGER.error("Error getting configuration: %s", e)
            raise

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
            _LOGGER.debug("Loading configuration from file")
            return await self._config_manager.load_config()
        except Exception as e:
            _LOGGER.error("Error loading configuration: %s", e)
            raise

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
            _LOGGER.debug("Saving configuration to file")
            return await self._config_manager.save_config(config)
        except Exception as e:
            _LOGGER.error("Error saving configuration: %s", e)
            raise

    async def update_mode(self, mode: str) -> bool:
        """
        Actualizar modo de la aplicación.
        
        Args:
            mode: Nuevo modo (supervisor, client, standalone)
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si el modo no es válido
            OSError: Si hay error actualizando la configuración
        """
        try:
            _LOGGER.debug("Updating mode to: %s", mode)
            
            # Validar modo
            if not mode or not mode.strip():
                raise ValueError("Mode cannot be empty")
            
            # Ensure configuration is loaded
            await self.get_config()
            
            # Actualizar configuración
            return await self._config_manager.update_config(mode=mode.strip())
            
        except Exception as e:
            _LOGGER.error("Error updating mode: %s", e)
            raise

    async def update_llm_url(self, url: str) -> bool:
        """
        Actualizar URL del modelo LLM.
        
        Args:
            url: Nueva URL del modelo LLM
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si la URL no es válida
            OSError: Si hay error actualizando la configuración
        """
        try:
            _LOGGER.debug("Updating LLM URL to: %s", url)
            
            # Validar URL
            if not url or not url.strip():
                raise ValueError("LLM URL cannot be empty")
            
            # Ensure configuration is loaded
            await self.get_config()
            
            # Actualizar configuración
            return await self._config_manager.update_config(llm_url=url.strip())
            
        except Exception as e:
            _LOGGER.error("Error updating LLM URL: %s", e)
            raise

    async def update_llm_model(self, model: str) -> bool:
        """
        Actualizar modelo LLM.
        
        Args:
            model: Nuevo modelo LLM
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si el modelo no es válido
            OSError: Si hay error actualizando la configuración
        """
        try:
            _LOGGER.debug("Updating LLM model to: %s", model)
            
            # Validar modelo
            if not model or not model.strip():
                raise ValueError("LLM model cannot be empty")
            
            # Ensure configuration is loaded
            await self.get_config()
            
            # Actualizar configuración
            return await self._config_manager.update_config(llm_model=model.strip())
            
        except Exception as e:
            _LOGGER.error("Error updating LLM model: %s", e)
            raise

    async def update_llm_config(self, url: str, model: str, api_key: Optional[str] = None, personality: Optional[str] = None) -> bool:
        """
        Actualizar configuración completa del LLM.
        
        Args:
            url: Nueva URL del modelo LLM
            model: Nuevo modelo LLM
            api_key: Nueva API key (opcional)
            personality: Nueva personalidad (opcional)
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si la URL o modelo no son válidos
            OSError: Si hay error actualizando la configuración
        """
        try:
            _LOGGER.debug("Updating LLM config - URL: %s, Model: %s, Personality: %s", url, model, personality)
            
            # Validar parámetros
            if not url or not url.strip():
                raise ValueError("LLM URL cannot be empty")
            if not model or not model.strip():
                raise ValueError("LLM model cannot be empty")
            
            # Validar personalidad si se proporciona
            if personality and personality.strip():
                valid_personalities = ["hal9000", "mother", "jarvis", "kitt"]
                if personality.strip() not in valid_personalities:
                    raise ValueError(f"Invalid personality: {personality}. Must be one of: {', '.join(valid_personalities)}")
            
            # Ensure configuration is loaded
            await self.get_config()
            
            # Actualizar configuración
            return await self._config_manager.update_config(
                llm_url=url.strip(),
                llm_model=model.strip(),
                llm_api_key=api_key.strip() if api_key else None,
                llm_personality=personality.strip() if personality else None
            )
            
        except Exception as e:
            _LOGGER.error("Error updating LLM config: %s", e)
            raise

    async def update_llm_personality(self, personality: str) -> bool:
        """
        Actualizar personalidad del LLM.
        
        Args:
            personality: Nueva personalidad
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si la personalidad no es válida
            OSError: Si hay error actualizando la configuración
        """
        try:
            _LOGGER.debug("Updating LLM personality to: %s", personality)
            
            # Validar personalidad
            valid_personalities = ["hal9000", "mother", "jarvis", "kitt"]
            if not personality or not personality.strip():
                raise ValueError("LLM personality cannot be empty")
            if personality.strip() not in valid_personalities:
                raise ValueError(f"Invalid personality: {personality}. Must be one of: {', '.join(valid_personalities)}")
            
            # Ensure configuration is loaded
            await self.get_config()
            
            # Actualizar configuración
            return await self._config_manager.update_config(llm_personality=personality.strip())
            
        except Exception as e:
            _LOGGER.error("Error updating LLM personality: %s", e)
            raise

    async def validate_config(self, config: Optional[AppConfig] = None) -> ConfigValidationResult:
        """
        Validar configuración.
        
        Args:
            config: Configuración a validar (si no se proporciona, usa la actual)
            
        Returns:
            Resultado de validación
        """
        try:
            _LOGGER.debug("Validating configuration")
            return await self._config_manager.validate_config(config)
        except Exception as e:
            _LOGGER.error("Error validating configuration: %s", e)
            raise

    async def create_default_config(self) -> AppConfig:
        """
        Crear configuración por defecto.
        
        Returns:
            Configuración por defecto creada
        """
        try:
            _LOGGER.debug("Creating default configuration")
            return await self._config_manager.create_default_config()
        except Exception as e:
            _LOGGER.error("Error creating default configuration: %s", e)
            raise

    async def reset_config(self) -> AppConfig:
        """
        Resetear configuración a valores por defecto.
        
        Returns:
            Nueva configuración por defecto
        """
        try:
            _LOGGER.debug("Resetting configuration to defaults")
            return await self._config_manager.reset_config()
        except Exception as e:
            _LOGGER.error("Error resetting configuration: %s", e)
            raise

    async def backup_config(self, backup_path: str) -> bool:
        """
        Crear backup de la configuración actual.
        
        Args:
            backup_path: Ruta del archivo de backup
            
        Returns:
            True si se creó el backup correctamente
        """
        try:
            _LOGGER.debug("Creating configuration backup: %s", backup_path)
            return await self._config_manager.backup_config(backup_path)
        except Exception as e:
            _LOGGER.error("Error creating backup: %s", e)
            raise

    async def get_config_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de la configuración actual.
        
        Returns:
            Diccionario con resumen de configuración
        """
        try:
            _LOGGER.debug("Getting configuration summary")
            
            # Obtener configuración actual
            config = await self.get_config()
            
            # Crear resumen
            summary = {
                "mode": config.mode,
                "llm": {
                    "url": config.llm.url,
                    "model": config.llm.model,
                    "personality": config.llm.personality
                },
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat(),
                "is_loaded": self._config_manager.is_loaded,
                "config_file": self._config_manager.config_file_path
            }
            
            return summary
            
        except Exception as e:
            _LOGGER.error("Error getting configuration summary: %s", e)
            raise
