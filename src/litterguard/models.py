from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CameraEvent:
    camera_id: str
    zone: str
    timestamp: str
    motion_score: float
    object_id: str
    object_label: str
    object_size: str
    is_new_object: bool
    stationary_seconds: int
    person_present: bool
    person_distance_m: float | None
    person_left_scene: bool
    roi_match: bool
    dropped_from_hand: bool
    vehicle_recently_present: bool = False
    notes: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CameraEvent":
        return cls(**payload)


@dataclass
class ReviewRequest:
    event: CameraEvent
    trigger_reasons: list[str]
    prompt: str


@dataclass
class ReviewDecision:
    label: str
    confidence: float
    rationale: str
    recommended_action: str
    severity: str


@dataclass
class Incident:
    incident_id: str
    camera_id: str
    zone: str
    timestamp: str
    label: str
    confidence: float
    severity: str
    trigger_reasons: list[str] = field(default_factory=list)
    rationale: str = ""
    recommended_action: str = ""
    object_label: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "camera_id": self.camera_id,
            "zone": self.zone,
            "timestamp": self.timestamp,
            "label": self.label,
            "confidence": self.confidence,
            "severity": self.severity,
            "trigger_reasons": self.trigger_reasons,
            "rationale": self.rationale,
            "recommended_action": self.recommended_action,
            "object_label": self.object_label,
            "notes": self.notes,
        }
