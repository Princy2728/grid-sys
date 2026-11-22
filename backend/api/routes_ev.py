from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from backend.database.connection import get_db
from backend.services.ev_service import EVService
from backend.schemas.schemas import (
    EVOut, EVCreate, EVUpdate,
    ChargingStationOut, ChargingStationUpdate,
    ChargingRequestOut, ChargingRequestCreate, ChargingRequestUpdate,
    ChargingSessionOut
)

router = APIRouter(prefix="/ev", tags=["Electric Vehicles"])

# --- EV Fleet CRUD ---
@router.get("/vehicles", response_model=List[EVOut])
def list_vehicles(db: Session = Depends(get_db)):
    return EVService.get_all_evs(db)

@router.post("/vehicles", response_model=EVOut, status_code=status.HTTP_201_CREATED)
def register_vehicle(data: EVCreate, db: Session = Depends(get_db)):
    return EVService.create_ev(db, data)

@router.get("/vehicles/{ev_id}", response_model=EVOut)
def get_vehicle(ev_id: int, db: Session = Depends(get_db)):
    ev = EVService.get_ev_by_id(db, ev_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return ev

@router.put("/vehicles/{ev_id}", response_model=EVOut)
def update_vehicle(ev_id: int, data: EVUpdate, db: Session = Depends(get_db)):
    ev = EVService.update_ev(db, ev_id, data)
    if not ev:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return ev

@router.delete("/vehicles/{ev_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(ev_id: int, db: Session = Depends(get_db)):
    success = EVService.delete_ev(db, ev_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return None

# --- Charging Stations ---
@router.get("/stations", response_model=List[ChargingStationOut])
def list_stations(db: Session = Depends(get_db)):
    return EVService.get_all_stations(db)

@router.patch("/stations/{station_id}", response_model=ChargingStationOut)
def update_station(station_id: int, data: ChargingStationUpdate, db: Session = Depends(get_db)):
    station = EVService.update_station(db, station_id, status=data.status, current_power=data.current_power_kw)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station

# --- Charging Requests ---
@router.get("/requests", response_model=List[ChargingRequestOut])
def list_requests(db: Session = Depends(get_db)):
    return EVService.get_all_requests(db)

@router.post("/requests", response_model=ChargingRequestOut, status_code=status.HTTP_201_CREATED)
def create_request(data: ChargingRequestCreate, db: Session = Depends(get_db)):
    try:
        return EVService.create_charging_request(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/requests/{request_id}", response_model=ChargingRequestOut)
def update_request(request_id: int, data: ChargingRequestUpdate, db: Session = Depends(get_db)):
    req = EVService.update_request(db, request_id, data)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req

@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int, db: Session = Depends(get_db)):
    success = EVService.delete_request(db, request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return None

# --- Active Sessions ---
@router.get("/sessions", response_model=List[ChargingSessionOut])
def list_sessions(db: Session = Depends(get_db)):
    return EVService.get_all_sessions(db)
