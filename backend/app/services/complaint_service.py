import datetime
import random
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.complaint import Complaint
from app.models.ai_analysis import AIAnalysis
from app.models.complaint_history import ComplaintHistory
from app.services.storage_service import StorageService
from app.services.department_service import DepartmentService
from ml.text.text_pipeline import TextPipelineService
from ml.vision.vision_service import VisionService
from ml.priority.priority_engine import PriorityEngine
from ml.duplicate.duplicate_detector import DuplicateDetector

text_pipeline = TextPipelineService()
vision_service = VisionService()
duplicate_detector = DuplicateDetector()


class ComplaintService:

    @staticmethod
    def generate_complaint_id(db: Session) -> str:
        count = db.query(Complaint).count()
        rand_suffix = random.randint(100, 999)
        return f"CIV-{10000 + count + 1}-{rand_suffix}"

    @classmethod
    async def create_complaint(
        cls,
        db: Session,
        user_id: int,
        title: str,
        description: str,
        category: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        address: Optional[str] = None,
        image_file: Optional[UploadFile] = None
    ) -> Dict[str, Any]:
        """
        Submits complaint, performs end-to-end ML multimodal analysis,
        calculates priority, assigns SLA, and commits record.
        """
        complaint_id = cls.generate_complaint_id(db)
        image_url = None
        saved_img_path = None
        annotated_url = None

        # 1. Save uploaded image
        if image_file and image_file.filename:
            success, rel_url, abs_path = await StorageService.save_uploaded_complaint_image(complaint_id, image_file)
            if success:
                image_url = rel_url
                saved_img_path = abs_path

        # 2. NLP Analysis
        full_text = f"{title}. {description}"
        text_analysis = text_pipeline.analyze(full_text)
        
        # Use user category if provided, otherwise model category
        final_category = category if (category and category.strip()) else text_analysis["category"]
        text_severity = text_analysis["severity_score"]
        text_conf = text_analysis["confidence"]

        # 3. Vision Analysis
        vis_category = None
        vis_confidence = None
        vis_severity = None
        damage_area_pct = 0.0
        detected_objects = []

        if saved_img_path:
            annotated_abs_path, ann_rel_url = StorageService.get_annotated_path(complaint_id)
            vision_result = vision_service.analyze_image(
                image_path=saved_img_path,
                category_hint=final_category,
                output_annotated_path=annotated_abs_path
            )
            if vision_result.get("status") == "success":
                vis_category = vision_result.get("detected_issue")
                vis_confidence = vision_result.get("confidence")
                vis_severity = vision_result.get("visual_severity")
                damage_area_pct = vision_result.get("damage_area_percentage", 0.0)
                detected_objects = vision_result.get("detections", [])
                if detected_objects:
                    annotated_url = ann_rel_url

        # 4. Check for duplicate complaints
        existing_comps = db.query(Complaint).order_by(Complaint.created_at.desc()).limit(100).all()
        existing_data = [{"id": c.id, "title": c.title, "description": c.description, "category": c.category} for c in existing_comps]
        duplicate_info = duplicate_detector.check_for_duplicates(full_text, existing_data)

        # 5. Multimodal Priority & SLA Engine
        priority_res = PriorityEngine.calculate(
            text_severity=text_severity,
            visual_severity=vis_severity,
            location_risk=60.0 if (latitude and longitude) else 45.0,
            people_impact=50.0,
            critical_keywords=text_analysis.get("critical_keywords", []),
            damage_area_percentage=damage_area_pct,
            category=final_category
        )

        final_priority = priority_res["priority_score"]
        final_severity = priority_res["severity_level"]
        final_sla = priority_res["sla_hours"]
        explanation = priority_res["explanation"]

        # 6. Assign Department
        assigned_dept_obj = DepartmentService.get_by_category(db, final_category)
        assigned_dept_name = assigned_dept_obj.name if assigned_dept_obj else text_analysis["recommended_department"]

        # 7. Create and persist Complaint
        complaint = Complaint(
            id=complaint_id,
            user_id=user_id,
            title=title,
            description=description,
            category=final_category,
            status="SUBMITTED",
            severity=final_severity,
            priority_score=final_priority,
            department=assigned_dept_name,
            sla_hours=final_sla,
            latitude=latitude,
            longitude=longitude,
            address=address,
            image_url=annotated_url or image_url,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        db.add(complaint)

        # 8. Create and persist AI Analysis record
        ai_record = AIAnalysis(
            complaint_id=complaint_id,
            text_category=text_analysis["category"],
            text_confidence=text_conf,
            text_severity=text_severity,
            visual_category=vis_category,
            visual_confidence=vis_confidence,
            visual_severity=vis_severity,
            detected_objects=detected_objects,
            segmentation_data={},
            damage_area_percentage=damage_area_pct,
            duplicate_similarity=duplicate_info.get("similarity_score") if duplicate_info else None,
            multimodal_score=final_priority,
            explanation=explanation,
            model_version="CivicPrioritizer-v1.0.0",
            created_at=datetime.datetime.utcnow()
        )
        db.add(ai_record)

        # 9. Create history entry
        history_entry = ComplaintHistory(
            complaint_id=complaint_id,
            old_status=None,
            new_status="SUBMITTED",
            changed_by=user_id,
            comment="Complaint submitted and processed by AI engine.",
            timestamp=datetime.datetime.utcnow()
        )
        db.add(history_entry)

        db.commit()
        db.refresh(complaint)

        return {
            "complaint_id": complaint.id,
            "category": complaint.category,
            "severity": complaint.severity,
            "priority_score": complaint.priority_score,
            "department": complaint.department,
            "sla_hours": complaint.sla_hours,
            "explanation": explanation,
            "visual_category": vis_category,
            "damage_area_percentage": damage_area_pct,
            "duplicate_warning": duplicate_info,
            "complaint": complaint
        }

    @staticmethod
    def get_complaint_by_id(db: Session, complaint_id: str) -> Optional[Complaint]:
        return db.query(Complaint).filter(Complaint.id == complaint_id).first()

    @staticmethod
    def get_user_complaints(db: Session, user_id: int) -> List[Complaint]:
        return db.query(Complaint).filter(Complaint.user_id == user_id).order_by(Complaint.created_at.desc()).all()

    @staticmethod
    def get_all_complaints(
        db: Session,
        status: Optional[str] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        department: Optional[str] = None
    ) -> List[Complaint]:
        query = db.query(Complaint)
        if status:
            query = query.filter(Complaint.status == status)
        if category:
            query = query.filter(Complaint.category == category)
        if severity:
            query = query.filter(Complaint.severity == severity)
        if department:
            query = query.filter(Complaint.department == department)
        return query.order_by(Complaint.priority_score.desc(), Complaint.created_at.desc()).all()

    @staticmethod
    def update_complaint_status(
        db: Session,
        complaint_id: str,
        new_status: str,
        changed_by: int,
        comment: Optional[str] = None
    ) -> Optional[Complaint]:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            return None

        old_status = complaint.status
        complaint.status = new_status
        complaint.updated_at = datetime.datetime.utcnow()

        if new_status == "RESOLVED":
            complaint.resolved_at = datetime.datetime.utcnow()

        history_entry = ComplaintHistory(
            complaint_id=complaint_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            comment=comment or f"Status transitioned from {old_status} to {new_status}",
            timestamp=datetime.datetime.utcnow()
        )
        db.add(history_entry)
        db.commit()
        db.refresh(complaint)
        return complaint
