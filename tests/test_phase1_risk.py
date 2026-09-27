import pytest

from src.config import (
    PRESSURE_HIGH_THRESHOLD, PRESSURE_MEDIUM_THRESHOLD,
    GRID_ROWS, GRID_COLS, ZONE_DENSITY_THRESHOLD,
)
from src.risk import (
    RiskLevel, compute_pressure_index, classify_risk, risk_colors,
    risk_score_color, risk_colors,
)


class TestRiskLevel:
    def test_risk_level_constants(self):
        assert RiskLevel.LOW == "LOW"
        assert RiskLevel.MEDIUM == "MEDIUM"
        assert RiskLevel.HIGH == "HIGH"


class TestComputePressureIndex:
    def test_zero_crowd(self):
        assert compute_pressure_index(0, 0.5) == 0.0

    def test_zero_motion(self):
        assert compute_pressure_index(10, 0.0) == 0.0

    def test_typical(self):
        assert compute_pressure_index(5, 0.02) == pytest.approx(0.1)

    def test_high(self):
        assert compute_pressure_index(30, 0.1) == pytest.approx(3.0)

    def test_identity(self):
        assert compute_pressure_index(7, 1.0) == 7.0


class TestClassifyRisk:
    def test_low(self):
        assert classify_risk(0.0) == RiskLevel.LOW
        assert classify_risk(PRESSURE_MEDIUM_THRESHOLD - 0.1) == RiskLevel.LOW

    def test_medium(self):
        assert classify_risk(PRESSURE_MEDIUM_THRESHOLD + 1.0) == RiskLevel.MEDIUM
        assert classify_risk(PRESSURE_HIGH_THRESHOLD - 0.1) == RiskLevel.MEDIUM

    def test_high(self):
        assert classify_risk(PRESSURE_HIGH_THRESHOLD + 1.0) == RiskLevel.HIGH

    def test_boundary_medium_strict(self):
        assert classify_risk(PRESSURE_MEDIUM_THRESHOLD) == RiskLevel.LOW

    def test_boundary_high_strict(self):
        assert classify_risk(PRESSURE_HIGH_THRESHOLD) == RiskLevel.MEDIUM


class TestRiskColors:
    def test_color_map(self):
        assert risk_colors(RiskLevel.LOW) == (0, 255, 0)
        assert risk_colors(RiskLevel.MEDIUM) == (0, 165, 255)
        assert risk_colors(RiskLevel.HIGH) == (0, 0, 255)

    def test_unknown_level(self):
        assert risk_colors("UNKNOWN") == (255, 255, 255)


class TestRiskScoreColor:
    def test_low_score_green(self):
        color = risk_score_color(0.0)
        assert color[2] == 0
        assert color[1] == 255

    def test_high_score_red(self):
        color = risk_score_color(100.0)
        assert color[2] == 255
        assert color[1] == 0

    def test_mid_score_mixed(self):
        color = risk_score_color(50.0)
        assert color[1] == 255
        assert color[2] == 255

    def test_clamp_negative(self):
        color = risk_score_color(-10.0)
        assert color[2] == 0

    def test_clamp_above(self):
        color = risk_score_color(150.0)
        assert color[1] == 0
        assert color[2] == 255


class TestConfigIntegrity:
    def test_grid_dims(self):
        assert GRID_ROWS == 2
        assert GRID_COLS == 2
        assert ZONE_DENSITY_THRESHOLD == 3