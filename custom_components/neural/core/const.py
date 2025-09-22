"""Constants for the Neural AI integration."""

import logging

DOMAIN = "neural"

LOGGER = logging.getLogger(__package__)

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

# Default values
DEFAULT_WORK_MODE = WORK_MODE_ASSISTANT
DEFAULT_PERSONALITY = PERSONALITY_HAL9000
DEFAULT_STT_MODEL = "whisper-1"
DEFAULT_AI_MODEL = "openai/gpt-oss-20b"
DEFAULT_AI_URL = "https://openrouter.ai/api/v1"
DEFAULT_MICROPHONE_ENABLED = True
DEFAULT_VOICE_LANGUAGE = "es-ES"
DEFAULT_VOICE_TIMEOUT = 5
DEFAULT_HA_URL = "http://homeassistant.local:8123"  # Home Assistant default
DEFAULT_SCAN_INTERVAL = 10  # minutes
DEFAULT_CONFIG_FILE_PATH = "config.json"

SUPPORTED_LANGUAGES = [
    "es",  # Spanish
    "en",  # English
    "fr",  # French
    "de",  # German
    "it",  # Italian
    "pt",  # Portuguese
    "ru",  # Russian
    "ja",  # Japanese
    "ko",  # Korean
    "zh",  # Chinese
    "ar",  # Arabic
    "hi",  # Hindi
    "nl",  # Dutch
    "sv",  # Swedish
    "no",  # Norwegian
    "da",  # Danish
    "fi",  # Finnish
    "pl",  # Polish
    "tr",  # Turkish
    "he",  # Hebrew
]
