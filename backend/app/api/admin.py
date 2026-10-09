from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.complaint import Complaint
from app.models.department import Department
from app.schemas.user import UserResponse
from app.schemas.complaint import ComplaintResponse
from app.schemas.analytics import AdminDashboardStats
from app.schemas.department import DepartmentResponse, DepartmentCreate
from app.services.analytics_service import AnalyticsService
from app.services.complaint_service import ComplaintService
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Admin Portal"])


@router.get("/dashboard", response_model=AdminDashboardStats)
def get_dashboard_metrics(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return AnalyticsService.get_admin_dashboard_stats(db)


@router.get("/analytics", response_model=AdminDashboardStats)
def get_analytics(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return AnalyticsService.get_admin_dashboard_stats(db)


@router.get("/complaints", response_model=List[ComplaintResponse])
def get_all_complaints(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return ComplaintService.get_all_complaints(db)


@router.get("/users", response_model=List[UserResponse])
def get_all_users(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/departments", response_model=List[DepartmentResponse])
def get_departments(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(Department).all()


@router.post("/departments", response_model=DepartmentResponse)
def create_department(dept_in: DepartmentCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    dept = Department(
        name=dept_in.name,
        category=dept_in.category,
        sla_hours=dept_in.sla_hours,
        officer_id=dept_in.officer_id
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept
