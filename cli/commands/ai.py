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
        elif action == "decide":
            return await self._decide(**kwargs)
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
            url = kwargs.get('url')
            model = kwargs.get('model')
            api_key = kwargs.get('api_key')
            
            if url and model and api_key:
                # Update all LLM configuration
                print_info(f"Actualizando configuración LLM: URL={url}, Modelo={model}, API Key=***")
                success = await config_use_case.update_llm_config(url, model, api_key)
                if success:
                    print_success("✓ Configuración LLM actualizada correctamente")
                    return True
                else:
                    print_error("✗ Error actualizando configuración LLM")
                    return False
            elif url and model:
                # Update URL and model
                print_info(f"Actualizando configuración LLM: URL={url}, Modelo={model}")
                success = await config_use_case.update_llm_config(url, model)
                if success:
                    print_success("✓ Configuración LLM actualizada correctamente")
                    return True
                else:
                    print_error("✗ Error actualizando configuración LLM")
                    return False
            elif url:
                # Update only URL
                print_info(f"Actualizando URL del LLM: {url}")
                success = await config_use_case.update_llm_url(url)
                if success:
                    print_success("✓ URL del LLM actualizada correctamente")
                    return True
                else:
                    print_error("✗ Error actualizando URL del LLM")
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
            elif api_key:
                # Update only API key
                print_info(f"Actualizando API key del LLM")
                # Get current config first
                current_config = await config_use_case.get_config()
                success = await config_use_case.update_llm_config(
                    current_config.llm.url,
                    current_config.llm.model,
                    api_key
                )
                if success:
                    print_success("✓ API key del LLM actualizada correctamente")
                    return True
                else:
                    print_error("✗ Error actualizando API key del LLM")
                    return False
            else:
                # Show current configuration
                print_info("Mostrando configuración actual...")
                summary = await config_use_case.get_config_summary()
                
                print_success("Configuración actual:")
                print_info(f"  Modo: {summary['mode']}")
                print_info(f"  LLM URL: {summary['llm']['url']}")
                print_info(f"  LLM Modelo: {summary['llm']['model']}")
                print_info(f"  Archivo: {summary['config_file']}")
                print_info(f"  Cargado: {'Sí' if summary['is_loaded'] else 'No'}")
                print_info(f"  Creado: {summary['created_at']}")
                print_info(f"  Actualizado: {summary['updated_at']}")
                
                return True

        except Exception as e:
            print_error(f"Error en configuración de AI: {e}")
            return False

    async def _decide(self, prompt: str, mode: str = "assistant", **kwargs) -> bool:
        """Make a decision based on user prompt and Home Assistant state."""
        print_header("TOMA DE DECISIONES CON AI")
        
        try:
            if not await self.setup():
                return False

            # Get decision use case
            from core.dependency_injection.injector_container import get_decision_use_case
            decision_use_case = get_decision_use_case()
            
            print_info(f"Prompt del usuario: {prompt}")
            print_info(f"Modo de decisión: {mode}")
            print_info("Obteniendo información de Home Assistant...")
            
            # Make decision
            decision = await decision_use_case.make_decision(prompt, mode)
            
            print_success("✓ Decisión tomada correctamente")
            print_info(f"Mensaje: {decision.message}")
            
            if decision.actions:
                print_info("Acciones a ejecutar:")
                for i, action in enumerate(decision.actions, 1):
                    print_info(f"  {i}. Entidad: {action.entity}")
                    print_info(f"     Acción: {action.action}")
                    if action.parameters:
                        print_info(f"     Parámetros: {action.parameters}")
            else:
                print_info("No se requieren acciones")
            
            return True

        except Exception as e:
            print_error(f"Error en toma de decisiones: {e}")
            return False
