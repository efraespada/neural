"""Constants for Neural AI integration."""

from homeassistant.const import Platform

DOMAIN = "neural"
PLATFORMS: list[Platform] = [Platform.SENSOR]

# Configuration keys
CONF_HA_TOKEN = "ha_token"
CONF_OPENROUTER_TOKEN = "openrouter_token"
CONF_WORK_MODE = "work_mode"
CONF_PERSONALITY = "personality"
CONF_AI_MODEL = "ai_model"
CONF_MICROPHONE_ENABLED = "microphone_enabled"
CONF_VOICE_LANGUAGE = "voice_language"
CONF_VOICE_TIMEOUT = "voice_timeout"

# Work modes
WORK_MODE_ASSISTANT = "assistant"
WORK_MODE_SUPERVISOR = "supervisor"
WORK_MODE_AUTONOMIC = "autonomic"

WORK_MODES = [
    WORK_MODE_ASSISTANT,
    WORK_MODE_SUPERVISOR,
    WORK_MODE_AUTONOMIC,
]

# Personalities
PERSONALITY_HAL9000 = "hal9000"
PERSONALITY_JARVIS = "jarvis"
PERSONALITY_KITT = "kitt"
PERSONALITY_MOTHER = "mother"

PERSONALITIES = [
    PERSONALITY_HAL9000,
    PERSONALITY_JARVIS,
    PERSONALITY_KITT,
    PERSONALITY_MOTHER,
]

# AI Models
AI_MODELS = [
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/gpt-4-turbo",
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3-haiku",
    "google/gemini-pro-1.5",
    "meta-llama/llama-3.1-8b-instruct",
    "meta-llama/llama-3.1-70b-instruct",
]

# Default values
DEFAULT_WORK_MODE = WORK_MODE_ASSISTANT
DEFAULT_PERSONALITY = PERSONALITY_JARVIS
DEFAULT_AI_MODEL = "openai/gpt-4o-mini"
DEFAULT_MICROPHONE_ENABLED = True
DEFAULT_VOICE_LANGUAGE = "es-ES"
DEFAULT_VOICE_TIMEOUT = 5

# Service names
SERVICE_SEND_MESSAGE = "send_message"
SERVICE_START_LISTENING = "start_listening"
SERVICE_STOP_LISTENING = "stop_listening"
SERVICE_GET_STATUS = "get_status"
SERVICE_UPDATE_CONFIG = "update_config"

# Entity names
ENTITY_AI_STATUS = "ai_status"
ENTITY_AI_RESPONSE = "ai_response"
ENTITY_MICROPHONE_STATUS = "microphone_status"
