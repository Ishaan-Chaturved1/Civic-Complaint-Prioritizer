import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.schemas.ai_analysis import AIAnalysisResponse


class ComplaintHistoryResponse(BaseModel):
    id: int
    complaint_id: str
    old_status: Optional[str] = None
    new_status: str
    changed_by: Optional[int] = None
    comment: Optional[str] = None
    timestamp: datetime.datetime

    class Config:
        from_attributes = True


class ComplaintCreate(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None


class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    department: Optional[str] = None
    priority_score: Optional[float] = None
    severity: Optional[str] = None
    comment: Optional[str] = None


class ComplaintResponse(BaseModel):
    id: str
    user_id: int
    title: str
    description: str
    category: str
    status: str
    severity: str
    priority_score: float
    department: str
    sla_hours: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    resolved_at: Optional[datetime.datetime] = None
    sla_status: Optional[str] = "ON_TRACK"
    ai_analysis: Optional[AIAnalysisResponse] = None
    history: Optional[List[ComplaintHistoryResponse]] = []

    class Config:
        from_attributes = True


class ComplaintSubmissionResult(BaseModel):
    complaint_id: str
    category: str
    severity: str
    priority_score: float
    department: str
    sla_hours: int
    explanation: str
    visual_category: Optional[str] = None
    damage_area_percentage: Optional[float] = None
    duplicate_warning: Optional[Dict[str, Any]] = None
    complaint: ComplaintResponse
