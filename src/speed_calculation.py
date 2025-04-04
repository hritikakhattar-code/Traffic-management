import numpy as np
import math

class SpeedCalculator:
    def __init__(self, speed_factor=0.1):
        """
        Initialize the speed calculator
        
        Args:
            speed_factor (float): Calibration factor to convert pixel distance to real-world speed
        """
        self.speed_factor = speed_factor
        self.previous_speeds = {}  # Store previous speeds for smoothing
        
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    def calculate_speeds(self, tracked_vehicles, fps):
        """
        Calculate the speed of each tracked vehicle
        
        Args:
            tracked_vehicles (dict): Dictionary of tracked vehicles
            fps (float): Frames per second of the video
            
        Returns:
            dict: Dictionary with vehicle speeds
        """
        results = {}
        
        for vehicle_id, vehicle_data in tracked_vehicles.items():
            # Need at least 2 positions to calculate speed
            positions = vehicle_data.get('positions', [])
            if len(positions) < 2:
                continue
                
            # Calculate distance between last few positions
            distances = []
            for i in range(1, min(10, len(positions))):
                distances.append(self.calculate_distance(positions[-i-1], positions[-i]))
                
            if not distances:
                continue
                
            # Use average of last few distances to smooth speed calculation
            avg_distance = np.mean(distances)
            
            # Calculate speed (pixels per second)
            pixels_per_second = avg_distance * fps
            
            # Convert to km/h using speed factor
            speed_kmh = pixels_per_second * self.speed_factor
            
            # Apply smoothing with previous speed measurements if available
            if vehicle_id in self.previous_speeds:
                # Weighted average (70% new, 30% old)
                speed_kmh = 0.7 * speed_kmh + 0.3 * self.previous_speeds[vehicle_id]
                
            # Store for next frame
            self.previous_speeds[vehicle_id] = speed_kmh
            
            # Store result
            results[vehicle_id] = {
                "speed": speed_kmh,
                "bbox": vehicle_data['bbox']
            }
            
        return results

# Stand-alone function for external use
def estimate_speed(positions, fps, speed_factor=0.1):
    """
    Estimate speed based on positions
    
    Args:
        positions (list): List of (x, y) positions
        fps (float): Frames per second
        speed_factor (float): Conversion factor
        
    Returns:
        float: Estimated speed in km/h
    """
    if len(positions) < 2:
        return 0.0
        
    # Calculate distance between last two positions
    p1, p2 = positions[-2], positions[-1]
    distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    # Calculate speed
    pixels_per_second = distance * fps
    speed_kmh = pixels_per_second * speed_factor
    
    return speed_kmh