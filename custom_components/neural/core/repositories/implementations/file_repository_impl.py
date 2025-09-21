"""
Implementación del repositorio de archivos locales.
"""

import aiofiles
from pathlib import Path
from typing import Optional

from ..interfaces.file_repository import FileRepository


class FileRepositoryImpl(FileRepository):
    """Implementación del repositorio de archivos locales."""

    def __init__(self, base_path: str = "."):
        """
        Inicializa el repositorio de archivos.
        
        Args:
            base_path: Ruta base para los archivos (por defecto directorio actual)
        """
        self._base_path = Path(base_path).resolve()

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
        try:
            # Construir la ruta completa
            full_path = self._base_path / file_path
            
            # Verificar que el archivo existe
            if not full_path.exists():
                return None
            
            # Verificar que es un archivo (no un directorio)
            if not full_path.is_file():
                raise OSError(f"Path is not a file: {full_path}")
            
            # Leer el archivo de forma asíncrona
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as file:
                content = await file.read()
                return content
                
        except PermissionError:
            raise PermissionError(f"Permission denied to read file: {file_path}")
        except OSError as e:
            raise OSError(f"Error reading file {file_path}: {str(e)}")

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
        try:
            # Construir la ruta completa
            full_path = self._base_path / file_path
            
            # Crear directorios padre si no existen
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir el archivo de forma asíncrona
            async with aiofiles.open(full_path, 'w', encoding='utf-8') as file:
                await file.write(content)
                return True
                
        except PermissionError:
            raise PermissionError(f"Permission denied to write file: {file_path}")
        except OSError as e:
            raise OSError(f"Error writing file {file_path}: {str(e)}")
        except Exception as e:
            # Capturar cualquier otra excepción y convertirla en OSError
            raise OSError(f"Unexpected error writing file {file_path}: {str(e)}")
