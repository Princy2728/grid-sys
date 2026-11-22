import pytest
from backend.database.connection import SessionLocal
from backend.services.energy_service import EnergyService
from backend.services.ev_service import EVService
from backend.services.simulation_service import SimulationService
from backend.services.alert_service import AlertService
from backend.schemas.schemas import EVCreate, EVUpdate, SimulationRunRequest, AlertCreate

def test_energy_service_overview():
    db = SessionLocal()
    try:
        overview = EnergyService.get_kpi_overview(db)
        assert overview["total_consumption_kw"] > 0
        assert overview["grid_capacity_kw"] == 1200.0
        assert overview["solar_capacity_kw"] == 650.0
        assert "available_capacity_kw" in overview
    finally:
        db.close()

def test_energy_service_history():
    db = SessionLocal()
    try:
        hist = EnergyService.get_history(db, hours=12)
        assert len(hist) > 0
        assert "building_consumption_kw" in hist[0]
    finally:
        db.close()

def test_energy_forecasting_pipeline():
    db = SessionLocal()
    try:
        forecast = EnergyService.get_demand_forecast(db)
        assert len(forecast["forecast_series"]) == 24
        assert "peak_period" in forecast
        assert forecast["evaluation_metrics"]["samples"] > 0
    finally:
        db.close()

def test_ev_service_operations():
    db = SessionLocal()
    try:
        # 1. List
        evs = EVService.get_all_evs(db)
        assert len(evs) > 0

        # 2. Create
        data = EVCreate(
            model="Polestar 2 Test",
            owner_name="Fleet Test",
            license_plate="PL-889-TEST",
            battery_capacity_kwh=78.0,
            current_soc_pct=30.0,
            target_soc_pct=85.0,
            is_emergency_vehicle=False
        )
        new_ev = EVService.create_ev(db, data)
        assert new_ev.id is not None
        assert new_ev.model == "Polestar 2 Test"

        # 3. Update
        updated = EVService.update_ev(db, new_ev.id, EVUpdate(current_soc_pct=45.0))
        assert updated.current_soc_pct == 45.0

        # 4. Delete
        del_success = EVService.delete_ev(db, new_ev.id)
        assert del_success is True
    finally:
        db.close()

def test_simulation_service_heatwave():
    db = SessionLocal()
    try:
        req = SimulationRunRequest(
            preset_name="Heatwave Alert (Extreme Cooling)",
            temperature_c=39.0,
            cooling_multiplier=1.75
        )
        res = SimulationService.run_simulation(db, req)
        assert "baseline" in res
        assert "simulated" in res
        assert "recommendations" in res
        assert len(res["recommendations"]) > 0
        assert res["simulated"]["total_supply_kw"] > 0
    finally:
        db.close()

def test_alert_service_operations():
    db = SessionLocal()
    try:
        alerts = AlertService.get_alerts(db)
        assert len(alerts) > 0

        new_alert = AlertService.create_alert(db, AlertCreate(
            type="test_alert",
            severity="warning",
            title="Automated Test Alert",
            description="Testing alert dispatch service."
        ))
        assert new_alert.id is not None
        assert not new_alert.is_resolved

        resolved = AlertService.resolve_alert(db, new_alert.id)
        assert resolved.is_resolved is True
    finally:
        db.close()
