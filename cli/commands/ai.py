"""AI interaction command for the CLI."""

import logging
from typing import Optional

from .base import BaseCommand
from ..utils.display import (
    print_command_header,
    print_success,
    print_error,
    print_info,
    print_header,
)

logger = logging.getLogger(__name__)


class AICommand(BaseCommand):
    """AI interaction command."""

    async def execute(self, action: str, **kwargs) -> bool:
        """Execute AI command."""
        print_command_header("AI", "AI Interaction")

        if action == "chat":
            return await self._chat(**kwargs)
        elif action == "status":
            return await self._show_status(**kwargs)
        elif action == "models":
            return await self._list_models(**kwargs)
        else:
            print_error(f"Acción de AI desconocida: {action}")
            return False

    async def _chat(
        self, message: str, model: Optional[str] = None, interactive: bool = True
    ) -> bool:
        """Chat with AI."""
        print_header("CHAT CON AI")

        try:
            if not await self.setup():
                return False

            print_info(f"Enviando mensaje: {message}")
            if model:
                print_info(f"Usando modelo: {model}")

            # Get AI use case
            ai_use_case = self.get_ai_use_case()
            
            # Send message to AI
            response = await ai_use_case.send_message(message, model=model)
            
            if response:
                print_success("Respuesta de AI:")
                print_info(f"  {response}")
                return True
            else:
                print_error("No se recibió respuesta de AI")
                return False

        except Exception as e:
            print_error(f"Error enviando mensaje a AI: {e}")
            return False

    async def _show_status(self, interactive: bool = True) -> bool:
        """Show AI status."""
        print_header("ESTADO DE AI")

        try:
            if not await self.setup():
                return False

            print_info("Obteniendo estado de AI...")

            # Get AI use case
            ai_use_case = self.get_ai_use_case()
            
            # Get AI status
            status = await ai_use_case.get_status()
            
            if status:
                print_success("Estado de AI:")
                print_info(f"  Modelo: {status.get('model', 'Unknown')}")
                print_info(f"  Estado: {status.get('status', 'Unknown')}")
                print_info(f"  URL: {status.get('url', 'Unknown')}")
                return True
            else:
                print_error("No se pudo obtener el estado de AI")
                return False

        except Exception as e:
            print_error(f"Error obteniendo estado de AI: {e}")
            return False

    async def _list_models(self, interactive: bool = True) -> bool:
        """List available AI models."""
        print_header("MODELOS DE AI DISPONIBLES")

        try:
            if not await self.setup():
                return False

            print_info("Obteniendo modelos disponibles...")

            # Get AI use case
            ai_use_case = self.get_ai_use_case()
            
            # Get available models
            models = await ai_use_case.list_models()
            
            if models:
                print_success("Modelos disponibles:")
                for model in models:
                    print_info(f"  - {model}")
                return True
            else:
                print_error("No se pudieron obtener los modelos")
                return False

        except Exception as e:
            print_error(f"Error obteniendo modelos: {e}")
            return False
