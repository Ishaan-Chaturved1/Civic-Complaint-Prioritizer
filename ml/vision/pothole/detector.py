import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont


class PotholeDetector:
    """
    Ultralytics YOLO Pothole Object Detector Inference Service
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "models/vision/pothole_yolo.pt"
        self.model = None
        self.is_loaded = False

        if os.path.exists(self.model_path):
            self.load_model()

    def load_model(self):
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            self.is_loaded = True
        except Exception as e:
            self.is_loaded = False
            print(f"Failed to load YOLO model: {e}")

    def detect(self, image_input, conf_threshold: float = 0.25, output_annotated_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs object detection on image path or PIL image.
        Returns detection results or transparent model_unavailable response.
        """
        if not self.is_loaded or self.model is None:
            return {
                "status": "model_unavailable",
                "message": "Train the model using scripts/train_detection.py",
                "detected_issue": None,
                "confidence": None,
                "visual_severity": None,
                "damage_area_percentage": 0.0,
                "detections": []
            }

        # Run inference
        results = self.model(image_input, conf=conf_threshold, verbose=False)
        result = results[0]

        img_w, img_h = result.orig_shape[1], result.orig_shape[0]
        total_img_area = float(img_w * img_h)

        detections = []
        total_damage_bbox_area = 0.0

        boxes = result.boxes
        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                xyxy = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                cls_name = self.model.names.get(cls_id, "pothole")

                bw = max(0.0, xyxy[2] - xyxy[0])
                bh = max(0.0, xyxy[3] - xyxy[1])
                b_area = bw * bh
                total_damage_bbox_area += b_area

                detections.append({
                    "class": cls_name,
                    "confidence": round(conf, 4),
                    "bbox": [round(coord, 1) for coord in xyxy],
                    "area_pixels": round(b_area, 1),
                    "area_percentage": round((b_area / total_img_area) * 100, 2)
                })

        damage_area_pct = round(min(100.0, (total_damage_bbox_area / total_img_area) * 100), 2)
        top_conf = max([d["confidence"] for d in detections], default=0.0)

        # Calculate visual severity (0 - 100)
        # Based on number of potholes, area percentage, and detection confidence
        num_potholes = len(detections)
        if num_potholes == 0:
            visual_severity = 0.0
            detected_issue = "No road damage detected"
        else:
            base_sev = 40.0
            area_weight = min(damage_area_pct * 2.5, 40.0)  # up to 40 pts for area
            count_weight = min(num_potholes * 8.0, 20.0)     # up to 20 pts for multiple potholes
            visual_severity = round(min(100.0, base_sev + area_weight + count_weight), 1)
            detected_issue = f"{num_potholes} pothole(s) detected"

        # Save annotated image if requested
        if output_annotated_path and detections:
            try:
                annotated_img_bgr = result.plot()
                annotated_pil = Image.fromarray(annotated_img_bgr[..., ::-1])
                Path(output_annotated_path).parent.mkdir(parents=True, exist_ok=True)
                annotated_pil.save(output_annotated_path)
            except Exception as e:
                print(f"Warning: Failed to save annotated image: {e}")

        return {
            "status": "success",
            "detected_issue": detected_issue,
            "confidence": round(top_conf, 4) if num_potholes > 0 else 0.0,
            "visual_severity": visual_severity,
            "damage_area_percentage": damage_area_pct,
            "detections": detections,
            "model_version": "YOLOv8-Pothole-v1"
        }
