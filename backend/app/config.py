import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Civic Complaint Prioritizer"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"

    # Database: Supports PostgreSQL and falls back gracefully to SQLite for self-contained local runs
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./civic_complaints.db")

    # JWT Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "civic-complaint-prioritizer-super-secret-key-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Uploads & Storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = Path(__file__).resolve().parent.parent.parent / "uploads"
    MAX_UPLOAD_SIZE_MB: int = 15

    # Local Datasets
    DATA_ROOT: str = os.getenv("DATA_ROOT", "D:/Major Project")
    POTHOLE_DATASET_PATH: str = os.getenv("POTHOLE_DATASET_PATH", "D:/Major Project/potholes")
    GARBAGE_DATASET_PATH: str = os.getenv("GARBAGE_DATASET_PATH", "D:/Major Project/garbage/IndiUrbanClean-Dataset-main")

    # Models Paths
    MODELS_DIR: Path = Path(__file__).resolve().parent.parent.parent / "models"
    TEXT_MODEL_PATH: str = str(Path(__file__).resolve().parent.parent.parent / "models" / "text")
    VISION_MODEL_PATH: str = str(Path(__file__).resolve().parent.parent.parent / "models" / "vision" / "pothole_yolo.pt")
    GARBAGE_MODEL_PATH: str = str(Path(__file__).resolve().parent.parent.parent / "models" / "vision" / "garbage_classifier.pth")
    SEGMENTATION_MODEL_PATH: str = str(Path(__file__).resolve().parent.parent.parent / "models" / "vision" / "pothole_seg.pt")
    MULTIMODAL_MODEL_PATH: str = str(Path(__file__).resolve().parent.parent.parent / "models" / "multimodal" / "priority_fusion.pth")

    # ML Inference Parameters
    SIMILARITY_THRESHOLD: float = 0.82
    CONFIDENCE_THRESHOLD: float = 0.35

    # CORS
    CORS_ORIGINS: str = "http://localhost:5000,http://localhost:5173,http://localhost:3000,http://127.0.0.1:5000,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
(settings.UPLOAD_DIR / "complaints").mkdir(parents=True, exist_ok=True)
(settings.MODELS_DIR / "text").mkdir(parents=True, exist_ok=True)
(settings.MODELS_DIR / "vision").mkdir(parents=True, exist_ok=True)
(settings.MODELS_DIR / "multimodal").mkdir(parents=True, exist_ok=True)
