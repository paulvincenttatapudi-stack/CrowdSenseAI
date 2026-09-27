import cv2
import numpy as np

from src.config import (
    ZONE_DENSITY_THRESHOLD,
    HEATMAP_BLUR_KERNEL,
    HEATMAP_ALPHA,
    FRAME_ALPHA,
    GRID_ROWS,
    GRID_COLS,
)
from src.risk import risk_score_color
from src.event_engine import Severity


def draw_grid(frame, persons, grid_counts, show_ids=False):
    h, w = frame.shape[:2]

    for p in persons:
        cv2.circle(frame, (p["cx"], p["cy"]), 4, (0, 255, 0), -1)
        if show_ids:
            tid = p.get("track_id")
            if tid is not None:
                cv2.putText(frame, str(tid), (p["cx"] + 6, p["cy"] - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    cv2.line(frame, (w // 2, 0), (w // 2, h), (255, 255, 255), 2)
    cv2.line(frame, (0, h // 2), (w, h // 2), (255, 255, 255), 2)

    for i in range(GRID_ROWS):
        for j in range(GRID_COLS):
            text = f"Zone {i},{j}: {grid_counts[i][j]}"
            x = j * (w // GRID_COLS) + 20
            y = i * (h // GRID_ROWS) + 40
            color = (0, 0, 255) if grid_counts[i][j] > ZONE_DENSITY_THRESHOLD else (0, 255, 0)
            cv2.putText(frame, text, (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


def apply_heatmap(frame, heatmap):
    heatmap = cv2.GaussianBlur(heatmap, (HEATMAP_BLUR_KERNEL, HEATMAP_BLUR_KERNEL), 0)
    heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heatmap = heatmap.astype(np.uint8)
    heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    return cv2.addWeighted(frame, FRAME_ALPHA, heatmap_color, HEATMAP_ALPHA, 0)


def draw_hud(frame, risk_text, risk_color, pressure_index, fps):
    h, w = frame.shape[:2]

    cv2.putText(frame, f"Risk: {risk_text}",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, risk_color, 3)

    cv2.putText(frame, f"Pressure: {round(pressure_index, 2)}",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2)

    cv2.putText(frame, f"FPS: {int(fps)}",
                (w - 120, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 0), 2)


def draw_tracking_hud(frame, tracker):
    h, w = frame.shape[:2]

    y_offset = h - 10
    line_h = 22
    x_left = 20

    stats = [
        f"Crowd: {tracker.current_count}  Peak: {tracker.peak_count}  Avg: {tracker.average_count:.1f}",
        f"Est. Entries: {tracker.estimated_entries}  Est. Exits: {tracker.estimated_exits}",
    ]

    for line in stats:
        cv2.putText(frame, line, (x_left, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        y_offset -= line_h


def draw_risk_hud(frame, risk_result, fps):
    h, w = frame.shape[:2]
    color = risk_score_color(risk_result.smoothed_score)

    cv2.putText(frame, f"Risk: {risk_result.risk_level}",
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)

    cv2.putText(frame, f"Score: {risk_result.smoothed_score:.1f} / 100",
                (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    cv2.putText(frame, f"FPS: {int(fps)}",
                (w - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    y = 90
    for name, val, label in risk_result.top_contributors:
        cv2.putText(frame, f"{name}: {val:.0f}", (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y += 20

    y += 10
    cv2.putText(frame, "Zone Risks:", (20, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    y += 20
    for (row, col), zr in risk_result.zone_risks.items():
        zr_color = risk_score_color(zr)
        label = f"  ({row},{col}): {zr:.0f}"
        if (row, col) == risk_result.critical_zone:
            label += " *"
        cv2.putText(frame, label, (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, zr_color, 1)
        y += 18

    if risk_result.is_limited:
        cv2.putText(frame, "Limited Analysis (no tracking)",
                    (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 200, 255), 1)


def draw_event_hud(frame, events):
    if not events:
        return
    h, w = frame.shape[:2]
    x = w - 20
    y = 90
    line_h = 20

    severity_colors = {
        Severity.LOW: (200, 200, 200),
        Severity.MEDIUM: (0, 165, 255),
        Severity.HIGH: (0, 0, 255),
    }

    for event in events:
        color = severity_colors.get(event.severity, (255, 255, 255))
        zone_str = f" {event.zone}" if event.zone is not None else ""
        text = f"[{event.timestamp}] {event.severity_label} {event.type_label}{zone_str}"
        (text_w, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.putText(frame, text, (x - text_w, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        y += line_h

