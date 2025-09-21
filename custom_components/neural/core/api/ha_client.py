"""Home Assistant client for retrieving sensor and entity information."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp

from .base_client import BaseClient
from .exceptions import (
    MyVerisureConnectionError,
    MyVerisureError,
)

_LOGGER = logging.getLogger(__name__)


class HAClient(BaseClient):
    """Home Assistant client for retrieving sensor and entity information."""

    def __init__(self, ha_url: str = "http://homeassistant.local:8123", ha_token: str = None) -> None:
        """Initialize the Home Assistant client."""
        super().__init__()
        self._ha_url = ha_url.rstrip('/')
        
        # If no token provided, try to get it from credential manager
        if ha_token is None:
            try:
                from ..auth.credential_manager import CredentialManager
                credential_manager = CredentialManager()
                if credential_manager.has_credentials():
                    stored_token = credential_manager.get_token()
                    if stored_token:
                        ha_token = stored_token
                        _LOGGER.info("Using stored token from credential manager")
            except Exception as e:
                _LOGGER.debug("Could not load stored token: %s", e)
        
        self._ha_token = ha_token
        self._headers = {
            "Authorization": f"Bearer {ha_token}" if ha_token else None,
            "Content-Type": "application/json",
        }

    async def connect(self) -> None:
        """Connect to the Home Assistant service."""
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            # Test connection to Home Assistant
            is_connected = await self._test_connection()
            if is_connected:
                _LOGGER.info("Connected to Home Assistant at %s", self._ha_url)
            else:
                _LOGGER.warning("Could not connect to Home Assistant at %s", self._ha_url)
            
        except Exception as e:
            _LOGGER.error("Failed to connect to Home Assistant: %s", e)
            # Don't raise exception, just log the error

    async def _test_connection(self) -> bool:
        """Test connection to Home Assistant."""
        try:
            # Try the main API endpoint first
            async with self._session.get(
                f"{self._ha_url}/api/",
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    _LOGGER.info("Home Assistant API is accessible")
                    return True
                else:
                    _LOGGER.error("Home Assistant returned status %s", response.status)
                    return False
        except asyncio.TimeoutError:
            _LOGGER.error("Home Assistant connection timeout")
            return False
        except Exception as e:
            _LOGGER.error("Failed to test Home Assistant connection: %s", e)
            return False

    async def test_connection(self) -> bool:
        """Public method to test connection to Home Assistant."""
        try:
            # Ensure session exists
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            return await self._test_connection()
        except Exception as e:
            _LOGGER.error("Failed to test Home Assistant connection: %s", e)
            return False

    async def get_states(self) -> List[Dict[str, Any]]:
        """Get all states from Home Assistant."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

        try:
            async with self._session.get(
                f"{self._ha_url}/api/states",
                headers=self._headers
            ) as response:
                if response.status == 200:
                    states = await response.json()
                    _LOGGER.info("Retrieved %d states from Home Assistant", len(states))
                    return states
                else:
                    error_text = await response.text()
                    _LOGGER.error("Home Assistant error: %s", error_text)
                    raise MyVerisureError(f"Home Assistant error: {response.status}")
                    
        except Exception as e:
            _LOGGER.error("Failed to get states from Home Assistant: %s", e)
            raise MyVerisureError(f"Failed to get states from Home Assistant: {e}") from e

    async def get_entities_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get entities filtered by domain."""
        try:
            all_states = await self.get_states()
            filtered_states = [
                state for state in all_states 
                if state.get("entity_id", "").startswith(f"{domain}.")
            ]
            _LOGGER.info("Found %d entities for domain %s", len(filtered_states), domain)
            return filtered_states
        except Exception as e:
            _LOGGER.error("Failed to get entities by domain %s: %s", domain, e)
            raise

    async def get_sensors(self) -> List[Dict[str, Any]]:
        """Get all sensor entities."""
        return await self.get_entities_by_domain("sensor")

    async def get_binary_sensors(self) -> List[Dict[str, Any]]:
        """Get all binary sensor entities."""
        return await self.get_entities_by_domain("binary_sensor")

    async def get_switches(self) -> List[Dict[str, Any]]:
        """Get all switch entities."""
        return await self.get_entities_by_domain("switch")

    async def get_lights(self) -> List[Dict[str, Any]]:
        """Get all light entities."""
        return await self.get_entities_by_domain("light")

    async def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get state of a specific entity."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

        try:
            async with self._session.get(
                f"{self._ha_url}/api/states/{entity_id}",
                headers=self._headers
            ) as response:
                if response.status == 200:
                    state = await response.json()
                    return state
                elif response.status == 404:
                    _LOGGER.warning("Entity %s not found", entity_id)
                    return None
                else:
                    error_text = await response.text()
                    _LOGGER.error("Home Assistant error: %s", error_text)
                    raise MyVerisureError(f"Home Assistant error: {response.status}")
                    
        except Exception as e:
            _LOGGER.error("Failed to get entity state for %s: %s", entity_id, e)
            raise MyVerisureError(f"Failed to get entity state for {entity_id}: {e}") from e

    async def get_entity_history(self, entity_id: str, start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
        """Get history for a specific entity."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

        try:
            params = {}
            if start_time:
                params["start_time"] = start_time
            if end_time:
                params["end_time"] = end_time

            async with self._session.get(
                f"{self._ha_url}/api/history/period",
                headers=self._headers,
                params={**params, "filter_entity_id": entity_id}
            ) as response:
                if response.status == 200:
                    history = await response.json()
                    return history
                else:
                    error_text = await response.text()
                    _LOGGER.error("Home Assistant error: %s", error_text)
                    raise MyVerisureError(f"Home Assistant error: {response.status}")
                    
        except Exception as e:
            _LOGGER.error("Failed to get entity history for %s: %s", entity_id, e)
            raise MyVerisureError(f"Failed to get entity history for {entity_id}: {e}") from e

    async def get_services(self) -> Dict[str, Any]:
        """Get available services from Home Assistant."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

        try:
            async with self._session.get(
                f"{self._ha_url}/api/services",
                headers=self._headers
            ) as response:
                if response.status == 200:
                    services = await response.json()
                    return services
                else:
                    error_text = await response.text()
                    _LOGGER.error("Home Assistant error: %s", error_text)
                    raise MyVerisureError(f"Home Assistant error: {response.status}")
                    
        except Exception as e:
            _LOGGER.error("Failed to get services from Home Assistant: %s", e)
            raise MyVerisureError(f"Failed to get services from Home Assistant: {e}") from e

    async def get_config(self) -> Dict[str, Any]:
        """Get Home Assistant configuration."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

        try:
            async with self._session.get(
                f"{self._ha_url}/api/config",
                headers=self._headers
            ) as response:
                if response.status == 200:
                    config = await response.json()
                    return config
                else:
                    error_text = await response.text()
                    _LOGGER.error("Home Assistant error: %s", error_text)
                    raise MyVerisureError(f"Home Assistant error: {response.status}")
                    
        except Exception as e:
            _LOGGER.error("Failed to get config from Home Assistant: %s", e)
            raise MyVerisureError(f"Failed to get config from Home Assistant: {e}") from e

    async def call_service(self, domain: str, service: str, entity_id: str = None, service_data: dict = None) -> dict:
        """Call a service on Home Assistant."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

        try:
            # Prepare the service call data
            call_data = {}
            if entity_id:
                call_data["entity_id"] = entity_id
            if service_data:
                call_data.update(service_data)
            
            _LOGGER.debug("Calling service %s.%s with data: %s", domain, service, call_data)
            
            async with self._session.post(
                f"{self._ha_url}/api/services/{domain}/{service}",
                headers=self._headers,
                json=call_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    _LOGGER.info("Service call successful: %s.%s", domain, service)
                    return result
                else:
                    error_text = await response.text()
                    _LOGGER.error("Service call failed: %s.%s - Status: %d, Error: %s", 
                                 domain, service, response.status, error_text)
                    raise MyVerisureError(f"Service call failed: {response.status} - {error_text}")
                    
        except Exception as e:
            _LOGGER.error("Failed to call service %s.%s: %s", domain, service, e)
            raise MyVerisureError(f"Failed to call service {domain}.{service}: {e}") from e

    def update_ha_config(self, ha_url: str = None, ha_token: str = None) -> None:
        """Update Home Assistant configuration."""
        if ha_url:
            self._ha_url = ha_url.rstrip('/')
        if ha_token:
            self._ha_token = ha_token
            self._headers["Authorization"] = f"Bearer {ha_token}"
        elif ha_token is None and not self._ha_token:
            # If no token provided and we don't have one, try to get it from credential manager
            try:
                from ..auth.credential_manager import CredentialManager
                credential_manager = CredentialManager()
                if credential_manager.has_credentials():
                    stored_token = credential_manager.get_token()
                    if stored_token:
                        self._ha_token = stored_token
                        self._headers["Authorization"] = f"Bearer {stored_token}"
                        _LOGGER.info("Updated configuration with stored token from credential manager")
            except Exception as e:
                _LOGGER.debug("Could not load stored token for config update: %s", e)
        _LOGGER.debug("Home Assistant client configuration updated")

    async def get_complete_info(self) -> Dict[str, Any]:
        """Get complete information from Home Assistant."""
        if not self._session:
            raise MyVerisureConnectionError("Client not connected")

        try:
            _LOGGER.info("Getting complete information from Home Assistant")
            
            # Get all information in parallel for better performance
            import asyncio
            
            # Create tasks for all API calls
            tasks = {
                'config': self.get_config(),
                'states': self.get_states(),
                'services': self.get_services(),
            }
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            
            # Process results
            complete_info = {}
            for i, (key, task) in enumerate(tasks.items()):
                result = results[i]
                if isinstance(result, Exception):
                    _LOGGER.warning("Failed to get %s: %s", key, result)
                    complete_info[key] = None
                else:
                    complete_info[key] = result
            
            _LOGGER.info("Retrieved complete information from Home Assistant")
            return complete_info
            
        except Exception as e:
            _LOGGER.error("Failed to get complete information from Home Assistant: %s", e)
            raise MyVerisureError(f"Failed to get complete information from Home Assistant: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from the Home Assistant service."""
        if self._session:
            await self._session.close()
            self._session = None
        _LOGGER.info("Disconnected from Home Assistant")
