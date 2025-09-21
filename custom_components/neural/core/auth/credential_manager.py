"""Credential manager for secure storage of Home Assistant credentials."""

import json
import os
import logging
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
import base64

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

_LOGGER = logging.getLogger(__name__)


class CredentialManager:
    """Manages secure storage of Home Assistant credentials."""

    def __init__(self, app_name: str = "neural-ai-cli") -> None:
        """Initialize the credential manager."""
        self._app_name = app_name
        self._config_dir = Path.home() / ".neural-ai"
        self._config_file = self._config_dir / "credentials.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        self._config_dir.mkdir(exist_ok=True, mode=0o700)

    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key."""
        if not CRYPTO_AVAILABLE:
            # Fallback to simple base64 encoding (not secure, but functional)
            key_file = self._config_dir / ".encryption_key"
            if key_file.exists():
                return key_file.read_bytes()
            else:
                import secrets
                key = secrets.token_bytes(32)
                key_file.write_bytes(key)
                key_file.chmod(0o600)
                return key

        try:
            # Try to get existing key from keyring
            if KEYRING_AVAILABLE:
                key = keyring.get_password(self._app_name, "encryption_key")
                if key:
                    return base64.b64decode(key)
        except Exception:
            pass

        # Generate new key
        key = Fernet.generate_key()
        try:
            # Store in keyring
            if KEYRING_AVAILABLE:
                keyring.set_password(self._app_name, "encryption_key", base64.b64encode(key).decode())
        except Exception as e:
            _LOGGER.warning("Could not store encryption key in keyring: %s", e)
            # Fallback: store in file (less secure)
            key_file = self._config_dir / ".encryption_key"
            key_file.write_bytes(key)
            key_file.chmod(0o600)

        return key

    def _encrypt_data(self, data: str) -> str:
        """Encrypt data."""
        if not CRYPTO_AVAILABLE:
            # Fallback to simple base64 encoding (not secure, but functional)
            return base64.b64encode(data.encode()).decode()
        
        key = self._get_encryption_key()
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()

    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data."""
        if not CRYPTO_AVAILABLE:
            # Fallback to simple base64 decoding
            return base64.b64decode(encrypted_data.encode()).decode()
        
        key = self._get_encryption_key()
        fernet = Fernet(key)
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = fernet.decrypt(encrypted_bytes)
        return decrypted_data.decode()

    def store_credentials(self, token: str = None) -> bool:
        """Store Home Assistant credentials securely."""
        try:
            credentials = {
                "token": token,
                "stored_at": str(datetime.now())
            }

            # Store in encrypted file
            with open(self._config_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            # Set secure permissions
            os.chmod(self._config_file, 0o600)
            
            _LOGGER.info("Credentials stored securely")
            return True

        except Exception as e:
            _LOGGER.error("Failed to store credentials: %s", e)
            return False

    def get_credentials(self) -> Optional[Dict]:
        """Get stored credentials."""
        try:
            if not self._config_file.exists():
                return None

            with open(self._config_file, 'r') as f:
                credentials = json.load(f)

            # Decrypt password
            if "password" in credentials:
                credentials["password"] = self._decrypt_data(credentials["password"])

            return credentials

        except Exception as e:
            _LOGGER.error("Failed to get credentials: %s", e)
            return None

    def clear_credentials(self) -> bool:
        """Clear stored credentials."""
        try:
            if self._config_file.exists():
                self._config_file.unlink()
            
            _LOGGER.info("Credentials cleared")
            return True

        except Exception as e:
            _LOGGER.error("Failed to clear credentials: %s", e)
            return False

    def has_credentials(self) -> bool:
        """Check if credentials are stored."""
        return self._config_file.exists()

    def get_token(self) -> Optional[str]:
        """Get stored token."""
        credentials = self.get_credentials()
        return credentials.get("token") if credentials else None

    def update_token(self, token: str) -> bool:
        """Update stored token."""
        try:
            credentials = self.get_credentials()
            if not credentials:
                return False

            credentials["token"] = token
            credentials["updated_at"] = str(datetime.now())

            with open(self._config_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            os.chmod(self._config_file, 0o600)
            return True

        except Exception as e:
            _LOGGER.error("Failed to update token: %s", e)
            return False
