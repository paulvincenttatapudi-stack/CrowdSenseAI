import logging
import time
import threading

from src.config import ALERT_SOUND_PATH, ALERT_COOLDOWN_SECONDS

logger = logging.getLogger(__name__)


class AlertEngine:
    def __init__(self, sound_path=ALERT_SOUND_PATH, cooldown=ALERT_COOLDOWN_SECONDS):
        self.sound_path = str(sound_path)
        self.cooldown = cooldown
        self._last_trigger_time = 0.0
        self._lock = threading.Lock()

    def trigger(self):
        now = time.time()
        with self._lock:
            if now - self._last_trigger_time < self.cooldown:
                return
            self._last_trigger_time = now

        t = threading.Thread(target=self._play, daemon=True)
        t.start()

    def _play(self):
        try:
            from playsound import playsound
            playsound(self.sound_path)
        except Exception as e:
            logger.warning("Alert sound failed: %s", e)
