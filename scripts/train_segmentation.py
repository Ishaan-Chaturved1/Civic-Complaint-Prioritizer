"""
Civic Complaint Prioritizer - YOLO Instance Segmentation Training Script
Trains YOLOv8-seg on pothole polygonal annotations from the local COCO dataset.
Evaluates mask mAP@50 and box mAP@50.
Saves model weights to models/vision/pothole_seg.pt.
"""

import os
import sys
import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def convert_coco_polygons_to_yolo_seg(
    coco_json_path: Path,
    images_src_dir: Path,
    images_dest_dir: Path,
    labels_dest_dir: Path,
    class_id: int = 0
) -> int:
    """
    Converts polygon segmentations to YOLO segmentation format:
    <class-id> <x1> <y1> <x2> <y2> ... <xn> <yn> (normalized 0-1)
    """
    images_dest_dir.mkdir(parents=True, exist_ok=True)
    labels_dest_dir.mkdir(parents=True, exist_ok=True)

    if not coco_json_path.exists():
        return 0

    with open(coco_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    images_info = {img["id"]: img for img in data.get("images", [])}
    img_to_anns = {}
    for ann in data.get("annotations", []):
        img_id = ann["image_id"]
        if img_id not in img_to_anns:
            img_to_anns[img_id] = []
        img_to_anns[img_id].append(ann)

    converted = 0
    for img_id, img_info in images_info.items():
        fname = img_info["file_name"]
        src_img = images_src_dir / fname
        if not src_img.exists():
            continue

        dst_img = images_dest_dir / fname
        if not dst_img.exists():
            shutil.copy2(src_img, dst_img)

        width = float(img_info["width"])
        height = float(img_info["height"])

        label_file = labels_dest_dir / (Path(fname).stem + ".txt")
        lines = []

        for ann in img_to_anns.get(img_id, []):
            segs = ann.get("segmentation", [])
            if not segs:
                continue

            for seg in segs:
                if len(seg) < 6:  # need at least 3 points (x, y)
                    continue
                # Normalize points
                norm_pts = []
                for i in range(0, len(seg), 2):
                    px = max(0.0, min(1.0, seg[i] / width))
                    py = max(0.0, min(1.0, seg[i + 1] / height))
                    norm_pts.extend([f"{px:.6f}", f"{py:.6f}"])
                lines.append(f"{class_id} " + " ".join(norm_pts))

        with open(label_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        converted += 1

    return converted


def train_pothole_segmentation(epochs: int = 3, batch_size: int = 8):
    print("=" * 65)
    print("STARTING YOLO POTHOLE INSTANCE SEGMENTATION TRAINING")
    print("=" * 65)

    from ultralytics import YOLO

    seg_data_dir = BASE_DIR / "datasets" / "processed" / "potholes_seg"
    seg_data_dir.mkdir(parents=True, exist_ok=True)
    yaml_path = seg_data_dir / "data.yaml"

    if not yaml_path.exists():
        print("Converting COCO polygon segmentations to YOLO segmentation format...")
        src_root = Path("D:/Major Project/potholes")
        for split in ["train", "valid", "test"]:
            dst_split = "val" if split == "valid" else split
            convert_coco_polygons_to_yolo_seg(
                src_root / split / "_annotations.coco.json",
                src_root / split,
                seg_data_dir / "images" / dst_split,
                seg_data_dir / "labels" / dst_split,
                class_id=0
            )

        data_yaml = {
            "path": str(seg_data_dir.resolve()).replace("\\", "/"),
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "names": {0: "pothole"}
        }
        import yaml
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(data_yaml, f)

    print(f"Segmentation YAML configured at: {yaml_path}")

    print("Initializing YOLOv8n-seg backbone...")
    model = YOLO("yolov8n-seg.pt")

    print(f"Training segmentation for {epochs} epochs...")
    model.train(
        data=str(yaml_path),
        epochs=epochs,
        batch=batch_size,
        project=str(BASE_DIR / "runs" / "pothole_seg"),
        name="seg_exp",
        exist_ok=True,
        verbose=True
    )

    # Save target weights
    target_weights = BASE_DIR / "models" / "vision" / "pothole_seg.pt"
    target_weights.parent.mkdir(parents=True, exist_ok=True)
    best = Path(model.trainer.best) if hasattr(model.trainer, "best") and model.trainer.best else None
    if best and best.exists():
        shutil.copy2(best, target_weights)
    else:
        model.save(str(target_weights))
    print(f"Segmentation model weights saved to {target_weights}")


if __name__ == "__main__":
    train_pothole_segmentation(epochs=3, batch_size=8)
