"""Data coordinator for Neural AI integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .core.dependency_injection.providers import setup_dependencies, clear_dependencies
from .core.dependency_injection.injector_container import get_decision_use_case, get_do_actions_use_case, get_ha_use_case
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class NeuralDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage Neural AI integration using core use cases."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.hass = hass
        
        # State
        self.last_response = None
        self.last_command = None
        self.status = "idle"
        self.is_processing = False
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            # Update status
            status_data = {
                "status": self.status,
                "is_processing": self.is_processing,
                "last_response": self.last_response,
                "last_command": self.last_command,
                "ai_model": self.entry.data.get("ai_model"),
                "personality": self.entry.data.get("personality"),
                "work_mode": self.entry.data.get("work_mode"),
                "last_update": datetime.now().isoformat(),
            }
            
            return status_data
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Neural AI: {err}")

    async def process_command(self, command: str) -> str:
        """Process a command using the core use cases."""
        try:
            self.status = "processing"
            self.is_processing = True
            await self.async_request_refresh()
            
            # Setup dependencies with configuration
            await setup_dependencies(
                ai_url="https://openrouter.ai/api/v1",
                ai_model=self.entry.data.get("ai_model", "openai/gpt-4o-mini"),
                ai_api_key=self.entry.data.get("openrouter_token"),
                ha_url="http://supervisor/core",
                ha_token=self.entry.data.get("ha_token")
            )
            
            # Get use cases
            decision_use_case = get_decision_use_case()
            do_actions_use_case = get_do_actions_use_case()
            
            # Make decision
            decision_response = await decision_use_case.make_decision(
                command, 
                mode=self.entry.data.get("work_mode", "assistant")
            )
            
            # Execute actions if any
            if decision_response.actions:
                actions_response = await do_actions_use_case.execute_actions(decision_response.actions)
                _LOGGER.info("Executed %d actions, %d successful", 
                           actions_response.total_actions, 
                           actions_response.successful_actions)
            
            self.last_command = command
            self.last_response = decision_response.message
            self.status = "idle"
            self.is_processing = False
            
            await self.async_request_refresh()
            _LOGGER.info("AI response: %s", decision_response.message)
            return decision_response.message
            
        except Exception as e:
            _LOGGER.error("Error processing command: %s", e)
            self.status = "error"
            self.is_processing = False
            await self.async_request_refresh()
            raise
        finally:
            # Clean up dependencies
            clear_dependencies()

    async def get_status(self) -> dict[str, Any]:
        """Get current status."""
        return {
            "status": self.status,
            "is_processing": self.is_processing,
            "last_response": self.last_response,
            "last_command": self.last_command,
            "ai_model": self.entry.data.get("ai_model"),
            "personality": self.entry.data.get("personality"),
            "work_mode": self.entry.data.get("work_mode"),
        }
