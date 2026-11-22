from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database.connection import get_db
from backend.models.entities import ResourceAllocation, Campus, Building, ChargingRequest, SolarReading
from backend.algorithms.allocation import SmartAllocationEngine
from backend.schemas.schemas import AllocationRequest, AllocationOut

router = APIRouter(prefix="/allocation", tags=["Smart Resource Allocation"])

@router.get("/current", response_model=AllocationOut)
def get_current_allocation(db: Session = Depends(get_db)):
    latest = db.query(ResourceAllocation).order_by(desc(ResourceAllocation.timestamp)).first()
    if latest:
        return latest

    # If no record exists, run initial live allocation
    return run_live_allocation(AllocationRequest(), db)

@router.post("/calculate", response_model=AllocationOut)
def run_live_allocation(req: AllocationRequest, db: Session = Depends(get_db)):
    campus = db.query(Campus).first()
    grid_cap = campus.grid_capacity_kw if campus else 1200.0

    # Solar generation
    latest_solar = db.query(SolarReading).order_by(desc(SolarReading.timestamp)).first()
    solar_gen = latest_solar.generation_kw if latest_solar else 420.0
    if req.custom_solar_multiplier is not None:
        solar_gen *= req.custom_solar_multiplier

    if req.custom_grid_multiplier is not None:
        grid_cap *= req.custom_grid_multiplier

    # Building Loads
    buildings = db.query(Building).all()
    crit_demand = sum(b.current_load_kw for b in buildings if b.is_critical)
    ess_demand = sum(b.current_load_kw for b in buildings if not b.is_critical and b.priority_order <= 3)
    opt_demand = sum(b.current_load_kw for b in buildings if b.priority_order > 3)

    # EV Loads
    ev_requests = db.query(ChargingRequest).filter(ChargingRequest.status == "active").all()
    urgent_ev = sum(r.allocated_power_kw for r in ev_requests if r.priority_level in ["Urgent", "High"])
    flex_ev = sum(r.allocated_power_kw for r in ev_requests if r.priority_level in ["Normal", "Flexible"])

    if req.custom_ev_demand_multiplier is not None:
        urgent_ev *= req.custom_ev_demand_multiplier
        flex_ev *= req.custom_ev_demand_multiplier

    result = SmartAllocationEngine.allocate(
        grid_capacity_kw=grid_cap,
        solar_generation_kw=solar_gen,
        critical_demand_kw=crit_demand,
        essential_demand_kw=ess_demand,
        urgent_ev_demand_kw=urgent_ev,
        flexible_ev_demand_kw=flex_ev,
        optional_demand_kw=opt_demand,
        scenario_name=req.scenario_name or "Live Dynamic Dispatch"
    )

    # Save to DB
    record = ResourceAllocation(
        scenario_name=result["scenario_name"],
        total_supply_kw=result["total_supply_kw"],
        solar_allocated_kw=result["solar_allocated_kw"],
        grid_allocated_kw=result["grid_allocated_kw"],
        critical_load_kw=result["critical_load_kw"],
        essential_building_kw=result["essential_building_kw"],
        urgent_ev_kw=result["urgent_ev_kw"],
        flexible_ev_kw=result["flexible_ev_kw"],
        optional_curtailed_kw=result["optional_curtailed_kw"],
        deficit_kw=result["deficit_kw"],
        explanation=result["explanation"],
        is_constrained=result["is_constrained"]
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return result
