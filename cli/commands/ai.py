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

        if action == "message":
            return await self._message(**kwargs)
        elif action == "status":
            return await self._show_status(**kwargs)
        elif action == "models":
            return await self._list_models(**kwargs)
        elif action == "config":
            return await self._config(**kwargs)
        else:
            print_error(f"Acción de AI desconocida: {action}")
            return False

    async def _message(
        self, message: str, model: Optional[str] = None, interactive: bool = True
    ) -> bool:
        """Send a message to AI and get response - direct API test."""
        print_header("ENVIAR MENSAJE A AI")

        try:
            if not await self.setup():
                return False

            print_info(f"Probando API AI con mensaje: {message}")
            if model:
                print_info(f"Usando modelo: {model}")

            # Get AI use case (this consumes the repository and use case)
            ai_use_case = self.get_ai_use_case()
            
            # Check if model is ready first
            print_info("Verificando si el modelo está listo...")
            is_ready = await ai_use_case.is_model_ready()
            
            if not is_ready:
                print_error("El modelo AI no está listo. Verifica que el servicio esté ejecutándose.")
                return False
            
            print_success("✓ Modelo AI está listo")
            
            # Send message to AI using the repository/use case pattern
            print_info("Enviando mensaje a la API AI...")
            response = await ai_use_case.send_message(message, model=model)
            
            if response:
                print_success("✓ Respuesta recibida de la API AI:")
                print_info(f"  {response}")
                return True
            else:
                print_error("✗ No se recibió respuesta de la API AI")
                return False

        except Exception as e:
            print_error(f"✗ Error probando la API AI: {e}")
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
                print_info(f"  Modelo: {status.model}")
                print_info(f"  Estado: {status.status}")
                print_info(f"  URL: {status.url}")
                if status.available_models:
                    print_info(f"  Modelos disponibles: {', '.join(status.available_models)}")
                if status.error:
                    print_info(f"  Error: {status.error}")
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

    async def _config(self, **kwargs) -> bool:
        """Manage AI configuration."""
        print_header("CONFIGURACIÓN DE AI")
        
        try:
            if not await self.setup():
                return False

            # Get config use case
            from core.dependency_injection.injector_container import get_config_use_case
            config_use_case = get_config_use_case()
            
            # Parse configuration parameters
            ip = kwargs.get('ip')
            model = kwargs.get('model')
            
            if ip and model:
                # Update both IP and model
                print_info(f"Actualizando configuración LLM: IP={ip}, Modelo={model}")
                success = await config_use_case.update_llm_config(ip, model)
                if success:
                    print_success("✓ Configuración LLM actualizada correctamente")
                    return True
                else:
                    print_error("✗ Error actualizando configuración LLM")
                    return False
            elif ip:
                # Update only IP
                print_info(f"Actualizando IP del LLM: {ip}")
                success = await config_use_case.update_llm_ip(ip)
                if success:
                    print_success("✓ IP del LLM actualizada correctamente")
                    return True
                else:
                    print_error("✗ Error actualizando IP del LLM")
                    return False
            elif model:
                # Update only model
                print_info(f"Actualizando modelo del LLM: {model}")
                success = await config_use_case.update_llm_model(model)
                if success:
                    print_success("✓ Modelo del LLM actualizado correctamente")
                    return True
                else:
                    print_error("✗ Error actualizando modelo del LLM")
                    return False
            else:
                # Show current configuration
                print_info("Mostrando configuración actual...")
                summary = await config_use_case.get_config_summary()
                
                print_success("Configuración actual:")
                print_info(f"  Modo: {summary['mode']}")
                print_info(f"  LLM IP: {summary['llm']['ip']}")
                print_info(f"  LLM Modelo: {summary['llm']['model']}")
                print_info(f"  Archivo: {summary['config_file']}")
                print_info(f"  Cargado: {'Sí' if summary['is_loaded'] else 'No'}")
                print_info(f"  Creado: {summary['created_at']}")
                print_info(f"  Actualizado: {summary['updated_at']}")
                
                return True

        except Exception as e:
            print_error(f"Error en configuración de AI: {e}")
            return False
