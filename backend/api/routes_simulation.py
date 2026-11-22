from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.connection import get_db
from backend.models.entities import SimulationScenario
from backend.services.simulation_service import SimulationService
from backend.schemas.schemas import SimulationScenarioOut, SimulationRunRequest, SimulationRunResponse

router = APIRouter(prefix="/simulation", tags=["Simulation Lab"])

@router.get("/scenarios", response_model=List[SimulationScenarioOut])
def get_scenarios(db: Session = Depends(get_db)):
    return db.query(SimulationScenario).all()

@router.post("/run", response_model=SimulationRunResponse)
def run_simulation(req: SimulationRunRequest, db: Session = Depends(get_db)):
    return SimulationService.run_simulation(db, req)
