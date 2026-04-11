from __future__ import annotations

import json
from pathlib import Path

from .models import CameraEvent, Incident, ReviewDecision, ReviewRequest


class EventFilter:
    """Cheap trigger logic that decides whether a scene deserves deeper review."""

    def __init__(
        self,
        *,
        min_motion_score: float = 0.2,
        stationary_threshold_seconds: int = 20,
        unattended_distance_m: float = 2.5,
    ) -> None:
        self.min_motion_score = min_motion_score
        self.stationary_threshold_seconds = stationary_threshold_seconds
        self.unattended_distance_m = unattended_distance_m

    def evaluate(self, event: CameraEvent) -> list[str]:
        reasons: list[str] = []

        if not event.roi_match:
            return reasons

        if event.motion_score >= self.min_motion_score:
            reasons.append("motion_in_roi")

        if event.is_new_object:
            reasons.append("new_object_detected")

        if event.dropped_from_hand:
            reasons.append("drop_pattern_detected")

        if event.stationary_seconds >= self.stationary_threshold_seconds:
            reasons.append("stationary_object_threshold_exceeded")

        if event.person_left_scene and event.stationary_seconds >= self.stationary_threshold_seconds:
            reasons.append("person_left_object_behind")

        if (
            event.person_distance_m is not None
            and event.person_distance_m >= self.unattended_distance_m
            and event.stationary_seconds >= self.stationary_threshold_seconds
        ):
            reasons.append("person_object_separation_detected")

        if event.vehicle_recently_present and event.is_new_object:
            reasons.append("possible_vehicle_dumping")

        return reasons


class GemmaReviewAdapter:
    """Offline review layer shaped like a future multimodal prompt handoff."""

    def build_request(self, event: CameraEvent, trigger_reasons: list[str]) -> ReviewRequest:
        prompt = (
            "You are reviewing a CCTV event for public-space sanitation and safety.\n"
            f"Camera: {event.camera_id}\n"
            f"Zone: {event.zone}\n"
            f"Timestamp: {event.timestamp}\n"
            f"Object: {event.object_label} ({event.object_size})\n"
            f"Signals: {', '.join(trigger_reasons)}\n"
            f"Context: person_present={event.person_present}, "
            f"person_distance_m={event.person_distance_m}, "
            f"person_left_scene={event.person_left_scene}, "
            f"stationary_seconds={event.stationary_seconds}, "
            f"dropped_from_hand={event.dropped_from_hand}, "
            f"vehicle_recently_present={event.vehicle_recently_present}\n"
            f"Scene notes: {event.notes}\n"
            "Classify the event as littering, unattended_item, illegal_dumping, or non_issue. "
            "Return a concise operational rationale and recommended action."
        )
        return ReviewRequest(event=event, trigger_reasons=trigger_reasons, prompt=prompt)

    def review(self, request: ReviewRequest) -> ReviewDecision:
        event = request.event
        reasons = set(request.trigger_reasons)

        if "possible_vehicle_dumping" in reasons:
            return ReviewDecision(
                label="illegal_dumping",
                confidence=0.93,
                severity="high",
                rationale="A new object appeared after a vehicle-related event and remained in the monitored zone.",
                recommended_action="Dispatch site staff and retain clip for audit review.",
            )

        unattended_object = (
            "person_left_object_behind" in reasons
            or "person_object_separation_detected" in reasons
        )
        likely_litter = "drop_pattern_detected" in reasons and event.object_label in {
            "bottle",
            "cup",
            "wrapper",
            "packet",
            "tissue",
        }

        if unattended_object and event.object_label in {"bag", "backpack", "box", "suitcase"}:
            return ReviewDecision(
                label="unattended_item",
                confidence=0.9,
                severity="high",
                rationale="The item remained stationary after the nearby person left or moved beyond the safety distance.",
                recommended_action="Alert security staff for unattended-object verification.",
            )

        if likely_litter:
            return ReviewDecision(
                label="littering",
                confidence=0.88,
                severity="medium",
                rationale="A small discard-like object appeared through a drop pattern and stayed in the cleanup zone.",
                recommended_action="Queue housekeeping alert and log repeat hotspot activity.",
            )

        if event.stationary_seconds < self._non_issue_seconds(event.object_size):
            return ReviewDecision(
                label="non_issue",
                confidence=0.72,
                severity="low",
                rationale="The object has not persisted long enough to justify intervention.",
                recommended_action="Continue passive monitoring without staff notification.",
            )

        return ReviewDecision(
            label="non_issue",
            confidence=0.58,
            severity="low",
            rationale="The trigger conditions were met, but the scene lacks strong evidence of littering or abandonment.",
            recommended_action="Keep in incident queue for manual spot review if needed.",
        )

    @staticmethod
    def _non_issue_seconds(object_size: str) -> int:
        return 40 if object_size == "large" else 25


class LitterGuardPipeline:
    def __init__(self) -> None:
        self.filter = EventFilter()
        self.reviewer = GemmaReviewAdapter()

    def process_events(self, events: list[CameraEvent]) -> list[Incident]:
        incidents: list[Incident] = []

        for index, event in enumerate(events, start=1):
            trigger_reasons = self.filter.evaluate(event)
            if not trigger_reasons:
                continue

            request = self.reviewer.build_request(event, trigger_reasons)
            decision = self.reviewer.review(request)
            if decision.label == "non_issue" and decision.confidence < 0.65:
                continue

            incidents.append(
                Incident(
                    incident_id=f"INC-{index:04d}",
                    camera_id=event.camera_id,
                    zone=event.zone,
                    timestamp=event.timestamp,
                    label=decision.label,
                    confidence=decision.confidence,
                    severity=decision.severity,
                    trigger_reasons=trigger_reasons,
                    rationale=decision.rationale,
                    recommended_action=decision.recommended_action,
                    object_label=event.object_label,
                    notes=event.notes,
                )
            )

        return incidents


def load_events(path: Path) -> list[CameraEvent]:
    raw_events = json.loads(path.read_text())
    return [CameraEvent.from_dict(item) for item in raw_events]


def save_incidents(path: Path, incidents: list[Incident]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([incident.to_dict() for incident in incidents], indent=2))


def build_operator_report(incidents: list[Incident]) -> str:
    if not incidents:
        return "# Operator Report\n\nNo incidents were escalated."

    lines = [
        "# Operator Report",
        "",
        f"Total escalated incidents: {len(incidents)}",
        "",
    ]
    for incident in incidents:
        lines.extend(
            [
                f"## {incident.incident_id} | {incident.label}",
                f"- Camera: {incident.camera_id}",
                f"- Zone: {incident.zone}",
                f"- Time: {incident.timestamp}",
                f"- Confidence: {incident.confidence:.2f}",
                f"- Severity: {incident.severity}",
                f"- Object: {incident.object_label}",
                f"- Trigger reasons: {', '.join(incident.trigger_reasons)}",
                f"- Rationale: {incident.rationale}",
                f"- Recommended action: {incident.recommended_action}",
                "",
            ]
        )
    return "\n".join(lines)


def build_dashboard_js(incidents: list[Incident]) -> str:
    payload = [incident.to_dict() for incident in incidents]
    return f"window.LITTERGUARD_INCIDENTS = {json.dumps(payload, indent=2)};\n"
