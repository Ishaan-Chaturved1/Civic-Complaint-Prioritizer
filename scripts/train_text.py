"""
Civic Complaint Prioritizer - Text Classification Model Training Script
Trains TF-IDF + Logistic Regression / Linear SVM baseline on 10 Civic Categories.
Evaluates accuracy, precision, recall, F1-score, and confusion matrix.
Saves model artifacts to models/text/.
"""

import os
import sys
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from ml.text.baseline_classifier import BaselineTextClassifier
from ml.text.categories import CIVIC_CATEGORIES


# Curated realistic dataset of civic complaint grievances
DATASET_SAMPLES = [
    # Road Damage
    ("Huge pothole on MG Road near city hospital causing frequent two-wheeler accidents", "Road Damage"),
    ("Crater and broken asphalt on Ring Road near school gate, very dangerous for buses", "Road Damage"),
    ("Multiple deep potholes filled with rainwater after the storm on 5th cross road", "Road Damage"),
    ("Road surface has completely eroded and broken near metro station entrance", "Road Damage"),
    ("Dangerous sinkhole appearing in the middle of Main Street road", "Road Damage"),
    ("Severe tar peeling and cave-in on highway service road near flyover", "Road Damage"),
    ("Pavement is broken with large cracked slabs posing tripping hazard for pedestrians", "Road Damage"),
    ("Uneven road patch work caused biker to skid and suffer injury yesterday", "Road Damage"),

    # Garbage
    ("Open garbage dump overflowing on the corner of Market Street, terrible stench", "Garbage"),
    ("Overfilled public bins not cleared for 5 days attracting stray dogs and cattle", "Garbage"),
    ("Construction waste and debris dumped illegally by contractor on sidewalk", "Garbage"),
    ("Rotting solid waste dumped near residential apartment gate emitting foul odor", "Garbage"),
    ("Garbage truck has not collected waste in our lane for past one week", "Garbage"),
    ("Huge pile of plastic waste and food refuse dumped near vegetable market", "Garbage"),
    ("Stinking waste mound on public ground creating severe health hazard", "Garbage"),
    ("Uncollected municipal bins overflowing across the street blocking footpath", "Garbage"),

    # Water Supply
    ("Main drinking water pipeline has burst and potable water is flooding the street", "Water Supply"),
    ("No water supply in block C for the past 48 hours, residents suffering severely", "Water Supply"),
    ("Contaminated tap water coming with brownish muddy color and chemical smell", "Water Supply"),
    ("Underground supply pipe leaking with severe loss of clean municipal water", "Water Supply"),
    ("Low water pressure in municipal pipeline, unable to fill overhead tanks", "Water Supply"),
    ("Drinking water pipeline damaged during fiber optic digging work", "Water Supply"),
    ("Dirty yellow water with bad odor coming from municipal connection", "Water Supply"),

    # Sewage
    ("Manhole overflowing with black sewage water spilling directly into street", "Sewage"),
    ("Underground sewer line choked and blocked causing backflow into houses", "Sewage"),
    ("Sewage manhole cover is broken and left open, life-threatening danger", "Sewage"),
    ("Foul sewage water leaking onto pedestrian walkway near primary school", "Sewage"),
    ("Blocked drainage sewer causing black dirty water stagnant in our alley", "Sewage"),
    ("Open manhole on dark corner with raw sewage spilling out continuously", "Sewage"),

    # Drainage
    ("Stormwater drain completely clogged with silt causing severe waterlogging", "Drainage"),
    ("Road flooded with knee-deep rainwater due to blocked drainage canal", "Drainage"),
    ("Rainwater culvert collapsed, water entering ground floor shops", "Drainage"),
    ("Open storm drain uncovered and choked with plastic bottles and weeds", "Drainage"),
    ("Waterlogging on underpass road during moderate rain, cars getting stuck", "Drainage"),
    ("Monsoon drainage line blocked near railway crossing", "Drainage"),

    # Streetlight
    ("Streetlights on 12th main road not working for past 2 weeks, pitch dark at night", "Streetlight"),
    ("Flickering street lamp pole creating safety risk for women walking at night", "Streetlight"),
    ("Street light pole knocked down by truck, dangling wires on footpath", "Streetlight"),
    ("Dark street without functional lighting leading to thefts and safety issues", "Streetlight"),
    ("Solar streetlight battery dead, entire residential layout in total darkness", "Streetlight"),
    ("Streetlight bulb fused on main cross road opposite public park", "Streetlight"),

    # Electricity
    ("High tension electric wire snapped and hanging dangerously close to ground", "Electricity"),
    ("Electrical distribution transformer sparking with smoke on utility pole", "Electricity"),
    ("Open power junction box with exposed live wires near children playground", "Electricity"),
    ("Severe voltage fluctuation damaging household appliances in entire neighborhood", "Electricity"),
    ("Electric pole leaning precariously after heavy storm, risk of collapse", "Electricity"),
    ("Repeated power outages and transformer blast occurred this afternoon", "Electricity"),

    # Public Safety
    ("Dilapidated building boundary wall on verge of collapse on busy footpath", "Public Safety"),
    ("Stray dog pack attacking pedestrians and biting school children on street", "Public Safety"),
    ("Tree branch about to fall on electrical cables and passing vehicles", "Public Safety"),
    ("Fire hazard from illegal chemical storage in residential basement", "Public Safety"),
    ("Illegal fireworks stall setup blocking emergency exit and fire hydrant", "Public Safety"),
    ("Dangerous uncovered pit dug without barricading or warning signs", "Public Safety"),

    # Traffic
    ("Traffic signal not functioning at major 4-way intersection causing chaos", "Traffic"),
    ("Illegal parking on both sides of narrow commercial lane causing total gridlock", "Traffic"),
    ("Traffic lights stuck on red in all directions, severe traffic jam extending 2 km", "Traffic"),
    ("Broken divider on ring road allowing vehicles to make illegal hazardous U-turns", "Traffic"),
    ("Absence of zebra crossing or speed breaker near school causing overspeeding", "Traffic"),
    ("Encroachment on road by street vendors blocking vehicular movement", "Traffic"),

    # Other
    ("Illegal billboard installed without municipal permission blocking balcony", "Other"),
    ("Noise pollution from loud industrial generator running all night in zone", "Other"),
    ("Public park gate broken and benches vandalized by anti-social elements", "Other"),
    ("Unauthorized construction work continuing during night hours with heavy dust", "Other"),
    ("Public library reading room air conditioning and roof damaged", "Other")
]


def train_and_evaluate():
    print("=" * 65)
    print("TRAINING CIVIC COMPLAINT CATEGORY CLASSIFIER")
    print("=" * 65)

    texts = [sample[0] for sample in DATASET_SAMPLES]
    labels = [sample[1] for sample in DATASET_SAMPLES]

    print(f"Total labeled complaint records: {len(texts)}")
    print(f"Categories: {len(CIVIC_CATEGORIES)}")

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    print(f"Training samples: {len(X_train)} | Testing samples: {len(X_test)}")

    classifier = BaselineTextClassifier()
    classifier.fit(X_train, y_train)

    # Evaluate on test set
    y_pred = []
    for t in X_test:
        pred_label, _ = classifier.predict(t)
        y_pred.append(pred_label)

    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=CIVIC_CATEGORIES)

    print(f"\n--- EVALUATION METRICS ---")
    print(f"Accuracy: {acc * 100:.2f}%")
    print(f"Macro Precision: {report['macro avg']['precision']:.4f}")
    print(f"Macro Recall:    {report['macro avg']['recall']:.4f}")
    print(f"Macro F1-Score:  {report['macro avg']['f1-score']:.4f}")

    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Save trained model artifact
    save_path = BASE_DIR / "models" / "text" / "baseline_tfidf.joblib"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    classifier.save(str(save_path))
    print(f"Trained model saved to: {save_path}")

    # Save real metrics JSON
    metrics_path = BASE_DIR / "models" / "text" / "metrics.json"
    metrics_data = {
        "model_type": "TF-IDF + Balanced Logistic Regression",
        "accuracy": round(acc, 4),
        "macro_precision": round(report['macro avg']['precision'], 4),
        "macro_recall": round(report['macro avg']['recall'], 4),
        "macro_f1": round(report['macro avg']['f1-score'], 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "confusion_matrix": cm.tolist(),
        "categories": CIVIC_CATEGORIES
    }
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"Metrics saved to: {metrics_path}")


if __name__ == "__main__":
    train_and_evaluate()
