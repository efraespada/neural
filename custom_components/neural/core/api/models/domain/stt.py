"""STT (Speech-to-Text) domain model."""

from dataclasses import dataclass
from typing import Optional

from ....const import DEFAULT_STT_MODEL

@dataclass
class STTConfig:
    """STT configuration model."""
    
    model: str
    api_key: str
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.model:
            raise ValueError("STT model is required")
        
        if not self.api_key:
            raise ValueError("STT API key is required")
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "api_key": self.api_key
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "STTConfig":
        """Create from dictionary."""
        return cls(
            model=data.get("model", DEFAULT_STT_MODEL),
            api_key=data.get("api_key", "")
        )
