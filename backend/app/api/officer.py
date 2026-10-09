from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.complaint import ComplaintResponse
from app.services.complaint_service import ComplaintService
from app.auth.dependencies import require_officer

router = APIRouter(prefix="/officer", tags=["Officer Operations"])


class StatusUpdateBody(BaseModel):
    status: str
    comment: Optional[str] = None


@router.get("/complaints", response_model=List[ComplaintResponse])
def get_officer_complaints(
    current_user: User = Depends(require_officer),
    db: Session = Depends(get_db)
):
    # Retrieve assigned department for this officer if any
    dept_names = [d.name for d in current_user.assigned_departments]
    if dept_names:
        return ComplaintService.get_all_complaints(db, department=dept_names[0])
    return ComplaintService.get_all_complaints(db)


@router.patch("/complaints/{complaint_id}/status", response_model=ComplaintResponse)
def update_complaint_status(
    complaint_id: str,
    body: StatusUpdateBody,
    current_user: User = Depends(require_officer),
    db: Session = Depends(get_db)
):
    complaint = ComplaintService.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    updated = ComplaintService.update_complaint_status(
        db=db,
        complaint_id=complaint_id,
        new_status=body.status.upper(),
        changed_by=current_user.id,
        comment=body.comment
    )
    return updated
