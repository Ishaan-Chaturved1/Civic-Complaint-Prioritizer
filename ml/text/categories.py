from typing import List, Dict

CIVIC_CATEGORIES: List[str] = [
    "Road Damage",
    "Garbage",
    "Water Supply",
    "Sewage",
    "Drainage",
    "Streetlight",
    "Electricity",
    "Public Safety",
    "Traffic",
    "Other"
]

CATEGORY_TO_DEPARTMENT: Dict[str, str] = {
    "Road Damage": "Roads & Infrastructure Department",
    "Garbage": "Solid Waste Management & Sanitation Department",
    "Water Supply": "Water Supply Department",
    "Sewage": "Sewerage & Sanitation Department",
    "Drainage": "Stormwater & Drainage Department",
    "Streetlight": "Electrical & Street Lighting Department",
    "Electricity": "Electricity & Power Distribution Department",
    "Public Safety": "Emergency & Public Safety Department",
    "Traffic": "Traffic Management Department",
    "Other": "General Municipal Grievance Cell"
}

CATEGORY_DEFAULT_SLA: Dict[str, int] = {
    "Public Safety": 24,
    "Electricity": 24,
    "Sewage": 48,
    "Water Supply": 48,
    "Road Damage": 48,
    "Drainage": 48,
    "Garbage": 72,
    "Streetlight": 72,
    "Traffic": 48,
    "Other": 96
}
