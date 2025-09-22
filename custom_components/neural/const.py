"""Constants for Neural AI integration."""

from homeassistant.const import Platform

DOMAIN = "neural"
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.STT, Platform.CONVERSATION]

# Configuration keys
CONF_HA_TOKEN = "ha_token"
CONF_HA_URL = "ha_url"
CONF_AI_URL = "ai_url"
CONF_AI_MODEL = "ai_model"
CONF_AI_API_KEY = "ai_api_key"
CONF_STT_MODEL = "stt_model"
CONF_STT_API_KEY = "stt_api_key"
CONF_WORK_MODE = "work_mode"
CONF_PERSONALITY = "personality"
CONF_MICROPHONE_ENABLED = "microphone_enabled"
CONF_VOICE_LANGUAGE = "voice_language"
CONF_VOICE_TIMEOUT = "voice_timeout"

# AI Models
AI_MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/gpt-4-turbo",
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3-haiku",
    "google/gemini-pro-1.5",
    "meta-llama/llama-3.1-8b-instruct",
    "meta-llama/llama-3.1-70b-instruct",
]

STT_MODELS = [
    "whisper-1",  # OpenAI API model (recommended)
    "whisper-2",  # OpenAI API model (if available)
]

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

# Intent constants
INTENT_NEURAL_COMMAND = "NeuralCommand"
