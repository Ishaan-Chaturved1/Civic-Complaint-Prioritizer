from typing import Dict, Any, List, Optional


class PriorityEngine:
    """
    Transparent Multimodal Civic Priority Calculation Engine.
    Combines text severity, visual severity, location risk, people impacted,
    complaint age, historical reports, and safety indicators into a 0-100 score.
    """

    # Configurable weights summing to 1.0
    DEFAULT_WEIGHTS = {
        "text_severity": 0.30,
        "visual_severity": 0.35,
        "location_risk": 0.15,
        "people_impact": 0.10,
        "history_and_age": 0.10
    }

    @classmethod
    def get_severity_level(cls, score: float) -> str:
        if score >= 90.0:
            return "CRITICAL"
        elif score >= 75.0:
            return "HIGH"
        elif score >= 50.0:
            return "MEDIUM"
        else:
            return "LOW"

    @classmethod
    def get_sla_hours(cls, severity_level: str) -> int:
        sla_table = {
            "CRITICAL": 24,
            "HIGH": 48,
            "MEDIUM": 72,
            "LOW": 168  # 7 days
        }
        return sla_table.get(severity_level, 72)

    @classmethod
    def calculate(
        cls,
        text_severity: float,
        visual_severity: Optional[float] = None,
        location_risk: float = 50.0,
        people_impact: float = 50.0,
        complaint_age_hours: float = 0.0,
        historical_complaints: int = 0,
        critical_keywords: Optional[List[str]] = None,
        damage_area_percentage: Optional[float] = None,
        category: str = "Other"
    ) -> Dict[str, Any]:
        """
        Calculates 0-100 priority score with full mathematical transparency
        and feature attribution.
        """
        critical_keywords = critical_keywords or []
        
        # When image is not provided, redistribute visual weight to text and context
        weights = cls.DEFAULT_WEIGHTS.copy()
        if visual_severity is None:
            weights["text_severity"] = 0.55
            weights["location_risk"] = 0.20
            weights["people_impact"] = 0.15
            weights["history_and_age"] = 0.10
            eff_visual_severity = 0.0
        else:
            eff_visual_severity = float(visual_severity)

        # Normalize features
        eff_text_severity = max(0.0, min(100.0, float(text_severity)))
        eff_location_risk = max(0.0, min(100.0, float(location_risk)))
        eff_people_impact = max(0.0, min(100.0, float(people_impact)))

        # History and Age factor (0-100)
        age_factor = min(complaint_age_hours * 0.8, 50.0)
        history_factor = min(historical_complaints * 10.0, 50.0)
        history_and_age = min(100.0, age_factor + history_factor)

        # Base weighted calculation
        if visual_severity is not None:
            raw_score = (
                (eff_text_severity * weights["text_severity"]) +
                (eff_visual_severity * weights["visual_severity"]) +
                (eff_location_risk * weights["location_risk"]) +
                (eff_people_impact * weights["people_impact"]) +
                (history_and_age * weights["history_and_age"])
            )
        else:
            raw_score = (
                (eff_text_severity * weights["text_severity"]) +
                (eff_location_risk * weights["location_risk"]) +
                (eff_people_impact * weights["people_impact"]) +
                (history_and_age * weights["history_and_age"])
            )

        # Critical boosts for life-safety keywords (e.g. accident, hospital, school)
        boost = 0.0
        reasons = []

        if any(kw in critical_keywords for kw in ["accident", "injury", "dead", "fatal", "death"]):
            boost += 12.0
            reasons.append("Mentions immediate safety threat/injuries")

        if any(kw in critical_keywords for kw in ["hospital", "school", "emergency"]):
            boost += 8.0
            reasons.append("Located near critical infrastructure (school/hospital)")

        if damage_area_percentage and damage_area_percentage > 25.0:
            boost += 6.0
            reasons.append(f"High visual damage area ({damage_area_percentage}%)")

        final_score = round(min(100.0, max(0.0, raw_score + boost)), 1)
        severity_level = cls.get_severity_level(final_score)
        sla_hours = cls.get_sla_hours(severity_level)

        # Generate transparent factual explanation based on contributing factors
        explanation_parts = [
            f"Rated as {severity_level} priority (score {final_score}/100)."
        ]
        if visual_severity is not None:
            explanation_parts.append(f"Visual severity contributed {eff_visual_severity}/100.")
        explanation_parts.append(f"Text analysis indicated severity {eff_text_severity}/100.")

        if reasons:
            explanation_parts.append("Key escalation factors: " + "; ".join(reasons) + ".")

        explanation = " ".join(explanation_parts)

        return {
            "priority_score": final_score,
            "severity_level": severity_level,
            "sla_hours": sla_hours,
            "explanation": explanation,
            "factors": {
                "text_severity": eff_text_severity,
                "visual_severity": eff_visual_severity if visual_severity is not None else None,
                "location_risk": eff_location_risk,
                "people_impact": eff_people_impact,
                "history_and_age": round(history_and_age, 1),
                "safety_boost": boost,
                "weights_used": weights
            }
        }
