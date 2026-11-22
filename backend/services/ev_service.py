import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models.entities import EV, ChargingStation, ChargingRequest, ChargingSession
from backend.schemas.schemas import EVCreate, EVUpdate, ChargingRequestCreate, ChargingRequestUpdate

class EVService:
    # --- EV Fleet ---
    @staticmethod
    def get_all_evs(db: Session) -> List[EV]:
        return db.query(EV).order_by(EV.id).all()

    @staticmethod
    def get_ev_by_id(db: Session, ev_id: int) -> Optional[EV]:
        return db.query(EV).filter(EV.id == ev_id).first()

    @staticmethod
    def create_ev(db: Session, data: EVCreate) -> EV:
        new_ev = EV(
            model=data.model,
            owner_name=data.owner_name,
            license_plate=data.license_plate,
            battery_capacity_kwh=data.battery_capacity_kwh,
            current_soc_pct=data.current_soc_pct,
            target_soc_pct=data.target_soc_pct,
            is_emergency_vehicle=data.is_emergency_vehicle,
            registered_at=datetime.datetime.utcnow()
        )
        db.add(new_ev)
        db.commit()
        db.refresh(new_ev)
        return new_ev

    @staticmethod
    def update_ev(db: Session, ev_id: int, data: EVUpdate) -> Optional[EV]:
        ev = db.query(EV).filter(EV.id == ev_id).first()
        if not ev:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(ev, key, val)
        db.commit()
        db.refresh(ev)
        return ev

    @staticmethod
    def delete_ev(db: Session, ev_id: int) -> bool:
        ev = db.query(EV).filter(EV.id == ev_id).first()
        if not ev:
            return False
        # Remove active requests and sessions associated with EV
        db.query(ChargingSession).filter(ChargingSession.ev_id == ev_id).delete()
        db.query(ChargingRequest).filter(ChargingRequest.ev_id == ev_id).delete()
        db.delete(ev)
        db.commit()
        return True

    # --- Stations ---
    @staticmethod
    def get_all_stations(db: Session) -> List[ChargingStation]:
        return db.query(ChargingStation).order_by(ChargingStation.id).all()

    @staticmethod
    def get_station_by_id(db: Session, station_id: int) -> Optional[ChargingStation]:
        return db.query(ChargingStation).filter(ChargingStation.id == station_id).first()

    @staticmethod
    def update_station(db: Session, station_id: int, status: Optional[str] = None, current_power: Optional[float] = None) -> Optional[ChargingStation]:
        st = db.query(ChargingStation).filter(ChargingStation.id == station_id).first()
        if not st:
            return None
        if status is not None:
            st.status = status
        if current_power is not None:
            st.current_power_kw = current_power
        db.commit()
        db.refresh(st)
        return st

    # --- Charging Requests ---
    @staticmethod
    def get_all_requests(db: Session) -> List[ChargingRequest]:
        return db.query(ChargingRequest).order_by(desc(ChargingRequest.requested_at)).all()

    @staticmethod
    def create_charging_request(db: Session, data: ChargingRequestCreate) -> ChargingRequest:
        ev = db.query(EV).filter(EV.id == data.ev_id).first()
        if not ev:
            raise ValueError(f"EV with id {data.ev_id} not found.")

        # Determine default priority if emergency vehicle
        priority = "Urgent" if ev.is_emergency_vehicle else data.priority_level

        # Calculate needed energy if not provided accurately
        needed_pct = max(0.0, data.target_soc_pct - data.current_soc_pct)
        energy_req = round((needed_pct / 100.0) * ev.battery_capacity_kwh, 2)
        if data.requested_energy_kwh > 0:
            energy_req = data.requested_energy_kwh

        req = ChargingRequest(
            ev_id=data.ev_id,
            station_id=data.station_id,
            requested_energy_kwh=energy_req,
            current_soc_pct=data.current_soc_pct,
            target_soc_pct=data.target_soc_pct,
            departure_time=data.departure_time,
            priority_level=priority,
            status="pending" if not data.station_id else "active",
            requested_at=datetime.datetime.utcnow(),
            allocated_power_kw=11.0 if data.station_id else 0.0,
            reason_notes="Standard request submitted."
        )
        db.add(req)
        db.commit()
        db.refresh(req)

        # If station assigned, create active session
        if data.station_id:
            st = db.query(ChargingStation).filter(ChargingStation.id == data.station_id).first()
            if st:
                st.status = "in_use"
                st.current_power_kw = min(st.max_power_kw, 22.0)
                sess = ChargingSession(
                    request_id=req.id,
                    ev_id=data.ev_id,
                    station_id=data.station_id,
                    allocated_power_kw=st.current_power_kw,
                    energy_delivered_kwh=0.0,
                    start_time=datetime.datetime.utcnow(),
                    status="active"
                )
                db.add(sess)
                db.commit()

        return req

    @staticmethod
    def update_request(db: Session, request_id: int, data: ChargingRequestUpdate) -> Optional[ChargingRequest]:
        req = db.query(ChargingRequest).filter(ChargingRequest.id == request_id).first()
        if not req:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(req, key, val)
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def delete_request(db: Session, request_id: int) -> bool:
        req = db.query(ChargingRequest).filter(ChargingRequest.id == request_id).first()
        if not req:
            return False
        db.query(ChargingSession).filter(ChargingSession.request_id == request_id).delete()
        db.delete(req)
        db.commit()
        return True

    # --- Active Sessions ---
    @staticmethod
    def get_all_sessions(db: Session) -> List[ChargingSession]:
        return db.query(ChargingSession).order_by(desc(ChargingSession.start_time)).all()
