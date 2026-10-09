import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from app.schemas.ml import (
    TextAnalysisRequest, TextAnalysisResponse,
    ImageAnalysisResponse, MultimodalAnalysisRequest
)
from ml.text.text_pipeline import TextPipelineService
from ml.vision.vision_service import VisionService
from ml.priority.priority_engine import PriorityEngine

router = APIRouter(prefix="/ml", tags=["Machine Learning Inference"])

text_pipeline = TextPipelineService()
vision_service = VisionService()


@router.post("/analyze-text", response_model=TextAnalysisResponse)
def analyze_text(request: TextAnalysisRequest):
    result = text_pipeline.analyze(request.text)
    return {
        "category": result["category"],
        "confidence": result["confidence"],
        "severity_score": result["severity_score"],
        "keywords": result["critical_keywords"] + result["medium_keywords"],
        "clean_text": result["clean_text"],
        "model_name": result["model_used"]
    }


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(
    image: UploadFile = File(...),
    category_hint: str = Form(None)
):
    if not image or not image.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No image file provided")

    # Write temporarily to run vision inference
    ext = Path(image.filename).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await image.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        res = vision_service.analyze_image(tmp_path, category_hint=category_hint)
        return res
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/analyze")
def analyze_multimodal(request: MultimodalAnalysisRequest):
    """
    Multimodal analysis combining text analysis and contextual coordinates.
    """
    full_text = f"{request.title}. {request.description}"
    text_res = text_pipeline.analyze(full_text)

    # Context location risk
    loc_risk = 65.0 if (request.latitude and request.longitude) else 45.0

    priority_res = PriorityEngine.calculate(
        text_severity=text_res["severity_score"],
        visual_severity=None,
        location_risk=loc_risk,
        people_impact=50.0,
        critical_keywords=text_res["critical_keywords"],
        category=text_res["category"]
    )

    return {
        "text_analysis": text_res,
        "priority_analysis": priority_res
    }
