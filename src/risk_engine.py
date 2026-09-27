from dataclasses import dataclass, field

from src.config import (
    GRID_ROWS, GRID_COLS,
    RISK_SMOOTHING_ALPHA, RISK_HYSTERESIS,
    RISK_LOW_THRESHOLD, RISK_MEDIUM_THRESHOLD, MIN_CROWD_THRESHOLD,
    RISK_WEIGHT_STATE, RISK_WEIGHT_DYNAMICS, RISK_WEIGHT_HISTORY,
    RISK_W_DENSITY, RISK_W_CONCENTRATION, RISK_W_SPEED,
    RISK_W_GROWTH, RISK_W_STABILITY, RISK_W_CHAOS,
    RISK_W_OPTICAL_FLOW, RISK_W_CHURN,
    DENSITY_LOW, DENSITY_HIGH,
    SPEED_LOW, SPEED_HIGH,
    GROWTH_RATE_LOW, GROWTH_RATE_HIGH,
    STABILITY_LOW, STABILITY_HIGH,
    CHAOS_LOW, CHAOS_HIGH,
    OPTICAL_FLOW_LOW, OPTICAL_FLOW_HIGH,
    CHURN_RATE_LOW, CHURN_RATE_HIGH,
    CONCENTRATION_LOW, CONCENTRATION_HIGH,
    RISK_ZONE_W_DENSITY, RISK_ZONE_W_FRACTION, RISK_ZONE_W_SPEED,
)


@dataclass
class RiskResult:
    composite_score: float = 0.0
    smoothed_score: float = 0.0
    risk_level: str = "LOW"
    category_scores: dict = field(default_factory=dict)
    signal_values: dict = field(default_factory=dict)
    top_contributors: list = field(default_factory=list)
    critical_zone: tuple = (0, 0)
    critical_zone_risk: float = 0.0
    zone_risks: dict = field(default_factory=dict)
    is_limited: bool = False


def _clamp(value, lo=0.0, hi=100.0):
    return max(lo, min(hi, value))


def _normalize(value, low, high):
    if high == low:
        return 0.0
    return _clamp((value - low) / (high - low) * 100.0)


class RiskEngine:
    def __init__(self):
        self._prev_smoothed = 0.0
        self._prev_level = "LOW"

    def reset(self):
        self._prev_smoothed = 0.0
        self._prev_level = "LOW"

    def compute_risk(self, tracker, motion_variance, grid_counts,
                     frame_h, frame_w, tracking_enabled=True):
        if not tracking_enabled or tracker is None:
            return self._compute_limited(motion_variance, grid_counts,
                                         frame_h, frame_w)

        total = tracker.current_count
        if total < MIN_CROWD_THRESHOLD:
            return self._compute_low_crowd(total, tracker, motion_variance,
                                           grid_counts, frame_h, frame_w)

        signals = self._compute_signals(tracker, motion_variance,
                                        grid_counts, frame_h, frame_w)
        norm = self._normalize_signals(signals)
        categories = self._compute_category_scores(norm)
        raw = self._compute_composite(categories)
        smoothed = self._temporal_smooth(raw)
        level = self._classify(smoothed)

        contributors = self._identify_contributors(norm)
        zone_risks, crit_zone, crit_risk = self._compute_zone_risks(
            tracker, frame_h, frame_w, total)

        return RiskResult(
            composite_score=round(raw, 1),
            smoothed_score=round(smoothed, 1),
            risk_level=level,
            category_scores={k: round(v, 1) for k, v in categories.items()},
            signal_values={k: round(v, 1) for k, v in norm.items()},
            top_contributors=contributors,
            critical_zone=crit_zone,
            critical_zone_risk=round(crit_risk, 1),
            zone_risks={k: round(v, 1) for k, v in zone_risks.items()},
            is_limited=False,
        )

    def _compute_signals(self, tracker, motion_variance, grid_counts,
                         frame_h, frame_w):
        total = tracker.current_count
        frame_area = frame_h * frame_w
        density = total / (frame_area / 1000.0) if frame_area > 0 else 0.0

        max_zone = max(
            (grid_counts[r][c] for r in range(GRID_ROWS)
             for c in range(GRID_COLS)),
            default=0,
        )
        concentration = max_zone / total if total > 0 else 0.25

        avg_speed = tracker.get_crowd_mean_speed()
        growth_rate = tracker.get_growth_rate(window=15)
        stability = tracker.get_temporal_stability(window=30)
        chaos = tracker.get_chaos_index()
        churn_rate = tracker.get_churn_rate(window=30)

        return {
            "density": density,
            "concentration": concentration,
            "speed": avg_speed,
            "growth_rate": growth_rate,
            "stability": stability,
            "chaos": chaos,
            "optical_flow": motion_variance,
            "churn_rate": churn_rate,
        }

    def _normalize_signals(self, signals):
        return {
            "density": _normalize(signals["density"], DENSITY_LOW, DENSITY_HIGH),
            "concentration": _normalize(signals["concentration"],
                                        CONCENTRATION_LOW, CONCENTRATION_HIGH),
            "speed": _normalize(signals["speed"], SPEED_LOW, SPEED_HIGH),
            "growth_rate": _normalize(signals["growth_rate"],
                                     GROWTH_RATE_LOW, GROWTH_RATE_HIGH),
            "stability": _normalize(signals["stability"],
                                   STABILITY_LOW, STABILITY_HIGH),
            "chaos": _normalize(signals["chaos"], CHAOS_LOW, CHAOS_HIGH),
            "optical_flow": _normalize(signals["optical_flow"],
                                      OPTICAL_FLOW_LOW, OPTICAL_FLOW_HIGH),
            "churn_rate": _normalize(signals["churn_rate"],
                                    CHURN_RATE_LOW, CHURN_RATE_HIGH),
        }

    def _compute_category_scores(self, norm):
        crowd_state = (
            RISK_W_DENSITY * norm["density"]
            + RISK_W_CONCENTRATION * norm["concentration"]
            + RISK_W_SPEED * norm["speed"]
        )
        crowd_dynamics = (
            RISK_W_GROWTH * norm["growth_rate"]
            + RISK_W_STABILITY * norm["stability"]
            + RISK_W_CHAOS * norm["chaos"]
        )
        historical = (
            RISK_W_OPTICAL_FLOW * norm["optical_flow"]
            + RISK_W_CHURN * norm["churn_rate"]
        )
        return {
            "crowd_state": crowd_state,
            "crowd_dynamics": crowd_dynamics,
            "historical": historical,
        }

    def _compute_composite(self, categories):
        return (
            RISK_WEIGHT_STATE * categories["crowd_state"]
            + RISK_WEIGHT_DYNAMICS * categories["crowd_dynamics"]
            + RISK_WEIGHT_HISTORY * categories["historical"]
        )

    def _temporal_smooth(self, raw_score):
        smoothed = (RISK_SMOOTHING_ALPHA * raw_score
                    + (1.0 - RISK_SMOOTHING_ALPHA) * self._prev_smoothed)
        self._prev_smoothed = smoothed
        return smoothed

    def _classify(self, smoothed_score):
        prev = self._prev_level
        if prev == "LOW":
            if smoothed_score > RISK_MEDIUM_THRESHOLD + RISK_HYSTERESIS:
                level = "HIGH"
            elif smoothed_score > RISK_LOW_THRESHOLD + RISK_HYSTERESIS:
                level = "MEDIUM"
            else:
                level = "LOW"
        elif prev == "MEDIUM":
            if smoothed_score > RISK_MEDIUM_THRESHOLD + RISK_HYSTERESIS:
                level = "HIGH"
            elif smoothed_score < RISK_LOW_THRESHOLD - RISK_HYSTERESIS:
                level = "LOW"
            else:
                level = "MEDIUM"
        else:
            if smoothed_score < RISK_MEDIUM_THRESHOLD - RISK_HYSTERESIS:
                level = "MEDIUM"
            elif smoothed_score < RISK_LOW_THRESHOLD - RISK_HYSTERESIS:
                level = "LOW"
            else:
                level = "HIGH"
        self._prev_level = level
        return level

    def _identify_contributors(self, norm):
        weights = {
            "Crowd Density": RISK_WEIGHT_STATE * RISK_W_DENSITY,
            "Zone Concentration": RISK_WEIGHT_STATE * RISK_W_CONCENTRATION,
            "Movement Speed": RISK_WEIGHT_STATE * RISK_W_SPEED,
            "Growth Rate": RISK_WEIGHT_DYNAMICS * RISK_W_GROWTH,
            "Temporal Stability": RISK_WEIGHT_DYNAMICS * RISK_W_STABILITY,
            "Chaos Index": RISK_WEIGHT_DYNAMICS * RISK_W_CHAOS,
            "Optical Flow": RISK_WEIGHT_HISTORY * RISK_W_OPTICAL_FLOW,
            "Churn Rate": RISK_WEIGHT_HISTORY * RISK_W_CHURN,
        }
        signal_map = {
            "Crowd Density": "density",
            "Zone Concentration": "concentration",
            "Movement Speed": "speed",
            "Growth Rate": "growth_rate",
            "Temporal Stability": "stability",
            "Chaos Index": "chaos",
            "Optical Flow": "optical_flow",
            "Churn Rate": "churn_rate",
        }
        labels = {
            "Crowd Density": "Dense crowd in frame",
            "Zone Concentration": "People concentrated in one zone",
            "Movement Speed": "Fast crowd movement",
            "Growth Rate": "Rapid crowd increase detected",
            "Temporal Stability": "Unstable crowd count",
            "Chaos Index": "Chaotic movement directions",
            "Optical Flow": "High scene motion energy",
            "Churn Rate": "Heavy crowd turnover",
        }
        scored = []
        for name, w in weights.items():
            sig_val = norm[signal_map[name]]
            contribution = sig_val * w
            scored.append((name, round(sig_val, 1), labels[name], contribution))
        scored.sort(key=lambda x: x[3], reverse=True)
        return [(s[0], s[1], s[2]) for s in scored[:3]]

    def _compute_zone_risks(self, tracker, frame_h, frame_w, total):
        zone_risks = {}
        max_risk = 0.0
        max_zone = (0, 0)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                zone_total = tracker.get_zone_current_count(row, col)
                zone_area = (frame_h / GRID_ROWS) * (frame_w / GRID_COLS)
                zone_density = zone_total / (zone_area / 1000.0) if zone_area > 0 else 0.0
                zone_fraction = zone_total / total if total > 0 else 0.0
                zone_speed = tracker.get_zone_mean_speed(row, col, frame_h, frame_w)

                z_density_n = _normalize(zone_density, DENSITY_LOW, DENSITY_HIGH)
                z_fraction_n = _normalize(zone_fraction, 0.0, 1.0)
                z_speed_n = _normalize(zone_speed, SPEED_LOW, SPEED_HIGH)

                zone_risk = (
                    RISK_ZONE_W_DENSITY * z_density_n
                    + RISK_ZONE_W_FRACTION * z_fraction_n
                    + RISK_ZONE_W_SPEED * z_speed_n
                )
                zone_risks[(row, col)] = zone_risk
                if zone_risk > max_risk:
                    max_risk = zone_risk
                    max_zone = (row, col)

        return zone_risks, max_zone, max_risk

    def _compute_limited(self, motion_variance, grid_counts,
                         frame_h, frame_w):
        total = sum(sum(row) for row in grid_counts)
        frame_area = frame_h * frame_w
        density = total / (frame_area / 1000.0) if frame_area > 0 else 0.0
        max_zone = max(
            (grid_counts[r][c] for r in range(GRID_ROWS)
             for c in range(GRID_COLS)),
            default=0,
        )
        concentration = max_zone / total if total > 0 else 0.25

        norm = {
            "density": _normalize(density, DENSITY_LOW, DENSITY_HIGH),
            "concentration": _normalize(concentration,
                                        CONCENTRATION_LOW, CONCENTRATION_HIGH),
            "speed": 0.0,
            "growth_rate": 0.0,
            "stability": 0.0,
            "chaos": 0.0,
            "optical_flow": _normalize(motion_variance,
                                      OPTICAL_FLOW_LOW, OPTICAL_FLOW_HIGH),
            "churn_rate": 0.0,
        }

        categories = self._compute_category_scores(norm)
        raw = self._compute_composite(categories)
        smoothed = self._temporal_smooth(raw)
        level = self._classify(smoothed)

        contributors = self._identify_contributors(norm)

        zone_risks = {}
        crit_zone = (0, 0)
        crit_risk = 0.0
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                zone_risks[(row, col)] = 0.0

        return RiskResult(
            composite_score=round(raw, 1),
            smoothed_score=round(smoothed, 1),
            risk_level=level,
            category_scores={k: round(v, 1) for k, v in categories.items()},
            signal_values={k: round(v, 1) for k, v in norm.items()},
            top_contributors=contributors,
            critical_zone=crit_zone,
            critical_zone_risk=round(crit_risk, 1),
            zone_risks=zone_risks,
            is_limited=True,
        )

    def _compute_low_crowd(self, total, tracker, motion_variance,
                           grid_counts, frame_h, frame_w):
        signals = {
            "density": total / ((frame_h * frame_w) / 1000.0) if (frame_h * frame_w) > 0 else 0.0,
            "concentration": 0.25,
            "speed": tracker.get_crowd_mean_speed(),
            "growth_rate": 0.0,
            "stability": 0.0,
            "chaos": 0.0,
            "optical_flow": motion_variance,
            "churn_rate": 0.0,
        }
        norm = self._normalize_signals(signals)
        categories = self._compute_category_scores(norm)
        raw = self._compute_composite(categories)
        smoothed = self._temporal_smooth(raw)
        level = self._classify(smoothed)
        contributors = self._identify_contributors(norm)

        zone_risks = {}
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                zone_risks[(row, col)] = 0.0

        return RiskResult(
            composite_score=round(raw, 1),
            smoothed_score=round(smoothed, 1),
            risk_level=level,
            category_scores={k: round(v, 1) for k, v in categories.items()},
            signal_values={k: round(v, 1) for k, v in norm.items()},
            top_contributors=contributors,
            critical_zone=(0, 0),
            critical_zone_risk=0.0,
            zone_risks=zone_risks,
            is_limited=False,
        )
