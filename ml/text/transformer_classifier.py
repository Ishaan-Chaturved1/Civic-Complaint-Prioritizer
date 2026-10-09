import os
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from ml.preprocessing.text_preprocessor import TextPreprocessor
from ml.text.categories import CIVIC_CATEGORIES


class TransformerComplaintClassifier:
    """
    DistilBERT Transformer Classifier for Civic Complaint Classification
    text -> tokenizer -> transformer -> classifier -> category + confidence
    """

    def __init__(self, model_dir: Optional[str] = None, num_labels: int = len(CIVIC_CATEGORIES)):
        self.categories = CIVIC_CATEGORIES
        self.num_labels = num_labels
        self.label2id = {c: i for i, c in enumerate(self.categories)}
        self.id2label = {i: c for i, c in enumerate(self.categories)}
        self.preprocessor = TextPreprocessor()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = None
        self.model = None
        self.is_trained = False

        if model_dir and os.path.exists(model_dir) and (os.path.exists(os.path.join(model_dir, "config.json")) or os.path.exists(os.path.join(model_dir, "model.pt"))):
            self.load(model_dir)

    def load(self, model_dir: str):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
            self.model.to(self.device)
            self.model.eval()
            self.is_trained = True
        except Exception as e:
            self.is_trained = False
            raise RuntimeError(f"Could not load transformer model from {model_dir}: {e}")

    def predict(self, text: str) -> Tuple[str, float]:
        if not self.is_trained or self.model is None or self.tokenizer is None:
            raise RuntimeError("Transformer model is not trained or loaded. Train using scripts/train_text.py")

        cleaned = self.preprocessor.clean(text)
        inputs = self.tokenizer(
            cleaned,
            return_tensors="pt",
            truncation=True,
            max_length=128,
            padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1).squeeze(0)
            conf, pred_idx = torch.max(probs, dim=-1)

        category = self.id2label[pred_idx.item()]
        confidence = round(float(conf.item()), 4)
        return category, confidence

    def save(self, output_dir: str):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        if self.model and self.tokenizer:
            self.model.save_pretrained(output_dir)
            self.tokenizer.save_pretrained(output_dir)
