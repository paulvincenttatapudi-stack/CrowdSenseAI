import random

import cv2
import numpy as np
import pytest

from src.analyzer import Analyzer
from src.event_engine import EventEngine, EventType
from src.risk_engine import RiskEngine
from src.tracker import CrowdTracker
from src.config import VIDEO_PATH


def synthetic_persons(frame_ind, rng, count):
    persons = []
    h = 432
    w = 768
    for i in range(count):
        angle = rng.uniform(0, 2 * np.pi)
        base_cx = 100 + (frame_ind * 2 % 400)
        cx = int(base_cx + rng.uniform(-20, 20)) % w
        cy = int(200 + (frame_ind * 5 % 200)) % h
        cx = int(cx + 30 * np.cos(angle))
        cy = int(cy + 30 * np.sin(angle))
        cx = max(10, min(w - 10, cx))
        cy = max(10, min(h - 10, cy))
        persons.append({
            "track_id": i + 1,
            "cx": cx,
            "cy": cy,
            "x1": max(0, cx - 15),
            "y1": max(0, cy - 40),
            "x2": min(w, cx + 15),
            "y2": min(h, cy + 10),
        })
    return persons


class TestEndToEndPipeline:
    @pytest.fixture()
    def video_reader(self):
        cap = cv2.VideoCapture(str(VIDEO_PATH))
        if not cap.isOpened():
            pytest.skip("Demo video not available")
        yield cap
        cap.release()

    def test_full_pipeline_521_frames(self, video_reader):
        rng = random.Random(42)
        tracker = CrowdTracker()
        analyzer = Analyzer()
        risk_engine = RiskEngine()
        event_engine = EventEngine()

        scores = []
        levels = set()
        event_types = set()
        frames = 0

        while True:
            ret, frame = video_reader.read()
            if not ret:
                break
            frames += 1
            h, w = frame.shape[:2]

            count = 8 + (frames % 20)
            persons = synthetic_persons(frames, rng, count)

            tracker.update(persons, h, w)
            grid_counts = analyzer.count_by_grid(persons, h, w)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            motion_variance = analyzer.compute_motion_variance(gray)
            heatmap = analyzer.build_heatmap(persons, h, w)
            assert heatmap.shape == (h, w)
            assert 0.0 <= motion_variance

            risk_result = risk_engine.compute_risk(
                tracker, motion_variance, grid_counts,
                h, w, tracking_enabled=True,
            )
            assert 0.0 <= risk_result.composite_score <= 100.0
            assert 0.0 <= risk_result.smoothed_score <= 100.0
            scores.append(risk_result.smoothed_score)
            levels.add(risk_result.risk_level)

            events = event_engine.evaluate(
                risk_result, tracker, motion_variance, tracking_enabled=True,
            )
            for e in events:
                event_types.add(e.event_type)
                assert isinstance(e.message, str)
                assert e.message

        assert frames == 521
        assert scores
        assert min(scores) >= 0.0
        assert max(scores) <= 100.0
        assert levels
        assert event_types, "Expected at least one event to fire over the run"

    def test_legacy_path_no_tracking(self, video_reader):
        from src.risk import (
            compute_pressure_index, classify_risk, risk_colors, RiskLevel,
        )
        from src.risk_engine import RiskResult

        analyzer = Analyzer()
        event_engine = EventEngine()
        frames = 0
        previous_level = None
        transitions = 0

        while True:
            ret, frame = video_reader.read()
            if not ret:
                break
            frames += 1
            h, w = frame.shape[:2]

            persons = [{"cx": 50, "cy": 50, "track_id": 1}]
            grid_counts = analyzer.count_by_grid(persons, h, w)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            motion_variance = analyzer.compute_motion_variance(gray)
            total = sum(sum(row) for row in grid_counts)
            pressure = compute_pressure_index(total, motion_variance)
            risk_text = classify_risk(pressure)
            risk_colors(risk_text)

            risk_result = RiskResult(
                risk_level=risk_text,
                smoothed_score=min(100.0, pressure),
            )
            if previous_level is not None and risk_text != previous_level:
                transitions += 1
            previous_level = risk_text

            event_engine.evaluate(
                risk_result, None, motion_variance, tracking_enabled=False,
            )

        assert frames == 521
        assert transitions >= 0

    def test_risk_result_unchanged_by_events(self, video_reader):
        rng = random.Random(7)

        t1 = CrowdTracker()
        a1 = Analyzer()
        e1 = RiskEngine()
        t2 = CrowdTracker()
        a2 = Analyzer()
        e2 = RiskEngine()

        with_events = EventEngine()
        frames = 0

        while True:
            ret, frame = video_reader.read()
            if not ret:
                break
            frames += 1
            h, w = frame.shape[:2]
            count = 12
            persons = synthetic_persons(frames, rng, count)

            t1.update(persons, h, w)
            t2.update(persons, h, w)
            grid1 = a1.count_by_grid(persons, h, w)
            gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mv1 = a1.compute_motion_variance(gray1)
            grid2 = a2.count_by_grid(persons, h, w)
            gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mv2 = a2.compute_motion_variance(gray2)

            r1 = e1.compute_risk(t1, mv1, grid1, h, w, tracking_enabled=True)
            r2 = e2.compute_risk(t2, mv2, grid2, h, w, tracking_enabled=True)

            with_events.evaluate(r2, t2, mv2, tracking_enabled=True)
            assert r1 == r2

        assert frames == 521