"""
Tests unitarios para FileRepository.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch, mock_open
from core.repositories.interfaces.file_repository import FileRepository
from core.repositories.implementations.file_repository_impl import FileRepositoryImpl


class TestFileRepositoryInterface:
    """Tests para la interfaz FileRepository."""

    @pytest.fixture
    def mock_file_repository(self):
        """Fixture para mock del FileRepository."""
        return AsyncMock(spec=FileRepository)

    @pytest.mark.asyncio
    async def test_get_file_success(self, mock_file_repository):
        """Test get_file exitoso."""
        # Arrange
        file_path = "test.txt"
        expected_content = "Hello, World!"
        mock_file_repository.get_file.return_value = expected_content
        
        # Act
        result = await mock_file_repository.get_file(file_path)
        
        # Assert
        assert result == expected_content
        mock_file_repository.get_file.assert_called_once_with(file_path)

    @pytest.mark.asyncio
    async def test_get_file_not_found(self, mock_file_repository):
        """Test get_file cuando el archivo no existe."""
        # Arrange
        file_path = "nonexistent.txt"
        mock_file_repository.get_file.return_value = None
        
        # Act
        result = await mock_file_repository.get_file(file_path)
        
        # Assert
        assert result is None
        mock_file_repository.get_file.assert_called_once_with(file_path)

    @pytest.mark.asyncio
    async def test_get_file_permission_error(self, mock_file_repository):
        """Test get_file con error de permisos."""
        # Arrange
        file_path = "restricted.txt"
        mock_file_repository.get_file.side_effect = PermissionError("Permission denied")
        
        # Act & Assert
        with pytest.raises(PermissionError, match="Permission denied"):
            await mock_file_repository.get_file(file_path)

    @pytest.mark.asyncio
    async def test_get_file_os_error(self, mock_file_repository):
        """Test get_file con error del sistema operativo."""
        # Arrange
        file_path = "error.txt"
        mock_file_repository.get_file.side_effect = OSError("System error")
        
        # Act & Assert
        with pytest.raises(OSError, match="System error"):
            await mock_file_repository.get_file(file_path)

    @pytest.mark.asyncio
    async def test_save_file_success(self, mock_file_repository):
        """Test save_file exitoso."""
        # Arrange
        file_path = "test.txt"
        content = "Hello, World!"
        mock_file_repository.save_file.return_value = True
        
        # Act
        result = await mock_file_repository.save_file(file_path, content)
        
        # Assert
        assert result is True
        mock_file_repository.save_file.assert_called_once_with(file_path, content)

    @pytest.mark.asyncio
    async def test_save_file_failure(self, mock_file_repository):
        """Test save_file fallido."""
        # Arrange
        file_path = "test.txt"
        content = "Hello, World!"
        mock_file_repository.save_file.return_value = False
        
        # Act
        result = await mock_file_repository.save_file(file_path, content)
        
        # Assert
        assert result is False
        mock_file_repository.save_file.assert_called_once_with(file_path, content)

    @pytest.mark.asyncio
    async def test_save_file_permission_error(self, mock_file_repository):
        """Test save_file con error de permisos."""
        # Arrange
        file_path = "restricted.txt"
        content = "Hello, World!"
        mock_file_repository.save_file.side_effect = PermissionError("Permission denied")
        
        # Act & Assert
        with pytest.raises(PermissionError, match="Permission denied"):
            await mock_file_repository.save_file(file_path, content)

    @pytest.mark.asyncio
    async def test_save_file_os_error(self, mock_file_repository):
        """Test save_file con error del sistema operativo."""
        # Arrange
        file_path = "error.txt"
        content = "Hello, World!"
        mock_file_repository.save_file.side_effect = OSError("System error")
        
        # Act & Assert
        with pytest.raises(OSError, match="System error"):
            await mock_file_repository.save_file(file_path, content)


class TestFileRepositoryImpl:
    """Tests para la implementación FileRepositoryImpl."""

    @pytest.fixture
    def temp_dir(self):
        """Fixture para directorio temporal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def file_repository(self, temp_dir):
        """Fixture para FileRepositoryImpl con directorio temporal."""
        return FileRepositoryImpl(base_path=temp_dir)

    @pytest.mark.asyncio
    async def test_get_file_success(self, file_repository, temp_dir):
        """Test get_file exitoso con archivo real."""
        # Arrange
        file_path = "test.txt"
        content = "Hello, World!"
        full_path = Path(temp_dir) / file_path
        
        # Crear archivo de prueba
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Act
        result = await file_repository.get_file(file_path)
        
        # Assert
        assert result == content

    @pytest.mark.asyncio
    async def test_get_file_not_found(self, file_repository):
        """Test get_file cuando el archivo no existe."""
        # Arrange
        file_path = "nonexistent.txt"
        
        # Act
        result = await file_repository.get_file(file_path)
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_file_directory_not_file(self, file_repository, temp_dir):
        """Test get_file cuando la ruta es un directorio."""
        # Arrange
        file_path = "test_dir"
        full_path = Path(temp_dir) / file_path
        full_path.mkdir()
        
        # Act & Assert
        with pytest.raises(OSError, match="Path is not a file"):
            await file_repository.get_file(file_path)

    @pytest.mark.asyncio
    async def test_save_file_success(self, file_repository, temp_dir):
        """Test save_file exitoso."""
        # Arrange
        file_path = "test.txt"
        content = "Hello, World!"
        
        # Act
        result = await file_repository.save_file(file_path, content)
        
        # Assert
        assert result is True
        
        # Verificar que el archivo se creó
        full_path = Path(temp_dir) / file_path
        assert full_path.exists()
        
        # Verificar contenido
        with open(full_path, 'r', encoding='utf-8') as f:
            assert f.read() == content

    @pytest.mark.asyncio
    async def test_save_file_create_directories(self, file_repository, temp_dir):
        """Test save_file creando directorios padre."""
        # Arrange
        file_path = "subdir/nested/test.txt"
        content = "Hello, World!"
        
        # Act
        result = await file_repository.save_file(file_path, content)
        
        # Assert
        assert result is True
        
        # Verificar que el archivo se creó
        full_path = Path(temp_dir) / file_path
        assert full_path.exists()
        
        # Verificar contenido
        with open(full_path, 'r', encoding='utf-8') as f:
            assert f.read() == content

    @pytest.mark.asyncio
    async def test_save_file_overwrite(self, file_repository, temp_dir):
        """Test save_file sobrescribiendo archivo existente."""
        # Arrange
        file_path = "test.txt"
        original_content = "Original content"
        new_content = "New content"
        
        # Crear archivo original
        full_path = Path(temp_dir) / file_path
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # Act
        result = await file_repository.save_file(file_path, new_content)
        
        # Assert
        assert result is True
        
        # Verificar que el contenido se sobrescribió
        with open(full_path, 'r', encoding='utf-8') as f:
            assert f.read() == new_content

    @pytest.mark.asyncio
    async def test_save_file_empty_content(self, file_repository, temp_dir):
        """Test save_file con contenido vacío."""
        # Arrange
        file_path = "empty.txt"
        content = ""
        
        # Act
        result = await file_repository.save_file(file_path, content)
        
        # Assert
        assert result is True
        
        # Verificar que el archivo se creó
        full_path = Path(temp_dir) / file_path
        assert full_path.exists()
        
        # Verificar contenido
        with open(full_path, 'r', encoding='utf-8') as f:
            assert f.read() == ""

    @pytest.mark.asyncio
    async def test_save_file_multiline_content(self, file_repository, temp_dir):
        """Test save_file con contenido multilínea."""
        # Arrange
        file_path = "multiline.txt"
        content = "Line 1\nLine 2\nLine 3"
        
        # Act
        result = await file_repository.save_file(file_path, content)
        
        # Assert
        assert result is True
        
        # Verificar que el archivo se creó
        full_path = Path(temp_dir) / file_path
        assert full_path.exists()
        
        # Verificar contenido
        with open(full_path, 'r', encoding='utf-8') as f:
            assert f.read() == content

    @pytest.mark.asyncio
    async def test_save_file_special_characters(self, file_repository, temp_dir):
        """Test save_file con caracteres especiales."""
        # Arrange
        file_path = "special.txt"
        content = "Hello, 世界! 🌍\nSpecial chars: áéíóú ñ"
        
        # Act
        result = await file_repository.save_file(file_path, content)
        
        # Assert
        assert result is True
        
        # Verificar que el archivo se creó
        full_path = Path(temp_dir) / file_path
        assert full_path.exists()
        
        # Verificar contenido
        with open(full_path, 'r', encoding='utf-8') as f:
            assert f.read() == content

    @pytest.mark.asyncio
    async def test_get_file_after_save(self, file_repository, temp_dir):
        """Test get_file después de save_file."""
        # Arrange
        file_path = "test.txt"
        content = "Hello, World!"
        
        # Act - Guardar archivo
        save_result = await file_repository.save_file(file_path, content)
        assert save_result is True
        
        # Act - Leer archivo
        read_result = await file_repository.get_file(file_path)
        
        # Assert
        assert read_result == content

    @pytest.mark.asyncio
    async def test_base_path_initialization(self):
        """Test inicialización con base_path personalizado."""
        # Arrange
        custom_path = "/custom/path"
        
        # Act
        repository = FileRepositoryImpl(base_path=custom_path)
        
        # Assert
        assert repository._base_path == Path(custom_path).resolve()

    @pytest.mark.asyncio
    async def test_base_path_default(self):
        """Test inicialización con base_path por defecto."""
        # Act
        repository = FileRepositoryImpl()
        
        # Assert
        assert repository._base_path == Path(".").resolve()
