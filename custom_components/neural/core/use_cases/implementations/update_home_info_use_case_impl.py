"""
Implementation of update home information use case.
"""

import logging
import os
from typing import Optional

from core.use_cases.interfaces.update_home_info_use_case import UpdateHomeInfoUseCase

_LOGGER = logging.getLogger(__name__)


class UpdateHomeInfoUseCaseImpl(UpdateHomeInfoUseCase):
    """
    Implementation of update home information use case.
    """
    
    def __init__(self):
        """Initialize the use case."""
        self._home_info_file = "home_info.md"
    
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
        try:
            _LOGGER.debug("Updating home information")
            
            # Validate input
            if not home_info or not home_info.strip():
                raise ValueError("Home information cannot be empty")
            
            # Ensure content is not too short (at least 10 characters)
            if len(home_info.strip()) < 10:
                raise ValueError("Home information must be at least 10 characters long")
            
            # Save to file
            with open(self._home_info_file, 'w', encoding='utf-8') as f:
                f.write(home_info.strip())
            
            _LOGGER.info("Home information updated successfully")
            return True
            
        except Exception as e:
            _LOGGER.error("Error updating home information: %s", e)
            raise OSError(f"Error updating home information: {e}")
    
    async def get_home_info(self) -> Optional[str]:
        """
        Get current home information.
        
        Returns:
            Home information as markdown string, or None if not available
            
        Raises:
            OSError: If there's an error reading the information
        """
        try:
            _LOGGER.debug("Getting home information")
            
            if not os.path.exists(self._home_info_file):
                _LOGGER.info("Home information file not found")
                return None
            
            with open(self._home_info_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                _LOGGER.info("Home information file is empty")
                return None
            
            _LOGGER.info("Home information retrieved successfully")
            return content.strip()
            
        except Exception as e:
            _LOGGER.error("Error getting home information: %s", e)
            raise OSError(f"Error getting home information: {e}")
    
    async def clear_home_info(self) -> bool:
        """
        Clear home information.
        
        Returns:
            True if cleared successfully
            
        Raises:
            OSError: If there's an error clearing the information
        """
        try:
            _LOGGER.debug("Clearing home information")
            
            if os.path.exists(self._home_info_file):
                os.remove(self._home_info_file)
                _LOGGER.info("Home information cleared successfully")
            else:
                _LOGGER.info("Home information file does not exist")
            
            return True
            
        except Exception as e:
            _LOGGER.error("Error clearing home information: %s", e)
            raise OSError(f"Error clearing home information: {e}")
