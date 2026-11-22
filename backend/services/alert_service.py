import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models.entities import Alert, ResourceAllocation, EnergyReading, Campus
from backend.schemas.schemas import AlertCreate

class AlertService:
    @staticmethod
    def get_alerts(db: Session, resolved: Optional[bool] = None) -> List[Alert]:
        query = db.query(Alert)
        if resolved is not None:
            query = query.filter(Alert.is_resolved == resolved)
        return query.order_by(desc(Alert.timestamp)).all()

    @staticmethod
    def create_alert(db: Session, data: AlertCreate) -> Alert:
        alert = Alert(
            type=data.type,
            severity=data.severity,
            title=data.title,
            description=data.description,
            timestamp=datetime.datetime.utcnow(),
            is_resolved=False
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def resolve_alert(db: Session, alert_id: int) -> Optional[Alert]:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        alert.is_resolved = True
        alert.resolved_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def generate_incident_report(db: Session) -> Dict[str, Any]:
        campus = db.query(Campus).first()
        alerts = db.query(Alert).order_by(desc(Alert.timestamp)).limit(20).all()
        allocations = db.query(ResourceAllocation).order_by(desc(ResourceAllocation.timestamp)).limit(5).all()

        unresolved_count = db.query(Alert).filter(Alert.is_resolved == False).count()
        critical_count = db.query(Alert).filter(Alert.severity == "critical", Alert.is_resolved == False).count()
        warning_count = db.query(Alert).filter(Alert.severity == "warning", Alert.is_resolved == False).count()

        return {
            "report_timestamp": datetime.datetime.utcnow().isoformat(),
            "campus_name": campus.name if campus else "Metro Innovation Smart Campus",
            "grid_rating_kw": campus.grid_capacity_kw if campus else 1200.0,
            "solar_rating_kw": campus.solar_capacity_kw if campus else 650.0,
            "active_unresolved_alerts": unresolved_count,
            "critical_incident_count": critical_count,
            "warning_incident_count": warning_count,
            "recent_incidents": [{
                "id": a.id,
                "timestamp": a.timestamp.isoformat(),
                "severity": a.severity,
                "type": a.type,
                "title": a.title,
                "description": a.description,
                "is_resolved": a.is_resolved
            } for a in alerts],
            "recent_allocations": [{
                "id": al.id,
                "timestamp": al.timestamp.isoformat(),
                "scenario": al.scenario_name,
                "total_supply_kw": al.total_supply_kw,
                "solar_kw": al.solar_allocated_kw,
                "grid_kw": al.grid_allocated_kw,
                "deficit_kw": al.deficit_kw,
                "is_constrained": al.is_constrained,
                "explanation": al.explanation
            } for al in allocations]
        }
