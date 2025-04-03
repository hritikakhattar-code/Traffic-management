import time

frame_rate = 30  # FPS of video
distance_meters = 10  # Real-world distance between two points
vehicle_times = {}  # Track vehicle entry timestamps

def estimate_speed(vehicle_id, entry_time, exit_time):
    time_taken = exit_time - entry_time
    speed = (distance_meters / time_taken) * 3.6  # Convert m/s to km/h
    return speed
