import cv2
import time

from src.config import (
    VIDEO_PATH,
    WEBCAM_INDEX,
    WINDOW_TITLE,
)
from src.detector import Detector
from src.analyzer import Analyzer
from src.risk import RiskLevel, compute_pressure_index, classify_risk, risk_colors, risk_score_color
from src.risk_engine import RiskEngine, RiskResult
from src.alert import AlertEngine
from src.event_engine import EventEngine
from src.display import (draw_grid, apply_heatmap, draw_hud, draw_tracking_hud,
                         draw_risk_hud, draw_event_hud)
from src.tracker import CrowdTracker


class App:
    def __init__(self, video_path=None, model_path=None, tracking=False,
                 legacy_risk=False, events_enabled=True, log_events=False):
        self.video_path = video_path or VIDEO_PATH
        self.model_path = model_path
        self.tracking = tracking
        self.legacy_risk = legacy_risk

        self.detector = Detector(model_path) if model_path else Detector()
        self.analyzer = Analyzer()
        self.alert_engine = AlertEngine()
        self.prev_time = 0.0

        self.tracker = CrowdTracker() if tracking else None
        self.risk_engine = RiskEngine() if not legacy_risk else None
        self.event_engine = (EventEngine(log_events=log_events)
                             if events_enabled else None)

    def open_video_source(self):
        if self.video_path:
            cap = cv2.VideoCapture(str(self.video_path))
        else:
            cap = cv2.VideoCapture(WEBCAM_INDEX, cv2.CAP_DSHOW)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {self.video_path or WEBCAM_INDEX}")
        return cap

    def run(self):
        cap = self.open_video_source()
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                h, w = frame.shape[:2]

                fps = self._compute_fps()

                boxes = self.detector.detect(frame, tracking=self.tracking)
                persons = self.detector.filter_persons(boxes, tracking=self.tracking)

                if self.tracking:
                    self.tracker.update(persons, h, w)

                grid_counts = self.analyzer.count_by_grid(persons, h, w)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                motion_variance = self.analyzer.compute_motion_variance(gray)

                heatmap = self.analyzer.build_heatmap(persons, h, w)
                frame = apply_heatmap(frame, heatmap)
                draw_grid(frame, persons, grid_counts, show_ids=self.tracking)

                if self.legacy_risk:
                    total_people = sum(sum(row) for row in grid_counts)
                    pressure = compute_pressure_index(total_people, motion_variance)
                    risk_text = classify_risk(pressure)
                    risk_color = risk_colors(risk_text)
                    if risk_text == RiskLevel.HIGH:
                        self.alert_engine.trigger()
                    draw_hud(frame, risk_text, risk_color, pressure, fps)
                    risk_result = RiskResult(
                        risk_level=risk_text,
                        smoothed_score=min(100.0, pressure),
                    )
                else:
                    risk_result = self.risk_engine.compute_risk(
                        self.tracker, motion_variance, grid_counts,
                        h, w, tracking_enabled=self.tracking,
                    )
                    risk_color = risk_score_color(risk_result.smoothed_score)
                    if risk_result.risk_level == "HIGH":
                        self.alert_engine.trigger()
                    draw_risk_hud(frame, risk_result, fps)

                if self.event_engine is not None:
                    events = self.event_engine.evaluate(
                        risk_result, self.tracker, motion_variance,
                        tracking_enabled=self.tracking,
                    )
                    for event in events:
                        print(event)
                    draw_event_hud(frame, self.event_engine.recent_events)

                if self.tracking:
                    draw_tracking_hud(frame, self.tracker)
                cv2.imshow(WINDOW_TITLE, frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def _compute_fps(self):
        current_time = time.time()
        fps = 1.0 / (current_time - self.prev_time) if self.prev_time != 0 else 0.0
        self.prev_time = current_time
        return fps
