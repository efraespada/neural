"""
Interfaz para casos de uso de configuración.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from api.models.domain.config import AppConfig, ConfigValidationResult


class ConfigUseCase(ABC):
    """Interfaz para casos de uso de configuración."""

    @abstractmethod
    async def get_config(self) -> AppConfig:
        """
        Obtener configuración actual.
        
        Returns:
            Configuración actual
            
        Raises:
            ValueError: Si la configuración no está cargada
            OSError: Si hay error accediendo a la configuración
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def update_llm_ip(self, ip: str) -> bool:
        """
        Actualizar IP del modelo LLM.
        
        Args:
            ip: Nueva IP del modelo LLM
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si la IP no es válida
            OSError: Si hay error actualizando la configuración
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def update_llm_config(self, ip: str, model: str) -> bool:
        """
        Actualizar configuración completa del LLM.
        
        Args:
            ip: Nueva IP del modelo LLM
            model: Nuevo modelo LLM
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            ValueError: Si la IP o modelo no son válidos
            OSError: Si hay error actualizando la configuración
        """
        pass

    @abstractmethod
    async def validate_config(self, config: Optional[AppConfig] = None) -> ConfigValidationResult:
        """
        Validar configuración.
        
        Args:
            config: Configuración a validar (si no se proporciona, usa la actual)
            
        Returns:
            Resultado de validación
        """
        pass

    @abstractmethod
    async def create_default_config(self) -> AppConfig:
        """
        Crear configuración por defecto.
        
        Returns:
            Configuración por defecto creada
        """
        pass

    @abstractmethod
    async def reset_config(self) -> AppConfig:
        """
        Resetear configuración a valores por defecto.
        
        Returns:
            Nueva configuración por defecto
        """
        pass

    @abstractmethod
    async def backup_config(self, backup_path: str) -> bool:
        """
        Crear backup de la configuración actual.
        
        Args:
            backup_path: Ruta del archivo de backup
            
        Returns:
            True si se creó el backup correctamente
        """
        pass

    @abstractmethod
    async def get_config_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de la configuración actual.
        
        Returns:
            Diccionario con resumen de configuración
        """
        pass
