import pytest

from src.tracker import CrowdTracker
from src.config import (
    GRID_ROWS, GRID_COLS, POSITION_HISTORY_LENGTH, COUNT_HISTORY_LENGTH,
)


def person(tid, cx, cy):
    return {"track_id": tid, "cx": cx, "cy": cy}


class FakeTracker:
    """Minimal stub exposing the same surface EventEngine consumes."""

    def __init__(self, count, growth=0.0):
        self.current_count = count
        self._growth = growth

    def get_growth_rate(self, window=15):
        return self._growth


class TestTrackerBasics:
    def test_init_state(self):
        t = CrowdTracker()
        assert t.current_count == 0
        assert t.peak_count == 0
        assert t.average_count == 0.0
        assert t.estimated_entries == 0
        assert t.estimated_exits == 0
        assert t.frame_count == 0

    def test_reset(self):
        t = CrowdTracker()
        t.update([person(1, 10, 10)], 100, 100)
        t.update([person(1, 12, 12)], 100, 100)
        t.reset()
        assert t.current_count == 0
        assert t.peak_count == 0
        assert t.total_entries == 0
        assert t.total_exits == 0

    def test_single_person_entry(self):
        t = CrowdTracker()
        t.update([person(1, 10, 10)], 100, 100)
        assert t.current_count == 1
        assert t.estimated_entries == 1
        assert t.peak_count == 1

    def test_person_removed_counts_exit(self):
        t = CrowdTracker()
        t.update([person(1, 10, 10), person(2, 30, 30)], 100, 100)
        t.update([person(1, 12, 12)], 100, 100)
        assert t.current_count == 1
        assert t.estimated_exits == 1

    def test_id_reappears_not_new_entry(self):
        t = CrowdTracker()
        t.update([person(1, 10, 10)], 100, 100)
        t.update([], 100, 100)
        t.update([person(1, 12, 12)], 100, 100)
        assert t.estimated_entries == 1

    def test_peak_count(self):
        t = CrowdTracker()
        t.update([person(1, 10, 10)], 100, 100)
        t.update([person(1, 10, 10), person(2, 30, 30), person(3, 50, 50)], 100, 100)
        t.update([person(1, 10, 10)], 100, 100)
        assert t.peak_count == 3

    def test_average_count(self):
        t = CrowdTracker()
        t.update([person(1, 10, 10)], 100, 100)
        t.update([person(1, 10, 10), person(2, 30, 30)], 100, 100)
        assert t.average_count == pytest.approx(1.5)

    def test_count_history_warmup_growth_zero(self):
        t = CrowdTracker()
        for _ in range(10):
            t.update([person(1, 10, 10)], 100, 100)
        assert t.get_growth_rate(window=15) == 0.0

    def test_growth_rate_positive(self):
        t = CrowdTracker()
        for _ in range(14):
            t.update([person(1, 10, 10)], 100, 100)
        t.update([person(1, 10, 10), person(2, 30, 30)], 100, 100)
        assert t.get_growth_rate(window=15) == pytest.approx(2.0)


class TestTrackerZones:
    def test_zone_assignment(self):
        t = CrowdTracker()
        t.update([person(1, 10, 10), person(2, 90, 90)], 100, 100)
        assert t.get_zone_current_count(0, 0) == 1
        assert t.get_zone_current_count(1, 1) == 1

    def test_all_zones_present(self):
        t = CrowdTracker()
        t.update([person(1, 50, 50)], 100, 100)
        assert set(t.zone_stats.keys()) == {
            (r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)
        }

    def test_zone_id_persistence_across_motion(self):
        t = CrowdTracker()
        t.update([person(1, 10, 10)], 100, 100)
        t.update([person(1, 90, 90)], 100, 100)
        assert t.get_zone_current_count(1, 1) == 1
        assert t.get_zone_current_count(0, 0) == 0


class TestTrackerMovement:
    def setup_method(self):
        self.t = CrowdTracker()

    def test_person_speed_insufficient_history(self):
        self.t.update([person(1, 10, 10)], 100, 100)
        assert self.t.get_person_speed(1) == 0.0

    def test_person_displacement(self):
        self.t.update([person(1, 10, 10)], 100, 100)
        self.t.update([person(1, 20, 10)], 100, 100)
        assert self.t.get_person_displacement(1) == pytest.approx(10.0)

    def test_crowd_mean_speed(self):
        self.t.update([person(1, 10, 10)], 100, 100)
        self.t.update([person(1, 30, 10)], 100, 100)
        assert self.t.get_crowd_mean_speed() == pytest.approx(10.0)

    def test_chaos_index_low_parallel(self):
        self.t.update([person(1, 10, 10), person(2, 10, 20)], 100, 100)
        self.t.update([person(1, 20, 10), person(2, 20, 20)], 100, 100)
        assert 0.0 <= self.t.get_chaos_index() <= 1.0

    def test_chaos_requires_samples(self):
        assert self.t.get_chaos_index() == 0.0


class TestTrackerConfiguration:
    def test_position_history_length(self):
        t = CrowdTracker()
        for i in range(50):
            t.update([person(1, i % 10, 10)], 100, 100)
        assert len(t.position_history[1]) == POSITION_HISTORY_LENGTH

    def test_count_history_length(self):
        t = CrowdTracker()
        for i in range(COUNT_HISTORY_LENGTH + 50):
            t.update([person(i % 3, 10, 10)], 100, 100)
        assert len(t.count_history) == COUNT_HISTORY_LENGTH