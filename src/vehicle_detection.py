from ultralytics import YOLO
import cv2

model = YOLO("../models/yolov8n.pt")

def detect_vehicles(frame):
    results = model(frame)
    for result in results:
        for box in result.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box[:4])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return frame

