from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.department import Department
from ml.text.categories import CATEGORY_TO_DEPARTMENT, CATEGORY_DEFAULT_SLA


class DepartmentService:
    @staticmethod
    def seed_default_departments(db: Session):
        """
        Seeds standard civic departments into database if not present.
        """
        for cat, dept_name in CATEGORY_TO_DEPARTMENT.items():
            existing = db.query(Department).filter(Department.name == dept_name).first()
            if not existing:
                sla = CATEGORY_DEFAULT_SLA.get(cat, 48)
                dept = Department(
                    name=dept_name,
                    category=cat,
                    sla_hours=sla,
                    officer_id=None
                )
                db.add(dept)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> List[Department]:
        return db.query(Department).all()

    @staticmethod
    def get_by_category(db: Session, category: str) -> Optional[Department]:
        dept = db.query(Department).filter(Department.category == category).first()
        if not dept:
            dept = db.query(Department).filter(Department.name == "General Municipal Grievance Cell").first()
        return dept
