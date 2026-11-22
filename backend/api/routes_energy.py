from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.database.connection import get_db
from backend.services.energy_service import EnergyService
from backend.models.entities import Building
from backend.schemas.schemas import BuildingOut

router = APIRouter(prefix="/energy", tags=["Energy"])

@router.get("/overview")
def get_energy_overview(db: Session = Depends(get_db)):
    return EnergyService.get_kpi_overview(db)

@router.get("/history")
def get_energy_history(hours: int = Query(24, ge=1, le=168), db: Session = Depends(get_db)):
    return EnergyService.get_history(db, hours=hours)

@router.get("/solar")
def get_solar_intelligence(db: Session = Depends(get_db)):
    return EnergyService.get_solar_analytics(db)

@router.get("/forecast")
def get_demand_forecast(db: Session = Depends(get_db)):
    return EnergyService.get_demand_forecast(db)

@router.get("/buildings", response_model=List[BuildingOut])
def get_campus_buildings(db: Session = Depends(get_db)):
    return db.query(Building).order_by(Building.priority_order).all()
