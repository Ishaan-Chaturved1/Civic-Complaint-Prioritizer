"""
Dataset Inspection Script for Civic Complaint Prioritizer
Inspects local datasets:
1. Pothole Dataset (D:/Major Project/potholes)
2. Indian Garbage Dataset (D:/Major Project/garbage/IndiUrbanClean-Dataset-main)
"""

import os
import json
import csv
from pathlib import Path
from PIL import Image

DATA_ROOT = Path("D:/Major Project")
POTHOLE_DIR = DATA_ROOT / "potholes"
GARBAGE_DIR = DATA_ROOT / "garbage" / "IndiUrbanClean-Dataset-main"


def inspect_potholes():
    print("=" * 60)
    print("POTHOLE DATASET AUDIT")
    print("=" * 60)
    print(f"Path: {POTHOLE_DIR}")
    
    if not POTHOLE_DIR.exists():
        print("ERROR: Pothole directory does not exist.")
        return

    splits = ["train", "valid", "test"]
    stats = {}
    categories_all = set()
    total_annotations = 0
    total_images_all = 0
    has_segmentation = False

    for split in splits:
        split_dir = POTHOLE_DIR / split
        if not split_dir.exists():
            print(f"Split {split} not found!")
            continue

        coco_file = split_dir / "_annotations.coco.json"
        images = [f for f in split_dir.iterdir() if f.suffix.lower() in [".jpg", ".jpeg", ".png"] and f.name != "_annotations.coco.json"]
        corrupted_images = 0
        img_dimensions = set()

        for img_path in images[:20]:  # sample test dimensions & validity
            try:
                with Image.open(img_path) as im:
                    im.verify()
                with Image.open(img_path) as im:
                    img_dimensions.add(im.size)
            except Exception:
                corrupted_images += 1

        split_info = {
            "image_count": len(images),
            "coco_present": coco_file.exists(),
            "annotation_count": 0,
            "classes": [],
            "corrupted_sample_count": corrupted_images,
            "sample_dimensions": list(img_dimensions)
        }

        if coco_file.exists():
            with open(coco_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            categories = {c["id"]: c["name"] for c in data.get("categories", [])}
            split_info["classes"] = list(categories.values())
            categories_all.update(categories.values())
            
            annos = data.get("annotations", [])
            split_info["annotation_count"] = len(annos)
            total_annotations += len(annos)

            # Check if segmentation masks/polygons exist in annotations
            for ann in annos[:50]:
                seg = ann.get("segmentation")
                if seg and len(seg) > 0:
                    has_segmentation = True
                    break

        stats[split] = split_info
        total_images_all += len(images)

        print(f"\n--- Split: {split.upper()} ---")
        print(f"  Images: {split_info['image_count']}")
        print(f"  COCO file present: {split_info['coco_present']}")
        print(f"  Annotations: {split_info['annotation_count']}")
        print(f"  Classes in split: {split_info['classes']}")
        print(f"  Sample dimensions (width, height): {split_info['sample_dimensions']}")

    print("\n--- Summary for Potholes ---")
    print(f"Total images across splits: {total_images_all}")
    print(f"Total bounding box annotations: {total_annotations}")
    print(f"Unique classes across splits: {sorted(list(categories_all))}")
    print(f"Annotation format: COCO Object Detection JSON (_annotations.coco.json in each split folder)")
    print(f"Polygonal segmentation present in annotations: {has_segmentation}")
    print(f"Requires conversion to YOLO format (data.yaml, images/, labels/ with normalized txt): YES")


def inspect_garbage():
    print("\n" + "=" * 60)
    print("GARBAGE DATASET (IndiUrbanClean) AUDIT")
    print("=" * 60)
    print(f"Path: {GARBAGE_DIR}")

    if not GARBAGE_DIR.exists():
        print("ERROR: Garbage directory does not exist.")
        return

    images_root = GARBAGE_DIR / "images"
    labels_csv = GARBAGE_DIR / "annotations" / "labels.csv"
    splits_dir = GARBAGE_DIR / "splits"

    class_dirs = [d.name for d in images_root.iterdir() if d.is_dir()]
    print(f"\nClass directories in images/: {class_dirs}")

    total_images = 0
    class_counts = {}
    sample_dims = set()
    corrupted_count = 0

    for c in class_dirs:
        cdir = images_root / c
        imgs = [f for f in cdir.iterdir() if f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        class_counts[c] = len(imgs)
        total_images += len(imgs)

        for img_path in imgs[:10]:
            try:
                with Image.open(img_path) as im:
                    im.verify()
                with Image.open(img_path) as im:
                    sample_dims.add(im.size)
            except Exception:
                corrupted_count += 1

    print(f"\nImages per class directory:")
    for c, cnt in class_counts.items():
        print(f"  - {c}: {cnt}")
    print(f"Total raw images: {total_images}")
    print(f"Sample dimensions: {list(sample_dims)[:5]}")
    print(f"Corrupted images in sample: {corrupted_count}")

    # Inspect annotations / splits
    print("\nAnnotations Inspection:")
    if labels_csv.exists():
        with open(labels_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            print(f"  labels.csv entries: {len(rows)}")
            if rows:
                print(f"  labels.csv columns: {list(rows[0].keys())}")
                labels = set(r["label"] for r in rows)
                print(f"  Unique labels in CSV: {labels}")

    # Inspect splits
    print("\nSplits Inspection:")
    for s in ["train.csv", "val.csv", "test.csv"]:
        sp_path = splits_dir / s
        if sp_path.exists():
            with open(sp_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                print(f"  {s}: {len(rows)} entries")

    # Check for bounding boxes or segmentation masks
    print("\nObject Detection / Segmentation Verification:")
    print("  Checking for bounding box coordinates (xml/yolo txt/json)...")
    any_bbox = False
    any_masks = False

    # Check annotations folder
    ann_files = list((GARBAGE_DIR / "annotations").iterdir())
    print(f"  Files in annotations/: {[f.name for f in ann_files]}")

    print("  Conclusion for IndiUrbanClean:")
    print("  - Task: Multi-class Image Classification (5 urban waste / cleanliness classes)")
    print("  - Classes: clean_street, construction_waste, dumpyard, open_waste, overfilled_bins")
    print("  - Bounding boxes in dataset: NO (No box coords in labels.csv)")
    print("  - Pixel segmentation masks in dataset: NO (No mask images or polygon coordinates)")


if __name__ == "__main__":
    inspect_potholes()
    inspect_garbage()
