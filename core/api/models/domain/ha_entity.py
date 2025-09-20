"""Home Assistant domain models."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class HAEntity:
    """Home Assistant entity representation."""
    entity_id: str
    state: str
    attributes: Dict[str, Any]
    last_changed: datetime
    last_updated: datetime
    context: Dict[str, Any]
    domain: str
    object_id: str
    friendly_name: Optional[str] = None
    unit_of_measurement: Optional[str] = None
    device_class: Optional[str] = None
    icon: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "state": self.state,
            "attributes": self.attributes,
            "last_changed": self.last_changed.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "context": self.context,
            "domain": self.domain,
            "object_id": self.object_id,
            "friendly_name": self.friendly_name,
            "unit_of_measurement": self.unit_of_measurement,
            "device_class": self.device_class,
            "icon": self.icon,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HAEntity":
        """Create from dictionary."""
        return cls(
            entity_id=data.get("entity_id", ""),
            state=data.get("state", ""),
            attributes=data.get("attributes", {}),
            last_changed=datetime.fromisoformat(data["last_changed"].replace("Z", "+00:00")) if data.get("last_changed") else datetime.now(),
            last_updated=datetime.fromisoformat(data["last_updated"].replace("Z", "+00:00")) if data.get("last_updated") else datetime.now(),
            context=data.get("context", {}),
            domain=data.get("entity_id", "").split(".")[0] if data.get("entity_id") else "",
            object_id=data.get("entity_id", "").split(".")[1] if data.get("entity_id") else "",
            friendly_name=data.get("attributes", {}).get("friendly_name"),
            unit_of_measurement=data.get("attributes", {}).get("unit_of_measurement"),
            device_class=data.get("attributes", {}).get("device_class"),
            icon=data.get("attributes", {}).get("icon"),
        )


@dataclass
class HASensor:
    """Home Assistant sensor entity."""
    entity_id: str
    state: str
    unit_of_measurement: Optional[str] = None
    device_class: Optional[str] = None
    friendly_name: Optional[str] = None
    last_updated: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "state": self.state,
            "unit_of_measurement": self.unit_of_measurement,
            "device_class": self.device_class,
            "friendly_name": self.friendly_name,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HASensor":
        """Create from dictionary."""
        return cls(
            entity_id=data.get("entity_id", ""),
            state=data.get("state", ""),
            unit_of_measurement=data.get("unit_of_measurement"),
            device_class=data.get("device_class"),
            friendly_name=data.get("friendly_name"),
            last_updated=datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else None,
        )


@dataclass
class HASummary:
    """Home Assistant entities summary."""
    total_entities: int
    entities_by_domain: Dict[str, int]
    entities_by_state: Dict[str, int]
    last_updated: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_entities": self.total_entities,
            "entities_by_domain": self.entities_by_domain,
            "entities_by_state": self.entities_by_state,
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HASummary":
        """Create from dictionary."""
        return cls(
            total_entities=data.get("total_entities", 0),
            entities_by_domain=data.get("entities_by_domain", {}),
            entities_by_state=data.get("entities_by_state", {}),
            last_updated=datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else datetime.now(),
        )


@dataclass
class HAEntityState:
    """Home Assistant entity state summary."""
    entity_id: str
    state: str
    friendly_name: str
    domain: str
    last_updated: datetime
    unit_of_measurement: Optional[str] = None
    device_class: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "state": self.state,
            "friendly_name": self.friendly_name,
            "domain": self.domain,
            "last_updated": self.last_updated.isoformat(),
            "unit_of_measurement": self.unit_of_measurement,
            "device_class": self.device_class,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HAEntityState":
        """Create from dictionary."""
        return cls(
            entity_id=data.get("entity_id", ""),
            state=data.get("state", ""),
            friendly_name=data.get("friendly_name", ""),
            domain=data.get("domain", ""),
            last_updated=datetime.fromisoformat(data["last_updated"].replace("Z", "+00:00")) if data.get("last_updated") else datetime.now(),
            unit_of_measurement=data.get("unit_of_measurement"),
            device_class=data.get("device_class"),
        )


@dataclass
class HAEntitySummary:
    """Home Assistant entities summary."""
    total_entities: int
    entities_by_domain: Dict[str, int]
    entities_by_state: Dict[str, int]
    last_updated: datetime
    entities: List[HAEntityState]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_entities": self.total_entities,
            "entities_by_domain": self.entities_by_domain,
            "entities_by_state": self.entities_by_state,
            "last_updated": self.last_updated.isoformat(),
            "entities": [entity.to_dict() for entity in self.entities],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HAEntitySummary":
        """Create from dictionary."""
        return cls(
            total_entities=data.get("total_entities", 0),
            entities_by_domain=data.get("entities_by_domain", {}),
            entities_by_state=data.get("entities_by_state", {}),
            last_updated=datetime.fromisoformat(data["last_updated"].replace("Z", "+00:00")) if data.get("last_updated") else datetime.now(),
            entities=[HAEntityState.from_dict(entity_data) for entity_data in data.get("entities", [])],
        )


@dataclass
class HAConfig:
    """Home Assistant configuration."""
    version: str
    location_name: str
    time_zone: str
    unit_system: Dict[str, str]
    components: List[str]
    config_dir: str
    whitelist_external_dirs: List[str]
    allowlist_external_dirs: List[str]
    allowlist_external_urls: List[str]
    version_info: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "location_name": self.location_name,
            "time_zone": self.time_zone,
            "unit_system": self.unit_system,
            "components": self.components,
            "config_dir": self.config_dir,
            "whitelist_external_dirs": self.whitelist_external_dirs,
            "allowlist_external_dirs": self.allowlist_external_dirs,
            "allowlist_external_urls": self.allowlist_external_urls,
            "version_info": self.version_info,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HAConfig":
        """Create from dictionary."""
        return cls(
            version=data.get("version", ""),
            location_name=data.get("location_name", ""),
            time_zone=data.get("time_zone", ""),
            unit_system=data.get("unit_system", {}),
            components=data.get("components", []),
            config_dir=data.get("config_dir", ""),
            whitelist_external_dirs=data.get("whitelist_external_dirs", []),
            allowlist_external_dirs=data.get("allowlist_external_dirs", []),
            allowlist_external_urls=data.get("allowlist_external_urls", []),
            version_info=data.get("version_info", {}),
        )
