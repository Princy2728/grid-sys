from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.entities import Campus
from backend.schemas.schemas import CampusOut, CampusUpdate

router = APIRouter(prefix="/settings", tags=["Campus Settings"])

@router.get("", response_model=CampusOut)
def get_settings(db: Session = Depends(get_db)):
    campus = db.query(Campus).first()
    if not campus:
        raise HTTPException(status_code=404, detail="Campus settings not found")
    return campus

@router.put("", response_model=CampusOut)
def update_settings(data: CampusUpdate, db: Session = Depends(get_db)):
    campus = db.query(Campus).first()
    if not campus:
        raise HTTPException(status_code=404, detail="Campus settings not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(campus, key, val)
    db.commit()
    db.refresh(campus)
    return campus

@router.post("/reset-defaults", response_model=CampusOut)
def reset_default_settings(db: Session = Depends(get_db)):
    campus = db.query(Campus).first()
    if not campus:
        campus = Campus()
        db.add(campus)
    campus.name = "Metro Innovation Smart Campus"
    campus.grid_capacity_kw = 1200.0
    campus.solar_capacity_kw = 650.0
    campus.battery_capacity_kwh = 500.0
    campus.critical_load_ratio = 0.35
    campus.max_ev_allocation_kw = 400.0
    campus.alert_threshold_pct = 85.0
    db.commit()
    db.refresh(campus)
    return campus
