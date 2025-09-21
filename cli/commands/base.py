"""Base command class for the CLI."""

import sys
import os
import logging
from abc import ABC, abstractmethod
from typing import Optional

# Add custom_components/neural to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "custom_components", "neural"))

from core.dependency_injection.providers import (
    get_ai_use_case,
    get_ha_use_case,
    setup_dependencies,
)

from ..utils.display import print_error

logger = logging.getLogger(__name__)


class BaseCommand(ABC):
    """Base class for all CLI commands."""

    def __init__(self):
        self.ai_use_case = None
        self.ha_use_case = None

    async def setup(self, interactive: bool = True, ha_ip: str = None, ha_token: str = None) -> bool:
        """Setup the command by getting use cases."""
        try:            
            # Use fixed URL for Home Assistant
            ha_url = "http://homeassistant.local:8123"
            
            # Configure with dynamic values (will load from config file)
            await setup_dependencies(
                ai_url=None,  # Will load from config file
                ai_model=None,  # Will load from config file
                ha_url=ha_url,
                ha_token=ha_token
            )
            
            # Get use cases
            self.ai_use_case = get_ai_use_case()
            self.ha_use_case = get_ha_use_case()

            return True

        except Exception as e:
            print_error(f"Error setting up command: {e}")
            return False

    @abstractmethod
    async def execute(self, *args, **kwargs):
        """Execute the command. Must be implemented by subclasses."""
        pass

    async def cleanup(self):
        """Clean up resources."""
        try:
            # Clean up HTTP sessions if they exist
            if hasattr(self, 'ai_use_case') and self.ai_use_case:
                # Get the repository and close its client session
                if hasattr(self.ai_use_case, '_ai_repository'):
                    ai_repo = self.ai_use_case._ai_repository
                    if hasattr(ai_repo, '_ai_client') and ai_repo._ai_client:
                        await ai_repo._ai_client.disconnect()
            
            if hasattr(self, 'ha_use_case') and self.ha_use_case:
                # Get the repository and close its client session
                if hasattr(self.ha_use_case, '_ha_repository'):
                    ha_repo = self.ha_use_case._ha_repository
                    if hasattr(ha_repo, '_ha_client') and ha_repo._ha_client:
                        await ha_repo._ha_client.disconnect()
        except Exception as e:
            # Don't fail cleanup if there are issues
            pass

    def get_installation_id(
        self, installation_id: Optional[str] = None
    ) -> Optional[str]:
        """Get installation ID - not applicable for Neural AI."""
        # Neural AI doesn't use installations
        return None

    async def select_installation_if_needed(
        self, installation_id: Optional[str] = None
    ) -> Optional[str]:
        """Select installation - not applicable for Neural AI."""
        # Neural AI doesn't use installations
        return None

    def get_ai_use_case(self):
        """Get the AI use case."""
        return self.ai_use_case

    def get_ha_use_case(self):
        """Get the Home Assistant use case."""
        return self.ha_use_case
