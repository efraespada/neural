"""AI Data Transfer Objects."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class AIChatDTO:
    """AI Chat DTO."""
    message: str
    response: str
    model: str
    timestamp: datetime
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None


@dataclass
class AIStatusDTO:
    """AI Status DTO."""
    status: str
    url: str
    model: str
    available_models: List[str]
    error: Optional[str] = None
    last_updated: Optional[datetime] = None


@dataclass
class AIModelDTO:
    """AI Model DTO."""
    name: str
    size: Optional[str] = None
    modified_at: Optional[datetime] = None
    digest: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
