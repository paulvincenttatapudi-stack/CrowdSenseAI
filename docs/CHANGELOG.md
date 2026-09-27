# CrowdSenseAI — Changelog

## Phase 4 — Real-Time Event & Alert Intelligence (September 10, 2026)

### Added
- `src/event_engine.py` — Event intelligence engine with:
  - `Event` dataclass (timestamp, type, severity, message, zone, signal value, frame)
  - `EventType` and `Severity` enums
  - 7 event types:
    - `RISK_ESCALATION` — risk level increased (MEDIUM whenever firing, HIGH for →HIGH)
    - `RISK_DEESCALATION` — risk level decreased (LOW)
    - `CROWD_SURGE` — growth > 3.0 persons/sec (HIGH if > 8.0/sec)
    - `CROWD_REDUCTION` — growth < -3.0 persons/sec (LOW)
    - `ZONE_CONGESTION` — zone risk > 50 sustained for 10 frames (HIGH if > 75)
    - `MOVEMENT_SPIKE` — optical flow > 0.03 and > 2× recent average (MEDIUM)
    - `LOW_ACTIVITY` — count < 2 sustained for 30 frames (LOW)
  - Per-type cooldowns (frames): risk 60, surge/reduction 90, zone 120, movement 45, low activity 150
  - De-duplication via `_last_fired` keyed on `(event_type, zone)`
  - Bounded event history (50 events)
  - Optional CSV logging to `logs/events_YYYYMMDD_HHMMSS.csv`
- `src/config.py` — 19 new event engine constants:
  - Surge/reduction thresholds and minimum counts
  - Zone congestion thresholds + sustain frames
  - Movement spike threshold + ratio
  - Low activity threshold + sustain frames
  - Per-type cooldown values
  - `EVENT_HISTORY_SIZE` (50), `EVENT_MAX_DISPLAY` (3)
- `tests/` — 110 automated tests across all 4 phases (pytest)
- `main.py` — `--no-events` and `--log-events` CLI flags

### Changed
- `src/app.py`:
  - `App.__init__()` accepts `events_enabled` and `log_events` parameters
  - Creates `EventEngine` when enabled; passes through log configuration
  - Main loop evaluates events each frame, prints fired events to terminal
  - Legacy mode now builds a minimal `RiskResult` so risk-transition events still fire
- `src/display.py`:
  - Added `draw_event_hud(frame, events)` — last 3 events, bottom-right, color-coded by severity
- `src/config.py` — Added event engine configuration block
- `docs/PROJECT_REPORT.md` — Phase 4 architecture, features, tests, event definitions, demonstration procedure, conclusion
- `docs/CHANGELOG.md` — This entry

### Fixed
- Missing `EVENT_MAX_DISPLAY` import in `src/event_engine.py` (caught by unit test)

### Preserved (unchanged)
- `src/risk_engine.py` — RiskEngine internals completely unchanged
- `src/tracker.py` — No changes needed
- `src/analyzer.py` — No changes needed
- `src/alert.py` — Alert engine completely unchanged
- `src/detector.py` — No changes needed
- `test_yolo.py` — Original prototype untouched
- `sound.py` — Original test script untouched

### Tests
- 41 new Phase 4 tests performed, all passing (33 events, 6 display, 14 config, 3 integration; integration includes 521-frame end-to-end runs)
- 54 Phase 1+2+3 regression tests re-run, all passing
- Total: 110 tests passing across all phases
- End-to-end validation: full pipeline (tracking + composite risk + event engine + display) over all 521 frames of `crowd_video.mp4` with zero errors; EventEngine verified not to alter RiskEngine output

---

## Phase 3 — Intelligent Composite Risk Engine (September 10, 2026)

### Added
- `src/risk_engine.py` — Intelligent risk engine with:
  - 8-signal composite risk scoring (0-100)
  - 3-category weighted architecture (Crowd State, Crowd Dynamics, Historical)
  - Piecewise linear signal normalization with configurable ranges
  - EMA temporal smoothing (alpha=0.3)
  - Hysteresis-protected risk classification (LOW/MEDIUM/HIGH)
  - Per-zone independent risk scoring
  - Risk explanation system (top 3 contributors)
  - `RiskResult` dataclass for structured output
  - Limited-mode fallback (no tracker → reduced signal set)
- `src/config.py` — 31 new risk engine constants:
  - Smoothing/hysteresis/threshold parameters
  - Category weights (0.45, 0.35, 0.20)
  - Within-category weights (8 signal weights)
  - Normalization ranges (8 low/high pairs)
  - Zone risk weights (0.50, 0.30, 0.20)
- `src/tracker.py` — 5 new helper methods:
  - `get_growth_rate(window, fps)` — persons per second
  - `get_temporal_stability(window)` — coefficient of variation
  - `get_chaos_index()` — circular variance of movement angles
  - `get_zone_mean_speed(row, col, frame_h, frame_w)` — per-zone speed
  - `get_churn_rate(window, fps)` — entries+exits per second
- `src/risk.py` — `risk_score_color(score)` — green→orange→red gradient
- `src/display.py` — `draw_risk_hud(frame, risk_result, fps)` — composite risk display with zone risks
- `main.py` — `--legacy-risk` CLI flag

### Changed
- `src/app.py`:
  - `App.__init__()` accepts `legacy_risk` parameter
  - Creates `RiskEngine` instance when not in legacy mode
  - Main loop uses `RiskEngine.compute_risk()` or legacy `classify_risk()` based on flag
- `src/config.py`:
  - `DENSITY_HIGH` adjusted from 5.0 to 0.5 (realistic for 640x480 frames)
- `docs/PROJECT_REPORT.md` — Phase 3 architecture, features, tests, formulas, demonstration procedure, conclusion

### Fixed
- DENSITY_HIGH normalization range was unrealistic for typical video frame sizes

### Preserved (unchanged)
- `src/analyzer.py` — No changes needed
- `src/detector.py` — No changes needed
- `src/alert.py` — Alert engine completely unchanged
- `test_yolo.py` — Original prototype untouched
- `sound.py` — Original test script untouched

### Tests
- 33 new Phase 3 tests performed, all passing
- 28 Phase 1+2 regression tests re-run, all passing
- Total: 61+ tests passing across all phases

---

## Phase 2 — Person Tracking & Temporal Analytics (September 10, 2026)

### Added
- `src/tracker.py` — CrowdTracker class with:
  - Persistent person ID tracking via ByteTrack
  - Current, peak, and average crowd count
  - Estimated entry/exit statistics
  - Per-person position history (bounded at 30 frames)
  - Per-person speed and displacement calculation
  - Per-zone tracking statistics (current_ids and all_ids)
  - Rolling count history (bounded at 300 frames)
  - `reset()` method for state clearing
- `src/config.py` — New tracking constants:
  - `TRACKER_CONFIG` ("bytetrack.yaml")
  - `CONFIDENCE_THRESHOLD` (0.25)
  - `POSITION_HISTORY_LENGTH` (30)
  - `COUNT_HISTORY_LENGTH` (300)
- `src/display.py` — `draw_tracking_hud()` function for crowd statistics overlay
- `src/display.py` — Optional track ID labels in `draw_grid()`
- `main.py` — `--no-tracking` CLI flag for Phase 1 detection-only mode

### Changed
- `src/detector.py`:
  - `detect()` now accepts `tracking` parameter; calls `model.track()` when True
  - `filter_persons()` now extracts `track_id` and `conf` fields
  - Confidence filtering applied when `tracking=True`
- `src/app.py`:
  - `App.__init__()` accepts `tracking` parameter
  - Creates `CrowdTracker` instance when tracking enabled
  - Passes `tracking` flag to detector and display functions
  - Calls `CrowdTracker.update()` each frame when tracking enabled
- `src/display.py`:
  - `draw_grid()` accepts `show_ids` parameter for track ID labels

### Fixed
- Zone `all_ids` now persist across frames (Bug 5: previously reset every frame)

### Preserved (unchanged)
- `src/risk.py` — Risk engine completely unchanged
- `src/alert.py` — Alert engine completely unchanged
- `src/analyzer.py` — Backward-compatible; no changes needed
- `test_yolo.py` — Original prototype untouched
- `sound.py` — Original test script untouched

### Tests
- 25 new Phase 2 tests performed, all passing
- 17 Phase 1 regression tests re-run, all passing
- Total: 42 tests passing

---

## Phase 1 — Modular Architecture (September 10, 2026)

### Added
- `main.py` — Entry point with argparse (`--video`, `--webcam`, `--model`)
- `src/__init__.py` — Package marker
- `src/config.py` — Centralized configuration (15 constants)
- `src/detector.py` — YOLO model wrapper (`Detector` class)
- `src/analyzer.py` — Grid counting, optical flow, heatmap (`Analyzer` class)
- `src/risk.py` — Pressure index, risk classification, color mapping
- `src/alert.py` — Threaded alert engine with cooldown (`AlertEngine` class)
- `src/display.py` — OpenCV rendering functions
- `src/app.py` — Application loop and module wiring (`App` class)
- `requirements.txt` — Dependency specification
- `.gitignore` — Version control exclusions
- `assets/` — Directory for media files
- `models/` — Directory for model weights
- `docs/PROJECT_REPORT.md` — Technical documentation

### Fixed
- Bug 1: Swapped risk thresholds (HIGH=20, MEDIUM=5 instead of reversed)
- Bug 2: Silent sound failures (bare `except: pass` → logged warnings)
- Bug 3: No graceful shutdown (`try/finally` for resource cleanup)
- Bug 4: Single-fire alert (timestamp-based cooldown replaces global flag)

### Preserved
- `test_yolo.py` — Original 186-line prototype (untouched)
- `sound.py` — Original test script (untouched)
- All original assets copied to new locations; originals preserved

### Tests
- 17 Phase 1 tests performed, all passing

---

## Phase 0 — Original Prototype (February 24, 2026)

### Files
- `test_yolo.py` — Monolithic 186-line script
- `sound.py` — 3-line test script
- `yolov8n.pt` — YOLOv8 nano weights
- `crowd_video.mp4` — Demo video
- `alert.wav` — Alert sound

### Functionality
- YOLO person detection
- 2x2 grid zone counting
- Optical flow motion analysis
- Pressure index calculation
- Three-tier risk classification (LOW/MEDIUM/HIGH)
- Heatmap overlay
- Audio alerts
- Real-time HUD display
