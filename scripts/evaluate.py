"""
Civic Complaint Prioritizer - Unified Evaluation Script
Evaluates:
1. Text Classification Model
2. Pothole YOLO Detection Model
3. Garbage Classification Model
4. Multimodal Priority Engine
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from ml.text.text_pipeline import TextPipelineService
from ml.vision.vision_service import VisionService
from ml.priority.priority_engine import PriorityEngine


def evaluate_all():
    print("=" * 65)
    print("CIVIC COMPLAINT PRIORITIZER - SYSTEM EVALUATION")
    print("=" * 65)

    # 1. Text Pipeline Evaluation
    print("\n1. Text Pipeline Status:")
    text_service = TextPipelineService()
    test_sample = "Deep pothole near St. Mary's School gate, car tyre burst and biker injured yesterday"
    t_res = text_service.analyze(test_sample)
    print(f"  Sample: '{test_sample}'")
    print(f"  Model active: {t_res['model_used']}")
    print(f"  Predicted Category: {t_res['category']} (Confidence: {t_res['confidence']})")
    print(f"  Severity Score: {t_res['severity_score']}/100")
    print(f"  Keywords detected: {t_res['critical_keywords'] + t_res['medium_keywords']}")

    # 2. Vision Models Evaluation
    print("\n2. Vision Services Status:")
    vis_service = VisionService()
    pothole_ready = vis_service.pothole_detector.is_loaded
    garbage_ready = vis_service.garbage_classifier.is_loaded

    print(f"  Pothole YOLO Detector: {'READY (weights loaded)' if pothole_ready else 'NOT LOADED (Run scripts/train_detection.py)'}")
    print(f"  Garbage Classifier:    {'READY (weights loaded)' if garbage_ready else 'NOT LOADED (Run scripts/train_classification.py)'}")

    # Check for recorded metrics
    pothole_metrics_file = BASE_DIR / "models" / "vision" / "pothole_detection_metrics.json"
    if pothole_metrics_file.exists():
        with open(pothole_metrics_file, "r") as f:
            pm = json.load(f)
        print(f"  Pothole Detection Recorded Metrics: mAP@50={pm.get('mAP50')}, Precision={pm.get('precision')}, Recall={pm.get('recall')}")

    garbage_metrics_file = BASE_DIR / "models" / "vision" / "garbage_classification_metrics.json"
    if garbage_metrics_file.exists():
        with open(garbage_metrics_file, "r") as f:
            gm = json.load(f)
        print(f"  Garbage Classification Recorded Metrics: Accuracy={gm.get('val_accuracy')}, Macro F1={gm.get('macro_f1')}")

    # 3. Multimodal Priority Engine
    print("\n3. Multimodal Priority Engine Test:")
    priority_res = PriorityEngine.calculate(
        text_severity=t_res["severity_score"],
        visual_severity=85.0,
        location_risk=80.0,
        people_impact=75.0,
        critical_keywords=t_res["critical_keywords"],
        damage_area_percentage=18.5
    )
    print(f"  Final Priority Score: {priority_res['priority_score']}/100")
    print(f"  Priority Classification: {priority_res['severity_level']}")
    print(f"  Suggested SLA: {priority_res['sla_hours']} hours")
    print(f"  Explanation: {priority_res['explanation']}")

    print("\nEvaluation pipeline complete.")


if __name__ == "__main__":
    evaluate_all()
