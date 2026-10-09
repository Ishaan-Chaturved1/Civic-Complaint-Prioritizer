import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List
import yaml


def convert_coco_to_yolo(
    coco_json_path: Path,
    images_src_dir: Path,
    images_dest_dir: Path,
    labels_dest_dir: Path,
    target_class_index: int = 0
) -> int:
    """
    Converts COCO format annotations to YOLO normalized bounding box format:
    <class_id> <x_center> <y_center> <width> <height>
    """
    images_dest_dir.mkdir(parents=True, exist_ok=True)
    labels_dest_dir.mkdir(parents=True, exist_ok=True)

    if not coco_json_path.exists():
        print(f"Warning: COCO file {coco_json_path} does not exist.")
        return 0

    with open(coco_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Map image id to metadata
    images_info = {img["id"]: img for img in data.get("images", [])}

    # Group annotations by image_id
    img_to_anns: Dict[int, List[Dict[str, Any]]] = {}
    for ann in data.get("annotations", []):
        img_id = ann["image_id"]
        if img_id not in img_to_anns:
            img_to_anns[img_id] = []
        img_to_anns[img_id].append(ann)

    converted_count = 0

    for img_id, img_info in images_info.items():
        file_name = img_info["file_name"]
        src_img_file = images_src_dir / file_name

        if not src_img_file.exists():
            continue

        dest_img_file = images_dest_dir / file_name
        # Copy image if not already present
        if not dest_img_file.exists():
            shutil.copy2(src_img_file, dest_img_file)

        width = float(img_info["width"])
        height = float(img_info["height"])

        txt_file_name = Path(file_name).stem + ".txt"
        label_file = labels_dest_dir / txt_file_name

        annotations = img_to_anns.get(img_id, [])
        lines = []

        for ann in annotations:
            bbox = ann.get("bbox")
            if not bbox or len(bbox) != 4:
                continue

            x_min, y_min, w, h = bbox
            # Avoid invalid boxes
            if w <= 0 or h <= 0 or width <= 0 or height <= 0:
                continue

            # Convert COCO (x_min, y_min, w, h) to YOLO (x_center, y_center, w, h) normalized
            x_center = (x_min + w / 2.0) / width
            y_center = (y_min + h / 2.0) / height
            w_norm = w / width
            h_norm = h / height

            # Clip to [0, 1]
            x_center = max(0.0, min(1.0, x_center))
            y_center = max(0.0, min(1.0, y_center))
            w_norm = max(0.0, min(1.0, w_norm))
            h_norm = max(0.0, min(1.0, h_norm))

            lines.append(f"{target_class_index} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")

        with open(label_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        converted_count += 1

    return converted_count


def prepare_pothole_yolo_dataset(
    source_root: Path = Path("D:/Major Project/potholes"),
    dest_root: Path = Path("datasets/processed/potholes")
) -> Path:
    """
    Creates full YOLO dataset structure and data.yaml
    """
    dest_root.mkdir(parents=True, exist_ok=True)

    splits_map = {
        "train": "train",
        "valid": "val",
        "test": "test"
    }

    counts = {}
    for src_split, dst_split in splits_map.items():
        src_dir = source_root / src_split
        coco_json = src_dir / "_annotations.coco.json"
        img_dest = dest_root / "images" / dst_split
        lbl_dest = dest_root / "labels" / dst_split

        cnt = convert_coco_to_yolo(coco_json, src_dir, img_dest, lbl_dest, target_class_index=0)
        counts[dst_split] = cnt
        print(f"Pothole YOLO conversion: {src_split} -> {dst_split}: {cnt} images prepared.")

    # Create data.yaml
    data_yaml_content = {
        "path": str(dest_root.resolve()).replace("\\", "/"),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "names": {
            0: "pothole"
        }
    }

    yaml_path = dest_root / "data.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data_yaml_content, f, sort_keys=False)

    print(f"data.yaml generated at {yaml_path}")
    return yaml_path


if __name__ == "__main__":
    prepare_pothole_yolo_dataset()
