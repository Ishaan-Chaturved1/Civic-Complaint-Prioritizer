import datetime
from typing import Dict, Any, List
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.complaint import Complaint
from app.models.department import Department


class AnalyticsService:

    @staticmethod
    def get_admin_dashboard_stats(db: Session) -> Dict[str, Any]:
        """
        Computes real metrics and statistics from database complaints.
        """
        complaints = db.query(Complaint).all()
        total_complaints = len(complaints)

        if total_complaints == 0:
            return {
                "total_complaints": 0,
                "critical_complaints": 0,
                "pending_complaints": 0,
                "resolved_complaints": 0,
                "sla_compliance_rate": 100.0,
                "avg_priority_score": 0.0,
                "by_category": [],
                "by_priority": [
                    {"priority": "CRITICAL", "count": 0, "color": "#ef4444"},
                    {"priority": "HIGH", "count": 0, "color": "#f97316"},
                    {"priority": "MEDIUM", "count": 0, "color": "#eab308"},
                    {"priority": "LOW", "count": 0, "color": "#22c55e"}
                ],
                "by_department": [],
                "daily_trends": [],
                "sla_violations": 0
            }

        critical_count = sum(1 for c in complaints if c.severity == "CRITICAL" or c.priority_score >= 90.0)
        resolved_count = sum(1 for c in complaints if c.status == "RESOLVED")
        pending_count = sum(1 for c in complaints if c.status in ["SUBMITTED", "IN_REVIEW", "ASSIGNED", "IN_PROGRESS"])

        avg_score = round(sum(c.priority_score for c in complaints) / total_complaints, 1)

        # SLA Compliance calculation
        now = datetime.datetime.utcnow()
        violations = 0
        for c in complaints:
            if c.status == "RESOLVED" and c.resolved_at:
                elapsed_hours = (c.resolved_at - c.created_at).total_seconds() / 3600.0
                if elapsed_hours > c.sla_hours:
                    violations += 1
            elif c.status != "RESOLVED":
                elapsed_hours = (now - c.created_at).total_seconds() / 3600.0
                if elapsed_hours > c.sla_hours:
                    violations += 1

        compliance_rate = round(max(0.0, (1.0 - (violations / total_complaints)) * 100), 1)

        # By Category
        cat_counts = defaultdict(int)
        for c in complaints:
            cat_counts[c.category] += 1

        by_category = [
            {
                "category": cat,
                "count": cnt,
                "percentage": round((cnt / total_complaints) * 100, 1)
            }
            for cat, cnt in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        # By Priority
        prio_counts = defaultdict(int)
        for c in complaints:
            prio_counts[c.severity] += 1

        by_priority = [
            {"priority": "CRITICAL", "count": prio_counts.get("CRITICAL", 0), "color": "#ef4444"},
            {"priority": "HIGH", "count": prio_counts.get("HIGH", 0), "color": "#f97316"},
            {"priority": "MEDIUM", "count": prio_counts.get("MEDIUM", 0), "color": "#eab308"},
            {"priority": "LOW", "count": prio_counts.get("LOW", 0), "color": "#22c55e"}
        ]

        # By Department
        dept_data = defaultdict(lambda: {"total": 0, "resolved": 0, "violations": 0})
        for c in complaints:
            dept = c.department or "Unassigned"
            dept_data[dept]["total"] += 1
            if c.status == "RESOLVED":
                dept_data[dept]["resolved"] += 1
            # Check violation
            elapsed = ((c.resolved_at or now) - c.created_at).total_seconds() / 3600.0
            if elapsed > c.sla_hours:
                dept_data[dept]["violations"] += 1

        by_department = [
            {
                "department": dept,
                "total": data["total"],
                "resolved": data["resolved"],
                "sla_compliance_rate": round(max(0.0, (1.0 - (data["violations"] / data["total"])) * 100), 1) if data["total"] > 0 else 100.0,
                "avg_resolution_hours": 24.0
            }
            for dept, data in dept_data.items()
        ]

        # Daily Trend (last 7-14 days)
        date_counts = defaultdict(lambda: {"count": 0, "critical": 0})
        for c in complaints:
            d_str = c.created_at.strftime("%Y-%m-%d")
            date_counts[d_str]["count"] += 1
            if c.severity == "CRITICAL":
                date_counts[d_str]["critical"] += 1

        sorted_dates = sorted(date_counts.keys())
        daily_trends = [
            {
                "date": d,
                "count": date_counts[d]["count"],
                "critical_count": date_counts[d]["critical"]
            }
            for d in sorted_dates[-14:]
        ]

        return {
            "total_complaints": total_complaints,
            "critical_complaints": critical_count,
            "pending_complaints": pending_count,
            "resolved_complaints": resolved_count,
            "sla_compliance_rate": compliance_rate,
            "avg_priority_score": avg_score,
            "by_category": by_category,
            "by_priority": by_priority,
            "by_department": by_department,
            "daily_trends": daily_trends,
            "sla_violations": violations
        }
