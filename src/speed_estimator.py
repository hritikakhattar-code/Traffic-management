import cv2
import numpy as np

def estimate_speed_factor(video_path, known_lane_width_meters=3.5):
    """
    Estimate a speed factor to convert pixel distances to real-world speeds
    This is a simplified estimation method based on typical lane widths
    
    Args:
        video_path (str): Path to the video file
        known_lane_width_meters (float): The standard width of a traffic lane in meters
        
    Returns:
        float: Estimated speed factor
    """
    # Open video to get dimensions
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return 0.1  # Default value
    
    # Get video dimensions
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Read first frame for lane detection
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Error: Could not read frame from video")
        return 0.1  # Default value
    
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Try to detect lines (lanes)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=50)
    
    if lines is None or len(lines) == 0:
        print("No lines detected, using default value")
        return 0.1  # Default value
    
    # Estimate lane width in pixels
    # This is a simplification - in a real system, you would need a more sophisticated approach
    horizontal_lines = []
    vertical_lines = []
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(y2 - y1) < abs(x2 - x1):  # More horizontal than vertical
            horizontal_lines.append(line[0])
        else:
            vertical_lines.append(line[0])
    
    # If we have vertical lines (lane markings), estimate lane width
    if len(vertical_lines) >= 2:
        # Sort by x position
        vertical_lines.sort(key=lambda line: min(line[0], line[2]))
        
        # Calculate distances between adjacent lines
        distances = []
        for i in range(1, len(vertical_lines)):
            prev_x = (vertical_lines[i-1][0] + vertical_lines[i-1][2]) / 2
            curr_x = (vertical_lines[i][0] + vertical_lines[i][2]) / 2
            distances.append(abs(curr_x - prev_x))
        
        if distances:
            # Use median distance as it's more robust to outliers
            estimated_lane_width_pixels = np.median(distances)
            
            # Calculate conversion factor: meters/pixel * (km/1000m) * (3600s/h)
            meters_per_pixel = known_lane_width_meters / estimated_lane_width_pixels
            speed_factor = meters_per_pixel * 3.6  # Convert to km/h
            
            return speed_factor
    
    # If lane detection fails, use a default value based on frame size
    # This assumes a typical highway scene where the frame width is about 30-40 meters
    estimated_scene_width_meters = 35.0
    meters_per_pixel = estimated_scene_width_meters / frame_width
    speed_factor = meters_per_pixel * 3.6  # Convert to km/h
    
    return speed_factor