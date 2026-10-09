import os
import csv
from pathlib import Path
from typing import Optional, Callable, Tuple
import torch
from torch.utils.data import Dataset
from PIL import Image

GARBAGE_CLASSES = [
    "clean_street",
    "construction_waste",
    "dumpyard",
    "open_waste",
    "overfilled_bins"
]

CLASS_TO_IDX = {cls_name: idx for idx, cls_name in enumerate(GARBAGE_CLASSES)}
IDX_TO_CLASS = {idx: cls_name for idx, cls_name in enumerate(GARBAGE_CLASSES)}


class IndiUrbanCleanDataset(Dataset):
    """
    PyTorch Dataset for IndiUrbanClean urban waste classification.
    Reads filenames and labels from split CSV (train.csv, val.csv, test.csv).
    """

    def __init__(
        self,
        dataset_root: Path,
        split_csv: str = "splits/train.csv",
        transform: Optional[Callable] = None
    ):
        self.dataset_root = Path(dataset_root)
        self.transform = transform
        self.samples = []

        csv_path = self.dataset_root / split_csv
        if not csv_path.exists():
            raise FileNotFoundError(f"Split CSV not found at {csv_path}")

        images_root = self.dataset_root / "images"

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = row["filename"]
                label_name = row["label"]
                if label_name not in CLASS_TO_IDX:
                    continue

                img_path = images_root / label_name / filename
                if img_path.exists():
                    self.samples.append((img_path, CLASS_TO_IDX[label_name]))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label_idx = self.samples[idx]
        with Image.open(img_path) as im:
            image = im.convert("RGB")

        if self.transform:
            image = self.transform(image)

        return image, label_idx
