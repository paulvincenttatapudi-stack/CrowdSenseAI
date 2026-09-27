import pytest

from src.event_engine import EventEngine, Event, EventType, Severity
from src.risk_engine import RiskResult


class FakeTracker:
    def __init__(self, count, growth=0.0):
        self.current_count = count
        self._growth = growth

    def get_growth_rate(self, window=15):
        return self._growth


def make_result(level="LOW", score=10.0, zone_risks=None):
    return RiskResult(
        risk_level=level,
        smoothed_score=score,
        zone_risks=zone_risks or {(0, 0): 0.0, (0, 1): 0.0, (1, 0): 0.0, (1, 1): 0.0},
    )


class TestEventEngineInit:
    def test_empty_state(self):
        engine = EventEngine()
        assert engine.history == []
        assert engine.recent_events == []
        assert engine._prev_risk_level is None

    def test_reset(self):
        engine = EventEngine()
        engine.evaluate(make_result("MEDIUM"), FakeTracker(10), 0.01, True)
        engine.reset()
        assert engine.history == []
        assert engine._prev_risk_level is None

    def test_history_bounded(self):
        engine = EventEngine()
        for i in range(200):
            level = "MEDIUM" if i % 2 == 0 else "HIGH"
            engine.evaluate(make_result(level), FakeTracker(10, growth=5.0),
                            0.01, True)
        assert len(engine.history) <= 50


class TestRiskTransitionEvents:
    def test_low_to_medium_fires_escalation(self):
        engine = EventEngine()
        engine.evaluate(make_result("LOW"), FakeTracker(10), 0.01, True)
        events = engine.evaluate(make_result("MEDIUM"), FakeTracker(10), 0.01, True)
        types = [e.event_type for e in events]
        assert EventType.RISK_ESCALATION in types
        event = next(e for e in events
                     if e.event_type == EventType.RISK_ESCALATION)
        assert event.severity == Severity.MEDIUM

    def test_medium_to_high_fires_high_severity(self):
        engine = EventEngine()
        engine.evaluate(make_result("MEDIUM"), FakeTracker(10), 0.01, True)
        events = engine.evaluate(make_result("HIGH"), FakeTracker(10), 0.01, True)
        esc = [e for e in events
               if e.event_type == EventType.RISK_ESCALATION]
        assert esc
        assert esc[0].severity == Severity.HIGH

    def test_same_level_no_escalation(self):
        engine = EventEngine()
        engine.evaluate(make_result("MEDIUM"), FakeTracker(10), 0.01, True)
        events = engine.evaluate(make_result("MEDIUM"), FakeTracker(10), 0.01, True)
        assert not [e for e in events
                    if e.event_type in (EventType.RISK_ESCALATION,
                                        EventType.RISK_DEESCALATION)]

    def test_high_to_medium_fires_deescalation(self):
        engine = EventEngine()
        engine.evaluate(make_result("HIGH"), FakeTracker(10), 0.01, True)
        events = engine.evaluate(make_result("MEDIUM"), FakeTracker(10), 0.01, True)
        de = [e for e in events
              if e.event_type == EventType.RISK_DEESCALATION]
        assert de
        assert de[0].severity == Severity.LOW

    def test_medium_to_low_fires_deescalation(self):
        engine = EventEngine()
        engine.evaluate(make_result("MEDIUM"), FakeTracker(10), 0.01, True)
        events = engine.evaluate(make_result("LOW"), FakeTracker(10), 0.01, True)
        assert [e for e in events
                if e.event_type == EventType.RISK_DEESCALATION]


class TestCooldown:
    def test_same_type_suppressed(self):
        engine = EventEngine()
        engine.evaluate(make_result("MEDIUM"), FakeTracker(10), 0.01, True)
        events2 = engine.evaluate(make_result("HIGH"), FakeTracker(10), 0.01, True)
        assert any(e.event_type == EventType.RISK_ESCALATION for e in events2)
        engine._prev_risk_level = "LOW"
        events3 = engine.evaluate(make_result("MEDIUM"), FakeTracker(10), 0.01, True)
        assert not any(e.event_type == EventType.RISK_ESCALATION
                       for e in events3)

    def test_different_type_not_suppressed(self):
        engine = EventEngine()
        engine.evaluate(make_result("HIGH"), FakeTracker(30, growth=10.0),
                        0.05, True)
        events2 = engine.evaluate(make_result("MEDIUM"), FakeTracker(30, growth=10.0),
                                  0.05, True)
        types = {e.event_type for e in events2}
        assert EventType.RISK_DEESCALATION in types


class TestCrowdSurge:
    def test_surge_fires(self):
        engine = EventEngine()
        tracker = FakeTracker(20, growth=5.0)
        events = engine.evaluate(make_result("LOW"), tracker, 0.01, True)
        surge = [e for e in events
                 if e.event_type == EventType.CROWD_SURGE]
        assert surge
        assert surge[0].severity == Severity.MEDIUM

    def test_surge_high_severity(self):
        engine = EventEngine()
        tracker = FakeTracker(20, growth=9.0)
        events = engine.evaluate(make_result("LOW"), tracker, 0.01, True)
        surge = [e for e in events
                 if e.event_type == EventType.CROWD_SURGE]
        assert surge[0].severity == Severity.HIGH

    def test_surge_below_min_count(self):
        engine = EventEngine()
        tracker = FakeTracker(2, growth=5.0)
        events = engine.evaluate(make_result("LOW"), tracker, 0.01, True)
        assert not [e for e in events
                    if e.event_type == EventType.CROWD_SURGE]

    def test_surge_below_threshold(self):
        engine = EventEngine()
        tracker = FakeTracker(20, growth=1.0)
        events = engine.evaluate(make_result("LOW"), tracker, 0.01, True)
        assert not [e for e in events
                    if e.event_type == EventType.CROWD_SURGE]


class TestCrowdReduction:
    def test_reduction_fires(self):
        engine = EventEngine()
        tracker = FakeTracker(20, growth=-5.0)
        events = engine.evaluate(make_result("LOW"), tracker, 0.01, True)
        reduction = [e for e in events
                     if e.event_type == EventType.CROWD_REDUCTION]
        assert reduction
        assert reduction[0].severity == Severity.LOW

    def test_reduction_below_min_count(self):
        engine = EventEngine()
        tracker = FakeTracker(2, growth=-5.0)
        events = engine.evaluate(make_result("LOW"), tracker, 0.01, True)
        assert not [e for e in events
                    if e.event_type == EventType.CROWD_REDUCTION]


class TestZoneCongestion:
    def test_sustained_zone_congestion_fires(self):
        engine = EventEngine()
        zones = {(0, 0): 60.0, (0, 1): 10.0, (1, 0): 10.0, (1, 1): 10.0}
        result = make_result("MEDIUM", zone_risks=zones)
        for _ in range(10):
            engine.evaluate(result, FakeTracker(20), 0.01, True)
        zone_events = [e for e in engine.history
                       if e.event_type == EventType.ZONE_CONGESTION]
        assert zone_events
        assert zone_events[0].zone == (0, 0)

    def test_transient_does_not_fire(self):
        engine = EventEngine()
        zones = {(0, 0): 60.0, (0, 1): 10.0, (1, 0): 10.0, (1, 1): 10.0}
        result = make_result("MEDIUM", zone_risks=zones)
        engine.evaluate(result, FakeTracker(20), 0.01, True)
        clear_zones = {(0, 0): 5.0, (0, 1): 5.0, (1, 0): 5.0, (1, 1): 5.0}
        events = engine.evaluate(make_result("MEDIUM", zone_risks=clear_zones),
                                 FakeTracker(20), 0.01, True)
        assert not [e for e in events
                    if e.event_type == EventType.ZONE_CONGESTION]

    def test_high_zone_severity(self):
        engine = EventEngine()
        zones = {(0, 0): 80.0, (0, 1): 10.0, (1, 0): 10.0, (1, 1): 10.0}
        result = make_result("MEDIUM", zone_risks=zones)
        for _ in range(10):
            engine.evaluate(result, FakeTracker(20), 0.01, True)
        zc = [e for e in engine.history
              if e.event_type == EventType.ZONE_CONGESTION]
        assert zc[0].severity == Severity.HIGH

    def test_limited_mode_skips_zone(self):
        engine = EventEngine()
        zones = {(0, 0): 60.0, (0, 1): 10.0, (1, 0): 10.0, (1, 1): 10.0}
        result = make_result("MEDIUM", zone_risks=zones)
        for _ in range(12):
            engine.evaluate(result, None, 0.01, tracking_enabled=False)
        assert not [e for e in engine.history
                    if e.event_type == EventType.ZONE_CONGESTION]


class TestMovementSpike:
    def test_spike_fires(self):
        engine = EventEngine()
        events = None
        for i in range(4):
            events = engine.evaluate(make_result("LOW"), FakeTracker(10),
                                     0.001, True)
        events = engine.evaluate(make_result("LOW"), FakeTracker(10),
                                 0.05, True)
        spikes = [e for e in events
                  if e.event_type == EventType.MOVEMENT_SPIKE]
        assert spikes
        assert spikes[0].severity == Severity.MEDIUM

    def test_constant_low_motion_no_fire(self):
        engine = EventEngine()
        events = None
        for _ in range(20):
            events = engine.evaluate(make_result("LOW"), FakeTracker(10),
                                     0.001, True)
        assert not [e for e in events
                    if e.event_type == EventType.MOVEMENT_SPIKE]

    def test_spike_requires_ratio(self):
        engine = EventEngine()
        for _ in range(20):
            engine.evaluate(make_result("LOW"), FakeTracker(10), 0.05, True)
        events = engine.evaluate(make_result("LOW"), FakeTracker(10),
                                 0.05, True)
        assert not [e for e in events
                    if e.event_type == EventType.MOVEMENT_SPIKE]


class TestLowActivity:
    def test_low_activity_fires(self):
        engine = EventEngine()
        tracker = FakeTracker(1)
        for _ in range(30):
            engine.evaluate(make_result("LOW"), tracker, 0.01, True)
        low = [e for e in engine.history
               if e.event_type == EventType.LOW_ACTIVITY]
        assert low
        assert low[0].severity == Severity.LOW

    def test_low_activity_needs_sustain(self):
        engine = EventEngine()
        tracker = FakeTracker(1)
        events = engine.evaluate(make_result("LOW"), tracker, 0.01, True)
        assert not [e for e in events
                    if e.event_type == EventType.LOW_ACTIVITY]

    def test_low_activity_skipped_no_tracking(self):
        engine = EventEngine()
        for _ in range(35):
            engine.evaluate(make_result("LOW"), None, 0.01,
                            tracking_enabled=False)
        assert not [e for e in engine.history
                    if e.event_type == EventType.LOW_ACTIVITY]


class TestEventData:
    def test_timestamp_format(self):
        engine = EventEngine()
        events = engine.evaluate(make_result("LOW"), FakeTracker(10, growth=5.0),
                                 0.01, True)
        surge = [e for e in events
                 if e.event_type == EventType.CROWD_SURGE]
        assert surge
        assert len(surge[0].timestamp) == 8
        assert surge[0].timestamp[2] == ":"
        assert surge[0].timestamp[5] == ":"

    def test_message_nonempty(self):
        engine = EventEngine()
        events = engine.evaluate(make_result("LOW"), FakeTracker(10, growth=5.0),
                                 0.01, True)
        for event in events:
            assert isinstance(event.message, str)
            assert event.message

    def test_event_str_contains_severity(self):
        event = Event(
            timestamp="00:00:00", event_type=EventType.CROWD_SURGE,
            severity=Severity.MEDIUM, message="test message",
        )
        s = str(event)
        assert "MEDIUM" in s
        assert "Crowd" in s

    def test_to_row_csv(self):
        engine = EventEngine()
        events = engine.evaluate(make_result("LOW"), FakeTracker(10, growth=5.0),
                                 0.01, True)
        surge = [e for e in events
                 if e.event_type == EventType.CROWD_SURGE]
        row = surge[0].to_row()
        assert len(row) == 7
        assert row[1].endswith("Surge")
        assert row[2] == "MEDIUM"


class TestLegacyHelpership:
    def test_zone_events_skip_when_risk_result_none(self):
        engine = EventEngine()
        for _ in range(12):
            engine.evaluate(None, FakeTracker(20), 0.01, True)
        assert not [e for e in engine.history
                    if e.event_type == EventType.ZONE_CONGESTION]


class TestEnums:
    def test_severity_members(self):
        assert {s.name for s in Severity} == {"LOW", "MEDIUM", "HIGH"}
        assert {s.value for s in Severity} == {0, 1, 2}

    def test_event_type_members(self):
        expected = {
            "RISK_ESCALATION", "RISK_DEESCALATION", "CROWD_SURGE",
            "CROWD_REDUCTION", "ZONE_CONGESTION", "MOVEMENT_SPIKE",
            "LOW_ACTIVITY",
        }
        assert {e.name for e in EventType} == expected