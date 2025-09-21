"""AI domain models."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class AIStatus:
    """AI service status."""
    status: str
    url: str
    model: str
    available_models: List[str]
    error: Optional[str] = None
    last_updated: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "url": self.url,
            "model": self.model,
            "available_models": self.available_models,
            "error": self.error,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIStatus":
        """Create from dictionary."""
        return cls(
            status=data.get("status", "unknown"),
            url=data.get("url", ""),
            model=data.get("model", ""),
            available_models=data.get("available_models", []),
            error=data.get("error"),
            last_updated=datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else None,
        )


@dataclass
class AIChat:
    """AI chat conversation."""
    message: str
    response: str
    model: str
    timestamp: datetime
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message": self.message,
            "response": self.response,
            "model": self.model,
            "timestamp": self.timestamp.isoformat(),
            "tokens_used": self.tokens_used,
            "response_time": self.response_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIChat":
        """Create from dictionary."""
        return cls(
            message=data.get("message", ""),
            response=data.get("response", ""),
            model=data.get("model", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(),
            tokens_used=data.get("tokens_used"),
            response_time=data.get("response_time"),
        )


@dataclass
class AIResponse:
    """AI response."""
    message: str
    response: str
    model: str
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message": self.message,
            "response": self.response,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "response_time": self.response_time,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIResponse":
        """Create from dictionary."""
        return cls(
            message=data.get("message", ""),
            response=data.get("response", ""),
            model=data.get("model", ""),
            tokens_used=data.get("tokens_used"),
            response_time=data.get("response_time"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
        )


@dataclass
class AIModel:
    """AI model information."""
    name: str
    size: Optional[int] = None
    modified_at: Optional[datetime] = None
    digest: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "size": self.size,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "digest": self.digest,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIModel":
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            size=data.get("size"),
            modified_at=datetime.fromisoformat(data["modified_at"]) if data.get("modified_at") else None,
            digest=data.get("digest"),
        )
