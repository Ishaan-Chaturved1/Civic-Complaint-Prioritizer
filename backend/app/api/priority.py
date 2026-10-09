from fastapi import APIRouter
from app.schemas.ml import PriorityCalculationRequest, PriorityCalculationResponse
from ml.priority.priority_engine import PriorityEngine
from ml.text.categories import CATEGORY_TO_DEPARTMENT

router = APIRouter(prefix="/priority", tags=["Priority Engine"])


@router.post("/calculate", response_model=PriorityCalculationResponse)
def calculate_priority(req: PriorityCalculationRequest):
    res = PriorityEngine.calculate(
        text_severity=req.text_severity,
        visual_severity=req.visual_severity,
        location_risk=req.location_risk or 50.0,
        people_impact=req.people_impact or 50.0,
        complaint_age_hours=req.complaint_age_hours or 0.0,
        historical_complaints=req.historical_complaints or 0,
        critical_keywords=req.safety_indicators or []
    )

    recommended_dept = CATEGORY_TO_DEPARTMENT.get("Public Safety" if res["severity_level"] == "CRITICAL" else "General", "General Municipal Grievance Cell")

    return {
        "priority_score": res["priority_score"],
        "severity_level": res["severity_level"],
        "sla_hours": res["sla_hours"],
        "recommended_department": recommended_dept,
        "factors": res["factors"],
        "explanation": res["explanation"]
    }
