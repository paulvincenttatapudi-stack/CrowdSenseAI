import pytest

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


class TestEventConfig:
    def test_history_size(self):
        assert EVENT_HISTORY_SIZE == 50

    def test_surge_thresholds_ordering(self):
        assert EVENT_SURGE_THRESHOLD < EVENT_SURGE_THRESHOLD_HIGH
        assert EVENT_SURGE_THRESHOLD > 0
        assert EVENT_SURGE_THRESHOLD_HIGH > 0

    def test_reduction_threshold_negative(self):
        assert EVENT_REDUCTION_THRESHOLD < 0

    def test_min_counts_positive(self):
        assert EVENT_MIN_COUNT_FOR_SURGE > 0
        assert EVENT_MIN_COUNT_FOR_REDUCE > 0

    def test_zone_thresholds_ordering(self):
        assert EVENT_ZONE_CONGESTION_THRESHOLD < EVENT_ZONE_CONGESTION_HIGH
        assert 0 < EVENT_ZONE_CONGESTION_THRESHOLD <= 100

    def test_zone_sustain_positive(self):
        assert EVENT_ZONE_SUSTAIN_FRAMES > 0

    def test_motion_thresholds(self):
        assert EVENT_MOTION_SPIKE_THRESHOLD > 0
        assert EVENT_MOTION_RATIO > 1.0

    def test_low_activity_positive(self):
        assert EVENT_LOW_ACTIVITY_THRESHOLD >= 0
        assert EVENT_LOW_SUSTAIN_FRAMES > 0

    def test_cooldowns_positive(self):
        cooldowns = [
            EVENT_COOLDOWN_RISK, EVENT_COOLDOWN_SURGE, EVENT_COOLDOWN_ZONE,
            EVENT_COOLDOWN_MOVEMENT, EVENT_COOLDOWN_LOW_ACTIVITY,
        ]
        for c in cooldowns:
            assert isinstance(c, int)
            assert c > 0

    def test_max_display_positive(self):
        assert EVENT_MAX_DISPLAY >= 1


class TestCooldownOrdering:
    def test_zone_longer_than_surge(self):
        assert EVENT_COOLDOWN_ZONE > EVENT_COOLDOWN_SURGE

    def test_low_activity_longest(self):
        assert EVENT_COOLDOWN_LOW_ACTIVITY > EVENT_COOLDOWN_SURGE


class TestSyntaxAllSourceFiles:
    def test_all_src_files_compile(self):
        import py_compile
        from pathlib import Path
        src_dir = Path(__file__).resolve().parent.parent / "src"
        for pyfile in sorted(src_dir.glob("*.py")):
            py_compile.compile(str(pyfile), doraise=True)

    def test_main_compiles(self):
        import py_compile
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent
        py_compile.compile(str(root / "main.py"), doraise=True)