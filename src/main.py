import cv2
import time
import uuid
import os
import logging
from vehicle_detection import detect_vehicles
from speed_calculation import estimate_speed, vehicle_times
from challan import send_challan

# ✅ Ensure logs directory exists
log_dir = os.path.join(os.path.dirname(__file__), "../logs")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "test.log")

# ✅ Configure logging
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
file_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

video_path = "../data/traffic.mp4"
cap = cv2.VideoCapture(video_path)

def process_video():
    logger.info("🚦 Starting Traffic Monitoring System")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            logger.info("📌 Video processing completed.")
            break

        current_time = time.time()

        # ✅ Fix: Handle different return values from detect_vehicles
        result = detect_vehicles(frame)

        if isinstance(result, tuple) and len(result) == 2:
            frame, detected_vehicles = result  # ✅ Correct unpacking
        else:
            frame = result  # ✅ Only frame returned
            detected_vehicles = {}  # Avoid errors by setting an empty dictionary

        for vehicle_id, position in detected_vehicles.items():
            if vehicle_id not in vehicle_times:
                vehicle_times[vehicle_id] = current_time
            else:
                speed = estimate_speed(vehicle_id, vehicle_times[vehicle_id], current_time)
                vehicle_times[vehicle_id] = current_time  # Update time

                if speed > 60:
                    logger.warning(f"⚠️ OVERSPEEDING: Vehicle {vehicle_id} at {speed:.2f} km/h")
                    send_challan(speed)

        cv2.imshow("Traffic Monitoring", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            logger.info("🛑 Process terminated by user.")
            break

    cap.release()
    cv2.destroyAllWindows()
    logger.info("🚦 Traffic Monitoring System Stopped")

if __name__ == "__main__":
    process_video()
