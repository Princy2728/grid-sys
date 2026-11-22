import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_energy_overview():
    response = client.get("/api/energy/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_consumption_kw" in data
    assert "solar_generation_kw" in data
    assert "grid_import_kw" in data
    assert "available_capacity_kw" in data

def test_energy_history():
    response = client.get("/api/energy/history?hours=12")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_ev_crud():
    # 1. List EVs
    list_res = client.get("/api/ev/vehicles")
    assert list_res.status_code == 200
    initial_count = len(list_res.json())

    # 2. Create new EV
    new_ev = {
        "model": "Test Smart Shuttle",
        "owner_name": "Grid Operations",
        "license_plate": "TEST-EV-999",
        "battery_capacity_kwh": 85.0,
        "current_soc_pct": 45.0,
        "target_soc_pct": 85.0,
        "is_emergency_vehicle": False
    }
    create_res = client.post("/api/ev/vehicles", json=new_ev)
    assert create_res.status_code == 201
    created_id = create_res.json()["id"]

    # 3. Update EV
    update_res = client.put(f"/api/ev/vehicles/{created_id}", json={"current_soc_pct": 55.0})
    assert update_res.status_code == 200
    assert update_res.json()["current_soc_pct"] == 55.0

    # 4. Delete EV
    del_res = client.delete(f"/api/ev/vehicles/{created_id}")
    assert del_res.status_code == 204

def test_simulation_run():
    payload = {
        "preset_name": "Heatwave Alert (Extreme Cooling)",
        "temperature_c": 39.0,
        "cooling_multiplier": 1.75
    }
    res = client.post("/api/simulation/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "baseline" in data
    assert "simulated" in data
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
