import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from ml.preprocessing.text_preprocessor import TextPreprocessor
from ml.text.categories import CIVIC_CATEGORIES


class BaselineTextClassifier:
    """
    TF-IDF + Logistic Regression / Linear Classifier for Civic Complaints
    """

    def __init__(self, model_path: Optional[str] = None):
        self.preprocessor = TextPreprocessor()
        self.pipeline: Optional[Pipeline] = None
        self.categories = CIVIC_CATEGORIES
        self.model_path = model_path

        if model_path and os.path.exists(model_path):
            self.load(model_path)

    def build_pipeline(self) -> Pipeline:
        return Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=5000,
                sublinear_tf=True
            )),
            ("clf", LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                C=1.5
            ))
        ])

    def fit(self, texts, labels):
        cleaned_texts = [self.preprocessor.clean(t) for t in texts]
        self.pipeline = self.build_pipeline()
        self.pipeline.fit(cleaned_texts, labels)
        return self

    def predict(self, text: str) -> Tuple[str, float]:
        if self.pipeline is None:
            raise RuntimeError("Baseline classifier is not trained. Call fit() or load().")
        
        cleaned = self.preprocessor.clean(text)
        pred_label = self.pipeline.predict([cleaned])[0]
        
        # Calculate confidence probability
        proba = self.pipeline.predict_proba([cleaned])[0]
        max_idx = self.pipeline.classes_.tolist().index(pred_label)
        confidence = float(proba[max_idx])

        return pred_label, round(confidence, 4)

    def save(self, filepath: str):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, filepath)
        self.model_path = filepath

    def load(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found at {filepath}")
        self.pipeline = joblib.load(filepath)
        self.model_path = filepath
