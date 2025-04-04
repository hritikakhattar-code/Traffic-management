import cv2
import torch
import numpy as np
import os

class VehicleDetector:
    def __init__(self, model_path):
        """
        Initialize the vehicle detector with YOLOv8 model
        
        Args:
            model_path (str): Path to the YOLOv8 model weights
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Check if model file exists locally 
        if os.path.exists(model_path):
            print(f"Loading model from local file: {model_path}")
            try:
                self.model = torch.hub.load('ultralytics/yolov8', 'custom', path=model_path, device=self.device, trust_repo=True)
            except Exception as e:
                print(f"Error loading local model: {e}")
                self.load_default_model()
        else:
            print(f"Model path {model_path} not found, loading default model")
            self.load_default_model()
            
        # Classes we're interested in (vehicle classes from COCO dataset)
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
    
    def load_default_model(self):
        """Fallback to load a pre-trained model"""
        try:
            print("Attempting to load default YOLOv8n model")
            # Use torch hub with trust_repo=True
            self.model = torch.hub.load('ultralytics/yolov8', 'yolov8n', pretrained=True, trust_repo=True)
        except Exception as e:
            print(f"Error loading default model via torch.hub: {e}")
            try:
                # Second fallback - try importing YOLO from ultralytics
                from ultralytics import YOLO
                print("Loading model via ultralytics YOLO")
                self.model = YOLO("yolov8n.pt")
            except Exception as e2:
                print(f"Error loading via ultralytics YOLO: {e2}")
                raise RuntimeError("Failed to load any model. Please install ultralytics: pip install ultralytics")
        
    def detect(self, frame):
        """
        Detect vehicles in the frame
        
        Args:
            frame (numpy.ndarray): Input frame
            
        Returns:
            list: List of bounding boxes in format [x1, y1, x2, y2, confidence, class_id]
        """
        # Run detection
        try:
            results = self.model(frame)
            
            # Extract detections
            detections = []
            
            # Handling differences between ultralytics YOLO and torch.hub loaded model
            if hasattr(results, 'xyxy'):
                # torch.hub loaded model
                for result in results.xyxy[0].cpu().numpy():
                    x1, y1, x2, y2, conf, class_id = result
                    
                    # Check if detected object is a vehicle
                    if int(class_id) in self.vehicle_classes and conf > 0.4:
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(conf),
                            'class_id': int(class_id)
                        })
            else:
                # ultralytics YOLO model
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        conf = box.conf[0].item()
                        class_id = int(box.cls[0].item())
                        
                        # Check if detected object is a vehicle
                        if class_id in self.vehicle_classes and conf > 0.4:
                            detections.append({
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'confidence': float(conf),
                                'class_id': class_id
                            })
                    
            return detections
            
        except Exception as e:
            print(f"Error in vehicle detection: {e}")
            return []

