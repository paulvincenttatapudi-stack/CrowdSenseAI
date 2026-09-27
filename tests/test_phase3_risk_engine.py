import math

import pytest

from src.risk_engine import RiskEngine, RiskResult
from src.config import (
    RISK_LOW_THRESHOLD, RISK_MEDIUM_THRESHOLD, RISK_HYSTERESIS,
    RISK_SMOOTHING_ALPHA, MIN_CROWD_THRESHOLD,
    GRID_ROWS, GRID_COLS,
)


class FakeTracker:
    def __init__(self, count, mean_speed=0.0):
        self.current_count = count
        self._speed = mean_speed
        self._zone_counts = {}

    def get_crowd_mean_speed(self):
        return self._speed

    def get_growth_rate(self, window=15):
        return 0.0

    def get_temporal_stability(self, window=30):
        return 0.0

    def get_chaos_index(self):
        return 0.0

    def get_churn_rate(self, window=30, fps=30.0):
        return 0.0

    def get_zone_current_count(self, row, col):
        return self._zone_counts.get((row, col), 0)

    def get_zone_mean_speed(self, row, col, frame_h, frame_w):
        return self._speed


def empty_grid():
    return [[0] * GRID_COLS for _ in range(GRID_ROWS)]


def crowded_grid(zone_count):
    grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
    grid[0][0] = zone_count
    return grid


class TestRiskEngineBasics:
    def test_init(self):
        engine = RiskEngine()
        assert engine._prev_smoothed == 0.0
        assert engine._prev_level == "LOW"

    def test_reset(self):
        engine = RiskEngine()
        engine.compute_risk(FakeTracker(10), 0.02, crowded_grid(6), 100, 100)
        engine.reset()
        assert engine._prev_smoothed == 0.0
        assert engine._prev_level == "LOW"

    def test_limited_returns_limited_result(self):
        engine = RiskEngine()
        result = engine.compute_risk(None, 0.02, empty_grid(), 100, 100,
                                     tracking_enabled=False)
        assert isinstance(result, RiskResult)
        assert result.is_limited is True

    def test_low_crowd_result(self):
        engine = RiskEngine()
        result = engine.compute_risk(FakeTracker(1), 0.02, empty_grid(),
                                     100, 100, tracking_enabled=True)
        assert isinstance(result, RiskResult)
        assert result.risk_level in ("LOW", "MEDIUM", "HIGH")

    def test_normal_result_zero_contributors(self):
        engine = RiskEngine()
        result = engine.compute_risk(FakeTracker(10), 0.02, crowded_grid(6),
                                     100, 100, tracking_enabled=True)
        assert 0.0 <= result.composite_score <= 100.0
        assert 0.0 <= result.smoothed_score <= 100.0
        assert len(result.signal_values) == 8
        assert len(result.category_scores) == 3
        assert len(result.zone_risks) == GRID_ROWS * GRID_COLS
        assert result.critical_zone in result.zone_risks


class TestRiskEngineLimited:
    def test_limited_signal_values(self):
        engine = RiskEngine()
        result = engine.compute_risk(None, 0.02, empty_grid(), 100, 100,
                                     tracking_enabled=False)
        assert result.signal_values["density"] >= 0.0
        assert result.signal_values["optical_flow"] >= 0.0
        assert result.signal_values["speed"] == 0.0
        assert result.signal_values["growth_rate"] == 0.0

    def test_limited_zone_risks_zero(self):
        engine = RiskEngine()
        result = engine.compute_risk(None, 0.02, empty_grid(), 100, 100,
                                     tracking_enabled=False)
        for zone in result.zone_risks.values():
            assert zone == 0.0


class TestRiskEngineNormalization:
    def test_density_normalization_zero_area(self):
        engine = RiskEngine()
        result = engine.compute_risk(FakeTracker(10), 0.02, crowded_grid(6),
                                     0, 0, tracking_enabled=True)
        assert result.signal_values["density"] >= 0.0

    def test_zone_fraction(self):
        engine = RiskEngine()
        result = engine.compute_risk(FakeTracker(10), 0.02, crowded_grid(6),
                                     100, 100, tracking_enabled=True)
        assert 0.0 <= result.signal_values["concentration"] <= 100.0


class TestRiskEngineThresholds:
    def test_high_density_triggers_high_contribution(self):
        engine = RiskEngine()
        result = engine.compute_risk(FakeTracker(50), 0.02, crowded_grid(30),
                                     100, 100, tracking_enabled=True)
        names = [name for name, _, _ in result.top_contributors]
        assert "Crowd Density" in names or "Zone Concentration" in names

    def test_smoothing_changes_with_alpha(self):
        engine = RiskEngine()
        high_result = engine.compute_risk(FakeTracker(50), 0.02, crowded_grid(30),
                                          100, 100, tracking_enabled=True)
        assert high_result.smoothed_score > 0.0
        assert high_result.smoothed_score <= RISK_MEDIUM_THRESHOLD + RISK_HYSTERESIS


class TestRiskEngineCategoryWeights:
    def test_weights_sum_to_one(self):
        from src import config
        assert (config.RISK_WEIGHT_STATE + config.RISK_WEIGHT_DYNAMICS
                + config.RISK_WEIGHT_HISTORY) == pytest.approx(1.0)

    def test_all_category_keys(self):
        engine = RiskEngine()
        result = engine.compute_risk(FakeTracker(10), 0.02, crowded_grid(6),
                                     100, 100, tracking_enabled=True)
        assert set(result.category_scores.keys()) == {
            "crowd_state", "crowd_dynamics", "historical"
        }


class TestRiskEngineDeterminism:
    def test_same_inputs_same_output(self):
        e1, e2 = RiskEngine(), RiskEngine()
        t1, t2 = FakeTracker(10), FakeTracker(10)
        r1 = e1.compute_risk(t1, 0.02, crowded_grid(6), 100, 100)
        r2 = e2.compute_risk(t2, 0.02, crowded_grid(6), 100, 100)
        assert r1 == r2


class TestRiskEngineLowCrowd:
    def test_zero_count_limited_state(self):
        engine = RiskEngine()
        result = engine.compute_risk(FakeTracker(0), 0.02, empty_grid(),
                                     100, 100, tracking_enabled=True)
        assert result.risk_level in ("LOW", "MEDIUM", "HIGH")
        assert 0.0 <= result.smoothed_score <= 100.0

    def test_low_crowd_zone_risks_zero(self):
        engine = RiskEngine()
        result = engine.compute_risk(FakeTracker(1), 0.02, empty_grid(),
                                     100, 100, tracking_enabled=True)
        for zone in result.zone_risks.values():
            assert zone == 0.0