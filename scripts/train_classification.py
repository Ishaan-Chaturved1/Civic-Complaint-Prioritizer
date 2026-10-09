"""
Civic Complaint Prioritizer - IndiUrbanClean Garbage Classification Training Script
Trains ResNet-18 Transfer Learning classifier on 5 urban waste/cleanliness categories:
clean_street, construction_waste, dumpyard, open_waste, overfilled_bins.
Saves model weights to models/vision/garbage_classifier.pth.
"""

import os
import sys
import json
import time
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import models, transforms
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from ml.vision.garbage.dataset import IndiUrbanCleanDataset, GARBAGE_CLASSES


def train_garbage_classifier(epochs: int = 3, batch_size: int = 16, lr: float = 1e-4):
    print("=" * 65)
    print("STARTING INDIURBANCLEAN GARBAGE CLASSIFICATION TRAINING")
    print("=" * 65)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Execution Device: {device}")

    garbage_data_dir = Path("D:/Major Project/garbage/IndiUrbanClean-Dataset-main")
    if not garbage_data_dir.exists():
        print(f"Error: Dataset path {garbage_data_dir} does not exist.")
        return

    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_dataset = IndiUrbanCleanDataset(garbage_data_dir, split_csv="splits/train.csv", transform=train_transform)
    val_dataset = IndiUrbanCleanDataset(garbage_data_dir, split_csv="splits/val.csv", transform=val_transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    print(f"Training samples: {len(train_dataset)} | Validation samples: {len(val_dataset)}")
    print(f"Classes ({len(GARBAGE_CLASSES)}): {GARBAGE_CLASSES}")

    # Build model: ResNet-18 with ImageNet pretrained backbone
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, len(GARBAGE_CLASSES))
    )
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)

    best_val_acc = 0.0
    best_weights = None

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        start_t = time.time()
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        epoch_loss = running_loss / total
        epoch_acc = correct / total

        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)

        val_acc = val_correct / val_total
        elapsed = time.time() - start_t

        print(f"Epoch [{epoch}/{epochs}] - Loss: {epoch_loss:.4f} | Train Acc: {epoch_acc*100:.2f}% | Val Acc: {val_acc*100:.2f}% ({elapsed:.1f}s)")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_weights = model.state_dict().copy()

    # Final Evaluation on Validation Set
    model.load_state_dict(best_weights or model.state_dict())
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy().tolist())
            all_labels.extend(labels.numpy().tolist())

    acc = accuracy_score(all_labels, all_preds)
    report = classification_report(all_labels, all_preds, target_names=GARBAGE_CLASSES, output_dict=True)

    print("\n--- FINAL VALIDATION REPORT ---")
    print(classification_report(all_labels, all_preds, target_names=GARBAGE_CLASSES))

    # Save model weights
    save_dir = BASE_DIR / "models" / "vision"
    save_dir.mkdir(parents=True, exist_ok=True)
    target_path = save_dir / "garbage_classifier.pth"
    torch.save(best_weights or model.state_dict(), target_path)
    print(f"Trained model saved to: {target_path}")

    # Save metrics JSON
    metrics_path = save_dir / "garbage_classification_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({
            "model": "ResNet-18 Transfer Learning",
            "val_accuracy": round(acc, 4),
            "macro_f1": round(report['macro avg']['f1-score'], 4),
            "classes": GARBAGE_CLASSES,
            "report": report
        }, f, indent=2)
    print(f"Garbage classification metrics saved to: {metrics_path}")


if __name__ == "__main__":
    train_garbage_classifier(epochs=3, batch_size=16)
