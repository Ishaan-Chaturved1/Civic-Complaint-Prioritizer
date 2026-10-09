"""
Civic Complaint Prioritizer - YOLO Pothole Object Detection Training Script
Trains Ultralytics YOLO model using transfer learning on the pothole dataset.
Evaluates mAP@50, mAP@50-95, precision, recall.
Saves model weights to models/vision/pothole_yolo.pt.
"""

import os
import sys
import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from ml.vision.pothole.converter import prepare_pothole_yolo_dataset


def train_pothole_detector(epochs: int = 5, img_size: int = 640, batch_size: int = 8):
    print("=" * 65)
    print("STARTING YOLO POTHOLE OBJECT DETECTION TRAINING")
    print("=" * 65)

    from ultralytics import YOLO

    # 1. Ensure dataset exists in YOLO format
    yolo_data_dir = BASE_DIR / "datasets" / "processed" / "potholes"
    yaml_path = yolo_data_dir / "data.yaml"

    if not yaml_path.exists():
        print("data.yaml not found. Running dataset conversion...")
        yaml_path = prepare_pothole_yolo_dataset(
            source_root=Path("D:/Major Project/potholes"),
            dest_root=yolo_data_dir
        )

    print(f"Dataset YAML ready at: {yaml_path}")

    # 2. Initialize YOLO model with transfer learning weights
    print("Loading pretrained YOLOv8n backbone for fine-tuning...")
    model = YOLO("yolov8n.pt")

    # 3. Train
    print(f"Commencing training: {epochs} epochs, batch {batch_size}, img_size {img_size}...")
    results = model.train(
        data=str(yaml_path),
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        project=str(BASE_DIR / "runs" / "pothole_detect"),
        name="train_exp",
        exist_ok=True,
        verbose=True
    )

    # 4. Validate
    print("\nEvaluating model on validation split...")
    val_results = model.val(data=str(yaml_path), split="val")

    # Extract metrics
    metrics = {
        "precision": round(float(val_results.box.p[0]) if len(val_results.box.p) > 0 else float(val_results.box.mp), 4),
        "recall": round(float(val_results.box.r[0]) if len(val_results.box.r) > 0 else float(val_results.box.mr), 4),
        "mAP50": round(float(val_results.box.map50), 4),
        "mAP50_95": round(float(val_results.box.map), 4),
        "fitness": round(float(val_results.fitness), 4)
    }

    print("\n--- VALIDATION RESULTS ---")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"mAP@50:    {metrics['mAP50']:.4f}")
    print(f"mAP@50-95: {metrics['mAP50_95']:.4f}")

    # 5. Save final weights to models/vision/
    models_vision_dir = BASE_DIR / "models" / "vision"
    models_vision_dir.mkdir(parents=True, exist_ok=True)
    target_weights = models_vision_dir / "pothole_yolo.pt"

    best_weights = Path(model.trainer.best) if hasattr(model.trainer, "best") and model.trainer.best else None
    if best_weights and best_weights.exists():
        shutil.copy2(best_weights, target_weights)
        print(f"Best model weights saved to: {target_weights}")
    else:
        model.save(str(target_weights))
        print(f"Model weights saved to: {target_weights}")

    # Save metrics JSON
    metrics_path = models_vision_dir / "pothole_detection_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Detection metrics recorded at: {metrics_path}")


if __name__ == "__main__":
    train_pothole_detector(epochs=3, batch_size=8)
