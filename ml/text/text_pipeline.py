import os
from pathlib import Path
from typing import Dict, Any, Optional
from ml.preprocessing.text_preprocessor import TextPreprocessor
from ml.text.categories import CIVIC_CATEGORIES, CATEGORY_TO_DEPARTMENT, CATEGORY_DEFAULT_SLA
from ml.text.baseline_classifier import BaselineTextClassifier
from ml.text.transformer_classifier import TransformerComplaintClassifier


class TextPipelineService:
    """
    High-level NLP analysis pipeline for Civic Complaints.
    Integrates cleaning, category classification, and severity estimation.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.preprocessor = TextPreprocessor()
        self.baseline_classifier = None
        self.transformer_classifier = None
        self.model_type = "heuristic"

        # Check for trained models
        baseline_file = Path(model_path or "models/text") / "baseline_tfidf.joblib"
        transformer_dir = Path(model_path or "models/text") / "distilbert"

        if transformer_dir.exists() and (transformer_dir / "config.json").exists():
            try:
                self.transformer_classifier = TransformerComplaintClassifier(str(transformer_dir))
                self.model_type = "transformer_distilbert"
            except Exception:
                pass

        if not self.transformer_classifier and baseline_file.exists():
            try:
                self.baseline_classifier = BaselineTextClassifier(str(baseline_file))
                self.model_type = "baseline_tfidf_logistic_regression"
            except Exception:
                pass

    def classify_heuristically(self, cleaned_text: str) -> tuple[str, float]:
        """
        Interim heuristic classifier based on domain keywords when training has not yet completed.
        """
        words = set(cleaned_text.lower().split())

        category_rules = [
            ("Road Damage", {"pothole", "potholes", "road", "asphalt", "crater", "tarmac", "crack", "pavement"}),
            ("Garbage", {"garbage", "trash", "waste", "debris", "litter", "dump", "bin", "bins", "stinking", "rubbish"}),
            ("Water Supply", {"water", "pipeline", "leakage", "drinking", "contamination", "supply", "tap", "pipe"}),
            ("Sewage", {"sewage", "sewer", "drainage", "manhole", "overflow", "gutter", "sludge"}),
            ("Drainage", {"drain", "drains", "waterlogging", "rainwater", "stormwater", "culvert"}),
            ("Streetlight", {"streetlight", "street", "light", "lamp", "pole", "darkness", "bulb"}),
            ("Electricity", {"electricity", "wire", "cable", "transformer", "spark", "electric", "power", "shock"}),
            ("Public Safety", {"accident", "hazard", "dangerous", "injury", "emergency", "fire", "collapse", "falling"}),
            ("Traffic", {"traffic", "signal", "jam", "congestion", "blockage", "junction", "zebra"})
        ]

        best_cat = "Other"
        max_matches = 0

        for cat, kw_set in category_rules:
            matches = len(words.intersection(kw_set))
            if matches > max_matches:
                max_matches = matches
                best_cat = cat

        confidence = 0.5 + min(max_matches * 0.15, 0.45) if max_matches > 0 else 0.4
        return best_cat, round(confidence, 3)

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Full text analysis returning category, confidence, severity, and keywords.
        """
        cleaned_text = self.preprocessor.clean(text)
        indicators = self.preprocessor.extract_severity_indicators(cleaned_text)

        category = "Other"
        confidence = 0.5
        model_used = self.model_type

        # 1. Try transformer
        if self.transformer_classifier and self.transformer_classifier.is_trained:
            try:
                category, confidence = self.transformer_classifier.predict(cleaned_text)
                model_used = "transformer_distilbert"
            except Exception:
                pass
        # 2. Try baseline TF-IDF
        elif self.baseline_classifier and self.baseline_classifier.pipeline:
            try:
                category, confidence = self.baseline_classifier.predict(cleaned_text)
                model_used = "baseline_tfidf"
            except Exception:
                pass
        # 3. Transparent heuristic baseline
        else:
            category, confidence = self.classify_heuristically(cleaned_text)
            model_used = "domain_heuristic_baseline (Train using scripts/train_text.py for DistilBERT/TF-IDF)"

        recommended_dept = CATEGORY_TO_DEPARTMENT.get(category, "General Municipal Grievance Cell")
        default_sla = CATEGORY_DEFAULT_SLA.get(category, 48)

        return {
            "category": category,
            "confidence": confidence,
            "severity_score": indicators["score"],
            "critical_keywords": indicators["critical_keywords"],
            "medium_keywords": indicators["medium_keywords"],
            "clean_text": cleaned_text,
            "recommended_department": recommended_dept,
            "default_sla_hours": default_sla,
            "model_used": model_used
        }
