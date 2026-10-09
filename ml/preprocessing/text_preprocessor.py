import re
from typing import List, Dict, Set, Any


CRITICAL_SEVERITY_KEYWORDS: Set[str] = {
    "accident", "injury", "injured", "dead", "death", "fatal", "hospital",
    "school", "blocked", "dangerous", "hazard", "fire", "emergency", "collapsed",
    "electric", "shock", "sparking", "overflowing", "explosion", "flooding",
    "submerged", "casualty", "ambulance", "trapped", "sinkhole", "deep"
}

MEDIUM_SEVERITY_KEYWORDS: Set[str] = {
    "traffic", "delay", "smell", "odor", "stinking", "pothole", "garbage",
    "waste", "broken", "leak", "leaking", "crack", "dark", "no light", "dump",
    "unclean", "dust", "mosquito", "drain", "sewage", "pile", "unattended"
}


class TextPreprocessor:
    """
    NLP Text Preprocessing Pipeline
    Preserves critical civic severity cues while cleaning noise.
    """

    def __init__(self):
        # Compiled regex patterns for speed
        self.url_pattern = re.compile(r"https?://\S+|www\.\S+")
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        self.special_char_pattern = re.compile(r"[^\w\s\.\,\!\?\-]")
        self.duplicate_char_pattern = re.compile(r"(.)\1{2,}")
        self.multiple_spaces_pattern = re.compile(r"\s+")

    def clean(self, text: str) -> str:
        """
        Cleans and normalizes complaint text.
        """
        if not text:
            return ""

        # Lowercase
        cleaned = text.lower()

        # Remove URLs
        cleaned = self.url_pattern.sub(" ", cleaned)

        # Remove emails
        cleaned = self.email_pattern.sub(" ", cleaned)

        # Duplicate character normalization (e.g. 'sooooo deeeeep' -> 'so deep')
        cleaned = self.duplicate_char_pattern.sub(r"\1\1", cleaned)

        # Remove strange non-ASCII/non-punctuation symbols
        cleaned = self.special_char_pattern.sub(" ", cleaned)

        # Whitespace normalization
        cleaned = self.multiple_spaces_pattern.sub(" ", cleaned).strip()

        return cleaned

    def extract_severity_indicators(self, cleaned_text: str) -> Dict[str, Any]:
        """
        Extracts civic severity indicators from text without throwing away
        domain-critical terms like 'hospital', 'school', 'accident', 'injury'.
        """
        words = set(re.findall(r"\b\w+\b", cleaned_text.lower()))
        critical_found = sorted(list(words.intersection(CRITICAL_SEVERITY_KEYWORDS)))
        medium_found = sorted(list(words.intersection(MEDIUM_SEVERITY_KEYWORDS)))

        # Rule-based severity baseline (0-100)
        base_score = 30.0
        if "urgent" in words or "immediately" in words or "crisis" in words:
            base_score += 15.0
        
        base_score += min(len(critical_found) * 18.0, 50.0)
        base_score += min(len(medium_found) * 6.0, 20.0)

        severity_score = min(max(base_score, 10.0), 100.0)

        return {
            "score": round(severity_score, 1),
            "critical_keywords": critical_found,
            "medium_keywords": medium_found,
            "all_indicators": critical_found + medium_found
        }
