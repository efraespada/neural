"""Home Assistant Data Transfer Objects."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class HAEntityDTO:
    """Home Assistant Entity DTO."""
    entity_id: str
    state: str
    attributes: Dict[str, Any]
    last_changed: datetime
    last_updated: datetime
    context: Dict[str, Any]
    domain: str
    friendly_name: Optional[str] = None
    unit_of_measurement: Optional[str] = None
    device_class: Optional[str] = None
    icon: Optional[str] = None


@dataclass
class HASensorDTO:
    """Home Assistant Sensor DTO."""
    entity_id: str
    state: str
    last_updated: datetime
    unit_of_measurement: Optional[str] = None
    device_class: Optional[str] = None
    friendly_name: Optional[str] = None


@dataclass
class HASummaryDTO:
    """Home Assistant Summary DTO."""
    total_entities: int
    entities_by_domain: Dict[str, int]
    entities_by_state: Dict[str, int]
    last_updated: datetime
