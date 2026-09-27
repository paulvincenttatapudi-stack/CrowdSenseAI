import numpy as np
import pytest

from src.display import draw_event_hud, draw_grid, draw_risk_hud
from src.risk_engine import RiskResult
from src.event_engine import Event, EventType, Severity


def blank_frame(h=240, w=320):
    return np.zeros((h, w, 3), dtype=np.uint8)


class TestDrawEventHud:
    def test_empty_events_no_modification(self):
        frame = blank_frame()
        original = frame.copy()
        draw_event_hud(frame, [])
        assert np.array_equal(frame, original)

    def test_single_event_draws(self):
        frame = blank_frame()
        events = [
            Event(timestamp="10:00:00", event_type=EventType.CROWD_SURGE,
                  severity=Severity.MEDIUM, message="test",
                  signal_value=5.0, frame_number=10),
        ]
        draw_event_hud(frame, events)
        assert not np.array_equal(frame, np.zeros_like(frame))

    def test_multiple_events_draw_right_side(self):
        frame = blank_frame(240, 320)
        events = []
        for i in range(3):
            events.append(Event(
                timestamp="10:00:0%d" % i,
                event_type=EventType.ZONE_CONGESTION,
                severity=Severity.HIGH if i == 0 else Severity.MEDIUM,
                message="zone congestion",
                zone=(0, i % 2),
            ))
        draw_event_hud(frame, events)
        assert np.any(frame[:, :, 2] > 0)

    def test_severity_high_uses_red_channel(self):
        frame = blank_frame()
        events = [
            Event(timestamp="10:00:00", event_type=EventType.RISK_ESCALATION,
                  severity=Severity.HIGH, message="up"),
        ]
        draw_event_hud(frame, events)
        assert np.any(frame[:, :, 2] > 0)


class TestDrawGrid:
    def test_grid_draws(self):
        frame = blank_frame()
        persons = [{"track_id": 1, "cx": 10, "cy": 10}]
        grid = [[1, 0], [0, 0]]
        draw_grid(frame, persons, grid, show_ids=True)
        assert np.any(frame > 0)


class TestDrawRiskHud:
    def test_risk_hud_draws(self):
        frame = blank_frame()
        result = RiskResult(
            composite_score=40.0, smoothed_score=42.0, risk_level="MEDIUM",
            signal_values={}, top_contributors=[],
            zone_risks={(0, 0): 10.0, (0, 1): 20.0, (1, 0): 30.0, (1, 1): 40.0},
            critical_zone=(1, 1),
        )
        draw_risk_hud(frame, result, 30.0)
        assert np.any(frame > 0)