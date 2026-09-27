import csv
import os
import time
from collections import deque
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path

from src.config import (
    EVENT_HISTORY_SIZE,
    EVENT_SURGE_THRESHOLD,
    EVENT_SURGE_THRESHOLD_HIGH,
    EVENT_REDUCTION_THRESHOLD,
    EVENT_MIN_COUNT_FOR_SURGE,
    EVENT_MIN_COUNT_FOR_REDUCE,
    EVENT_ZONE_CONGESTION_THRESHOLD,
    EVENT_ZONE_CONGESTION_HIGH,
    EVENT_ZONE_SUSTAIN_FRAMES,
    EVENT_MOTION_SPIKE_THRESHOLD,
    EVENT_MOTION_RATIO,
    EVENT_LOW_ACTIVITY_THRESHOLD,
    EVENT_LOW_SUSTAIN_FRAMES,
    EVENT_COOLDOWN_RISK,
    EVENT_COOLDOWN_SURGE,
    EVENT_COOLDOWN_ZONE,
    EVENT_COOLDOWN_MOVEMENT,
    EVENT_COOLDOWN_LOW_ACTIVITY,
    EVENT_MAX_DISPLAY,
)


class Severity(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class EventType(IntEnum):
    RISK_ESCALATION = 0
    RISK_DEESCALATION = 1
    CROWD_SURGE = 2
    CROWD_REDUCTION = 3
    ZONE_CONGESTION = 4
    MOVEMENT_SPIKE = 5
    LOW_ACTIVITY = 6


_SEVERITY_LABELS = {Severity.LOW: "LOW", Severity.MEDIUM: "MEDIUM", Severity.HIGH: "HIGH"}

_EVENT_TYPE_LABELS = {
    EventType.RISK_ESCALATION: "Risk Escalation",
    EventType.RISK_DEESCALATION: "Risk De-escalation",
    EventType.CROWD_SURGE: "Crowd Surge",
    EventType.CROWD_REDUCTION: "Crowd Reduction",
    EventType.ZONE_CONGESTION: "Zone Congestion",
    EventType.MOVEMENT_SPIKE: "Movement Spike",
    EventType.LOW_ACTIVITY: "Low Activity",
}

_COOLDOWN_MAP = {
    EventType.RISK_ESCALATION: EVENT_COOLDOWN_RISK,
    EventType.RISK_DEESCALATION: EVENT_COOLDOWN_RISK,
    EventType.CROWD_SURGE: EVENT_COOLDOWN_SURGE,
    EventType.CROWD_REDUCTION: EVENT_COOLDOWN_SURGE,
    EventType.ZONE_CONGESTION: EVENT_COOLDOWN_ZONE,
    EventType.MOVEMENT_SPIKE: EVENT_COOLDOWN_MOVEMENT,
    EventType.LOW_ACTIVITY: EVENT_COOLDOWN_LOW_ACTIVITY,
}


@dataclass
class Event:
    timestamp: str
    event_type: EventType
    severity: Severity
    message: str
    zone: tuple = None
    signal_value: float = 0.0
    frame_number: int = 0

    @property
    def type_label(self):
        return _EVENT_TYPE_LABELS.get(self.event_type, "Unknown")

    @property
    def severity_label(self):
        return _SEVERITY_LABELS.get(self.severity, "LOW")

    def __str__(self):
        zone_str = f"  Zone {self.zone}" if self.zone is not None else ""
        return f"[{self.timestamp}] {self.severity_label} — {self.type_label}{zone_str}\n           {self.message}"

    def to_row(self):
        return [
            self.timestamp,
            _EVENT_TYPE_LABELS.get(self.event_type, "Unknown"),
            _SEVERITY_LABELS.get(self.severity, "LOW"),
            str(self.zone) if self.zone is not None else "",
            f"{self.signal_value:.2f}",
            str(self.frame_number),
            self.message,
        ]


class EventEngine:
    def __init__(self, log_events=False, log_dir="logs"):
        self._history = deque(maxlen=EVENT_HISTORY_SIZE)
        self._last_fired = {}
        self._prev_risk_level = None
        self._prev_motion = 0.0
        self._motion_window = deque(maxlen=15)
        self._zone_sustain = {}
        self._low_activity_count = 0
        self._frame_count = 0
        self._log_events = log_events
        self._log_dir = log_dir
        self._log_writer = None
        self._log_file = None

    def reset(self):
        self._history.clear()
        self._last_fired.clear()
        self._prev_risk_level = None
        self._prev_motion = 0.0
        self._motion_window.clear()
        self._zone_sustain.clear()
        self._low_activity_count = 0
        self._frame_count = 0
        if self._log_file:
            self._log_file.close()
            self._log_file = None
            self._log_writer = None

    def evaluate(self, risk_result, tracker, motion_variance,
                 tracking_enabled=True):
        self._frame_count += 1
        events = []

        if self._prev_risk_level is not None and risk_result is not None:
            events.extend(self._check_risk_transitions(risk_result))

        if tracking_enabled and tracker is not None:
            events.extend(self._check_crowd_surge(tracker))
            events.extend(self._check_crowd_reduction(tracker))
            events.extend(self._check_zone_congestion(risk_result))

        events.extend(self._check_movement_spike(motion_variance))
        events.extend(self._check_low_activity(tracker, tracking_enabled))

        for event in events:
            self._history.append(event)
            if self._log_events:
                self._log_event(event)

        self._update_state(risk_result, motion_variance)
        return events

    def _check_risk_transitions(self, risk_result):
        events = []
        current_level = risk_result.risk_level
        prev_level = self._prev_risk_level

        if current_level == prev_level:
            return events

        _LEVEL_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        cur_val = _LEVEL_ORDER.get(current_level, 0)
        prev_val = _LEVEL_ORDER.get(prev_level, 0)

        key = (EventType.RISK_ESCALATION, None)
        key_de = (EventType.RISK_DEESCALATION, None)

        if cur_val > prev_val:
            severity = Severity.HIGH if current_level == "HIGH" else Severity.MEDIUM
            if self._can_fire(key):
                msg = (f"Risk level changed from {prev_level} to {current_level} "
                       f"(score: {risk_result.smoothed_score:.1f})")
                events.append(self._make_event(
                    EventType.RISK_ESCALATION, severity, msg,
                    signal_value=risk_result.smoothed_score,
                ))
                self._last_fired[key] = self._frame_count
        elif cur_val < prev_val:
            if self._can_fire(key_de):
                msg = (f"Risk level decreased from {prev_level} to {current_level} "
                       f"(score: {risk_result.smoothed_score:.1f})")
                events.append(self._make_event(
                    EventType.RISK_DEESCALATION, Severity.LOW, msg,
                    signal_value=risk_result.smoothed_score,
                ))
                self._last_fired[key_de] = self._frame_count

        return events

    def _check_crowd_surge(self, tracker):
        events = []
        if tracker.current_count < EVENT_MIN_COUNT_FOR_SURGE:
            return events

        growth_rate = tracker.get_growth_rate(window=15)
        key = (EventType.CROWD_SURGE, None)

        if growth_rate > EVENT_SURGE_THRESHOLD and self._can_fire(key):
            severity = (Severity.HIGH
                        if growth_rate > EVENT_SURGE_THRESHOLD_HIGH
                        else Severity.MEDIUM)
            msg = (f"Crowd growing at {growth_rate:.1f} persons/sec "
                   f"(current: {tracker.current_count})")
            events.append(self._make_event(
                EventType.CROWD_SURGE, severity, msg,
                signal_value=growth_rate,
            ))
            self._last_fired[key] = self._frame_count

        return events

    def _check_crowd_reduction(self, tracker):
        events = []
        if tracker.current_count < EVENT_MIN_COUNT_FOR_REDUCE:
            return events

        growth_rate = tracker.get_growth_rate(window=15)
        key = (EventType.CROWD_REDUCTION, None)

        if growth_rate < EVENT_REDUCTION_THRESHOLD and self._can_fire(key):
            msg = (f"Crowd shrinking at {abs(growth_rate):.1f} persons/sec "
                   f"(current: {tracker.current_count})")
            events.append(self._make_event(
                EventType.CROWD_REDUCTION, Severity.LOW, msg,
                signal_value=growth_rate,
            ))
            self._last_fired[key] = self._frame_count

        return events

    def _check_zone_congestion(self, risk_result):
        events = []
        if risk_result is None:
            return events

        active_zones = set()
        for (row, col), zr in risk_result.zone_risks.items():
            zone_key = (row, col)
            if zr > EVENT_ZONE_CONGESTION_THRESHOLD:
                self._zone_sustain[zone_key] = self._zone_sustain.get(zone_key, 0) + 1
                active_zones.add(zone_key)
            else:
                self._zone_sustain[zone_key] = 0

        for zone_key, count in self._zone_sustain.items():
            if count >= EVENT_ZONE_SUSTAIN_FRAMES:
                event_key = (EventType.ZONE_CONGESTION, zone_key)
                if self._can_fire(event_key):
                    zr = risk_result.zone_risks.get(zone_key, 0.0)
                    severity = (Severity.HIGH
                                if zr > EVENT_ZONE_CONGESTION_HIGH
                                else Severity.MEDIUM)
                    msg = (f"Zone {zone_key} sustained high density "
                           f"(risk: {zr:.1f})")
                    events.append(self._make_event(
                        EventType.ZONE_CONGESTION, severity, msg,
                        zone=zone_key, signal_value=zr,
                    ))
                    self._last_fired[event_key] = self._frame_count

        return events

    def _check_movement_spike(self, motion_variance):
        events = []
        self._motion_window.append(motion_variance)

        if len(self._motion_window) < 5:
            return events

        avg_motion = sum(self._motion_window) / len(self._motion_window)
        key = (EventType.MOVEMENT_SPIKE, None)

        if (motion_variance > EVENT_MOTION_SPIKE_THRESHOLD
                and avg_motion > 0
                and motion_variance > avg_motion * EVENT_MOTION_RATIO
                and self._can_fire(key)):
            msg = (f"High scene motion detected "
                   f"(variance: {motion_variance:.4f}, avg: {avg_motion:.4f})")
            events.append(self._make_event(
                EventType.MOVEMENT_SPIKE, Severity.MEDIUM, msg,
                signal_value=motion_variance,
            ))
            self._last_fired[key] = self._frame_count

        return events

    def _check_low_activity(self, tracker, tracking_enabled):
        events = []
        if not tracking_enabled or tracker is None:
            return events

        if tracker.current_count < EVENT_LOW_ACTIVITY_THRESHOLD:
            self._low_activity_count += 1
        else:
            self._low_activity_count = 0

        key = (EventType.LOW_ACTIVITY, None)
        if (self._low_activity_count >= EVENT_LOW_SUSTAIN_FRAMES
                and self._can_fire(key)):
            msg = (f"Very few people detected "
                   f"(count: {tracker.current_count})")
            events.append(self._make_event(
                EventType.LOW_ACTIVITY, Severity.LOW, msg,
                signal_value=float(tracker.current_count),
            ))
            self._last_fired[key] = self._frame_count
            self._low_activity_count = 0

        return events

    def _can_fire(self, key):
        last = self._last_fired.get(key)
        if last is None:
            return True
        cooldown = _COOLDOWN_MAP.get(key[0], 60)
        return (self._frame_count - last) >= cooldown

    def _make_event(self, event_type, severity, message, zone=None,
                    signal_value=0.0):
        ts = time.strftime("%H:%M:%S")
        return Event(
            timestamp=ts,
            event_type=event_type,
            severity=severity,
            message=message,
            zone=zone,
            signal_value=signal_value,
            frame_number=self._frame_count,
        )

    def _update_state(self, risk_result, motion_variance):
        if risk_result is not None:
            self._prev_risk_level = risk_result.risk_level
        self._prev_motion = motion_variance

    @property
    def history(self):
        return list(self._history)

    @property
    def recent_events(self):
        n = min(EVENT_MAX_DISPLAY, len(self._history))
        return list(self._history)[-n:]

    def _init_log(self):
        os.makedirs(self._log_dir, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self._log_dir, f"events_{ts}.csv")
        self._log_file = open(filepath, "w", newline="")
        self._log_writer = csv.writer(self._log_file)
        self._log_writer.writerow([
            "timestamp", "event_type", "severity", "zone",
            "signal_value", "frame", "message",
        ])

    def _log_event(self, event):
        if self._log_writer is None:
            self._init_log()
        self._log_writer.writerow(event.to_row())
        self._log_file.flush()

    def close_log(self):
        if self._log_file:
            self._log_file.close()
            self._log_file = None
            self._log_writer = None
