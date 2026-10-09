import os
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
from ml.vision.pothole.detector import PotholeDetector
from ml.vision.garbage.classifier import GarbageClassifier


class VisionService:
    """
    Unified Computer Vision inference service for Civic Complaint Prioritizer.
    Routes image to Pothole YOLO detector and Garbage Classifier.
    """

    def __init__(
        self,
        pothole_model_path: Optional[str] = None,
        garbage_model_path: Optional[str] = None
    ):
        self.pothole_detector = PotholeDetector(pothole_model_path)
        self.garbage_classifier = GarbageClassifier(garbage_model_path)

    def analyze_image(
        self,
        image_path: str,
        category_hint: Optional[str] = None,
        output_annotated_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes uploaded civic image.
        Selects or compares vision models and returns visual severity and detections.
        """
        if not os.path.exists(image_path):
            return {
                "status": "error",
                "message": f"Image file not found at {image_path}"
            }

        # Check if any model is available
        pothole_ready = self.pothole_detector.is_loaded
        garbage_ready = self.garbage_classifier.is_loaded

        if not pothole_ready and not garbage_ready:
            return {
                "status": "model_unavailable",
                "message": "Computer vision models are not trained yet. Run scripts/train_detection.py or scripts/train_classification.py",
                "detected_issue": None,
                "confidence": None,
                "visual_severity": None,
                "damage_area_percentage": 0.0,
                "detections": []
            }

        # Route by category hint if specified
        if category_hint in ["Road Damage", "Traffic"]:
            if pothole_ready:
                return self.pothole_detector.detect(image_path, output_annotated_path=output_annotated_path)
        elif category_hint in ["Garbage", "Sewage", "Drainage"]:
            if garbage_ready:
                return self.garbage_classifier.predict(image_path)

        # If no hint or model not ready for that specific category, run available models
        results = []
        if pothole_ready:
            p_res = self.pothole_detector.detect(image_path, output_annotated_path=output_annotated_path)
            if p_res.get("status") == "success" and p_res.get("detections"):
                results.append(p_res)

        if garbage_ready:
            g_res = self.garbage_classifier.predict(image_path)
            if g_res.get("status") == "success" and g_res.get("waste_class") != "clean_street":
                results.append(g_res)

        if results:
            # Pick highest visual severity
            best = max(results, key=lambda x: x.get("visual_severity", 0.0))
            return best

        # If nothing detected or both clean
        if pothole_ready:
            return self.pothole_detector.detect(image_path, output_annotated_path=output_annotated_path)
        elif garbage_ready:
            return self.garbage_classifier.predict(image_path)

        return {
            "status": "success",
            "detected_issue": "No significant civic hazard detected",
            "confidence": 0.5,
            "visual_severity": 10.0,
            "damage_area_percentage": 0.0,
            "detections": []
        }
