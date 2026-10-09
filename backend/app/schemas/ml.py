from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class TextAnalysisRequest(BaseModel):
    text: str


class TextAnalysisResponse(BaseModel):
    category: str
    confidence: float
    severity_score: float
    keywords: List[str]
    clean_text: str
    model_name: str


class ImageAnalysisResponse(BaseModel):
    status: str
    detected_issue: Optional[str] = None
    confidence: Optional[float] = None
    visual_severity: Optional[float] = None
    damage_area_percentage: Optional[float] = None
    detections: List[Dict[str, Any]] = []
    segmentation: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class PriorityCalculationRequest(BaseModel):
    text_severity: float
    visual_severity: Optional[float] = None
    location_risk: Optional[float] = 50.0
    people_impact: Optional[float] = 50.0
    complaint_age_hours: Optional[float] = 0.0
    historical_complaints: Optional[int] = 0
    safety_indicators: Optional[List[str]] = []


class PriorityCalculationResponse(BaseModel):
    priority_score: float
    severity_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    sla_hours: int
    recommended_department: str
    factors: Dict[str, Any]
    explanation: str


class MultimodalAnalysisRequest(BaseModel):
    title: str
    description: str
    image_path: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
