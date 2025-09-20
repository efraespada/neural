"""
Modelos de dominio para configuración.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class LLMConfig:
    """Configuración del modelo de lenguaje."""
    ip: str
    model: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "ip": self.ip,
            "model": self.model
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMConfig':
        """Crear desde diccionario."""
        return cls(
            ip=data.get("ip", ""),
            model=data.get("model", "")
        )


@dataclass
class AppConfig:
    """Configuración principal de la aplicación."""
    mode: str
    llm: LLMConfig
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            "mode": self.mode,
            "llm": self.llm.to_dict(),
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
            mode=data.get("mode", "supervisor"),
            llm=LLMConfig.from_dict(data.get("llm", {})),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def update_llm(self, ip: str, model: str) -> None:
        """Actualizar configuración LLM."""
        self.llm = LLMConfig(ip=ip, model=model)
        self.updated_at = datetime.now()
    
    def update_mode(self, mode: str) -> None:
        """Actualizar modo de la aplicación."""
        self.mode = mode
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
