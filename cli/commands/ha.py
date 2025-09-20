"""Home Assistant interaction command for the CLI."""

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


class HACommand(BaseCommand):
    """Home Assistant interaction command."""

    async def execute(self, action: str, **kwargs) -> bool:
        """Execute Home Assistant command."""
        print_command_header("HA", "Home Assistant Integration")
        
        # Extract HA connection parameters
        ha_token = kwargs.pop('ha_token', None)
        
        # Show connection info
        print_info("Conectando a Home Assistant en: homeassistant.local:8123")

        if action == "entities":
            return await self._get_entities(ha_token=ha_token, **kwargs)
        elif action == "sensors":
            return await self._get_sensors(ha_token=ha_token, **kwargs)
        elif action == "summary":
            return await self._get_summary(ha_token=ha_token, **kwargs)
        elif action == "entity":
            return await self._get_entity(ha_token=ha_token, **kwargs)
        elif action == "test":
            return await self._test_connection(ha_token=ha_token, **kwargs)
        elif action == "complete":
            return await self._get_complete_info(ha_token=ha_token, **kwargs)
        elif action == "info":
            return await self._show_info(ha_token=ha_token, **kwargs)
        elif action == "config":
            return await self._config(**kwargs)
        else:
            print_error(f"Acción de Home Assistant desconocida: {action}")
            return False

    async def _get_entities(
        self, domain: Optional[str] = None, interactive: bool = True
    ) -> bool:
        """Get entities from Home Assistant."""
        print_header("ENTIDADES DE HOME ASSISTANT")

        try:
            if not await self.setup():
                return False

            print_info("Obteniendo entidades de Home Assistant...")

            # Get HA use case
            ha_use_case = self.get_ha_use_case()
            
            if domain:
                entities = await ha_use_case.get_entities_by_domain(domain)
                print_info(f"Entidades del dominio '{domain}':")
            else:
                entities = await ha_use_case.get_all_entities()
                print_info("Todas las entidades:")
            
            if entities:
                print_success(f"Encontradas {len(entities)} entidades:")
                for entity in entities[:20]:  # Show first 20
                    state_info = f" ({entity.unit_of_measurement})" if entity.unit_of_measurement else ""
                    print_info(f"  {entity.entity_id}: {entity.state}{state_info}")
                
                if len(entities) > 20:
                    print_info(f"  ... y {len(entities) - 20} más")
                
                return True
            else:
                print_error("No se encontraron entidades")
                return False

        except Exception as e:
            print_error(f"Error obteniendo entidades: {e}")
            return False

    async def _get_sensors(self, interactive: bool = True) -> bool:
        """Get sensor entities from Home Assistant."""
        print_header("SENSORES DE HOME ASSISTANT")

        try:
            if not await self.setup():
                return False

            print_info("Obteniendo sensores de Home Assistant...")

            # Get HA use case
            ha_use_case = self.get_ha_use_case()
            
            # Get sensors
            sensors = await ha_use_case.get_sensors()
            
            if sensors:
                print_success(f"Encontrados {len(sensors)} sensores:")
                for sensor in sensors[:15]:  # Show first 15
                    unit_info = f" ({sensor.unit_of_measurement})" if sensor.unit_of_measurement else ""
                    print_info(f"  {sensor.entity_id}: {sensor.state}{unit_info}")
                
                if len(sensors) > 15:
                    print_info(f"  ... y {len(sensors) - 15} más")
                
                return True
            else:
                print_error("No se encontraron sensores")
                return False

        except Exception as e:
            print_error(f"Error obteniendo sensores: {e}")
            return False

    async def _get_summary(self, interactive: bool = True) -> bool:
        """Get entity summary from Home Assistant."""
        print_header("RESUMEN DE HOME ASSISTANT")

        try:
            if not await self.setup():
                return False

            print_info("Obteniendo resumen de Home Assistant...")

            # Get HA use case
            ha_use_case = self.get_ha_use_case()
            
            # Get entity summary
            summary = await ha_use_case.get_entity_summary()
            
            print_success("Resumen de entidades:")
            print_info(f"  Total de entidades: {summary.total_entities}")
            print_info(f"  Última actualización: {summary.last_updated}")
            
            print_info("\nEntidades por dominio:")
            for domain, count in sorted(summary.entities_by_domain.items()):
                print_info(f"  {domain}: {count}")
            
            print_info("\nEntidades por estado:")
            for state, count in sorted(summary.entities_by_state.items()):
                print_info(f"  {state}: {count}")
            
            return True

        except Exception as e:
            print_error(f"Error obteniendo resumen: {e}")
            return False

    async def _get_entity(
        self, entity_id: str, interactive: bool = True
    ) -> bool:
        """Get specific entity from Home Assistant."""
        print_header(f"ENTIDAD: {entity_id}")

        try:
            if not await self.setup():
                return False

            print_info(f"Obteniendo información de la entidad: {entity_id}")

            # Get HA use case
            ha_use_case = self.get_ha_use_case()
            
            # Get entity state
            entity = await ha_use_case.get_entity_state(entity_id)
            
            if entity:
                print_success("Información de la entidad:")
                print_info(f"  ID: {entity.entity_id}")
                print_info(f"  Estado: {entity.state}")
                print_info(f"  Dominio: {entity.domain}")
                print_info(f"  Nombre: {entity.friendly_name}")
                print_info(f"  Última actualización: {entity.last_updated}")
                
                if entity.unit_of_measurement:
                    print_info(f"  Unidad: {entity.unit_of_measurement}")
                
                if entity.device_class:
                    print_info(f"  Clase de dispositivo: {entity.device_class}")
                
                if entity.icon:
                    print_info(f"  Icono: {entity.icon}")
                
                return True
            else:
                print_error(f"Entidad {entity_id} no encontrada")
                return False

        except Exception as e:
            print_error(f"Error obteniendo entidad {entity_id}: {e}")
            return False

    async def _test_connection(self, interactive: bool = True, ha_token: str = None) -> bool:
        """Test connection to Home Assistant."""
        print_header("PRUEBA DE CONEXIÓN A HOME ASSISTANT")

        try:
            if not await self.setup(ha_token=ha_token):
                return False

            print_info("Probando conexión a Home Assistant...")

            # Get HA use case
            ha_use_case = self.get_ha_use_case()
            
            # Test connection
            is_connected = await ha_use_case.test_connection()
            
            if is_connected:
                print_success("Conexión a Home Assistant exitosa")
                return True
            else:
                print_error("No se pudo conectar a Home Assistant")
                return False

        except Exception as e:
            print_error(f"Error probando conexión: {e}")
            return False

    async def _get_complete_info(self, interactive: bool = True, ha_token: str = None) -> bool:
        """Get complete Home Assistant information."""
        print_header("INFORMACIÓN COMPLETA DE HOME ASSISTANT")

        try:
            if not await self.setup(ha_token=ha_token):
                return False

            print_info("Obteniendo información completa de Home Assistant...")

            # Get HA use case
            ha_use_case = self.get_ha_use_case()
            
            # Test connection first
            print_info("1. Probando conexión...")
            try:
                is_connected = await ha_use_case.test_connection()
                if not is_connected:
                    print_error("No se pudo conectar a Home Assistant")
                    print_info("Continuando con información limitada...")
                else:
                    print_success("✓ Conexión exitosa")
            except Exception as e:
                print_error(f"Error de conexión: {e}")
                print_info("Continuando con información limitada...")
                is_connected = False
            
            # Get configuration
            print_info("\n2. Obteniendo configuración...")
            if is_connected:
                try:
                    config = await ha_use_case.get_config()
                    print_success(f"✓ Versión: {config.version}")
                    print_info(f"  Ubicación: {config.location_name}")
                    print_info(f"  Zona horaria: {config.time_zone}")
                except Exception as e:
                    print_error(f"Error obteniendo configuración: {e}")
            else:
                print_info("⏭️  Saltando configuración (sin conexión)")
            
            # Get entity summary
            print_info("\n3. Obteniendo resumen de entidades...")
            if is_connected:
                try:
                    summary = await ha_use_case.get_entity_summary()
                    print_success(f"✓ Total de entidades: {summary.total_entities}")
                    print_info(f"  Última actualización: {summary.last_updated}")
                    
                    print_info("\n  Entidades por dominio:")
                    for domain, count in sorted(summary.entities_by_domain.items()):
                        print_info(f"    {domain}: {count}")
                    
                    print_info("\n  Entidades por estado:")
                    for state, count in sorted(summary.entities_by_state.items()):
                        print_info(f"    {state}: {count}")
                except Exception as e:
                    print_error(f"Error obteniendo resumen: {e}")
            else:
                print_info("⏭️  Saltando resumen de entidades (sin conexión)")
            
            # Get services
            print_info("\n4. Obteniendo servicios disponibles...")
            if is_connected:
                try:
                    services = await ha_use_case.get_services()
                    if services and isinstance(services, list):
                        # Calculate total service count
                        service_count = sum(len(domain_data.get('services', {})) for domain_data in services)
                        print_success(f"✓ {service_count} servicios disponibles")
                        
                        # Show first few services from each domain
                        for domain_data in services[:5]:
                            domain = domain_data.get('domain', 'unknown')
                            domain_services = domain_data.get('services', {})
                            print_info(f"  {domain}: {len(domain_services)} servicios")
                            # Show first 3 services from this domain
                            for service_name in list(domain_services.keys())[:3]:
                                print_info(f"    - {service_name}")
                            if len(domain_services) > 3:
                                print_info(f"    ... y {len(domain_services) - 3} más")
                        
                        if len(services) > 5:
                            print_info(f"  ... y {len(services) - 5} dominios más")
                    else:
                        print_info("No se encontraron servicios")
                except Exception as e:
                    print_error(f"Error obteniendo servicios: {e}")
            else:
                print_info("⏭️  Saltando servicios (sin conexión)")
            
            # Get different entity types
            print_info("\n5. Obteniendo entidades por tipo...")
            
            if is_connected:
                # Sensors
                try:
                    sensors = await ha_use_case.get_sensors()
                    print_success(f"✓ Sensores: {len(sensors)}")
                    if sensors:
                        print_info("  Primeros sensores:")
                        for sensor in sensors[:5]:
                            unit_info = f" ({sensor.unit_of_measurement})" if sensor.unit_of_measurement else ""
                            print_info(f"    {sensor.entity_id}: {sensor.state}{unit_info}")
                        if len(sensors) > 5:
                            print_info(f"    ... y {len(sensors) - 5} más")
                except Exception as e:
                    print_error(f"Error obteniendo sensores: {e}")
                
                # Binary sensors
                try:
                    binary_sensors = await ha_use_case.get_binary_sensors()
                    print_success(f"✓ Sensores binarios: {len(binary_sensors)}")
                except Exception as e:
                    print_error(f"Error obteniendo sensores binarios: {e}")
                
                # Switches
                try:
                    switches = await ha_use_case.get_switches()
                    print_success(f"✓ Interruptores: {len(switches)}")
                except Exception as e:
                    print_error(f"Error obteniendo interruptores: {e}")
                
                # Lights
                try:
                    lights = await ha_use_case.get_lights()
                    print_success(f"✓ Luces: {len(lights)}")
                except Exception as e:
                    print_error(f"Error obteniendo luces: {e}")
            else:
                print_info("⏭️  Saltando entidades por tipo (sin conexión)")
            
            if is_connected:
                print_success("\n✓ Información completa obtenida exitosamente")
            else:
                print_info("\n⚠️  Información limitada obtenida (Home Assistant no disponible)")
                print_info("   Para obtener información completa, asegúrate de que Home Assistant esté ejecutándose")
            
            # Clean up resources
            await self.cleanup()
            return True

        except Exception as e:
            print_error(f"Error obteniendo información completa: {e}")
            # Clean up resources even on error
            await self.cleanup()
            return False

    async def _show_info(self, interactive: bool = True, ha_token: str = None) -> bool:
        """Show Home Assistant connection information."""
        print_header("INFORMACIÓN DE CONEXIÓN A HOME ASSISTANT")

        try:
            # Check stored credentials
            try:
                from core.auth.credential_manager import CredentialManager
                credential_manager = CredentialManager()
                
                if credential_manager.has_credentials():
                    credentials = credential_manager.get_credentials()
                    print_info("📋 Credenciales almacenadas:")
                    print_info(f"  URL: {credentials.get('ha_url', 'No configurada')}")
                    print_info(f"  Usuario: {credentials.get('username', 'No configurado')}")
                    print_info(f"  Token: {'Configurado' if credentials.get('token') else 'No configurado'}")
                    print_info(f"  Almacenado: {credentials.get('stored_at', 'Desconocido')}")
                else:
                    print_info("📋 No hay credenciales almacenadas")
                    print_info("  Usa 'neural auth login' para configurar credenciales")
            except Exception as e:
                print_error(f"Error obteniendo credenciales: {e}")

            # Show current connection parameters
            print_info("\n🔗 Parámetros de conexión actuales:")
            print_info("  URL: homeassistant.local:8123")
            
            if ha_token:
                print_info(f"  Token especificado: {'Configurado' if ha_token else 'No configurado'}")
            else:
                print_info("  Token: Usando credenciales almacenadas o sin autenticación")

            # Test connection
            print_info("\n🧪 Probando conexión...")
            if not await self.setup(ha_token=ha_token):
                print_error("Error configurando conexión")
                return False

            ha_use_case = self.get_ha_use_case()
            is_connected = await ha_use_case.test_connection()
            
            if is_connected:
                print_success("✓ Conexión exitosa a Home Assistant")
            else:
                print_error("✗ No se pudo conectar a Home Assistant")
                print_info("  Verifica que Home Assistant esté ejecutándose")
                print_info("  Usa 'neural auth login' para configurar credenciales")

            return True

        except Exception as e:
            print_error(f"Error obteniendo información: {e}")
            return False

    async def _config(self, **kwargs) -> bool:
        """Manage HA configuration."""
        print_header("CONFIGURACIÓN DE HOME ASSISTANT")
        
        try:
            if not await self.setup():
                return False

            # Get config use case
            from core.dependency_injection.injector_container import get_config_use_case
            config_use_case = get_config_use_case()
            
            # Parse configuration parameters
            mode = kwargs.get('mode')
            
            if mode:
                # Update mode
                print_info(f"Actualizando modo de la aplicación: {mode}")
                success = await config_use_case.update_mode(mode)
                if success:
                    print_success("✓ Modo de la aplicación actualizado correctamente")
                    return True
                else:
                    print_error("✗ Error actualizando modo de la aplicación")
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
            print_error(f"Error en configuración de Home Assistant: {e}")
            return False

    def get_ha_use_case(self):
        """Get the Home Assistant use case."""
        return self.ha_use_case
