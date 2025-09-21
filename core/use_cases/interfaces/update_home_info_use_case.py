"""
Interface for updating home information use case.
"""

from abc import ABC, abstractmethod
from typing import Optional


class UpdateHomeInfoUseCase(ABC):
    """
    Interface for updating home information.
    """
    
    @abstractmethod
    async def update_home_info(self, home_info: str) -> bool:
        """
        Update home information.
        
        Args:
            home_info: Markdown content with home information
            
        Returns:
            True if updated successfully
            
        Raises:
            ValueError: If home_info is empty or invalid
            OSError: If there's an error saving the information
        """
        pass
    
    @abstractmethod
    async def get_home_info(self) -> Optional[str]:
        """
        Get current home information.
        
        Returns:
            Home information as markdown string, or None if not available
            
        Raises:
            OSError: If there's an error reading the information
        """
        pass
    
    @abstractmethod
    async def clear_home_info(self) -> bool:
        """
        Clear home information.
        
        Returns:
            True if cleared successfully
            
        Raises:
            OSError: If there's an error clearing the information
        """
        pass
