"""Unit tests for UpdateHomeInfoUseCase interface and implementation."""

import os
import pytest
import tempfile
from unittest.mock import patch, mock_open
from typing import Optional

from core.use_cases.interfaces.update_home_info_use_case import UpdateHomeInfoUseCase
from core.use_cases.implementations.update_home_info_use_case_impl import UpdateHomeInfoUseCaseImpl


@pytest.fixture
def update_home_info_use_case():
    """Create UpdateHomeInfoUseCaseImpl instance."""
    return UpdateHomeInfoUseCaseImpl()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestUpdateHomeInfoUseCaseInterface:
    """Test UpdateHomeInfoUseCase interface behavior."""
    
    @pytest.mark.asyncio
    async def test_update_home_info_success(self, update_home_info_use_case, temp_dir):
        """Test successful home information update."""
        # Arrange
        home_info = "# Mi Casa\n\nEsta es la información de mi hogar.\n\n- Sala de estar\n- Cocina\n- Dormitorio"
        
        with patch.object(update_home_info_use_case, '_home_info_file', os.path.join(temp_dir, 'home_info.md')):
            # Act
            result = await update_home_info_use_case.update_home_info(home_info)
            
            # Assert
            assert result is True
            
            # Verify file was created and contains correct content
            assert os.path.exists(update_home_info_use_case._home_info_file)
            with open(update_home_info_use_case._home_info_file, 'r', encoding='utf-8') as f:
                content = f.read()
            assert content == home_info.strip()
    
    @pytest.mark.asyncio
    async def test_update_home_info_empty_string(self, update_home_info_use_case):
        """Test update with empty string."""
        # Act & Assert
        with pytest.raises(OSError, match="Error updating home information"):
            await update_home_info_use_case.update_home_info("")
    
    @pytest.mark.asyncio
    async def test_update_home_info_whitespace_only(self, update_home_info_use_case):
        """Test update with whitespace only."""
        # Act & Assert
        with pytest.raises(OSError, match="Error updating home information"):
            await update_home_info_use_case.update_home_info("   \n\t  ")
    
    @pytest.mark.asyncio
    async def test_update_home_info_too_short(self, update_home_info_use_case):
        """Test update with content too short."""
        # Act & Assert
        with pytest.raises(OSError, match="Error updating home information"):
            await update_home_info_use_case.update_home_info("Short")
    
    @pytest.mark.asyncio
    async def test_update_home_info_exactly_minimum_length(self, update_home_info_use_case, temp_dir):
        """Test update with exactly minimum length content."""
        # Arrange
        home_info = "1234567890"  # Exactly 10 characters
        
        with patch.object(update_home_info_use_case, '_home_info_file', os.path.join(temp_dir, 'home_info.md')):
            # Act
            result = await update_home_info_use_case.update_home_info(home_info)
            
            # Assert
            assert result is True
    
    @pytest.mark.asyncio
    async def test_update_home_info_strips_whitespace(self, update_home_info_use_case, temp_dir):
        """Test that whitespace is stripped from content."""
        # Arrange
        home_info = "  \n  # Mi Casa\n\nInformación del hogar.  \n  "
        expected_content = "# Mi Casa\n\nInformación del hogar."
        
        with patch.object(update_home_info_use_case, '_home_info_file', os.path.join(temp_dir, 'home_info.md')):
            # Act
            result = await update_home_info_use_case.update_home_info(home_info)
            
            # Assert
            assert result is True
            
            # Verify content was stripped
            with open(update_home_info_use_case._home_info_file, 'r', encoding='utf-8') as f:
                content = f.read()
            assert content == expected_content
    
    @pytest.mark.asyncio
    async def test_update_home_info_file_error(self, update_home_info_use_case):
        """Test update when file write fails."""
        # Arrange
        home_info = "# Mi Casa\n\nEsta es la información de mi hogar."
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            # Act & Assert
            with pytest.raises(OSError, match="Error updating home information"):
                await update_home_info_use_case.update_home_info(home_info)
    
    @pytest.mark.asyncio
    async def test_get_home_info_success(self, update_home_info_use_case, temp_dir):
        """Test successful home information retrieval."""
        # Arrange
        home_info = "# Mi Casa\n\nEsta es la información de mi hogar."
        file_path = os.path.join(temp_dir, 'home_info.md')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(home_info)
        
        with patch.object(update_home_info_use_case, '_home_info_file', file_path):
            # Act
            result = await update_home_info_use_case.get_home_info()
            
            # Assert
            assert result == home_info
    
    @pytest.mark.asyncio
    async def test_get_home_info_file_not_exists(self, update_home_info_use_case, temp_dir):
        """Test get home info when file doesn't exist."""
        # Arrange
        file_path = os.path.join(temp_dir, 'nonexistent.md')
        
        with patch.object(update_home_info_use_case, '_home_info_file', file_path):
            # Act
            result = await update_home_info_use_case.get_home_info()
            
            # Assert
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_home_info_empty_file(self, update_home_info_use_case, temp_dir):
        """Test get home info when file is empty."""
        # Arrange
        file_path = os.path.join(temp_dir, 'empty.md')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("")
        
        with patch.object(update_home_info_use_case, '_home_info_file', file_path):
            # Act
            result = await update_home_info_use_case.get_home_info()
            
            # Assert
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_home_info_whitespace_only(self, update_home_info_use_case, temp_dir):
        """Test get home info when file contains only whitespace."""
        # Arrange
        file_path = os.path.join(temp_dir, 'whitespace.md')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("   \n\t  ")
        
        with patch.object(update_home_info_use_case, '_home_info_file', file_path):
            # Act
            result = await update_home_info_use_case.get_home_info()
            
            # Assert
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_home_info_strips_whitespace(self, update_home_info_use_case, temp_dir):
        """Test that whitespace is stripped when reading."""
        # Arrange
        home_info = "  \n  # Mi Casa\n\nInformación del hogar.  \n  "
        expected_content = "# Mi Casa\n\nInformación del hogar."
        file_path = os.path.join(temp_dir, 'home_info.md')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(home_info)
        
        with patch.object(update_home_info_use_case, '_home_info_file', file_path):
            # Act
            result = await update_home_info_use_case.get_home_info()
            
            # Assert
            assert result == expected_content
    
    @pytest.mark.asyncio
    async def test_get_home_info_file_error(self, update_home_info_use_case):
        """Test get home info when file read fails."""
        # Arrange
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            # Act & Assert
            with pytest.raises(OSError, match="Error getting home information"):
                await update_home_info_use_case.get_home_info()
    
    @pytest.mark.asyncio
    async def test_clear_home_info_success(self, update_home_info_use_case, temp_dir):
        """Test successful home information clearing."""
        # Arrange
        file_path = os.path.join(temp_dir, 'home_info.md')
        
        # Create a file to clear
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# Mi Casa\n\nInformación del hogar.")
        
        with patch.object(update_home_info_use_case, '_home_info_file', file_path):
            # Act
            result = await update_home_info_use_case.clear_home_info()
            
            # Assert
            assert result is True
            assert not os.path.exists(file_path)
    
    @pytest.mark.asyncio
    async def test_clear_home_info_file_not_exists(self, update_home_info_use_case, temp_dir):
        """Test clear home info when file doesn't exist."""
        # Arrange
        file_path = os.path.join(temp_dir, 'nonexistent.md')
        
        with patch.object(update_home_info_use_case, '_home_info_file', file_path):
            # Act
            result = await update_home_info_use_case.clear_home_info()
            
            # Assert
            assert result is True  # Should still return True even if file doesn't exist
    
    @pytest.mark.asyncio
    async def test_clear_home_info_file_error(self, update_home_info_use_case):
        """Test clear home info when file removal fails."""
        # Arrange
        with patch('os.path.exists', return_value=True), \
             patch('os.remove', side_effect=OSError("Permission denied")):
            # Act & Assert
            with pytest.raises(OSError, match="Error clearing home information"):
                await update_home_info_use_case.clear_home_info()
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, update_home_info_use_case, temp_dir):
        """Test complete workflow: update -> get -> clear."""
        # Arrange
        home_info = "# Mi Casa\n\nEsta es la información de mi hogar.\n\n- Sala de estar\n- Cocina"
        file_path = os.path.join(temp_dir, 'home_info.md')
        
        with patch.object(update_home_info_use_case, '_home_info_file', file_path):
            # Act 1: Update
            update_result = await update_home_info_use_case.update_home_info(home_info)
            
            # Assert 1: Update successful
            assert update_result is True
            assert os.path.exists(file_path)
            
            # Act 2: Get
            get_result = await update_home_info_use_case.get_home_info()
            
            # Assert 2: Get successful
            assert get_result == home_info
            
            # Act 3: Clear
            clear_result = await update_home_info_use_case.clear_home_info()
            
            # Assert 3: Clear successful
            assert clear_result is True
            assert not os.path.exists(file_path)
            
            # Act 4: Get after clear
            get_after_clear = await update_home_info_use_case.get_home_info()
            
            # Assert 4: Should return None after clear
            assert get_after_clear is None
    
    @pytest.mark.asyncio
    async def test_update_overwrites_existing(self, update_home_info_use_case, temp_dir):
        """Test that update overwrites existing content."""
        # Arrange
        initial_content = "# Casa Vieja\n\nContenido inicial."
        new_content = "# Casa Nueva\n\nContenido actualizado."
        file_path = os.path.join(temp_dir, 'home_info.md')
        
        with patch.object(update_home_info_use_case, '_home_info_file', file_path):
            # Act 1: Initial update
            await update_home_info_use_case.update_home_info(initial_content)
            
            # Act 2: Update with new content
            result = await update_home_info_use_case.update_home_info(new_content)
            
            # Assert
            assert result is True
            
            # Verify content was overwritten
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert content == new_content
            assert initial_content not in content
    
    @pytest.mark.asyncio
    async def test_markdown_content_handling(self, update_home_info_use_case, temp_dir):
        """Test handling of markdown content with special characters."""
        # Arrange
        markdown_content = """# Mi Casa

## Habitaciones

- **Sala de estar**: Espacio principal con TV
- **Cocina**: Con electrodomésticos modernos
- **Dormitorio**: Cama king size

### Dispositivos

| Dispositivo | Estado | Ubicación |
|-------------|--------|-----------|
| TV | Encendida | Sala |
| Luces | Apagadas | Cocina |

> **Nota**: La casa tiene sistema de domótica.
"""
        file_path = os.path.join(temp_dir, 'home_info.md')
        
        with patch.object(update_home_info_use_case, '_home_info_file', file_path):
            # Act
            result = await update_home_info_use_case.update_home_info(markdown_content)
            
            # Assert
            assert result is True
            
            # Verify content was saved correctly
            retrieved_content = await update_home_info_use_case.get_home_info()
            assert retrieved_content == markdown_content.strip()  # Should match stripped version
            assert "**Sala de estar**" in retrieved_content
            assert "| Dispositivo |" in retrieved_content
            assert "> **Nota**" in retrieved_content
