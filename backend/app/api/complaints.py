from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.complaint import ComplaintResponse, ComplaintSubmissionResult, ComplaintUpdate
from app.services.complaint_service import ComplaintService
from app.auth.dependencies import get_current_user, require_citizen, require_admin

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("", response_model=ComplaintSubmissionResult, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    title: str = Form(...),
    description: str = Form(...),
    category: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    address: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    result = await ComplaintService.create_complaint(
        db=db,
        user_id=current_user.id,
        title=title,
        description=description,
        category=category,
        latitude=latitude,
        longitude=longitude,
        address=address,
        image_file=image
    )
    return result


@router.get("", response_model=List[ComplaintResponse])
def get_complaints(
    status: Optional[str] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == UserRole.CITIZEN.value:
        return ComplaintService.get_user_complaints(db, current_user.id)
    else:
        return ComplaintService.get_all_complaints(db, status=status, category=category, severity=severity)


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint_details(
    complaint_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    complaint = ComplaintService.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    # Authorization: citizens can view own, officers/admins can view any
    if current_user.role == UserRole.CITIZEN.value and complaint.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return complaint


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
def update_complaint(
    complaint_id: str,
    update_data: ComplaintUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    complaint = ComplaintService.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    # Only officer or admin can update status or priority
    if current_user.role == UserRole.CITIZEN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Citizens cannot alter complaint status")

    if update_data.status:
        complaint = ComplaintService.update_complaint_status(
            db=db,
            complaint_id=complaint_id,
            new_status=update_data.status,
            changed_by=current_user.id,
            comment=update_data.comment
        )

    if update_data.department and current_user.role == UserRole.ADMIN.value:
        complaint.department = update_data.department
        db.commit()
        db.refresh(complaint)

    if update_data.priority_score is not None and current_user.role == UserRole.ADMIN.value:
        complaint.priority_score = update_data.priority_score
        from ml.priority.priority_engine import PriorityEngine
        complaint.severity = PriorityEngine.get_severity_level(update_data.priority_score)
        db.commit()
        db.refresh(complaint)

    return complaint


@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_complaint(
    complaint_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    complaint = ComplaintService.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    db.delete(complaint)
    db.commit()
    return None
