"""
Interfaz para el repositorio de archivos locales.
"""

from abc import ABC, abstractmethod
from typing import Optional

class FileRepository(ABC):
    """Interfaz para el repositorio de archivos locales."""

    @abstractmethod
    async def get_file(self, file_path: str) -> Optional[str]:
        """
        Recupera el contenido de un archivo local.
        
        Args:
            file_path: Ruta del archivo a recuperar
            
        Returns:
            Contenido del archivo como string, o None si no existe
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            PermissionError: Si no se tienen permisos para leer el archivo
            OSError: Si hay un error del sistema operativo
        """
        pass

    @abstractmethod
    async def save_file(self, file_path: str, content: str) -> bool:
        """
        Guarda contenido en un archivo local.
        
        Args:
            file_path: Ruta donde guardar el archivo
            content: Contenido a guardar
            
        Returns:
            True si se guardó correctamente, False en caso contrario
            
        Raises:
            PermissionError: Si no se tienen permisos para escribir
            OSError: Si hay un error del sistema operativo
        """
        pass
