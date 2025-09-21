"""Home Assistant authentication client."""

import asyncio
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

import aiohttp


_LOGGER = logging.getLogger(__name__)


class HAAuthClient:
    """Home Assistant authentication client."""

    def __init__(self, ha_url: str = "http://homeassistant.local:8123") -> None:
        """Initialize the Home Assistant authentication client."""
        self._ha_url = ha_url.rstrip('/')
        self._session: Optional[aiohttp.ClientSession] = None
        self._token: Optional[str] = None
        self._user_info: Optional[Dict] = None
        self._token_expires: Optional[datetime] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self) -> None:
        """Connect to Home Assistant."""
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()
            _LOGGER.info("Connected to Home Assistant authentication service")
        except Exception as e:
            _LOGGER.error("Failed to connect to Home Assistant: %s", e)
            raise Exception(f"Failed to connect to Home Assistant: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from Home Assistant."""
        if self._session:
            await self._session.close()
            self._session = None
        _LOGGER.info("Disconnected from Home Assistant authentication service")

    async def login(self, token: str) -> Tuple[bool, str]:
        """Login to Home Assistant using a long-lived access token."""
        if not self._session:
            raise Exception("Client not connected")

        try:
            _LOGGER.info("Attempting login to Home Assistant with token")
            
            # Home Assistant uses Bearer token authentication
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            # Test connection with Bearer token
            async with self._session.get(
                f"{self._ha_url}/api/",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    # Connection successful, store token
                    self._token = token
                    self._user_info = {
                        "authenticated": True,
                        "token_used": True
                    }
                    
                    # Set token expiration (typically 10 years for long-lived tokens)
                    self._token_expires = datetime.now() + timedelta(days=3650)
                    
                    _LOGGER.info("Successfully authenticated with Home Assistant using token")
                    return True, "Authentication successful"
                else:
                    error_text = await response.text()
                    _LOGGER.error("Authentication failed with status %s: %s", response.status, error_text)
                    return False, f"Authentication failed: {response.status}"

        except asyncio.TimeoutError:
            error_msg = "Authentication timeout"
            _LOGGER.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Authentication error: {e}"
            _LOGGER.error(error_msg)
            return False, error_msg

    async def validate_token(self, token: str = None) -> bool:
        """Validate the current token or a provided token."""
        # Use provided token or current token
        token_to_validate = token or self._token
        if not token_to_validate or not self._session:
            return False

        try:
            # Check if token is expired (only for current token)
            if not token and self._token_expires and datetime.now() > self._token_expires:
                _LOGGER.warning("Token has expired")
                return False

            # Validate token with Home Assistant (using Bearer token)
            headers = {
                "Authorization": f"Bearer {token_to_validate}",
                "Content-Type": "application/json"
            }

            async with self._session.get(
                f"{self._ha_url}/api/",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                
                if response.status == 200:
                    _LOGGER.info("Authentication is valid")
                    return True
                else:
                    _LOGGER.warning("Authentication validation failed with status %s", response.status)
                    return False

        except Exception as e:
            _LOGGER.error("Authentication validation error: %s", e)
            return False

    async def get_user_info(self) -> Optional[Dict]:
        """Get current user information."""
        if not self._token or not self._session:
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json"
            }

            # Get user info from the config API endpoint
            async with self._session.get(
                f"{self._ha_url}/api/config",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("Successfully retrieved user info")
                    return data
                else:
                    _LOGGER.warning("Failed to get user info with status %s", response.status)
                    return None

        except Exception as e:
            _LOGGER.error("Error getting user info: %s", e)
            return None

    def get_token(self) -> Optional[str]:
        """Get the current token."""
        return self._token

    def get_user_info_cached(self) -> Optional[Dict]:
        """Get cached user information."""
        return self._user_info

    def is_logged_in(self) -> bool:
        """Check if currently logged in."""
        return self._token is not None

    def logout(self) -> None:
        """Logout and clear credentials."""
        self._token = None
        self._user_info = None
        self._token_expires = None
        _LOGGER.info("Logged out from Home Assistant")
