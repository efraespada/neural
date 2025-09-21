"""Constants for the Neural AI integration."""

import logging

DOMAIN = "neural"

LOGGER = logging.getLogger(__package__)

# Configuration keys
CONF_SCAN_INTERVAL = "scan_interval"
CONF_AI_URL = "ai_url"
CONF_AI_MODEL = "ai_model"
CONF_HA_URL = "ha_url"
CONF_HA_TOKEN = "ha_token"

# Default values
DEFAULT_SCAN_INTERVAL = 10  # minutes
DEFAULT_AI_URL = "http://localhost:11434"  # Ollama default
DEFAULT_AI_MODEL = "llama3.2"
DEFAULT_HA_URL = "http://homeassistant.local:8123"  # Home Assistant default

# Entity configuration
ENTITY_NAMES = {
    "ai_chat": "Neural AI Chat",
    "ai_status": "AI Status",
    "ai_model": "AI Model",
    "ai_last_response": "Last AI Response",
    "ai_response_time": "AI Response Time",
    "ai_tokens_used": "AI Tokens Used",
}

# Device configuration
DEVICE_INFO = {
    "manufacturer": "Neural",
    "model": "AI Assistant",
    "sw_version": "1.0.0",
    "configuration_url": "https://github.com/efraespada/neural",
}

# API endpoints - removed Verisure specific endpoints
