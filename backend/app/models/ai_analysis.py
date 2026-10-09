import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    complaint_id = Column(String(50), ForeignKey("complaints.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    text_category = Column(String(80), nullable=False)
    text_confidence = Column(Float, default=0.0, nullable=False)
    text_severity = Column(Float, default=0.0, nullable=False)
    
    visual_category = Column(String(80), nullable=True)
    visual_confidence = Column(Float, nullable=True)
    visual_severity = Column(Float, nullable=True)
    
    detected_objects = Column(JSON, default=list, nullable=False)
    segmentation_data = Column(JSON, default=dict, nullable=True)
    damage_area_percentage = Column(Float, default=0.0, nullable=True)
    duplicate_similarity = Column(Float, nullable=True)
    
    multimodal_score = Column(Float, default=0.0, nullable=False)
    explanation = Column(Text, nullable=False)
    model_version = Column(String(50), default="1.0.0", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    complaint = relationship("Complaint", back_populates="ai_analysis")
