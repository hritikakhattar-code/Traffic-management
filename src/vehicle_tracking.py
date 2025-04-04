import numpy as np
from scipy.optimize import linear_sum_assignment

class VehicleTracker:
    def __init__(self, max_age=10, min_hits=3, iou_threshold=0.3):
        """
        Initialize the vehicle tracker
        
        Args:
            max_age (int): Maximum frames to keep a track alive without matching
            min_hits (int): Minimum hits needed to establish a track
            iou_threshold (float): IOU threshold for matching detections to tracks
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.tracks = {}
        self.next_id = 1

    def iou(self, bbox1, bbox2):
        """Calculate IoU between two bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate area of intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        area_i = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate areas of both bounding boxes
        area_1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area_2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        
        # Calculate IoU
        iou = area_i / float(area_1 + area_2 - area_i)
        return iou

    def get_center(self, bbox):
        """Get center point of bounding box"""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    def update(self, detections):
        """
        Update tracks with new detections
        
        Args:
            detections (list): List of detection dictionaries
            
        Returns:
            dict: Updated tracks
        """
        # If no tracks yet, initialize with current detections
        if not self.tracks:
            for det in detections:
                self.tracks[self.next_id] = {
                    'bbox': det['bbox'],
                    'hits': 1,
                    'age': 0,
                    'active': False,
                    'class_id': det['class_id'],
                    'positions': [self.get_center(det['bbox'])]
                }
                self.next_id += 1
            return self.tracks
            
        # If no detections, increment age of all tracks
        if not detections:
            for track_id in list(self.tracks.keys()):
                self.tracks[track_id]['age'] += 1
                if self.tracks[track_id]['age'] > self.max_age:
                    del self.tracks[track_id]
            return self.tracks
            
        # Calculate IoU between each detection and each track
        cost_matrix = np.zeros((len(self.tracks), len(detections)))
        track_indices = list(self.tracks.keys())
        
        for i, track_id in enumerate(track_indices):
            for j, det in enumerate(detections):
                cost_matrix[i, j] = 1 - self.iou(self.tracks[track_id]['bbox'], det['bbox'])
                
        # Use Hungarian algorithm to find optimal assignment
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        # Mark all tracks as unmatched first
        unmatched_tracks = set(track_indices)
        unmatched_detections = set(range(len(detections)))
        
        # Process matches
        for i, j in zip(row_ind, col_ind):
            track_id = track_indices[i]
            
            # Skip if IoU is too low
            if cost_matrix[i, j] > 1 - self.iou_threshold:
                continue
                
            # Update track with new detection
            self.tracks[track_id]['bbox'] = detections[j]['bbox']
            self.tracks[track_id]['hits'] += 1
            self.tracks[track_id]['age'] = 0
            self.tracks[track_id]['class_id'] = detections[j]['class_id']
            self.tracks[track_id]['positions'].append(self.get_center(detections[j]['bbox']))
            
            # Mark track as active if it has enough hits
            if self.tracks[track_id]['hits'] >= self.min_hits:
                self.tracks[track_id]['active'] = True
                
            # Mark as matched
            unmatched_tracks.remove(track_id)
            unmatched_detections.remove(j)
            
        # Handle unmatched detections
        for j in unmatched_detections:
            self.tracks[self.next_id] = {
                'bbox': detections[j]['bbox'],
                'hits': 1,
                'age': 0,
                'active': False,
                'class_id': detections[j]['class_id'],
                'positions': [self.get_center(detections[j]['bbox'])]
            }
            self.next_id += 1
            
        # Handle unmatched tracks
        for track_id in unmatched_tracks:
            self.tracks[track_id]['age'] += 1
            # Keep only last 30 positions to avoid memory growth
            self.tracks[track_id]['positions'] = self.tracks[track_id]['positions'][-30:]
            
        # Remove old tracks
        for track_id in list(self.tracks.keys()):
            if self.tracks[track_id]['age'] > self.max_age:
                del self.tracks[track_id]
                
        # Return active tracks
        return {k: v for k, v in self.tracks.items() if v['active']}

# Function wrapper for backward compatibility
def track_vehicles(frame, frame_count, prev_tracks=None):
    """
    Legacy wrapper function for backward compatibility
    """
    # This would need customization to match your original implementation
    if prev_tracks is None:
        tracker = VehicleTracker()
    
    # Implementation depends on your original code design
    # This is just a placeholder
    return {}