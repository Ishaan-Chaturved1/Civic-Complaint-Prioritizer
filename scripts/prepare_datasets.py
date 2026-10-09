"""
Civic Complaint Prioritizer - Dataset Preparation Script
Prepares:
1. Pothole dataset conversion to Ultralytics YOLO format with data.yaml
2. Indian Garbage (IndiUrbanClean) verification and preprocessing checks
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from ml.vision.pothole.converter import prepare_pothole_yolo_dataset


def main():
    print("=" * 60)
    print("STEP 1: PREPARING POTHOLE YOLO DATASET")
    print("=" * 60)
    source_potholes = Path("D:/Major Project/potholes")
    dest_potholes = BASE_DIR / "datasets" / "processed" / "potholes"
    
    if not source_potholes.exists():
        print(f"Error: Pothole source path {source_potholes} does not exist.")
        return

    yaml_path = prepare_pothole_yolo_dataset(source_potholes, dest_potholes)
    print(f"Pothole dataset preparation complete. YAML at: {yaml_path}")

    print("\n" + "=" * 60)
    print("STEP 2: PREPARING INDIURBANCLEAN GARBAGE DATASET")
    print("=" * 60)
    garbage_dir = Path("D:/Major Project/garbage/IndiUrbanClean-Dataset-main")
    if not garbage_dir.exists():
        print(f"Error: Garbage source path {garbage_dir} does not exist.")
        return

    splits_dir = garbage_dir / "splits"
    print(f"Checking pre-stratified splits in {splits_dir}:")
    for s in ["train.csv", "val.csv", "test.csv"]:
        sp = splits_dir / s
        if sp.exists():
            with open(sp, "r", encoding="utf-8") as f:
                lines = f.readlines()
            print(f"  - {s}: {len(lines) - 1} samples ready for training.")
        else:
            print(f"  - Warning: {s} missing!")

    print("\nDataset preparation finished successfully.")


if __name__ == "__main__":
    main()
