from typing import List, Dict, Any
from pydantic import BaseModel


class StatusCounts(BaseModel):
    total: int
    pending: int
    in_progress: int
    resolved: int
    critical: int


class CategoryDistribution(BaseModel):
    category: str
    count: int
    percentage: float


class PriorityDistribution(BaseModel):
    priority: str
    count: int
    color: str


class DepartmentPerformance(BaseModel):
    department: str
    total: int
    resolved: int
    sla_compliance_rate: float
    avg_resolution_hours: float


class DailyTrend(BaseModel):
    date: str
    count: int
    critical_count: int


class AdminDashboardStats(BaseModel):
    total_complaints: int
    critical_complaints: int
    pending_complaints: int
    resolved_complaints: int
    sla_compliance_rate: float
    avg_priority_score: float
    by_category: List[CategoryDistribution]
    by_priority: List[PriorityDistribution]
    by_department: List[DepartmentPerformance]
    daily_trends: List[DailyTrend]
    sla_violations: int
