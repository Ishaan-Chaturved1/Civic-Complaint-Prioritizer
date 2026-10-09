import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class DetectedObject(BaseModel):
    label: str
    confidence: float
    bbox: Optional[List[float]] = None  # [x, y, w, h] or [x1, y1, x2, y2]
    area: Optional[float] = None


class AIAnalysisBase(BaseModel):
    complaint_id: str
    text_category: str
    text_confidence: float
    text_severity: float
    visual_category: Optional[str] = None
    visual_confidence: Optional[float] = None
    visual_severity: Optional[float] = None
    detected_objects: List[Dict[str, Any]] = []
    segmentation_data: Optional[Dict[str, Any]] = None
    damage_area_percentage: Optional[float] = 0.0
    duplicate_similarity: Optional[float] = None
    multimodal_score: float
    explanation: str
    model_version: str = "1.0.0"


class AIAnalysisResponse(AIAnalysisBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True
