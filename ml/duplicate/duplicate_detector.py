from typing import List, Dict, Any, Optional
import numpy as np


class DuplicateDetector:
    """
    Duplicate Complaint Detection Service using Semantic Embeddings
    Uses sentence-transformers / cosine similarity to identify related civic reports.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            # Fallback to local scikit-learn TF-IDF similarity if network/download is restricted
            print(f"Notice: SentenceTransformer initialization ({e}). Using robust TF-IDF embedding fallback.")
            self.model = None

    def compute_embedding(self, text: str) -> np.ndarray:
        if not text:
            return np.zeros(384, dtype=np.float32)

        if self.model is not None:
            try:
                emb = self.model.encode(text, convert_to_numpy=True)
                return emb
            except Exception:
                pass

        # Robust TF-IDF character/word n-gram vector fallback
        from sklearn.feature_extraction.text import HashingVectorizer
        vec = HashingVectorizer(n_features=384, alternate_sign=False)
        return vec.fit_transform([text]).toarray()[0].astype(np.float32)

    @staticmethod
    def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (norm1 * norm2))

    def check_for_duplicates(
        self,
        new_text: str,
        existing_complaints: List[Dict[str, Any]],
        threshold: float = 0.80
    ) -> Optional[Dict[str, Any]]:
        """
        Compares new complaint against existing active complaints.
        Returns highest similarity match if above threshold.
        """
        if not existing_complaints or not new_text:
            return None

        new_emb = self.compute_embedding(new_text)
        best_match = None
        highest_sim = 0.0
        matching_count = 0

        for comp in existing_complaints:
            comp_text = f"{comp.get('title', '')}. {comp.get('description', '')}"
            comp_emb = self.compute_embedding(comp_text)
            sim = self.cosine_similarity(new_emb, comp_emb)

            if sim > threshold:
                matching_count += 1
                if sim > highest_sim:
                    highest_sim = sim
                    best_match = comp

        if best_match and highest_sim >= threshold:
            return {
                "is_duplicate": True,
                "similarity_score": round(highest_sim, 4),
                "matched_complaint_id": best_match.get("id"),
                "matched_title": best_match.get("title"),
                "matched_category": best_match.get("category"),
                "related_reports_count": matching_count,
                "message": f"Similar complaint detected ({round(highest_sim * 100, 1)}% match with {best_match.get('id')})."
            }

        return None
