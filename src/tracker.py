import math
from collections import deque

from src.config import (
    GRID_ROWS,
    GRID_COLS,
    POSITION_HISTORY_LENGTH,
    COUNT_HISTORY_LENGTH,
)


class ZoneStats:
    def __init__(self):
        self.current_ids = set()
        self.all_ids = set()
        self.total_detections = 0


class CrowdTracker:
    def __init__(self):
        self.seen_ids = set()
        self.prev_active_ids = set()
        self.total_entries = 0
        self.total_exits = 0
        self.frame_count = 0
        self.count_history = deque(maxlen=COUNT_HISTORY_LENGTH)
        self.position_history = {}
        self.zone_stats = {}

    def reset(self):
        self.seen_ids = set()
        self.prev_active_ids = set()
        self.total_entries = 0
        self.total_exits = 0
        self.frame_count = 0
        self.count_history.clear()
        self.position_history = {}
        self.zone_stats = {}

    def update(self, persons, frame_h, frame_w):
        self.frame_count += 1

        active_ids = set()
        for p in persons:
            tid = p.get("track_id")
            if tid is not None:
                active_ids.add(tid)

        new_ids = active_ids - self.prev_active_ids
        lost_ids = self.prev_active_ids - active_ids

        truly_new = new_ids - self.seen_ids
        self.total_entries += len(truly_new)
        self.total_exits += len(lost_ids)

        self.seen_ids.update(new_ids)

        self.position_history = {
            tid: self.position_history[tid]
            for tid in self.position_history
            if tid in active_ids
        }
        for p in persons:
            tid = p.get("track_id")
            if tid is not None:
                if tid not in self.position_history:
                    self.position_history[tid] = deque(maxlen=POSITION_HISTORY_LENGTH)
                self.position_history[tid].append((p["cx"], p["cy"]))

        self._update_zone_stats(persons, frame_h, frame_w)

        self.count_history.append(len(active_ids))
        self.prev_active_ids = active_ids

    def _update_zone_stats(self, persons, frame_h, frame_w):
        prev_all_ids = {
            key: zs.all_ids.copy()
            for key, zs in self.zone_stats.items()
        }

        self.zone_stats = {}
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                key = (row, col)
                zs = ZoneStats()
                if key in prev_all_ids:
                    zs.all_ids = prev_all_ids[key]
                self.zone_stats[key] = zs

        for p in persons:
            row = 0 if p["cy"] < frame_h / 2 else 1
            col = 0 if p["cx"] < frame_w / 2 else 1
            key = (row, col)
            if key not in self.zone_stats:
                self.zone_stats[key] = ZoneStats()
            tid = p.get("track_id")
            if tid is not None:
                self.zone_stats[key].current_ids.add(tid)
                self.zone_stats[key].all_ids.add(tid)
            self.zone_stats[key].total_detections += 1

    @property
    def current_count(self):
        return len(self.prev_active_ids)

    @property
    def peak_count(self):
        if not self.count_history:
            return 0
        return max(self.count_history)

    @property
    def average_count(self):
        if not self.count_history:
            return 0.0
        return sum(self.count_history) / len(self.count_history)

    @property
    def estimated_entries(self):
        return self.total_entries

    @property
    def estimated_exits(self):
        return self.total_exits

    def get_zone_current_count(self, row, col):
        stats = self.zone_stats.get((row, col))
        if stats is None:
            return 0
        return len(stats.current_ids)

    def get_zone_peak_count(self, row, col):
        stats = self.zone_stats.get((row, col))
        if stats is None:
            return 0
        return len(stats.all_ids)

    def get_person_speed(self, track_id):
        history = self.position_history.get(track_id)
        if history is None or len(history) < 2:
            return 0.0
        dx = history[-1][0] - history[0][0]
        dy = history[-1][1] - history[0][1]
        frames = len(history)
        return math.sqrt(dx * dx + dy * dy) / frames

    def get_person_displacement(self, track_id):
        history = self.position_history.get(track_id)
        if history is None or len(history) < 2:
            return 0.0
        dx = history[-1][0] - history[0][0]
        dy = history[-1][1] - history[0][1]
        return math.sqrt(dx * dx + dy * dy)

    def get_crowd_mean_speed(self):
        speeds = []
        for tid in self.prev_active_ids:
            s = self.get_person_speed(tid)
            if s > 0:
                speeds.append(s)
        if not speeds:
            return 0.0
        return sum(speeds) / len(speeds)

    def get_growth_rate(self, window=15, fps=30.0):
        if len(self.count_history) < window:
            return 0.0
        old_count = self.count_history[-window]
        new_count = self.count_history[-1]
        elapsed = window / fps
        if elapsed <= 0:
            return 0.0
        return (new_count - old_count) / elapsed

    def get_temporal_stability(self, window=30):
        if len(self.count_history) < 2:
            return 0.0
        recent = list(self.count_history)[-window:]
        n = len(recent)
        if n < 2:
            return 0.0
        mean_val = sum(recent) / n
        if mean_val == 0:
            return 0.0
        variance = sum((x - mean_val) ** 2 for x in recent) / n
        std_val = math.sqrt(variance)
        return std_val / mean_val

    def get_chaos_index(self):
        angles = []
        for tid in self.prev_active_ids:
            history = self.position_history.get(tid)
            if history is None or len(history) < 3:
                continue
            dx = history[-1][0] - history[-3][0]
            dy = history[-1][1] - history[-3][1]
            if dx == 0 and dy == 0:
                continue
            angles.append(math.atan2(dy, dx))
        if len(angles) < 2:
            return 0.0
        cos_sum = sum(math.cos(a) for a in angles)
        sin_sum = sum(math.sin(a) for a in angles)
        r = math.sqrt(cos_sum ** 2 + sin_sum ** 2) / len(angles)
        return max(0.0, min(1.0, 1.0 - r))

    def get_zone_mean_speed(self, row, col, frame_h, frame_w):
        speeds = []
        for p_tid, history in self.position_history.items():
            if p_tid not in self.prev_active_ids:
                continue
            if len(history) < 2:
                continue
            cy = history[-1][1]
            cx = history[-1][0]
            p_row = 0 if cy < frame_h / 2 else 1
            p_col = 0 if cx < frame_w / 2 else 1
            if p_row == row and p_col == col:
                s = self.get_person_speed(p_tid)
                if s > 0:
                    speeds.append(s)
        if not speeds:
            return 0.0
        return sum(speeds) / len(speeds)

    def get_churn_rate(self, window=30, fps=30.0):
        if len(self.count_history) < 2:
            return 0.0
        recent_window = min(window, len(self.count_history))
        elapsed = recent_window / fps
        if elapsed <= 0:
            return 0.0
        churn = self.total_entries + self.total_exits
        return churn / elapsed
