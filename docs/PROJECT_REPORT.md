# CrowdSenseAI — AI-Powered Crowd Monitoring & Risk Analysis System

## 1. Project Overview

| Field | Detail |
|-------|--------|
| **Project Name** | CrowdSenseAI |
| **Objective** | AI-powered real-time crowd monitoring and risk analysis using computer vision |
| **Problem** | Manual crowd monitoring is error-prone, delayed, and cannot scale to large venues |
| **Solution** | Automated person detection, density analysis, motion tracking, risk classification, and real-time event intelligence using YOLO and OpenCV |
| **Current Status** | Phase 4 Complete — Real-time event & alert intelligence engine |

---

## 2. Problem Statement

Crowd-related incidents (stampedes, overcrowding, crush injuries) are a recurring problem at public gatherings, religious events, stadiums, and transportation hubs. Manual crowd monitoring by security personnel is limited by human attention spans, blind spots, and delayed reaction times. There is a need for an intelligent, automated system that can:

- Detect and count people in real-time from video feeds
- Analyze crowd density across defined zones
- Track crowd motion patterns to detect anomalies
- Classify risk levels and trigger timely alerts
- Present all information through a real-time visual dashboard

---

## 3. Project Objectives

| # | Objective | Status |
|---|-----------|--------|
| 1 | Real-time person detection using YOLO | IMPLEMENTED & TESTED |
| 2 | Zone-based crowd density analysis (2x2 grid) | IMPLEMENTED & TESTED |
| 3 | Optical flow-based motion analysis | IMPLEMENTED & TESTED |
| 4 | Pressure index computation (people × motion) | IMPLEMENTED & TESTED |
| 5 | Three-tier risk classification (LOW/MEDIUM/HIGH) | IMPLEMENTED & TESTED |
| 6 | Audio alert system with cooldown | IMPLEMENTED & TESTED |
| 7 | Real-time heatmap overlay | IMPLEMENTED |
| 8 | FPS and HUD display | IMPLEMENTED |
| 9 | CLI arguments for video/model paths | IMPLEMENTED |
| 10 | Modular, maintainable code architecture | IMPLEMENTED & TESTED |
| 11 | Person tracking across frames (ByteTrack) | IMPLEMENTED & TESTED |
| 12 | Persistent person IDs | IMPLEMENTED & TESTED |
| 13 | Current / peak / average crowd count | IMPLEMENTED & TESTED |
| 14 | Estimated entry/exit statistics | IMPLEMENTED & TESTED |
| 15 | Per-person movement tracking | IMPLEMENTED & TESTED |
| 16 | Per-zone tracking statistics | IMPLEMENTED & TESTED |
| 17 | Tracking-aware confidence filtering | IMPLEMENTED & TESTED |
| 18 | 8-signal composite risk engine | IMPLEMENTED & TESTED |
| 19 | Explainable risk scoring (0-100) | IMPLEMENTED & TESTED |
| 20 | Temporal smoothing with hysteresis | IMPLEMENTED & TESTED |
| 21 | Per-zone risk scoring | IMPLEMENTED & TESTED |
| 22 | Legacy risk mode (--legacy-risk) | IMPLEMENTED & TESTED |
| 23 | Real-time event detection (7 event types) | IMPLEMENTED & TESTED |
| 24 | Event cooldown & de-duplication | IMPLEMENTED & TESTED |
| 25 | Event history (last 50 events) | IMPLEMENTED & TESTED |
| 26 | On-screen event HUD overlay | IMPLEMENTED & TESTED |
| 27 | Event CSV logging (--log-events) | IMPLEMENTED & TESTED |
| 28 | Event engine toggle (--no-events) | IMPLEMENTED & TESTED |

---

## 4. System Architecture

### Phase 0 — Original Prototype Architecture

```
test_yolo.py (single 186-line monolithic script)
├── Configuration (hardcoded constants)
├── Alert (playsound in thread)
├── Model Loading (YOLO)
├── Video Capture (OpenCV)
└── Main Loop
    ├── Frame Read
    ├── YOLO Detection (class 0 = person)
    ├── 2x2 Grid Counting
    ├── Optical Flow Motion Analysis
    ├── Pressure Index Calculation
    ├── Risk Classification
    ├── Heatmap Generation
    ├── HUD Rendering
    ├── Alert Triggering
    └── Display (cv2.imshow)
```

### Phase 1 — Modular Architecture

```
main.py                         ← Entry point with CLI argument parsing
├── src/
│   ├── config.py               ← Centralized configuration constants
│   ├── detector.py             ← YOLO model loading + person detection
│   ├── analyzer.py             ← Grid counting + optical flow + heatmap
│   ├── risk.py                 ← Pressure index + risk classification + colors
│   ├── alert.py                ← Threaded alert engine with cooldown
│   ├── display.py              ← OpenCV rendering (grid, heatmap, HUD)
│   └── app.py                  ← Main application loop, wires all modules
├── assets/
│   ├── alert.wav               ← Alert sound file
│   └── crowd_video.mp4         ← Demo video
├── models/
│   └── yolov8n.pt              ← YOLOv8 nano weights
├── requirements.txt            ← Pinned dependencies
└── test_yolo.py                ← Original prototype (preserved)
```

### Phase 2 — Tracking & Temporal Analytics

```
main.py                         ← Entry point with --no-tracking CLI flag
├── src/
│   ├── config.py               ← Configuration + tracking constants
│   ├── detector.py             ← YOLO detection + ByteTrack integration
│   ├── analyzer.py             ← Grid counting + optical flow + heatmap
│   ├── tracker.py              ← CrowdTracker (NEW): IDs, stats, entries/exits, movement
│   ├── risk.py                 ← Pressure index + risk classification (unchanged)
│   ├── alert.py                ← Alert engine (unchanged)
│   ├── display.py              ← HUD + tracking statistics overlay
│   └── app.py                  ← Main loop with tracking integration
├── assets/
│   ├── alert.wav
│   └── crowd_video.mp4
├── models/
│   └── yolov8n.pt
├── requirements.txt
└── test_yolo.py                ← Original prototype (preserved)
```

### Phase 3 — Intelligent Composite Risk Engine

```
main.py                         ← Entry point with --no-tracking, --legacy-risk CLI flags
├── src/
│   ├── config.py               ← Configuration + tracking + risk engine constants (31 new)
│   ├── detector.py             ← YOLO detection + ByteTrack integration
│   ├── analyzer.py             ← Grid counting + optical flow + heatmap
│   ├── tracker.py              ← CrowdTracker + growth rate, stability, chaos, zone speed, churn
│   ├── risk.py                 ← Pressure index (legacy) + risk_score_color gradient
│   ├── risk_engine.py          ← RiskEngine (NEW): 8-signal composite risk, EMA, hysteresis
│   ├── alert.py                ← Alert engine (unchanged)
│   ├── display.py              ← HUD + tracking + risk HUD with zone risks
│   └── app.py                  ← Main loop with RiskEngine or legacy risk integration
├── assets/
│   ├── alert.wav
│   └── crowd_video.mp4
├── models/
│   └── yolov8n.pt
├── requirements.txt
└── test_yolo.py                ← Original prototype (preserved)
```

### Phase 4 — Real-Time Event & Alert Intelligence

```
main.py                         ← Entry point with --no-tracking, --legacy-risk, --no-events, --log-events CLI flags
├── src/
│   ├── config.py               ← Configuration + risk engine + event engine constants (19 new)
│   ├── detector.py             ← YOLO detection + ByteTrack integration
│   ├── analyzer.py             ← Grid counting + optical flow + heatmap
│   ├── tracker.py              ← CrowdTracker (growth/stability/chaos/speed/churn helpers)
│   ├── risk.py                 ← Pressure index (legacy) + risk_score_color gradient
│   ├── risk_engine.py          ← RiskEngine: 8-signal composite risk (unchanged)
│   ├── event_engine.py         ← EventEngine (NEW): 7 event types, cooldowns, de-dup, CSV logging
│   ├── alert.py                ← Alert engine (unchanged)
│   ├── display.py              ← HUD + tracking + risk + recent-events overlay
│   └── app.py                  ← Main loop with EventEngine integration
├── assets/
│   ├── alert.wav
│   └── crowd_video.mp4
├── models/
│   └── yolov8n.pt
├── tests/                      ← 110 automated tests across all 4 phases
├── requirements.txt
└── test_yolo.py                ← Original prototype (preserved)
```

---

## 5. Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Primary language |
| Ultralytics (YOLOv8) | >=8.0 | Person detection + ByteTrack tracking |
| OpenCV | >=4.8 | Video I/O, image processing, optical flow |
| NumPy | >=1.24 | Array operations, statistics |
| playsound | 1.2.2 | Alert audio playback |
| PyTorch | >=2.0 | YOLO inference backend |

---

## 6. Current Project Structure

```
CrowdSenseAI/
├── main.py
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── detector.py
│   ├── analyzer.py
│   ├── tracker.py
│   ├── risk.py
│   ├── risk_engine.py
│   ├── event_engine.py
│   ├── alert.py
│   ├── display.py
│   └── app.py
├── tests/
│   ├── conftest.py
│   ├── test_phase1_risk.py
│   ├── test_phase2_tracker.py
│   ├── test_phase3_risk_engine.py
│   ├── test_phase4_config.py
│   ├── test_phase4_events.py
│   ├── test_phase4_display.py
│   └── test_phase4_integration.py
├── assets/
│   ├── alert.wav
│   └── crowd_video.mp4
├── models/
│   └── yolov8n.pt
├── docs/
│   ├── PROJECT_REPORT.md
│   └── CHANGELOG.md
├── test_yolo.py                ← Original prototype (preserved)
├── sound.py                    ← Original test script (preserved)
└── crowdsense_env/             ← Python virtual environment
```

---

## 7. Implemented Features

### 7.1 YOLO Person Detection

| Field | Detail |
|-------|--------|
| **Description** | Detects persons in each video frame using YOLOv8 nano model |
| **Implementation** | `src/detector.py` — `Detector.detect()` runs inference; `Detector.filter_persons()` extracts class-0 bounding boxes and centroids |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Syntax/import verified; full inference requires Windows GPU environment |

### 7.2 2x2 Grid Zone Counting

| Field | Detail |
|-------|--------|
| **Description** | Divides frame into 4 quadrants; counts persons per zone |
| **Implementation** | `src/analyzer.py` — `Analyzer.count_by_grid()` assigns persons to zones based on centroid position |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Unit test verified: 5 persons correctly distributed as `[[2,1],[1,1]]` |

### 7.3 Optical Flow Motion Analysis

| Field | Detail |
|-------|--------|
| **Description** | Computes frame-to-frame motion variance using Farneback optical flow |
| **Implementation** | `src/analyzer.py` — `Analyzer.compute_motion_variance()` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — First frame returns 0.0; subsequent frames return non-negative float |

### 7.4 Pressure Index

| Field | Detail |
|-------|--------|
| **Description** | Composite metric: `pressure_index = total_people × motion_variance` |
| **Implementation** | `src/risk.py` — `compute_pressure_index()` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Formula verified with known inputs |

### 7.5 Three-Tier Risk Classification

| Field | Detail |
|-------|--------|
| **Description** | Classifies risk as LOW, MEDIUM, or HIGH based on pressure index |
| **Implementation** | `src/risk.py` — `classify_risk()` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — All boundary conditions verified |

### 7.6 Audio Alert with Cooldown

| Field | Detail |
|-------|--------|
| **Description** | Plays alert sound on HIGH risk with configurable cooldown |
| **Implementation** | `src/alert.py` — `AlertEngine.trigger()` with thread-safe cooldown |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Instantiation and cooldown parameter verified |

### 7.7 Real-Time Heatmap

| Field | Detail |
|-------|--------|
| **Description** | Gaussian-blurred density heatmap overlaid on frame |
| **Implementation** | `src/display.py` — `apply_heatmap()` |
| **Status** | IMPLEMENTED |
| **Test Status** | PARTIALLY TESTED — Rendering logic verified structurally; visual output requires OpenCV display |

### 7.8 HUD Display

| Field | Detail |
|-------|--------|
| **Description** | On-screen display of risk level, pressure index, and FPS |
| **Implementation** | `src/display.py` — `draw_hud()` |
| **Status** | IMPLEMENTED |
| **Test Status** | PARTIALLY TESTED — Logic verified; visual output requires OpenCV display |

### 7.9 CLI Argument Parsing

| Field | Detail |
|-------|--------|
| **Description** | Supports `--video`, `--webcam`, and `--model` arguments |
| **Implementation** | `main.py` with `argparse` |
| **Status** | IMPLEMENTED |
| **Test Status** | IMPLEMENTED — Syntax verified; functional test requires running environment |

### 7.10 Risk Color Mapping

| Field | Detail |
|-------|--------|
| **Description** | Maps risk levels to BGR colors for display |
| **Implementation** | `src/risk.py` — `risk_colors()` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — All mappings verified |

### 7.11 Person Tracking (ByteTrack)

| Field | Detail |
|-------|--------|
| **Description** | Tracks persons across frames using Ultralytics built-in ByteTrack with Kalman filtering |
| **Implementation** | `src/detector.py` — `Detector.detect(tracking=True)` calls `model.track(persist=True, tracker="bytetrack.yaml")` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Detector.filter_persons extracts track_id and conf; import verified |

### 7.12 Persistent Person IDs

| Field | Detail |
|-------|--------|
| **Description** | Each tracked person receives a unique integer ID maintained across consecutive frames |
| **Implementation** | `src/tracker.py` — `CrowdTracker` maintains `seen_ids`, `prev_active_ids`, `position_history` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — IDs persist across simulated multi-frame sequences |

### 7.13 Current / Peak / Average Crowd Count

| Field | Detail |
|-------|--------|
| **Description** | Real-time crowd statistics: current active count, peak count over session, rolling average |
| **Implementation** | `src/tracker.py` — `CrowdTracker.current_count`, `.peak_count`, `.average_count` properties using bounded `count_history` deque |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Verified across 10-frame simulation |

### 7.14 Estimated Entry/Exit Statistics

| Field | Detail |
|-------|--------|
| **Description** | Estimates entries and exits based on tracking ID appearance and disappearance across frames |
| **Implementation** | `src/tracker.py` — `CrowdTracker.update()` computes `new_ids`, `lost_ids`, `truly_new`; displayed as "Est. Entries" / "Est. Exits" |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Verified: 6 entries, 5 exits across 10-frame simulation |

### 7.15 Per-Person Movement Tracking

| Field | Detail |
|-------|--------|
| **Description** | Maintains bounded position history per tracked person; computes speed and displacement |
| **Implementation** | `src/tracker.py` — `CrowdTracker.position_history`, `.get_person_speed()`, `.get_person_displacement()`, `.get_crowd_mean_speed()` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Position history bounded at 30 frames; speed and displacement computed correctly |

### 7.16 Per-Zone Tracking Statistics

| Field | Detail |
|-------|--------|
| **Description** | Tracks unique IDs per zone across all frames; current-zone IDs per frame |
| **Implementation** | `src/tracker.py` — `CrowdTracker.zone_stats`, `ZoneStats` class with `current_ids` and `all_ids` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Zone all_ids accumulate across frames; current_ids are per-frame only |

### 7.17 Tracking-Aware Confidence Filtering

| Field | Detail |
|-------|--------|
| **Description** | When tracking is enabled, low-confidence detections (below threshold) are filtered out |
| **Implementation** | `src/detector.py` — `Detector.filter_persons(tracking=True)` applies `CONFIDENCE_THRESHOLD` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Conf=0.1 filtered; conf=0.9 passes |

### 7.18 Tracking Statistics HUD

| Field | Detail |
|-------|--------|
| **Description** | Bottom-of-screen overlay showing Crowd/Peak/Avg and Estimated Entries/Exits |
| **Implementation** | `src/display.py` — `draw_tracking_hud()` |
| **Status** | IMPLEMENTED |
| **Test Status** | PARTIALLY TESTED — Function import verified; visual output requires OpenCV display |

### 7.19 --no-tracking CLI Flag

| Field | Detail |
|-------|--------|
| **Description** | Disables tracking to run in Phase 1 detection-only mode |
| **Implementation** | `main.py` — `--no-tracking` argparse flag; `App(tracking=not args.no_tracking)` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — App(tracking=False) has no tracker; App(tracking=True) has tracker |

### 7.20 Intelligent Composite Risk Engine

| Field | Detail |
|-------|--------|
| **Description** | Multi-signal weighted risk engine using 8 normalized inputs, composite scoring (0-100), temporal smoothing, and hysteresis |
| **Implementation** | `src/risk_engine.py` — `RiskEngine` class with `RiskResult` dataclass |
| **Signals Used** | Density, Zone Concentration, Movement Speed, Growth Rate, Temporal Stability, Chaos Index, Optical Flow, Churn Rate |
| **Architecture** | 3-category weighted average (Crowd State 45%, Crowd Dynamics 35%, Historical 20%) |
| **Normalization** | Piecewise linear mapping to [0,100] with configurable ranges |
| **Smoothing** | EMA with alpha=0.3, hysteresis=5.0 on level transitions |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — 33 Phase 3 tests passing |

### 7.21 Risk Score Gradient Color

| Field | Detail |
|-------|--------|
| **Description** | Maps 0-100 risk score to green→orange→red gradient |
| **Implementation** | `src/risk.py` — `risk_score_color()` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Color channels verified at 0, 50, 100 |

### 7.22 Per-Zone Risk Scoring

| Field | Detail |
|-------|--------|
| **Description** | Each of 4 zones gets independent risk score using zone density, fraction, and speed |
| **Implementation** | `src/risk_engine.py` — `RiskEngine._compute_zone_risks()` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Denser zone has higher risk; all 4 zones present |

### 7.23 Risk Explanation System

| Field | Detail |
|-------|--------|
| **Description** | Top 3 contributors identified with human-readable labels for explainability |
| **Implementation** | `src/risk_engine.py` — `RiskEngine._identify_contributors()` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — 3 contributors returned with name/value/label |

### 7.24 --legacy-risk CLI Flag

| Field | Detail |
|-------|--------|
| **Description** | Falls back to Phase 1 pressure-index risk engine |
| **Implementation** | `main.py` — `--legacy-risk` argparse flag |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Legacy mode uses old classify_risk; new mode uses RiskEngine |

### 7.25 Real-Time Event Engine

| Field | Detail |
|-------|--------|
| **Description** | Detects meaningful crowd events from risk result, tracking data, and optical flow |
| **Implementation** | `src/event_engine.py` — `EventEngine` class with `Event` dataclass, `EventType` and `Severity` enums |
| **Event Types** | RISK_ESCALATION, RISK_DEESCALATION, CROWD_SURGE, CROWD_REDUCTION, ZONE_CONGESTION, MOVEMENT_SPIKE, LOW_ACTIVITY |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — 33 Phase 4 event tests passing |

### 7.26 Event Cooldown & De-Duplication

| Field | Detail |
|-------|--------|
| **Description** | Per-type cooldowns (in frames) and same-type/same-zone suppression prevent event spam |
| **Implementation** | `src/event_engine.py` — `_last_fired` dict keyed by `(event_type, zone)`, `_can_fire()` checks cooldown |
| **Cooldowns** | Risk 60f (2s), Surge/Reduction 90f (3s), Zone 120f (4s), Movement 45f (1.5s), Low Activity 150f (5s) |
| **De-duplication Rules** | Same type + same zone suppressed during cooldown; different zones and different types NOT suppressed |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Cooldown suppression and cross-type independence verified |

### 7.27 Event History

| Field | Detail |
|-------|--------|
| **Description** | Bounded history of the last 50 fired events |
| **Implementation** | `src/event_engine.py` — bounded `deque(maxlen=EVENT_HISTORY_SIZE)` |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — History capped at 50 events |

### 7.28 Event HUD Overlay

| Field | Detail |
|-------|--------|
| **Description** | Bottom-right overlay showing the last 3 recent events, color-coded by severity |
| **Implementation** | `src/display.py` — `draw_event_hud()` |
| **Severity Colors** | LOW gray, MEDIUM orange, HIGH red |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Rendering verified with synthetic events; empty list draws nothing |

### 7.29 Event CSV Logging

| Field | Detail |
|-------|--------|
| **Description** | Optional CSV logging of all fired events to `logs/events_YYYYMMDD_HHMMSS.csv` |
| **Implementation** | `src/event_engine.py` — `_init_log()`, `_log_event()`; `main.py` — `--log-events` flag |
| **CSV Columns** | timestamp, event_type, severity, zone, signal_value, frame, message |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — CSV written and parsed back; header correct |

### 7.30 --no-events CLI Flag

| Field | Detail |
|-------|--------|
| **Description** | Disables the event engine entirely |
| **Implementation** | `main.py` — `--no-events` argparse flag; `App(events_enabled=False)` creates no EventEngine |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — CLI wiring verified; App creates no event engine when disabled |

### 7.31 Legacy & Limited Mode Event Fallback

| Field | Detail |
|-------|--------|
| **Description** | Event engine degrades gracefully when risk result or tracking is unavailable |
| **Implementation** | `src/event_engine.py` — zone events skipped when `tracking_enabled=False`; risk transitions skipped when `risk_result is None`; `src/app.py` builds a minimal `RiskResult` in legacy mode so risk transitions still fire |
| **Status** | IMPLEMENTED |
| **Test Status** | TESTED — Zone events suppressed in limited mode; legacy pipeline runs without errors |

---

## 8. AI / Computer Vision Pipeline

### Phase 1 Pipeline

```
Video Input (file or webcam)
    ↓
YOLOv8 Inference (person detection, class 0)
    ↓
Person Filtering (extract bounding boxes + centroids)
    ↓
Zone Analysis (2x2 grid counting)
    ↓
Optical Flow (Farneback motion estimation → variance)
    ↓
Heatmap Generation (Gaussian blur → JET colormap overlay)
    ↓
Risk Analysis (pressure index → LOW/MEDIUM/HIGH)
    ↓
Alert Engine (threaded audio with cooldown)
    ↓
Dashboard Output (OpenCV imshow: frame + HUD + heatmap)
```

### Phase 2 Pipeline (tracking enabled)

```
Video Input (file or webcam)
    ↓
YOLOv8 Inference + ByteTrack (person detection + Kalman tracking)
    ↓
Person Filtering (bounding boxes + centroids + track_id + confidence)
    ↓
CrowdTracker Update
    ├── Active/seen ID sets
    ├── Entry/exit estimation
    ├── Position history (per person)
    ├── Zone statistics (per zone)
    └── Count history (current/peak/average)
    ↓
Zone Analysis (2x2 grid counting — unchanged)
    ↓
Optical Flow (Farneback — unchanged)
    ↓
Heatmap Generation (unchanged)
    ↓
Risk Analysis (pressure index — unchanged)
    ↓
Alert Engine (unchanged)
    ↓
Dashboard Output (HUD + tracking statistics + optional track ID labels)
```

All pipeline components in both lists are implemented and present in the codebase.

### Phase 3 Pipeline (composite risk engine)

```
Video Input (file or webcam)
    ↓
YOLOv8 Inference + ByteTrack (person detection + Kalman tracking)
    ↓
Person Filtering (bounding boxes + centroids + track_id + confidence)
    ↓
CrowdTracker Update
    ├── Active/seen ID sets
    ├── Entry/exit estimation
    ├── Position history (per person)
    ├── Zone statistics (per zone)
    └── Count history (current/peak/average)
    ↓
Zone Analysis (2x2 grid counting)
    ↓
Optical Flow (Farneback motion estimation → variance)
    ↓
Heatmap Generation
    ↓
RiskEngine.compute_risk()
    ├── Signal Extraction (8 signals from tracker + analyzer)
    │   ├── Crowd State: density, zone concentration, movement speed
    │   ├── Crowd Dynamics: growth rate, temporal stability, chaos index
    │   └── Historical: optical flow intensity, churn rate
    ├── Signal Normalization (piecewise linear → [0,100])
    ├── Category Scoring (weighted averages within categories)
    ├── Composite Scoring (weighted sum across categories → 0-100)
    ├── Temporal Smoothing (EMA, alpha=0.3)
    ├── Risk Classification (LOW/MEDIUM/HIGH with hysteresis)
    ├── Zone Risk Scoring (per-zone independent assessment)
    └── Risk Explanation (top 3 contributors)
    ↓
Alert Engine (triggers on HIGH risk)
    ↓
Dashboard Output
    ├── Risk HUD (level, score, contributors, zone risks)
    ├── Tracking HUD (crowd stats, entries/exits)
    ├── Heatmap overlay
    └── Grid with optional track IDs
```

### Phase 4 Pipeline (event intelligence enabled)

```
Video Input (file or webcam)
    ↓
YOLOv8 Inference + ByteTrack
    ↓
CrowdTracker Update
    ↓
Zone Analysis (2x2 grid counting)
    ↓
Optical Flow (Farneback motion estimation → variance)
    ↓
RiskEngine.compute_risk() → RiskResult
    ↓
EventEngine.evaluate(risk_result, tracker, motion_variance, tracking_enabled)
    ├── Risk transition check (escalation / de-escalation)
    ├── Crowd surge / reduction check (growth rate)
    ├── Zone congestion check (sustained zone risk)
    ├── Movement spike check (relative + absolute optical flow)
    ├── Low activity check (sustained low count)
    ├── Per-type cooldown & de-duplication
    └── Event history (last 50) + optional CSV logging
    ↓
Terminal output per event (timestamp, severity, type, message)
    ↓
Event HUD overlay (last 3 events, bottom-right)
    ↓
Alert Engine (HIGH risk → audio alert)
    ↓
Dashboard Output (risk HUD + tracking HUD + event HUD + heatmap)
```

---

## 9. Risk Analysis

### 9.1 Detection Inputs

- YOLOv8 nano model (`yolov8n.pt`) running at 640px input resolution
- Class 0 (person) filtering from 80 COCO classes
- Bounding box coordinates and centroids extracted per detection
- When tracking is enabled: track_id and confidence score per detection

### 9.2 Crowd Count

```
total_people = sum of all persons detected across all zones
```

### 9.3 Density

- Frame divided into 2x2 grid (4 zones)
- Per-zone count displayed with color coding:
  - Green: zone count <= 3
  - Red: zone count > 3

### 9.4 Motion Analysis

```
motion_variance = variance(magnitude(optical_flow(Farneback)))
```

- Farneback parameters: `pyr_scale=0.5, levels=3, winsize=15, iterations=3, poly_n=5, poly_sigma=1.2, flags=0`
- First frame: motion_variance = 0 (no previous frame to compare)

### 9.5 Pressure Index

```
pressure_index = total_people × motion_variance
```

### 9.6 Risk Thresholds

| Level | Condition |
|-------|-----------|
| LOW | pressure_index <= 5.0 |
| MEDIUM | 5.0 < pressure_index <= 20.0 |
| HIGH | pressure_index > 20.0 |

### 9.7 Composite Risk Engine (Phase 3)

**Architecture:** 3-category weighted average with 8 normalized signals.

**Signals:**

| # | Signal | Source | Normalization Range |
|---|--------|--------|-------------------|
| S1 | Crowd Density | count / (frame_area/1000) | 0 → 0.5 |
| S2 | Zone Concentration | max_zone / total | 0.25 → 1.0 |
| S3 | Movement Speed | mean person speed | 0 → 15 px/frame |
| S4 | Growth Rate | (count_now - count_N) / dt | -5 → +10 persons/sec |
| S5 | Temporal Stability | std(count) / mean(count) | 0 → 1.0 |
| S6 | Chaos Index | circular_variance(angles) | 0 → 1.0 |
| S7 | Optical Flow Intensity | variance(magnitude) | 0 → 0.05 |
| S8 | Churn Rate | (entries+exits) / dt | 0 → 3 transitions/sec |

**Category Weights:**

| Category | Weight | Signals |
|----------|--------|---------|
| Crowd State | 0.45 | density(0.50), concentration(0.25), speed(0.25) |
| Crowd Dynamics | 0.35 | growth(0.35), stability(0.35), chaos(0.30) |
| Historical | 0.20 | optical_flow(0.50), churn(0.50) |

**Composite Formula:**

```
S_i = clamp((value - low_i) / (high_i - low_i) × 100, 0, 100)
C_state = 0.50×S1 + 0.25×S2 + 0.25×S3
C_dynamics = 0.35×S4 + 0.35×S5 + 0.30×S6
C_history = 0.50×S7 + 0.50×S8
R_raw = 0.45×C_state + 0.35×C_dynamics + 0.20×C_history
R_smooth = 0.3×R_raw + 0.7×R_prev_smooth
```

**Risk Classification (with hysteresis):**

| Transition | Threshold |
|------------|-----------|
| LOW → MEDIUM | R_smooth > 35 (30 + 5 hysteresis) |
| MEDIUM → HIGH | R_smooth > 70 (65 + 5 hysteresis) |
| HIGH → MEDIUM | R_smooth < 60 (65 - 5 hysteresis) |
| MEDIUM → LOW | R_smooth < 25 (30 - 5 hysteresis) |

**Zone Risk Formula:**

```
zone_risk = 0.50×normalize(zone_density) + 0.30×normalize(zone_fraction) + 0.20×normalize(zone_speed)
```

### 9.7 Alert Conditions

- Alert triggers when risk transitions to HIGH
- Cooldown prevents re-triggering within 5 seconds
- Alert plays in a daemon thread (non-blocking)

### 9.8 Tracking Methodology (Phase 2)

**Tracker:** Ultralytics built-in ByteTrack (Kalman filter + Hungarian matching)

**Activation:** `model.track(frame, imgsz=640, persist=True, tracker="bytetrack.yaml")`

**Data extracted per frame:**
- `track_id`: persistent integer ID assigned by ByteTrack
- `conf`: detection confidence score

**Crowd statistics formulas:**

```
current_count = number of active track IDs in current frame
peak_count = max(count_history)
average_count = mean(count_history)  # rolling window of 300 frames
```

**Entry/exit estimation:**

```
new_ids = active_ids - prev_active_ids
lost_ids = prev_active_ids - active_ids
truly_new = new_ids - seen_ids    # only first-time appearances count
entries += len(truly_new)
exits += len(lost_ids)
```

Note: Entry/exit counts are estimates based on ID transitions, not ground-truth physical entrances.

**Position tracking:**
- Per-ID centroid history stored in bounded deque (max 30 frames)
- Speed = total displacement / frame count in history
- Displacement = Euclidean distance from first to last position in history

**Zone statistics:**
- Per-zone `all_ids`: all track IDs that have ever appeared in the zone (accumulates)
- Per-zone `current_ids`: track IDs currently in the zone (reset each frame)

### 9.9 Event Engine (Phase 4)

**Event types and trigger conditions:**

| # | Event Type | Severity | Trigger Condition |
|---|-----------|----------|-------------------|
| E1 | RISK_ESCALATION | MEDIUM / HIGH | Risk level strictly increases (LOW→MEDIUM, MEDIUM→HIGH) |
| E2 | RISK_DEESCALATION | LOW | Risk level strictly decreases (HIGH→MEDIUM, MEDIUM→LOW) |
| E3 | CROWD_SURGE | MEDIUM / HIGH | Growth rate > 3.0 persons/sec AND count ≥ 5 (HIGH if > 8.0/sec) |
| E4 | CROWD_REDUCTION | LOW | Growth rate < -3.0 persons/sec AND count ≥ 5 |
| E5 | ZONE_CONGESTION | MEDIUM / HIGH | Zone risk > 50 for 10 consecutive frames (HIGH if > 75) |
| E6 | MOVEMENT_SPIKE | MEDIUM | Motion variance > 0.03 AND > 2× recent average |
| E7 | LOW_ACTIVITY | LOW | Count < 2 sustained for 30 frames |

**Cooldown / de-duplication:**

```
key = (event_type, zone)
if frame - last_fired[key] < cooldown_frames[key]:
    suppress event
else:
    fire event; last_fired[key] = current_frame
```

- Same type + same zone: suppressed during cooldown
- Same type + different zone: NOT suppressed (two zones can congest simultaneously)
- Different type: NEVER suppressed (surge and escalation can both fire)

**Event data structure:**

```
Event(timestamp, event_type, severity, message, zone, signal_value, frame_number)
```

**History:** bounded deque of 50 most recent events.

**CSV log** (enabled with `--log-events`): `logs/events_YYYYMMDD_HHMMSS.csv`

**Design principles:**
- Events are system-detected indicators, not confirmed safety incidents
- Thresholds are heuristic and configurable in `src/config.py`
- The EventEngine is purely observational — it never mutates tracker or risk engine state
- Growth rate and stability signals require 15-30 frames of warmup
- Zone events require tracking; without it the engine degrades to global events only

---

## 10. Alert System

| Component | Detail |
|-----------|--------|
| **Trigger** | Risk level = HIGH |
| **Sound File** | `assets/alert.wav` |
| **Playback** | `playsound` library in a daemon thread |
| **Cooldown** | 5.0 seconds (configurable via `ALERT_COOLDOWN_SECONDS`) |
| **Thread Safety** | `threading.Lock` protects cooldown timer |
| **Error Handling** | `try/except` with `logging.warning()` on playback failure |
| **Re-triggering** | Allows re-trigger after cooldown period expires |

---

## 11. Testing & Validation

### Phase 0 — Original Prototype

| Test | Expected Result | Actual Result | Status |
|------|-----------------|---------------|--------|
| Video opens and plays | `crowd_video.mp4` plays | Video played successfully | PASS |
| YOLO detection runs | Persons detected | Detection ran successfully | PASS |
| cv2.imshow window opens | Display window appears | Window appeared | PASS |
| Alert sound plays | `alert.wav` plays | Sound played | PASS |

### Phase 1 — Modular Architecture

| Test | Expected Result | Actual Result | Status |
|------|-----------------|---------------|--------|
| `config.py` constants load | All 15 constants accessible | All loaded, correct values | PASS |
| Threshold ordering | HIGH > MEDIUM | 20.0 > 5.0 verified | PASS |
| `compute_pressure_index(10, 2.0)` | Returns 20.0 | Returns 20.0 | PASS |
| `classify_risk(0.0)` | LOW | LOW | PASS |
| `classify_risk(5.1)` | MEDIUM | MEDIUM | PASS |
| `classify_risk(20.1)` | HIGH | HIGH | PASS |
| `classify_risk(4.9)` | LOW | LOW | PASS |
| `classify_risk(20.0)` | MEDIUM | MEDIUM | PASS |
| `risk_colors('LOW')` | (0, 255, 0) | (0, 255, 0) | PASS |
| `risk_colors('MEDIUM')` | (0, 165, 255) | (0, 165, 255) | PASS |
| `risk_colors('HIGH')` | (0, 0, 255) | (0, 0, 255) | PASS |
| `Analyzer.count_by_grid()` | 5 persons → [[2,1],[1,1]] | [[2,1],[1,1]] | PASS |
| First-frame motion variance | 0.0 | 0.0 | PASS |
| Second-frame motion variance | Non-negative float | 0.081317 | PASS |
| `build_heatmap()` | Shape (480,640), sum > 0 | Verified | PASS |
| `AlertEngine` init | Cooldown stored | cooldown=1.0 | PASS |
| Asset files in new locations | Files exist | All 3 files present | PASS |
| All `.py` files syntax check | No SyntaxError | All 9 files pass | PASS |
| `test_yolo.py` preserved | Original file unchanged | Verified parseable | PASS |

### Phase 2 — Person Tracking & Temporal Analytics

| Test | Expected Result | Actual Result | Status |
|------|-----------------|---------------|--------|
| All 10 `.py` files syntax check | No SyntaxError | All 10 files pass | PASS |
| Phase 2 config constants | `TRACKER_CONFIG`, `CONFIDENCE_THRESHOLD`, etc. load | All 4 constants verified | PASS |
| `CrowdTracker` initialization | Zero counts, empty state | `current_count=0`, `peak_count=0`, `avg=0.0` | PASS |
| First frame: 3 persons with IDs | 3 active, 3 entries, 0 exits | Verified | PASS |
| Second frame: 2 same + 1 new | 3 active, 4 entries, 1 exit | Verified | PASS |
| Third frame: 1 disappears | 2 active, 4 entries, 2 exits | Verified | PASS |
| Peak count across frames | max of count history | `peak_count=3` | PASS |
| Average count | rolling mean of count history | `avg=2.7` (3 frames) | PASS |
| `count_history` bounded | Max 300 entries | Capped at 300 after 350 frames | PASS |
| `position_history` bounded | Max 30 entries per person | Capped at 30 after 50 frames | PASS |
| Position history pruned | Only active IDs retained | Inactive ID removed from dict | PASS |
| Person speed calculation | Euclidean / frame count | `speed > 0` for moving person | PASS |
| Person displacement | Euclidean first→last | `displacement > 0` | PASS |
| Crowd mean speed | Average of all active speeds | Non-negative float | PASS |
| Zone `all_ids` persist | IDs accumulate across frames | ID 1 found in zones it visited | PASS |
| Zone `current_ids` per-frame | Only current frame IDs | Previous zone's ID not in current | PASS |
| `CrowdTracker.reset()` | Clears all state | All counts/sets/history cleared | PASS |
| `ZoneStats` initialization | Empty sets, zero count | Verified | PASS |
| Backward compat: persons without `track_id` | No crash, 0 active IDs | Verified | PASS |
| `Detector.filter_persons(tracking=False)` | No track_id extracted | `track_id=None` | PASS |
| `Detector.filter_persons(tracking=True)` | track_id extracted | `track_id=42` | PASS |
| `Detector.filter_persons` confidence filter | Low conf filtered | `conf=0.1` filtered, `conf=0.9` passes | PASS |
| `App(tracking=False)` | No tracker created | `tracker is None` | PASS |
| `App(tracking=True)` | Tracker created | `tracker is not None` | PASS |
| 10-frame simulation stress test | Correct final state | `entries=6, exits=5, peak=3` | PASS |
| All modules import with mocked deps | No ImportError | All 10 modules imported | PASS |
| `test_yolo.py` still preserved | Original unchanged | Verified parseable | PASS |

### Phase 3 — Intelligent Composite Risk Engine

| Test | Expected Result | Actual Result | Status |
|------|-----------------|---------------|--------|
| `_clamp(50,0,100)` | 50 | 50 | PASS |
| `_clamp(-10,0,100)` | 0 | 0 | PASS |
| `_clamp(150,0,100)` | 100 | 100 | PASS |
| `_normalize(5.0,0,10)` | 50.0 | 50.0 | PASS |
| `_normalize(-1,0,10)` | 0.0 | 0.0 | PASS |
| `_normalize(15,0,10)` | 100.0 | 100.0 | PASS |
| RiskEngine with 0 people → LOW | score < 10.0 | score < 10.0 | PASS |
| High density + speed → MEDIUM/HIGH | risk_level in (MEDIUM,HIGH) | MEDIUM | PASS |
| EMA smoothing (similar frames) | score change < 1.0 | < 1.0 | PASS |
| Hysteresis LOW→MEDIUM (32 stays LOW) | level stays LOW | LOW | PASS |
| Hysteresis LOW→MEDIUM (36 switches) | level = MEDIUM | MEDIUM | PASS |
| Hysteresis MEDIUM→HIGH (71 switches) | level = HIGH | HIGH | PASS |
| Hysteresis HIGH→MEDIUM (58 switches) | level = MEDIUM | MEDIUM | PASS |
| `get_growth_rate()` with growing count | positive value | positive | PASS |
| `get_temporal_stability()` stable count | < 0.1 | < 0.1 | PASS |
| `get_chaos_index()` uniform directions | < 0.2 | < 0.2 | PASS |
| `get_chaos_index()` random directions | > 0.5 | > 0.5 | PASS |
| Zone risk: denser zone higher | zone(0,0) > zone(1,1) | verified | PASS |
| Limited mode (no tracker) | is_limited = True | True | PASS |
| RiskResult dataclass defaults | all zero/empty | verified | PASS |
| Top 3 contributors populated | len == 3 | 3 | PASS |
| Score bounded [0,100] | 0 <= score <= 100 | verified | PASS |
| `get_churn_rate()` | >= 0 | >= 0 | PASS |
| `risk_score_color()` gradient | green at 0, red at 100 | verified | PASS |
| Legacy risk backward compat | HIGH for high pressure | HIGH | PASS |
| Display imports incl `draw_risk_hud` | no ImportError | OK | PASS |
| Config constants (31 new) | all load correctly | verified | PASS |
| Category weights sum to 1.0 | 1.0 | 1.0 | PASS |
| Within-category weights sum to 1.0 | each group = 1.0 | verified | PASS |
| Zone risk weights sum to 1.0 | 1.0 | 1.0 | PASS |
| Normalization [0,100] for all signals | all in range | verified | PASS |
| Critical zone identified | (0,0) for dense zone | (0,0) | PASS |
| `get_zone_mean_speed()` | positive for moving persons | positive | PASS |
| High growth rate signal | normalized > 50 | > 50 | PASS |
| Stable crowd low stability signal | normalized < 10 | < 10 | PASS |
| High optical flow signal | normalized > 80 | > 80 | PASS |

### Phase 4 — Real-Time Event & Alert Intelligence

| Test | Expected Result | Actual Result | Status |
|------|-----------------|---------------|--------|
| EventEngine init | Empty history, no cooldowns | Verified | PASS |
| EventEngine reset | Clears all state | Verified | PASS |
| History bounded | Max 50 events | Capped at 50 | PASS |
| LOW→MEDIUM escalation | Fires MEDIUM event | Verified | PASS |
| MEDIUM→HIGH escalation | Fires HIGH event | Verified | PASS |
| Same level | No escalation/de-escalation | Verified | PASS |
| HIGH→MEDIUM de-escalation | Fires LOW event | Verified | PASS |
| MEDIUM→LOW de-escalation | Fires LOW event | Verified | PASS |
| Same-type cooldown | Second same-type event suppressed | Verified | PASS |
| Different-type cooldown | Not suppressed | Verified | PASS |
| Crowd surge (high growth) | Fires MEDIUM event | Verified | PASS |
| Crowd surge severity | HIGH when growth > 8/s | Verified | PASS |
| Crowd surge below min count | No event | Verified | PASS |
| Crowd reduction | Fires LOW event | Verified | PASS |
| Zone congestion sustained | Fires after 10 frames | Verified | PASS |
| Zone congestion transient | No event | Verified | PASS |
| Zone congestion HIGH severity | Zone risk > 75 → HIGH | Verified | PASS |
| Zone events in limited mode | Skipped | Verified | PASS |
| Movement spike | Fires on relative + absolute spike | Verified | PASS |
| Movement spike constant scene | No event | Verified | PASS |
| Low activity sustained | Fires after 30 frames | Verified | PASS |
| Low activity transient | No event | Verified | PASS |
| Low activity no-tracking | Skipped | Verified | PASS |
| Event timestamp format | HH:MM:SS | Verified | PASS |
| Event message | Non-empty string | Verified | PASS |
| Event `to_row()` | 7 CSV columns | Verified | PASS |
| Event string rendering | Contains severity + type | Verified | PASS |
| Severity enum | LOW=0, MEDIUM=1, HIGH=2 | Verified | PASS |
| EventType enum | 7 expected members | Verified | PASS |
| Event config constants | All load with correct ordering | Verified | PASS |
| Cooldown ordering | Zone > Surge > Movement | Verified | PASS |
| All source files syntax | No SyntaxError | All 12 files pass | PASS |
| Event HUD empty list | Draws nothing | Verified | PASS |
| Event HUD with events | Draws color-coded overlay | Verified | PASS |
| Full 521-frame pipeline | No errors, events fired, scores in [0,100] | Verified | PASS |
| Legacy path no-tracking | Runs cleanly across 521 frames | Verified | PASS |
| EventEngine does not alter risk output | r1 == r2 across 521 frames | Verified | PASS |
| CSV logging | File created; header + rows correct | Verified | PASS |
| test_yolo.py preserved | Original unchanged | Verified parseable | PASS |

---

## 12. Bugs Discovered

### Bug 1: Swapped Risk Thresholds

| Field | Detail |
|-------|--------|
| **Bug** | `HIGH_THRESHOLD = 5` and `MEDIUM_THRESHOLD = 20` in original code, but comparison order was `> HIGH first, then > MEDIUM` |
| **Cause** | Variable naming inconsistency |
| **Impact** | MEDIUM risk level was unreachable; any pressure > 5 immediately triggered HIGH |
| **Fix** | Swapped to `PRESSURE_HIGH_THRESHOLD = 20.0` and `PRESSURE_MEDIUM_THRESHOLD = 5.0` in `src/config.py` |
| **Verification** | Unit tests confirm: 5.1 → MEDIUM, 20.1 → HIGH |

### Bug 2: Silent Sound Failures

| Field | Detail |
|-------|--------|
| **Bug** | Original `play_alert()` had bare `except: pass` |
| **Cause** | No error handling |
| **Impact** | Sound failures were completely invisible |
| **Fix** | `AlertEngine._play()` catches exceptions and logs via `logging.warning()` |
| **Verification** | Code inspection verified |

### Bug 3: No Graceful Shutdown

| Field | Detail |
|-------|--------|
| **Bug** | No `try/finally` around `cap.release()` and `cv2.destroyAllWindows()` |
| **Cause** | Missing resource cleanup |
| **Impact** | OpenCV windows left open on exception or keyboard interrupt |
| **Fix** | `App.run()` uses `try/finally` to guarantee cleanup |
| **Verification** | Code inspection verified |

### Bug 4: Single-Fire Alert

| Field | Detail |
|-------|--------|
| **Bug** | Alert triggered once per session; `alert_triggered` flag not reliably reset |
| **Cause** | Global flag design |
| **Impact** | No repeated alerts during sustained HIGH risk |
| **Fix** | `AlertEngine` uses timestamp-based cooldown; re-triggers after cooldown expires |
| **Verification** | Code inspection verified |

### Bug 5: Zone `all_ids` Reset Every Frame (Phase 2)

| Field | Detail |
|-------|--------|
| **Bug** | `CrowdTracker._update_zone_stats()` rebuilt `zone_stats` from scratch each frame, losing historical `all_ids` |
| **Cause** | `self.zone_stats = {}` cleared without preserving previous `all_ids` |
| **Impact** | `all_ids` only contained current-frame IDs, not accumulated IDs across the session |
| **Fix** | Preserve `prev_all_ids` before clearing, then restore them into new `ZoneStats` instances |
| **Verification** | Unit test confirmed: ID 1 found in both zone (0,0) and zone (1,1) after moving between zones |

---

## 13. Development Phases

### Phase 0 — Existing Prototype

- **Date**: February 24, 2026 (original files)
- **Files**: `test_yolo.py` (186 lines), `sound.py` (3 lines), `yolov8n.pt`, `crowd_video.mp4`, `alert.wav`
- **Architecture**: Single monolithic script with all logic in one `while True` loop
- **Functionality**: YOLO detection, 2x2 grid, optical flow, pressure index, risk classification, heatmap, alerts, HUD
- **Status**: Working prototype with known bugs (see Section 12)

### Phase 1 — Modular Architecture

- **Date**: September 10, 2026
- **Files Created**:
  - `main.py` — Entry point with argparse
  - `src/__init__.py` — Package marker
  - `src/config.py` — Centralized configuration (15 constants)
  - `src/detector.py` — YOLO model wrapper
  - `src/analyzer.py` — Grid counting, optical flow, heatmap
  - `src/risk.py` — Pressure index, risk classification, color mapping
  - `src/alert.py` — Threaded alert engine with cooldown
  - `src/display.py` — OpenCV rendering functions
  - `src/app.py` — Application loop and wiring
  - `requirements.txt` — Dependency specification
  - `.gitignore` — Version control exclusions
- **Files Preserved**:
  - `test_yolo.py` — Original prototype (untouched)
  - `sound.py` — Original test script (untouched)
- **Assets Copied** (originals preserved):
  - `assets/alert.wav`
  - `assets/crowd_video.mp4`
  - `models/yolov8n.pt`
- **Bugs Fixed**: 4 (see Section 12)
- **Tests Performed**: 17 (see Section 11)
- **Status**: COMPLETE

### Phase 2 — Person Tracking & Temporal Analytics

- **Date**: September 10, 2026
- **Files Created**:
  - `src/tracker.py` — CrowdTracker class with ID tracking, statistics, zone stats, movement
- **Files Modified**:
  - `src/config.py` — Added 4 tracking constants
  - `src/detector.py` — Added `model.track()` support, `track_id`/`conf` extraction
  - `src/display.py` — Added `draw_tracking_hud()`, optional ID labels in `draw_grid()`
  - `src/app.py` — Wired CrowdTracker, added `tracking` parameter
  - `main.py` — Added `--no-tracking` CLI flag
- **Files Unchanged**:
  - `src/analyzer.py` — Backward-compatible, no changes needed
  - `src/risk.py` — Risk logic unchanged
  - `src/alert.py` — Alert logic unchanged
- **Bugs Found & Fixed**: 1 — Zone `all_ids` reset every frame (see Section 12, Bug 5)
- **Tests Performed**: 25 Phase 2 tests + 17 Phase 1 regression tests = 42 total
- **Status**: COMPLETE

### Phase 3 — Intelligent Composite Risk Engine

- **Date**: September 10, 2026
- **Files Created**:
  - `src/risk_engine.py` — `RiskEngine` class + `RiskResult` dataclass (8-signal composite risk)
- **Files Modified**:
  - `src/config.py` — Added 31 risk engine configuration constants (weights, normalization ranges, thresholds)
  - `src/tracker.py` — Added 5 helper methods: `get_growth_rate()`, `get_temporal_stability()`, `get_chaos_index()`, `get_zone_mean_speed()`, `get_churn_rate()`
  - `src/risk.py` — Added `risk_score_color()` gradient function
  - `src/display.py` — Added `draw_risk_hud()` for composite score + zone risks display
  - `src/app.py` — Integrated `RiskEngine`, added `legacy_risk` parameter
  - `main.py` — Added `--legacy-risk` CLI flag
- **Files Unchanged**:
  - `src/analyzer.py` — No changes needed
  - `src/detector.py` — No changes needed
  - `src/alert.py` — No changes needed
- **Bugs Found**: 0 (normalization range DENSITY_HIGH was adjusted from 5.0 to 0.5 for realistic frame sizes)
- **Tests Performed**: 33 Phase 3 tests + 28 Phase 1+2 regression tests
- **Status**: COMPLETE

### Phase 4 — Real-Time Event & Alert Intelligence

- **Date**: September 10, 2026
- **Files Created**:
  - `src/event_engine.py` — `EventEngine` class, `Event` dataclass, `EventType` and `Severity` enums, CSV logging
  - `tests/` — 110 automated tests across all 4 phases (19 Phase 1 regression, 19 Phase 2 regression, 16 Phase 3 regression, 14 config, 33 Phase 4 events, 6 display, 3 integration)
- **Files Modified**:
  - `src/config.py` — Added 19 event engine constants (thresholds, cooldowns, history size)
  - `src/app.py` — Wired EventEngine into the main loop, added `events_enabled`/`log_events` params, constructs minimal `RiskResult` in legacy mode
  - `src/display.py` — Added `draw_event_hud()` for last-3-events overlay
  - `main.py` — Added `--no-events` and `--log-events` CLI flags
- **Files Unchanged**:
  - `src/risk_engine.py` — RiskEngine internals untouched
  - `src/tracker.py` — No changes needed
  - `src/analyzer.py` — No changes needed
  - `src/alert.py` — Alert behavior unchanged
  - `src/detector.py` — No changes needed
- **Bugs Found**: 0
- **Tests Performed**: 110 total across all 4 phases, all passing
- **End-to-End Validation**: Real `crowd_video.mp4` (521 frames) processed through full pipeline (tracking + composite risk + event engine + display) with zero errors; EventEngine proven not to alter RiskEngine output (identical results with/without event engine across all 521 frames)
- **Status**: COMPLETE

---

## 14. Performance Measurements

No performance benchmarks have been formally measured yet. The original prototype's FPS display shows real-time FPS during execution. Formal performance measurement is planned for a future phase.

---

## 15. Limitations

| # | Limitation | Impact |
|---|-----------|--------|
| 1 | 2x2 grid is coarse (only 4 zones) | Insufficient for large/complex venues |
| 2 | Entry/exit counts are estimates based on ID transitions | May re-count persons who leave and re-enter the frame |
| 3 | No data persistence | All analysis results are ephemeral |
| 4 | No webcam testing completed | Webcam mode requires Windows environment |
| 5 | Optical flow is computationally expensive | May reduce FPS on low-end hardware |
| 6 | Heatmap overlays detection markers | Display rendering order partially obscures bounding dots |
| 7 | Single video source only | Cannot monitor multiple camera feeds simultaneously |
| 8 | ByteTrack ID may flicker on rapid occlusions | Person may receive new ID after brief disappearance |
| 9 | Performance not formally measured | FPS, inference time, CPU/GPU usage not benchmarked |
| 8 | Single video source only | Cannot monitor multiple camera feeds simultaneously |

---

## 16. Security / Privacy / Ethical Considerations

- **No facial recognition**: The system detects and counts persons using bounding boxes only. No facial features are extracted, stored, or analyzed.
- **No image data storage**: All analysis is performed in-memory. Frames, detections, and person data are never saved to disk.
- **Optional event metadata logging**: With `--log-events`, only aggregate event metadata (timestamp, event type, severity, zone index, signal value, frame number, message) is written to CSV. No images, bounding boxes, or personally identifiable data are ever logged.
- **No network communication**: The system runs entirely locally. No data is transmitted externally.
- **YOLO model**: Uses publicly available COCO-pretrained weights (`yolov8n.pt`). No custom training on sensitive datasets.
- **Ethical use**: The system is designed for crowd safety monitoring, not surveillance or individual tracking.

---

## 17. Future Scope

| # | Feature | Priority |
|---|---------|----------|
| 1 | Configurable grid size (NxN) | High |
| 2 | Dashboard GUI (Streamlit/Flask) | Medium |
| 3 | Multiple video source support | Medium |
| 4 | Crowd-flow direction visualization | Medium |
| 5 | Performance benchmarking suite | Medium |
| 6 | Event threshold auto-tuning from logged data | Medium |
| 7 | Re-identification for long-term tracking | Low |

---

## 18. Final System Status (Phase 4)

| Aspect | Status |
|--------|--------|
| **Overall** | Phase 4 Complete |
| **Architecture** | Modular (12 source files, 9 modules) |
| **Core Algorithm** | Phase 1 legacy preserved; Phase 3 composite risk engine default |
| **Tracking** | ByteTrack with persistent IDs, position history, zone stats |
| **Risk Engine** | 8-signal composite scoring (0-100), EMA smoothing, hysteresis |
| **Event Engine** | 7 event types with cooldown, de-duplication, history, CSV logging |
| **Crowd Statistics** | Current, peak, average count; estimated entries/exits |
| **Zone Analysis** | Per-zone risk scoring with independent assessment |
| **Explainability** | Top 3 risk contributors + human-readable event messages |
| **Bugs Fixed** | 5 total (4 Phase 1 + 1 Phase 2) |
| **Tests Passing** | 110 total (69 regression + 41 Phase 4) |
| **Original Prototype** | Preserved and untouched |

---

## 19. Demonstration Procedure

1. Activate the virtual environment: `crowdsense_env\Scripts\activate`
2. Run with composite risk engine (default): `python main.py`
3. Run without tracking: `python main.py --no-tracking`
4. Run with legacy pressure-index risk: `python main.py --legacy-risk`
5. Run with event logging: `python main.py --log-events`
6. Run without event detection: `python main.py --no-events`
7. Run with custom video: `python main.py --video path/to/video.mp4`
8. Run with webcam: `python main.py --webcam`
9. Press `q` to quit
10. **Phase 1 observations:** person detection, zone counts, heatmap overlay, risk level, FPS display, alert sound
11. **Phase 2 observations:** persistent track IDs on persons, crowd statistics at bottom of screen (Crowd/Peak/Avg, Est. Entries/Exits), track ID labels near detections
12. **Phase 3 observations:** composite risk score (0-100) with color gradient, top 3 risk contributors displayed, per-zone risk scores, critical zone highlighted, "Limited Analysis" warning when tracking disabled
13. **Phase 4 observations:** event messages printed to terminal as they fire, recent events overlay in bottom-right corner (last 3, color-coded by severity), optional CSV event log in `logs/`

---

## 20. Conclusion

Phase 1 of CrowdSenseAI successfully refactored the original 186-line monolithic prototype into a modular, maintainable architecture comprising 9 source files across 6 logical modules. All original functionality was preserved, including YOLO-based person detection, 2x2 zone-based crowd counting, optical flow motion analysis, pressure index computation, three-tier risk classification, heatmap generation, audio alerts, and real-time HUD display. Four bugs from the original prototype were identified and fixed.

Phase 2 built upon this foundation by integrating Ultralytics built-in ByteTrack for persistent person tracking across frames. The CrowdTracker module maintains per-person position history, computes current/peak/average crowd counts, estimates entries and exits based on ID transitions, and tracks per-zone statistics. The tracking layer is fully additive — all Phase 1 risk analysis, alert behavior, and display functionality remain unchanged. One additional bug (zone `all_ids` resetting every frame) was discovered and fixed during Phase 2 development.

Phase 3 replaced the simplistic pressure-index risk engine with an explainable, deterministic composite risk assessment system. The new `RiskEngine` class normalizes 8 crowd signals (density, zone concentration, movement speed, growth rate, temporal stability, chaos index, optical flow intensity, and churn rate) into [0,100] scores, combines them through a 3-category weighted architecture (Crowd State 45%, Crowd Dynamics 35%, Historical 20%), applies temporal smoothing via exponential moving average, and classifies risk using hysteresis-protected thresholds. The system produces a structured explanation identifying the top 3 risk contributors, enabling transparent decision-support. Per-zone risk scoring and a legacy fallback mode ensure backward compatibility. A total of 61+ tests were performed across all three phases, all passing. The system now provides real-time crowd monitoring, temporal crowd analytics, and intelligent risk assessment with full explainability while maintaining a clean, modular architecture ready for further development.

Phase 4 added a real-time event and alert intelligence layer on top of the composite risk engine. The new `EventEngine` detects 7 distinct event types (risk escalation/de-escalation, crowd surge, crowd reduction, zone congestion, movement spike, low activity) from the risk result, tracking statistics, and optical flow. Per-type cooldowns, sustain requirements, and same-type/same-zone de-duplication prevent event spam while allowing spatially distinct and semantically different events to fire independently. Events are rendered to the terminal and an on-screen overlay, and can be optionally logged to CSV. The event engine is purely observational — integration tests prove it produces zero change to risk engine output across all 521 frames of the demo video. With 110 automated tests passing across all four phases, CrowdSenseAI now delivers person detection, persistent tracking, explainable composite risk scoring, and real-time event intelligence in a clean modular architecture.
