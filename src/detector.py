from src.config import MODEL_PATH, IMAGE_SIZE, TRACKER_CONFIG, CONFIDENCE_THRESHOLD
from ultralytics import YOLO


class Detector:
    def __init__(self, model_path=MODEL_PATH):
        self.model = YOLO(str(model_path))

    def detect(self, frame, imgsz=IMAGE_SIZE, tracking=False):
        if tracking:
            results = self.model.track(
                frame,
                imgsz=imgsz,
                persist=True,
                tracker=TRACKER_CONFIG,
            )
        else:
            results = self.model(frame, imgsz=imgsz)
        return results[0].boxes

    @staticmethod
    def filter_persons(boxes, tracking=False):
        persons = []
        for box in boxes:
            cls = int(box.cls[0])
            if cls != 0:
                continue

            conf = float(box.conf[0]) if box.conf is not None else 0.0
            if tracking and conf < CONFIDENCE_THRESHOLD:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            track_id = None
            if tracking and box.id is not None:
                track_id = int(box.id[0])

            persons.append({
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "cx": cx, "cy": cy,
                "track_id": track_id,
                "conf": conf,
            })
        return persons
