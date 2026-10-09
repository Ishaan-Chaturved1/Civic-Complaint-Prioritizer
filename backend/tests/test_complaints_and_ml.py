import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    # Login with demo citizen
    res = client.post("/api/auth/login", json={
        "email": "citizen@civic.gov",
        "password": "citizen123"
    })
    if res.status_code == 200:
        return res.json()["access_token"]
    
    # Or register new if needed
    reg = client.post("/api/auth/register", json={
        "name": "Fixture Citizen",
        "email": "fixture_citizen@civic.gov",
        "password": "citizen123",
        "role": "CITIZEN"
    })
    return reg.json()["access_token"]


def test_text_analysis_endpoint():
    res = client.post("/api/ml/analyze-text", json={
        "text": "Deep hazardous pothole causing accidents near General Hospital entrance"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["category"] in ["Road Damage", "Public Safety", "Other"]
    assert data["severity_score"] > 50.0
    assert "hospital" in data["keywords"] or "accident" in data["keywords"] or "pothole" in data["keywords"]


def test_priority_calculation_endpoint():
    res = client.post("/api/priority/calculate", json={
        "text_severity": 85.0,
        "visual_severity": 90.0,
        "location_risk": 75.0,
        "people_impact": 80.0,
        "safety_indicators": ["hospital", "accident"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["priority_score"] >= 80.0
    assert data["severity_level"] in ["HIGH", "CRITICAL"]
    assert data["sla_hours"] in [24, 48]
    assert "factors" in data


def test_create_and_fetch_complaint(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    create_res = client.post(
        "/api/complaints",
        data={
            "title": "Severe road crater on Market Road",
            "description": "Large road damage filled with muddy water causing traffic hazards near local school.",
            "latitude": "12.9716",
            "longitude": "77.5946",
            "address": "Market Road, Ward 12"
        },
        headers=headers
    )
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["complaint_id"].startswith("CIV-")
    assert data["category"] == "Road Damage"
    assert data["priority_score"] > 0
    assert "explanation" in data

    comp_id = data["complaint_id"]

    # Fetch details
    detail_res = client.get(f"/api/complaints/{comp_id}", headers=headers)
    assert detail_res.status_code == 200
    comp_data = detail_res.json()
    assert comp_data["id"] == comp_id
    assert comp_data["status"] == "SUBMITTED"
    assert comp_data["ai_analysis"] is not None
