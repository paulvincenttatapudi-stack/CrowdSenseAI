import cv2
import numpy as np

from src.config import GRID_ROWS, GRID_COLS


class Analyzer:
    def __init__(self):
        self.prev_gray = None

    def count_by_grid(self, persons, frame_h, frame_w):
        grid_counts = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
        for p in persons:
            row = 0 if p["cy"] < frame_h / 2 else 1
            col = 0 if p["cx"] < frame_w / 2 else 1
            grid_counts[row][col] += 1
        return grid_counts

    def compute_motion_variance(self, gray_frame):
        if self.prev_gray is None:
            self.prev_gray = gray_frame
            return 0.0

        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, gray_frame,
            None,
            0.5, 3, 15, 3, 5, 1.2, 0,
        )
        magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        self.prev_gray = gray_frame
        return float(np.var(magnitude))

    def build_heatmap(self, persons, frame_h, frame_w):
        heatmap = np.zeros((frame_h, frame_w), dtype=np.float32)
        for p in persons:
            heatmap[p["y1"]:p["y2"], p["x1"]:p["x2"]] += 1
        return heatmap
