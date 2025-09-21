"""Authentication command for the CLI."""

import logging
import getpass
import sys
import os

from .base import BaseCommand
from ..utils.display import (
    print_command_header,
    print_success,
    print_error,
    print_info,
    print_header,
)

# Add core to path for imports

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "custom_components", "neural"))

from core.api.ha_auth_client import HAAuthClient
from core.auth.credential_manager import CredentialManager

logger = logging.getLogger(__name__)


class AuthCommand(BaseCommand):
    """Authentication command for Home Assistant."""

    def __init__(self):
        super().__init__()
        self._credential_manager = CredentialManager()

    async def execute(self, action: str, **kwargs) -> bool:
        """Execute authentication command."""
        print_command_header("AUTH", "Home Assistant Authentication")

        if action == "status":
            return await self._show_status(**kwargs)
        elif action == "login":
            return await self._login(**kwargs)
        elif action == "logout":
            return await self._logout(**kwargs)
        else:
            print_error(f"Acción de autenticación desconocida: {action}")
            return False

    async def _show_status(self, interactive: bool = True) -> bool:
        """Show authentication status."""
        print_header("ESTADO DE AUTENTICACIÓN")

        try:
            # Check if credentials are stored
            if not self._credential_manager.has_credentials():
                print_info("No hay credenciales almacenadas")
                print_info("Usa 'neural auth login' para iniciar sesión")
                return True

            # Get stored credentials
            credentials = self._credential_manager.get_credentials()
            if not credentials:
                print_error("Error al obtener credenciales almacenadas")
                return False

            print_info(f"URL de Home Assistant: homeassistant.local:8123")
            print_info(f"Tipo de autenticación: Token de acceso de larga duración")
            print_info(f"Token: {'Configurado' if credentials.get('token') else 'No configurado'}")
            print_info(f"Almacenado en: {credentials.get('stored_at', 'Desconocido')}")

            # Use fixed URL for Home Assistant
            ha_url = "http://homeassistant.local:8123"

            print_info("\nProbando conexión con token almacenado...")
            
            async with HAAuthClient(ha_url) as auth_client:
                # Try to validate existing token first
                if credentials.get('token'):
                    print_info("Validando token existente...")
                    stored_token = credentials.get('token')
                    if await auth_client.validate_token(stored_token):
                        print_success("✓ Token válido - Sesión activa")
                        
                        # Set the token in the client for get_user_info
                        auth_client._token = stored_token
                        
                        # Get user information
                        print_info("\n👤 Información del perfil:")
                        user_info = await auth_client.get_user_info()
                        if user_info:
                            # Extract relevant information from Home Assistant API response
                            if 'version' in user_info:
                                print_info(f"  🏠 Versión de Home Assistant: {user_info['version']}")
                            if 'location_name' in user_info:
                                print_info(f"  📍 Ubicación: {user_info['location_name']}")
                            if 'time_zone' in user_info:
                                print_info(f"  🕐 Zona horaria: {user_info['time_zone']}")
                            if 'unit_system' in user_info and isinstance(user_info['unit_system'], dict):
                                unit_system = user_info['unit_system']
                                temp_unit = unit_system.get('temperature', '°C')
                                length_unit = unit_system.get('length', 'km')
                                print_info(f"  📏 Sistema de unidades: {temp_unit}, {length_unit}")
                            if 'country' in user_info:
                                print_info(f"  🌍 País: {user_info['country']}")
                            if 'language' in user_info:
                                print_info(f"  🗣️  Idioma: {user_info['language']}")
                        else:
                            print_info("  No se pudo obtener información del perfil")
                        
                        return True
                    else:
                        print_info("Token expirado o inválido")
                        print_error("✗ Token no válido - Necesitas crear un nuevo token")
                        print_info("Usa 'neural auth login' para configurar un nuevo token")
                        return False
                else:
                    print_error("✗ No hay token configurado")
                    print_info("Usa 'neural auth login' para configurar un token")
                    return False

        except Exception as e:
            print_error(f"Error verificando estado de autenticación: {e}")
            return False

    async def _login(self, interactive: bool = True, token: str = None) -> bool:
        """Login to Home Assistant using a long-lived access token."""
        print_header("INICIO DE SESIÓN EN HOME ASSISTANT")

        try:
            # Use fixed URL for Home Assistant
            ha_url = "http://homeassistant.local:8123"

            # Get token
            if not token:
                if interactive:
                    print_info("Para obtener un token de acceso de larga duración:")
                    print_info("1. Ve a Home Assistant > Perfil > Tokens de acceso")
                    print_info("2. Crea un nuevo token de larga duración")
                    print_info("3. Copia el token generado")
                    print()
                    token = getpass.getpass("Token de acceso: ").strip()
                    if not token:
                        print_error("Token de acceso requerido")
                        return False
                else:
                    print_error("Token de acceso requerido para login")
                    return False

            print_info(f"Conectando a: {ha_url}")
            print_info("Usando token de acceso de larga duración")

            # Attempt login
            async with HAAuthClient(ha_url) as auth_client:
                success, message = await auth_client.login(token)
                
                if success:
                    print_success("✓ Login exitoso")
                    
                    # Store credentials (using token as both username and password for compatibility)
                    if self._credential_manager.store_credentials(ha_url, "token_user", token, token):
                        print_success("✓ Token almacenado de forma segura")
                        print_info("El token se usará automáticamente en el futuro")
                    else:
                        print_error("✗ Error almacenando token")
                    
                    return True
                else:
                    print_error(f"✗ Login falló: {message}")
                    return False

        except Exception as e:
            print_error(f"Error durante login: {e}")
            return False

    async def _logout(self, interactive: bool = True) -> bool:
        """Logout from Home Assistant."""
        print_header("CERRAR SESIÓN")

        try:
            # Clear stored credentials
            if self._credential_manager.clear_credentials():
                print_success("✓ Sesión cerrada y credenciales eliminadas")
                print_info("Las credenciales han sido eliminadas de forma segura")
                return True
            else:
                print_error("✗ Error eliminando credenciales")
                return False

        except Exception as e:
            print_error(f"Error durante logout: {e}")
            return False

    def get_credentials(self):
        """Get stored credentials."""
        return self._credential_manager.get_credentials()

    def get_ha_url(self):
        """Get stored HA URL."""
        return self._credential_manager.get_ha_url()

    def get_token(self):
        """Get stored token."""
        return self._credential_manager.get_token()
