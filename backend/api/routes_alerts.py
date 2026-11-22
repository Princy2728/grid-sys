from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.connection import get_db
from backend.services.alert_service import AlertService
from backend.schemas.schemas import AlertOut, AlertCreate

router = APIRouter(prefix="/alerts", tags=["Alerts and Incident Reports"])

@router.get("", response_model=List[AlertOut])
def list_alerts(resolved: Optional[bool] = Query(None), db: Session = Depends(get_db)):
    return AlertService.get_alerts(db, resolved=resolved)

@router.post("", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def trigger_alert(data: AlertCreate, db: Session = Depends(get_db)):
    return AlertService.create_alert(db, data)

@router.patch("/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = AlertService.resolve_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.get("/report")
def export_incident_report(db: Session = Depends(get_db)):
    return AlertService.generate_incident_report(db)
