import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_auth_registration_and_login():
    import uuid
    test_email = f"testcitizen_{uuid.uuid4().hex[:8]}@civic.gov"
    # Register
    reg_res = client.post("/api/auth/register", json={
        "name": "Test Citizen User",
        "email": test_email,
        "password": "Password123!",
        "role": "CITIZEN"
    })
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert "access_token" in data
    assert data["user"]["email"] == test_email
    assert data["user"]["role"] == "CITIZEN"

    # Login
    login_res = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # Verify Profile
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["name"] == "Test Citizen User"
