import sys
from pathlib import Path
import pytest

# Ensure backend and root are in python path
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(root_dir))

from app.database import engine, Base, SessionLocal
from app.models.user import User, UserRole
from app.auth.security import hash_password
from app.services.department_service import DepartmentService


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        DepartmentService.seed_default_departments(db)
        if not db.query(User).filter(User.email == "citizen@civic.gov").first():
            citizen = User(
                name="Aarav Sharma (Citizen)",
                email="citizen@civic.gov",
                password_hash=hash_password("citizen123"),
                role=UserRole.CITIZEN.value
            )
            admin = User(
                name="Admin User",
                email="admin@civic.gov",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN.value
            )
            db.add_all([citizen, admin])
            db.commit()
    finally:
        db.close()
    yield
