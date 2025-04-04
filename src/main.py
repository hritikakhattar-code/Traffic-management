import os
import cv2
import time
import logging
from datetime import datetime
import torch

# Fix imports to prevent circular dependencies
from vehicle_detection import VehicleDetector
from vehicle_tracking import VehicleTracker
from speed_calculation import SpeedCalculator
from test_logging import setup_logger

def main():
    # Setup paths
    input_video = "traffic.mp4"
    output_log = os.path.join("logs", "output.log")
    test_log = os.path.join("logs", "test.log")
    csv_file = os.path.join("logs", "speed_data.csv")
    snapshot_dir = "snapshots"
    model_path = os.path.join("models", "yolov8n.pt")
    
    # Make sure the video file exists
    if not os.path.exists(input_video):
        print(f"Error: Input video file '{input_video}' not found")
        print("Please place your traffic.mp4 file in the same directory as main.py")
        return
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(output_log), exist_ok=True)
    os.makedirs(snapshot_dir, exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    # Setup logging
    main_logger = setup_logger("main_logger", output_log)
    test_logger = setup_logger("test_logger", test_log)
    
    main_logger.info(f"Starting traffic management system at {datetime.now()}")
    test_logger.info(f"TEST LOG: System initialized at {datetime.now()}")
    
    print(f"🚀 Initializing traffic management system")
    print(f"🎥 Input video: {input_video}")
    print(f"📝 Output log: {output_log}")
    print(f"📝 Test log: {test_log}")
    
    try:
        # Initialize components
        print(f"🔍 Loading vehicle detector model from: {model_path}")
        detector = VehicleDetector(model_path)
        
        print("🔄 Initializing vehicle tracker")
        tracker = VehicleTracker()
        
        # Estimate speed factor (meters per pixel)
        speed_factor = 0.1  # Default value
        print(f"📏 Using speed factor: {speed_factor}")
        speed_calculator = SpeedCalculator(speed_factor)
        
        # Set speed limit (km/h)
        speed_limit = 50
        print(f"🚦 Speed limit set to: {speed_limit} km/h")
        
        # Open video
        print(f"📂 Opening video: {input_video}")
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            main_logger.error(f"Error: Could not open video {input_video}")
            print(f"❌ Error: Could not open video {input_video}")
            return
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"ℹ️ Video properties: {frame_width}x{frame_height} at {fps} FPS")
        main_logger.info(f"Video properties: {frame_width}x{frame_height} at {fps} FPS")
        
        # Initialize CSV file with headers if it doesn't exist
        if not os.path.exists(csv_file):
            with open(csv_file, 'w') as f:
                f.write("timestamp,vehicle_id,speed,snapshot_path\n")
        
        frame_count = 0
        start_time = time.time()
        
        print("▶️ Processing video...")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if frame_count % 20 == 0:
                print(f"📊 Processed {frame_count} frames...")
            
            # Detect vehicles
            detections = detector.detect(frame)
            
            # Track vehicles
            tracked_vehicles = tracker.update(detections)
            
            # Calculate speeds
            speeds = speed_calculator.calculate_speeds(tracked_vehicles, fps)
            
            # Process each vehicle
            for vehicle_id, vehicle_data in speeds.items():
                speed = vehicle_data["speed"]
                bbox = vehicle_data["bbox"]
                
                # Draw bounding box and speed
                x1, y1, x2, y2 = bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {vehicle_id}, {speed:.1f} km/h", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Log speeding vehicles and save snapshots
                if speed > speed_limit:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    snapshot_path = os.path.join(snapshot_dir, f"vehicle_{vehicle_id}_{timestamp}.jpg")
                    
                    # Save snapshot
                    vehicle_img = frame[max(0, y1):min(frame_height, y2), 
                                    max(0, x1):min(frame_width, x2)]
                    if vehicle_img.size > 0:
                        cv2.imwrite(snapshot_path, vehicle_img)
                        
                        # Log to test.log
                        test_logger.warning(f"OVERSPEEDING: Vehicle ID {vehicle_id} detected at {speed:.1f} km/h, limit: {speed_limit} km/h")
                        
                        # Save to CSV
                        with open(csv_file, 'a') as f:
                            f.write(f"{timestamp},{vehicle_id},{speed:.1f},{snapshot_path}\n")
            
            # Display FPS on frame
            elapsed_time = time.time() - start_time
            fps_actual = frame_count / elapsed_time if elapsed_time > 0 else 0
            cv2.putText(frame, f"FPS: {fps_actual:.1f}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Display frame
            cv2.imshow("Traffic Management", frame)
            
            # Check for key press to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        main_logger.info(f"Processing complete. Processed {frame_count} frames in {elapsed_time:.2f} seconds")
        print(f"✅ Processing complete. Processed {frame_count} frames in {elapsed_time:.2f} seconds")
        
    except Exception as e:
        main_logger.error(f"Error in main: {e}")
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()