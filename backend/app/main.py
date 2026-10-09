import logging
import sys
from pathlib import Path

# Ensure root and backend directories are in sys.path
BASE_APP_DIR = Path(__file__).resolve().parent.parent
ROOT_PROJECT_DIR = BASE_APP_DIR.parent
if str(ROOT_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_PROJECT_DIR))
if str(BASE_APP_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_APP_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models.user import User, UserRole
from app.auth.security import hash_password
from app.services.department_service import DepartmentService
from app.api.auth import router as auth_router
from app.api.complaints import router as complaints_router
from app.api.ml import router as ml_router
from app.api.priority import router as priority_router
from app.api.admin import router as admin_router
from app.api.officer import router as officer_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("civic.main")

app = FastAPI(
    title=settings.APP_NAME,
    description="A Multimodal AI Platform for Intelligent Civic Complaint Detection, Severity Analysis and Priority Routing.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local full-stack development and testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount local uploads directory for complaint images
uploads_dir = Path(settings.UPLOAD_DIR)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(complaints_router, prefix=settings.API_V1_PREFIX)
app.include_router(ml_router, prefix=settings.API_V1_PREFIX)
app.include_router(priority_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)
app.include_router(officer_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
def startup_event():
    # 1. Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")

    # 2. Seed departments and demo users
    db = SessionLocal()
    try:
        DepartmentService.seed_default_departments(db)

        # Seed initial demo accounts if not present
        if db.query(User).count() == 0:
            logger.info("Seeding initial role-based demonstration accounts...")
            admin_user = User(
                name="Municipal Commissioner Admin",
                email="admin@civic.gov",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN.value
            )
            officer_user = User(
                name="Roads & Sanitation Officer",
                email="officer@civic.gov",
                password_hash=hash_password("officer123"),
                role=UserRole.OFFICER.value
            )
            citizen_user = User(
                name="Aarav Sharma (Citizen)",
                email="citizen@civic.gov",
                password_hash=hash_password("citizen123"),
                role=UserRole.CITIZEN.value
            )
            db.add_all([admin_user, officer_user, citizen_user])
            db.commit()
            logger.info("Demo accounts created: admin@civic.gov, officer@civic.gov, citizen@civic.gov (pw: admin123, officer123, citizen123)")
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": settings.DATABASE_URL.split("://")[0]
    }
