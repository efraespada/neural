"""
Modelos de dominio para configuración.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from ....const import DEFAULT_HA_URL
from .stt import STTConfig


@dataclass
class LLMConfig:
    """Configuración del modelo de lenguaje."""
    url: str = "https://openrouter.ai/api/v1"
    model: str = "anthropic/claude-3.5-sonnet"
    api_key: Optional[str] = None
    personality: str = "hal9000"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "url": self.url,
            "model": self.model,
            "api_key": self.api_key,
            "personality": self.personality
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMConfig':
        """Crear desde diccionario."""
        return cls(
            url=data.get("url", data.get("ip", "https://openrouter.ai/api/v1")),  # Backward compatibility
            model=data.get("model", "anthropic/claude-3.5-sonnet"),
            api_key=data.get("api_key"),
            personality=data.get("personality", "assistant")
        )


@dataclass
class HAConfig:
    """Configuración de Home Assistant."""
    url: str = DEFAULT_HA_URL
    token: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "url": self.url,
            "token": self.token
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HAConfig':
        """Crear desde diccionario."""
        return cls(
            url=data.get("url", DEFAULT_HA_URL),
            token=data.get("token")
        )


@dataclass
class AppConfig:
    """Configuración principal de la aplicación."""
    llm: LLMConfig
    ha: HAConfig
    stt: STTConfig
    work_mode: str = "assistant"
    personality: str = "jarvis"
    microphone_enabled: bool = True
    voice_language: str = "es-ES"
    voice_timeout: int = 5
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "llm": self.llm.to_dict(),
            "ha": self.ha.to_dict(),
            "stt": self.stt.to_dict(),
            "work_mode": self.work_mode,
            "personality": self.personality,
            "microphone_enabled": self.microphone_enabled,
            "voice_language": self.voice_language,
            "voice_timeout": self.voice_timeout,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Crear desde diccionario."""
        # Parsear fechas si existen
        created_at = datetime.now()
        updated_at = datetime.now()
        
        if "created_at" in data:
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except ValueError:
                pass
                
        if "updated_at" in data:
            try:
                updated_at = datetime.fromisoformat(data["updated_at"])
            except ValueError:
                pass
        
        return cls(
            llm=LLMConfig.from_dict(data.get("llm", {})),
            ha=HAConfig.from_dict(data.get("ha", {})),
            stt=STTConfig.from_dict(data.get("stt", {})),
            work_mode=data.get("work_mode", "assistant"),
            personality=data.get("personality", "jarvis"),
            microphone_enabled=data.get("microphone_enabled", True),
            voice_language=data.get("voice_language", "es-ES"),
            voice_timeout=data.get("voice_timeout", 5),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def update_llm(self, url: str, model: str, api_key: Optional[str] = None, personality: Optional[str] = None) -> None:
        """Actualizar configuración LLM."""
        # Preserve existing personality if not provided
        current_personality = self.llm.personality if self.llm else "assistant"
        new_personality = personality if personality is not None else current_personality
        
        self.llm = LLMConfig(url=url, model=model, api_key=api_key, personality=new_personality)
        self.updated_at = datetime.now()
    
    def update_work_mode(self, work_mode: str) -> None:
        """Actualizar modo de trabajo de la aplicación."""
        self.work_mode = work_mode
        self.updated_at = datetime.now()


@dataclass
class ConfigValidationResult:
    """Resultado de validación de configuración."""
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    def add_error(self, error: str) -> None:
        """Añadir error de validación."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Añadir advertencia de validación."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }
