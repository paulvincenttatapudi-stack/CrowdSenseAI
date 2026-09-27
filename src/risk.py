from src.config import PRESSURE_HIGH_THRESHOLD, PRESSURE_MEDIUM_THRESHOLD


class RiskLevel:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


def compute_pressure_index(total_people, motion_variance):
    return total_people * motion_variance


def classify_risk(pressure_index):
    if pressure_index > PRESSURE_HIGH_THRESHOLD:
        return RiskLevel.HIGH
    elif pressure_index > PRESSURE_MEDIUM_THRESHOLD:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


RISK_COLORS = {
    RiskLevel.LOW: (0, 255, 0),
    RiskLevel.MEDIUM: (0, 165, 255),
    RiskLevel.HIGH: (0, 0, 255),
}


def risk_colors(risk_text):
    return RISK_COLORS.get(risk_text, (255, 255, 255))


def risk_score_color(score):
    score = max(0.0, min(100.0, score))
    if score <= 50.0:
        r = int(score / 50.0 * 255)
        g = 255
    else:
        r = 255
        g = int((1.0 - (score - 50.0) / 50.0) * 255)
    return (0, g, r)
