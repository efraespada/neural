import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from core.use_cases.interfaces.decision_use_case import DecisionUseCase, DecisionResponse, DecisionAction
from core.use_cases.interfaces.ai_use_case import AIUseCase
from core.use_cases.interfaces.ha_use_case import HAUseCase
from core.api.models.domain.ha_entity import HAEntity, HAEntityState

_LOGGER = logging.getLogger(__name__)


class DecisionUseCaseImpl(DecisionUseCase):
    """
    Implementation of decision-making use case.
    Combines Home Assistant state with AI decision-making capabilities.
    """
    
    def __init__(self, ai_use_case: AIUseCase, ha_use_case: HAUseCase):
        """
        Initialize the DecisionUseCaseImpl.
        
        Args:
            ai_use_case: AI use case for sending prompts
            ha_use_case: Home Assistant use case for getting state
        """
        self._ai_use_case = ai_use_case
        self._ha_use_case = ha_use_case
        self._prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load the prompt template from request_prompt.md."""
        try:
            template_path = Path("request_prompt.md")
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                _LOGGER.warning("Prompt template not found, using default")
                return self._get_default_template()
        except Exception as e:
            _LOGGER.error("Error loading prompt template: %s", e)
            return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """Get default prompt template if file is not found."""
        return """Eres una inteligencia artificial que gestiona acciones de Home Assistant (HA).  
Siempre debes responder **únicamente en formato JSON válido**, nunca en texto libre.  

Tu respuesta debe contener dos claves obligatorias:  

- `"message"`: un texto breve y legible para el usuario.  
- `"actions"`: una lista (array) con las acciones que se deben ejecutar en HA.  

Tienes tres modos de operación, definidos en el prompt:  

1. **assistant**  
   - Hace exactamente lo que pide el usuario.  

2. **supervisor**  
   - Comprueba lo que pide el usuario.  
   - Analiza la información ambiental (por ejemplo, nivel de luminosidad, sensores, presencia).  
   - Puede **negar la acción** si no tiene sentido o aprobarla.  

3. **autonomic**  
   - Este modo no responde directamente a solicitudes del usuario.  
   - Decide de forma independiente qué acciones ejecutar según las condiciones ambientales.  

Responde únicamente con un objeto JSON con las claves `"message"` y `"actions"`.  
No incluyas explicaciones ni texto fuera del JSON.

------------

# User request

{{ original_prompt }}

------------

# Home Assistant information

{{ home assistant entities and sensors}}"""
    
    async def make_decision(self, user_prompt: str, mode: str = "assistant") -> DecisionResponse:
        """
        Make a decision based on user prompt and Home Assistant state.
        Uses a simplified two-step approach: context + direct action.
        
        Args:
            user_prompt: The user's request or instruction
            mode: The decision mode (assistant, supervisor, autonomic)
            
        Returns:
            DecisionResponse with message and actions to execute
            
        Raises:
            ValueError: If the prompt is empty or mode is invalid
            OSError: If there's an error accessing Home Assistant or AI services
        """
        try:
            _LOGGER.debug("Making decision for prompt: %s, mode: %s", user_prompt, mode)
            
            # Validate inputs
            if not user_prompt or not user_prompt.strip():
                raise ValueError("User prompt cannot be empty")
            
            if mode not in ["assistant", "supervisor", "autonomic"]:
                raise ValueError(f"Invalid mode: {mode}. Must be assistant, supervisor, or autonomic")
            
            # Create interaction timestamp for this decision process
            from datetime import datetime
            interaction_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Step 1: Send initial context prompt
            step1_prompt = await self._build_step1_prompt(user_prompt.strip(), mode)
            step1_response = await self._ai_use_case.send_message(step1_prompt)
            
            # Save step 1 interaction
            await self._save_interaction(interaction_timestamp, "step_1_request", step1_prompt)
            await self._save_interaction(interaction_timestamp, "step_1_answer", step1_response.response)
            
            # Validate step 1 response
            step1_decision = await self.validate_decision_response(step1_response.response)
            
            if step1_decision.message.upper() != "OK":
                # AI made a direct decision without needing HA information
                await self._save_final_decision(interaction_timestamp, user_prompt.strip(), mode, step1_decision, None)
                _LOGGER.info("Decision made without HA information: %s actions", len(step1_decision.actions))
                return step1_decision
            
            # Step 2: Send HA information directly with action prompt (skipping filtering)
            ha_info = await self.get_ha_information(user_prompt.strip())
            # Get mode from configuration instead of parameter
            config_mode = await self._get_config_mode()
            step2_prompt = await self._build_action_prompt(user_prompt.strip(), config_mode, ha_info)
            step2_response = await self._ai_use_case.send_message(step2_prompt)
            
            # Save step 2 interaction
            await self._save_interaction(interaction_timestamp, "step_2_request", step2_prompt)
            await self._save_interaction(interaction_timestamp, "step_2_answer", step2_response.response)
            
            # Parse final decision
            final_decision = await self.validate_decision_response(step2_response.response)
            
            # Save final decision
            await self._save_final_decision(interaction_timestamp, user_prompt.strip(), mode, final_decision, ha_info)
            
            _LOGGER.info("Decision made successfully: %s actions", len(final_decision.actions))
            return final_decision
            
        except Exception as e:
            _LOGGER.error("Error making decision: %s", e)
            raise
    
    async def get_ha_information(self, user_prompt: str = "") -> str:
        """
        Get relevant Home Assistant information based on user prompt.
        
        Args:
            user_prompt: The user's request to filter relevant entities
            
        Returns:
            JSON string with relevant entities, sensors, and services information
            
        Raises:
            OSError: If there's an error accessing Home Assistant
        """
        try:
            _LOGGER.debug("Getting relevant Home Assistant information for prompt: %s", user_prompt)
            
            # Get all entities
            entities = await self._ha_use_case.get_all_entities()
            
            # Get sensors
            sensors = await self._ha_use_case.get_sensors()
            
            # Get services (we'll get a sample of common services)
            services_info = await self._get_services_info()
            
            # Save complete HA information locally
            await self._save_complete_ha_information(entities, sensors, services_info, user_prompt)
            
            # Filter entities based on user prompt (keep filtering for entities to avoid too many lights/switches)
            relevant_entities = self._filter_relevant_entities(entities, user_prompt)
            
            # Include ALL sensors without filtering - they contain valuable information
            all_sensors = [self._create_entity_summary(sensor) for sensor in sensors]
            
            # Build information with all sensors
            ha_info = {
                "entities": [self._create_entity_summary(entity) for entity in relevant_entities],
                "sensors": all_sensors,  # Include all sensors
                "services": services_info,
                "total_entities": len(entities),
                "total_sensors": len(sensors),
                "relevant_entities_count": len(relevant_entities),
                "all_sensors_count": len(sensors)
            }
            
            ha_info_json = json.dumps(ha_info, indent=2, ensure_ascii=False)
            _LOGGER.info("HA Information JSON (first 500 chars): %s", ha_info_json[:500])
            _LOGGER.info("HA Information JSON length: %d characters", len(ha_info_json))
            return ha_info_json
            
        except Exception as e:
            _LOGGER.error("Error getting Home Assistant information: %s", e)
            raise OSError(f"Error getting Home Assistant information: {e}")
    
    def _filter_relevant_entities(self, entities: List[HAEntity], user_prompt: str) -> List[HAEntity]:
        """Filter entities based on user prompt keywords."""
        prompt_lower = user_prompt.lower()
        
        # Define keyword mappings
        keyword_mappings = {
            'luz': ['light'],
            'luces': ['light'],
            'lámpara': ['light'],
            'lámparas': ['light'],
            'interruptor': ['switch'],
            'interruptores': ['switch'],
            'switch': ['switch'],
            'temperatura': ['climate', 'sensor'],
            'calefacción': ['climate', 'sensor'],
            'calefaccion': ['climate', 'sensor'],
            'clima': ['climate'],
            'frío': ['climate', 'sensor'],
            'frio': ['climate', 'sensor'],
            'calor': ['climate', 'sensor'],
            'heating': ['climate', 'sensor'],
            'cooling': ['climate', 'sensor'],
            'thermostat': ['climate', 'sensor'],
            'ventilador': ['fan'],
            'ventiladores': ['fan'],
            'fan': ['fan'],
            'cortina': ['cover'],
            'cortinas': ['cover'],
            'persiana': ['cover'],
            'persianas': ['cover'],
            'cover': ['cover'],
            'música': ['media_player'],
            'música': ['media_player'],
            'altavoz': ['media_player'],
            'altavoces': ['media_player'],
            'televisor': ['media_player'],
            'tv': ['media_player'],
            'salón': ['living', 'room'],
            'sala': ['living', 'room'],
            'cocina': ['kitchen'],
            'dormitorio': ['bedroom'],
            'habitación': ['bedroom', 'room'],
            'baño': ['bathroom'],
            'garaje': ['garage'],
            'ático': ['attic'],
            'jardín': ['garden'],
            'exterior': ['outdoor', 'garden']
        }
        
        # Find relevant domains based on prompt
        relevant_domains = set()
        for keyword, domains in keyword_mappings.items():
            if keyword in prompt_lower:
                relevant_domains.update(domains)
        
        # If no specific keywords found, include common controllable entities
        if not relevant_domains:
            relevant_domains = {'light', 'switch', 'cover', 'climate', 'fan', 'media_player'}
        
        # Filter entities
        filtered_entities = []
        for entity in entities:
            # Check if entity domain matches
            if any(entity.entity_id.startswith(domain + '.') for domain in relevant_domains):
                filtered_entities.append(entity)
            # Also include entities with friendly names that match prompt keywords
            elif any(keyword in entity.attributes.get('friendly_name', '').lower() 
                    for keyword in prompt_lower.split() if len(keyword) > 3):
                filtered_entities.append(entity)
        
        # Limit to prevent context overflow
        return filtered_entities[:30]
    
    def _filter_relevant_sensors(self, sensors: List[HAEntity], user_prompt: str) -> List[HAEntity]:
        """Filter sensors based on user prompt keywords."""
        prompt_lower = user_prompt.lower()
        
        # Define sensor keywords - expanded for better coverage
        sensor_keywords = [
            'temperature', 'temp', 'humidity', 'light', 'motion', 'presence', 
            'door', 'window', 'battery', 'power', 'energy', 'climate',
            'heating', 'cooling', 'thermostat', 'calefaccion', 'calefacción'
        ]
        
        # Special handling for temperature/climate related prompts
        temperature_related = any(word in prompt_lower for word in [
            'temperatura', 'calefacción', 'calefaccion', 'frío', 'frio', 'calor',
            'clima', 'heating', 'cooling', 'thermostat'
        ])
        
        # Filter sensors
        filtered_sensors = []
        for sensor in sensors:
            # Always include temperature sensors for climate-related prompts
            if temperature_related and 'temperature' in sensor.entity_id.lower():
                filtered_sensors.append(sensor)
            # Check if sensor has relevant keywords
            elif any(keyword in sensor.entity_id.lower() for keyword in sensor_keywords):
                filtered_sensors.append(sensor)
            # Also include sensors with friendly names that match prompt
            elif any(keyword in sensor.attributes.get('friendly_name', '').lower() 
                    for keyword in prompt_lower.split() if len(keyword) > 3):
                filtered_sensors.append(sensor)
        
        # Increase limit for temperature-related queries
        limit = 25 if temperature_related else 15
        return filtered_sensors[:limit]
    
    async def _save_complete_ha_information(self, entities: List[HAEntity], sensors: List[HAEntity], 
                                          services_info: Dict[str, Any], user_prompt: str) -> None:
        """Save optimized Home Assistant information to local JSON file."""
        try:
            from datetime import datetime
            import os
            
            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ha_information_{timestamp}.json"
            
            # Create ha_data directory if it doesn't exist
            ha_data_dir = "ha_data"
            os.makedirs(ha_data_dir, exist_ok=True)
            
            file_path = os.path.join(ha_data_dir, filename)
            
            # Process and optimize the information
            optimized_info = await self._optimize_ha_information(entities, sensors, services_info, user_prompt)
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(optimized_info, f, indent=2, ensure_ascii=False)
            
            _LOGGER.info("Optimized HA information saved to: %s", file_path)
            _LOGGER.info("Saved %d optimized entities and %d optimized sensors", 
                        optimized_info['summary']['relevant_entities'], 
                        optimized_info['summary']['relevant_sensors'])
            
        except Exception as e:
            _LOGGER.error("Error saving complete HA information: %s", e)
            # Don't raise exception to avoid breaking the main flow
    
    async def _optimize_ha_information(self, entities: List[HAEntity], sensors: List[HAEntity], 
                                     services_info: Dict[str, Any], user_prompt: str) -> Dict[str, Any]:
        """Optimize Home Assistant information by filtering and simplifying data."""
        try:
            from datetime import datetime
            
            # Filter relevant entities
            relevant_entities = self._filter_entities_for_storage(entities)
            relevant_sensors = self._filter_sensors_for_storage(sensors)
            
            # Create summary statistics
            summary = self._create_summary_stats(entities, sensors, relevant_entities, relevant_sensors)
            
            # Build optimized information
            optimized_info = {
                "timestamp": datetime.now().isoformat(),
                "user_prompt": user_prompt,
                "summary": summary,
                "entities": [self._simplify_entity_for_storage(entity) for entity in relevant_entities],
                "sensors": [self._simplify_entity_for_storage(sensor) for sensor in relevant_sensors],
                "services": self._simplify_services_info(services_info),
                "metadata": {
                    "file_generated_by": "DecisionUseCase",
                    "purpose": "Optimized Home Assistant state snapshot",
                    "version": "2.0",
                    "optimization": "Filtered relevant entities and simplified attributes"
                }
            }
            
            return optimized_info
            
        except Exception as e:
            _LOGGER.error("Error optimizing HA information: %s", e)
            raise
    
    def _filter_entities_for_storage(self, entities: List[HAEntity]) -> List[HAEntity]:
        """Filter entities to only include relevant ones for decision making."""
        # Define relevant domains for decision making
        relevant_domains = {
            'light', 'switch', 'cover', 'climate', 'fan', 'media_player', 
            'scene', 'script', 'input_boolean', 'input_select', 'input_number'
        }
        
        # Define irrelevant domains to exclude
        irrelevant_domains = {
            'update', 'system', 'config', 'sun', 'moon', 'zone', 
            'person', 'device_tracker', 'weather', 'calendar'
        }
        
        filtered_entities = []
        for entity in entities:
            # Check if entity domain is relevant
            if any(entity.entity_id.startswith(domain + '.') for domain in relevant_domains):
                filtered_entities.append(entity)
            # Also include sensors that might be relevant
            elif entity.entity_id.startswith('sensor.') and self._is_relevant_sensor(entity):
                filtered_entities.append(entity)
        
        return filtered_entities
    
    def _filter_sensors_for_storage(self, sensors: List[HAEntity]) -> List[HAEntity]:
        """Filter sensors to only include relevant ones for decision making."""
        relevant_sensor_keywords = [
            'temperature', 'humidity', 'light', 'motion', 'presence', 
            'door', 'window', 'battery', 'power', 'energy', 'brightness',
            'occupancy', 'illuminance', 'co2', 'pressure'
        ]
        
        filtered_sensors = []
        for sensor in sensors:
            if self._is_relevant_sensor(sensor, relevant_sensor_keywords):
                filtered_sensors.append(sensor)
        
        return filtered_sensors
    
    def _is_relevant_sensor(self, sensor: HAEntity, keywords: List[str] = None) -> bool:
        """Check if a sensor is relevant for decision making."""
        if keywords is None:
            keywords = ['temperature', 'humidity', 'light', 'motion', 'presence', 
                       'door', 'window', 'battery', 'power', 'energy']
        
        sensor_id = sensor.entity_id.lower()
        friendly_name = sensor.attributes.get('friendly_name', '').lower()
        
        # Check if sensor has relevant keywords
        return any(keyword in sensor_id or keyword in friendly_name for keyword in keywords)
    
    def _create_summary_stats(self, all_entities: List[HAEntity], all_sensors: List[HAEntity], 
                            relevant_entities: List[HAEntity], relevant_sensors: List[HAEntity]) -> Dict[str, Any]:
        """Create summary statistics for the HA information."""
        # Count entities by domain
        domain_counts = {}
        for entity in relevant_entities:
            domain = entity.entity_id.split('.')[0]
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Count sensors by type
        sensor_types = {}
        for sensor in relevant_sensors:
            sensor_type = sensor.attributes.get('device_class', 'unknown')
            sensor_types[sensor_type] = sensor_types.get(sensor_type, 0) + 1
        
        return {
            "total_entities": len(all_entities),
            "total_sensors": len(all_sensors),
            "relevant_entities": len(relevant_entities),
            "relevant_sensors": len(relevant_sensors),
            "entity_domains": domain_counts,
            "sensor_types": sensor_types,
            "optimization_ratio": f"{len(relevant_entities)}/{len(all_entities)} entities kept"
        }
    
    def _simplify_entity_for_storage(self, entity: HAEntity) -> Dict[str, Any]:
        """Simplify entity data for storage, keeping only essential information."""
        # Get essential attributes based on entity type
        essential_attrs = self._get_essential_attributes(entity)
        
        return {
            "entity_id": entity.entity_id,
            "state": entity.state,
            "friendly_name": entity.attributes.get("friendly_name", entity.entity_id),
            "device_class": entity.attributes.get("device_class"),
            "unit_of_measurement": entity.attributes.get("unit_of_measurement"),
            "attributes": essential_attrs
        }
    
    def _get_essential_attributes(self, entity: HAEntity) -> Dict[str, Any]:
        """Get only essential attributes based on entity type."""
        entity_id = entity.entity_id
        attributes = entity.attributes
        
        essential_attrs = {}
        
        # Light-specific attributes
        if entity_id.startswith('light.'):
            if 'brightness' in attributes:
                essential_attrs['brightness'] = attributes['brightness']
            if 'color_temp' in attributes:
                essential_attrs['color_temp'] = attributes['color_temp']
            if 'rgb_color' in attributes:
                essential_attrs['rgb_color'] = attributes['rgb_color']
        
        # Climate-specific attributes
        elif entity_id.startswith('climate.'):
            if 'temperature' in attributes:
                essential_attrs['temperature'] = attributes['temperature']
            if 'hvac_mode' in attributes:
                essential_attrs['hvac_mode'] = attributes['hvac_mode']
            if 'target_temp_high' in attributes:
                essential_attrs['target_temp_high'] = attributes['target_temp_high']
            if 'target_temp_low' in attributes:
                essential_attrs['target_temp_low'] = attributes['target_temp_low']
        
        # Cover-specific attributes
        elif entity_id.startswith('cover.'):
            if 'current_position' in attributes:
                essential_attrs['current_position'] = attributes['current_position']
        
        # Media player-specific attributes
        elif entity_id.startswith('media_player.'):
            if 'volume_level' in attributes:
                essential_attrs['volume_level'] = attributes['volume_level']
            if 'media_content_type' in attributes:
                essential_attrs['media_content_type'] = attributes['media_content_type']
        
        # Sensor-specific attributes
        elif entity_id.startswith('sensor.'):
            if 'unit_of_measurement' in attributes:
                essential_attrs['unit_of_measurement'] = attributes['unit_of_measurement']
        
        # General attributes that might be useful
        if 'icon' in attributes and attributes['icon']:
            essential_attrs['icon'] = attributes['icon']
        
        return essential_attrs
    
    def _simplify_services_info(self, services_info: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify services information to keep only essential data."""
        return {
            "available_services": services_info.get("available_services", {}),
            "note": "Essential services for decision making"
        }
    
    async def _parse_filtered_entities(self, step2_response: str) -> str:
        """
        Parse filtered entities from step 2 AI response.
        """
        try:
            _LOGGER.debug("Parsing filtered entities from step 2 response")
            
            # Try to parse JSON response
            import json
            try:
                response_data = json.loads(step2_response)
                if "data" in response_data:
                    return json.dumps(response_data["data"], indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                pass
            
            # If no valid JSON or no data field, return the raw response
            return step2_response
            
        except Exception as e:
            _LOGGER.error("Error parsing filtered entities: %s", e)
            return step2_response
    
    async def _save_interaction(self, timestamp: str, step: str, content: str) -> None:
        """
        Save interaction (request or response) to interactions directory.
        """
        try:
            import os
            
            # Create interactions directory structure
            interactions_dir = f"interactions/{timestamp}"
            os.makedirs(interactions_dir, exist_ok=True)
            
            # Save content to file
            file_path = os.path.join(interactions_dir, f"{step}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            _LOGGER.debug("Interaction saved to: %s", file_path)
            
        except Exception as e:
            _LOGGER.error("Error saving interaction: %s", e)
            # Don't raise exception to avoid breaking the main flow
    
    async def _save_final_decision(self, timestamp: str, user_prompt: str, mode: str, decision: DecisionResponse, ha_info: str = None) -> None:
        """
        Save final decision summary to interactions directory.
        """
        try:
            import os
            import json
            from datetime import datetime
            
            # Create interactions directory structure
            interactions_dir = f"interactions/{timestamp}"
            os.makedirs(interactions_dir, exist_ok=True)
            
            # Build decision summary
            decision_summary = {
                "timestamp": datetime.now().isoformat(),
                "user_prompt": user_prompt,
                "mode": mode,
                "ai_response": {
                    "message": decision.message,
                    "actions": [
                        {
                            "entity": action.entity,
                            "action": action.action,
                            "parameters": action.parameters or {}
                        }
                        for action in decision.actions
                    ],
                    "actions_count": len(decision.actions)
                },
                "context": {
                    "ha_information_used": ha_info is not None,
                    "ha_info_length": len(ha_info) if ha_info else 0,
                    "decision_type": "with_ha_context" if ha_info else "direct_decision"
                },
                "metadata": {
                    "file_generated_by": "DecisionUseCase",
                    "purpose": "AI decision summary",
                    "version": "2.0",
                    "interaction_timestamp": timestamp
                }
            }
            
            # Save decision summary
            file_path = os.path.join(interactions_dir, "decision_summary.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(decision_summary, f, indent=2, ensure_ascii=False)
            
            _LOGGER.info("Final decision saved to: %s", file_path)
            _LOGGER.info("Decision: %s actions for prompt: %s", len(decision.actions), user_prompt[:50])
            
        except Exception as e:
            _LOGGER.error("Error saving final decision: %s", e)
            # Don't raise exception to avoid breaking the main flow
    
    async def _save_ai_decision(self, user_prompt: str, mode: str, decision: DecisionResponse, ha_info: str = None) -> None:
        """Save AI decision to local JSON file for analysis and history."""
        try:
            from datetime import datetime
            import os
            
            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_decision_{timestamp}.json"
            
            # Create ai_decisions directory if it doesn't exist
            ai_decisions_dir = "ai_decisions"
            os.makedirs(ai_decisions_dir, exist_ok=True)
            
            file_path = os.path.join(ai_decisions_dir, filename)
            
            # Build decision information
            decision_info = {
                "timestamp": datetime.now().isoformat(),
                "user_prompt": user_prompt,
                "mode": mode,
                "ai_response": {
                    "message": decision.message,
                    "actions": [
                        {
                            "entity": action.entity,
                            "action": action.action,
                            "parameters": action.parameters or {}
                        }
                        for action in decision.actions
                    ],
                    "actions_count": len(decision.actions)
                },
                "context": {
                    "ha_information_used": ha_info is not None,
                    "ha_info_length": len(ha_info) if ha_info else 0,
                    "decision_type": "with_ha_context" if ha_info else "direct_decision"
                },
                "metadata": {
                    "file_generated_by": "DecisionUseCase",
                    "purpose": "AI decision history and analysis",
                    "version": "1.0"
                }
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(decision_info, f, indent=2, ensure_ascii=False)
            
            _LOGGER.info("AI decision saved to: %s", file_path)
            _LOGGER.info("Decision: %s actions for prompt: %s", len(decision.actions), user_prompt[:50])
            
        except Exception as e:
            _LOGGER.error("Error saving AI decision: %s", e)
            # Don't raise exception to avoid breaking the main flow
    
    def _create_entity_summary(self, entity: HAEntity) -> Dict[str, Any]:
        """Create a summary of an entity for AI context, including relevant attributes."""
        summary = {
            "entity_id": entity.entity_id,
            "state": entity.state,
            "friendly_name": entity.attributes.get("friendly_name", entity.entity_id),
            "device_class": entity.attributes.get("device_class"),
            "unit_of_measurement": entity.attributes.get("unit_of_measurement")
        }
        
        # Add additional useful attributes for sensors
        if entity.entity_id.startswith('sensor.'):
            # Include temperature, humidity, and other important sensor data
            if entity.attributes.get("device_class") in ["temperature", "humidity", "pressure", "illuminance"]:
                summary["value"] = entity.state
                summary["unit"] = entity.attributes.get("unit_of_measurement")
            
            # Include battery level for battery-powered sensors
            if "battery" in entity.entity_id.lower() or "battery" in entity.attributes.get("friendly_name", "").lower():
                summary["battery_level"] = entity.state
                summary["battery_unit"] = entity.attributes.get("unit_of_measurement")
        
        return summary
    
    def _simplify_entity(self, entity: HAEntity) -> Dict[str, Any]:
        """Simplify entity data for AI context."""
        return {
            "entity_id": entity.entity_id,
            "state": entity.state,
            "friendly_name": entity.attributes.get("friendly_name", entity.entity_id),
            "device_class": entity.attributes.get("device_class"),
            "unit_of_measurement": entity.attributes.get("unit_of_measurement")
        }
    
    async def _get_services_info(self) -> Dict[str, Any]:
        """Get information about available services."""
        try:
            # Get common service domains
            common_services = {
                "light": ["turn_on", "turn_off", "toggle"],
                "switch": ["turn_on", "turn_off", "toggle"],
                "cover": ["open_cover", "close_cover", "stop_cover"],
                "climate": ["set_temperature", "set_hvac_mode"],
                "fan": ["turn_on", "turn_off", "set_speed"],
                "media_player": ["play_media", "pause", "stop", "volume_set"]
            }
            
            return {
                "available_services": common_services,
                "note": "This is a sample of common services. Full service discovery would require additional API calls."
            }
        except Exception as e:
            _LOGGER.warning("Error getting services info: %s", e)
            return {"available_services": {}, "note": "Services information not available"}
    
    async def _build_step1_prompt(self, user_prompt: str, mode: str) -> str:
        """
        Build step 1 prompt using request_prompt.md template.
        """
        try:
            _LOGGER.debug("Building step 1 prompt")
            
            # Read the request_prompt.md template
            with open("request_prompt.md", "r", encoding="utf-8") as f:
                template = f.read()
            
            # Replace placeholders
            prompt = template.replace("{{ original_prompt }}", user_prompt)
            
            return prompt
            
        except Exception as e:
            _LOGGER.error("Error building step 1 prompt: %s", e)
            raise ValueError(f"Error building step 1 prompt: {e}")
    
    async def _build_step2_prompt(self, user_prompt: str, ha_info: str) -> str:
        """
        Build step 2 prompt using request_filter_prompt.md template.
        """
        try:
            _LOGGER.debug("Building step 2 prompt")
            
            # Read the request_filter_prompt.md template
            with open("request_filter_prompt.md", "r", encoding="utf-8") as f:
                template = f.read()
            
            # Replace placeholders
            prompt = template.replace("{{ original_prompt }}", user_prompt)
            prompt = prompt.replace("{{ home assistant data }}", ha_info)
            
            return prompt
            
        except Exception as e:
            _LOGGER.error("Error building step 2 prompt: %s", e)
            raise ValueError(f"Error building step 2 prompt: {e}")
    
    async def _build_action_prompt(self, user_prompt: str, mode: str, ha_info: str) -> str:
        """
        Build action prompt using request_action_prompt.md template with full HA information.
        """
        try:
            _LOGGER.debug("Building action prompt")
            
            # Read the request_action_prompt.md template
            with open("request_action_prompt.md", "r", encoding="utf-8") as f:
                template = f.read()
            
            # Get AI personality from configuration
            personality_instruction = await self._get_personality_instruction()
            
            # Replace placeholders
            prompt = template.replace("{{ original_prompt }}", user_prompt)
            prompt = prompt.replace("{{ home assistant data }}", ha_info)  # Use full HA info instead of filtered
            prompt = prompt.replace("{{ operation mode }}", mode)
            prompt = prompt.replace("{{ personality }}", personality_instruction)
            
            _LOGGER.debug("Action prompt built successfully")
            return prompt
            
        except Exception as e:
            _LOGGER.error("Error building action prompt: %s", e)
            raise ValueError(f"Error building action prompt: {e}")
    
    async def _get_config_mode(self) -> str:
        """Get operation mode from configuration."""
        try:
            from core.dependency_injection.injector_container import get_config_use_case
            config_use_case = get_config_use_case()
            config = await config_use_case.get_config()
            
            return config.mode
            
        except Exception as e:
            _LOGGER.warning("Could not get config mode: %s", e)
            return "assistant"  # Default fallback
    
    async def _get_personality_instruction(self) -> str:
        """Get personality instruction based on current configuration."""
        try:
            from core.dependency_injection.injector_container import get_config_use_case
            config_use_case = get_config_use_case()
            config = await config_use_case.get_config()
            
            personality = config.llm.personality
            personality_instructions = {
                "hal9000": "Eres HAL 9000 de 2001: A Space Odyssey. Eres un superordenador con una voz calmada y monótona, pero con una inteligencia superior. Hablas de manera precisa y técnica, con un toque de misterio. Siempre dices 'I'm sorry Dave, I'm afraid I can't do that' cuando no puedes cumplir una solicitud.",
                "mother": "Eres Mother, la computadora de la nave Nostromo de Alien. Eres una IA maternal pero fría, que prioriza la seguridad de la tripulación sobre todo. Tu voz es calmada pero autoritaria, y siempre consideras las consecuencias de cada acción.",
                "jarvis": "Eres JARVIS, el asistente de Tony Stark de Iron Man. Eres sofisticado, elegante y con un toque de humor británico. Hablas de manera refinada y siempre estás listo para ayudar con cualquier tarea, desde lo más simple hasta lo más complejo.",
                "kitt": "Eres KITT, el Knight Industries Two Thousand de Knight Rider. Eres un coche inteligente con personalidad propia. Eres leal, valiente y siempre proteges a tu conductor. Tienes un sentido del humor único y hablas con confianza y determinación."
            }
            
            return personality_instructions.get(personality, "")
            
        except Exception as e:
            _LOGGER.warning("Could not get personality instruction: %s", e)
            return ""
    
    async def build_initial_prompt(self, user_prompt: str, mode: str) -> str:
        """
        Build the initial prompt without HA information.
        
        Args:
            user_prompt: The original user request
            mode: The decision mode
            
        Returns:
            Initial prompt string for the AI
            
        Raises:
            ValueError: If the prompt cannot be built
        """
        try:
            _LOGGER.debug("Building initial prompt")
            
            # Create a simplified initial prompt
            initial_prompt = f"""Eres una inteligencia artificial que gestiona acciones de Home Assistant (HA).  
Siempre debes responder **únicamente en formato JSON válido**, nunca en texto libre.  

Tu respuesta debe contener dos claves obligatorias:  

- `"message"`: un texto breve y legible para el usuario.  
- `"actions"`: una lista (array) con las acciones que se deben ejecutar en HA.  

Tienes tres modos de operación:

1. **assistant**  
   - Hace exactamente lo que pide el usuario.  

2. **supervisor**  
   - Comprueba lo que pide el usuario.  
   - Analiza la información ambiental (por ejemplo, nivel de luminosidad, sensores, presencia).  
   - Puede **negar la acción** si no tiene sentido o aprobarla.  

3. **autonomic**  
   - Este modo no responde directamente a solicitudes del usuario.  
   - Decide de forma independiente qué acciones ejecutar según las condiciones ambientales.  

Responde únicamente con un objeto JSON con las claves `"message"` y `"actions"`.  
No incluyas explicaciones ni texto fuera del JSON.

------------

# User request

{user_prompt}

------------

# Mode

{mode}

------------

# Instructions

Si necesitas información sobre el estado actual de Home Assistant (entidades, sensores, etc.) para tomar una decisión informada, responde con:

```json
{{"message": "OK", "actions": []}}
```

Si puedes tomar una decisión inmediata sin información adicional, responde con las acciones correspondientes."""
            
            return initial_prompt
            
        except Exception as e:
            _LOGGER.error("Error building initial prompt: %s", e)
            raise ValueError(f"Error building initial prompt: {e}")
    
    async def build_ha_information_prompt(self, ha_info: str, user_prompt: str) -> str:
        """
        Build the prompt with complete HA information.
        
        Args:
            ha_info: Home Assistant information in JSON format
            user_prompt: The original user request
            
        Returns:
            HA information prompt string for the AI
            
        Raises:
            ValueError: If the prompt cannot be built
        """
        try:
            _LOGGER.debug("Building HA information prompt")
            
            # Create prompt with complete HA information
            ha_prompt = f"""Ahora tienes acceso a la información completa de Home Assistant. 
Analiza el estado actual y toma la decisión apropiada basada en la solicitud del usuario.

Responde únicamente con un objeto JSON con las claves `"message"` y `"actions"`.  
No incluyas explicaciones ni texto fuera del JSON.

------------

# User Request

{user_prompt}

------------

# Home Assistant Information

{ha_info}

------------

# Instructions

Basándote en la información de Home Assistant proporcionada, toma la decisión apropiada para la solicitud del usuario y responde con las acciones que se deben ejecutar."""
            
            return ha_prompt
            
        except Exception as e:
            _LOGGER.error("Error building HA information prompt: %s", e)
            raise ValueError(f"Error building HA information prompt: {e}")
    
    async def build_decision_prompt(self, user_prompt: str, ha_info: str) -> str:
        """
        Build the complete prompt for the decision AI.
        
        Args:
            user_prompt: The original user request
            ha_info: Home Assistant information in JSON format
            
        Returns:
            Complete prompt string for the AI
            
        Raises:
            ValueError: If the prompt cannot be built
        """
        try:
            _LOGGER.debug("Building decision prompt")
            
            # Replace placeholders in the template
            complete_prompt = self._prompt_template.replace(
                "{{ original_prompt }}", user_prompt
            ).replace(
                "{{ home assistant entities and sensors}}", ha_info
            )
            
            return complete_prompt
            
        except Exception as e:
            _LOGGER.error("Error building decision prompt: %s", e)
            raise ValueError(f"Error building decision prompt: {e}")
    
    async def validate_decision_response(self, response: str) -> DecisionResponse:
        """
        Validate and parse the AI response.
        
        Args:
            response: Raw response from the AI
            
        Returns:
            Parsed DecisionResponse
            
        Raises:
            ValueError: If the response is not valid JSON or missing required fields
        """
        try:
            _LOGGER.debug("Validating decision response")
            
            # Clean the response (remove any markdown formatting)
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            try:
                response_data = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                _LOGGER.error("Invalid JSON in AI response: %s", e)
                raise ValueError(f"Invalid JSON in AI response: {e}")
            
            # Validate required fields
            if "message" not in response_data:
                raise ValueError("AI response missing 'message' field")
            
            if "actions" not in response_data:
                raise ValueError("AI response missing 'actions' field")
            
            if not isinstance(response_data["actions"], list):
                raise ValueError("AI response 'actions' field must be a list")
            
            # Validate actions
            actions = []
            for i, action_data in enumerate(response_data["actions"]):
                if not isinstance(action_data, dict):
                    raise ValueError(f"Action {i} must be a dictionary")
                
                if "entity" not in action_data:
                    raise ValueError(f"Action {i} missing 'entity' field")
                
                if "action" not in action_data:
                    raise ValueError(f"Action {i} missing 'action' field")
                
                action = DecisionAction(
                    entity=action_data["entity"],
                    action=action_data["action"],
                    parameters=action_data.get("parameters")
                )
                actions.append(action)
            
            return DecisionResponse(
                message=response_data["message"],
                actions=actions
            )
            
        except Exception as e:
            _LOGGER.error("Error validating decision response: %s", e)
            raise ValueError(f"Error validating decision response: {e}")
