import pytest
from backend.algorithms.allocation import SmartAllocationEngine
from backend.algorithms.forecasting import SolarIntelligenceEngine

def test_smart_allocation_unconstrained():
    # Grid: 1000 kW, Solar: 400 kW, Total: 1400 kW
    # Demands: Crit: 200, Ess: 300, Urg EV: 100, Flex EV: 100, Opt: 100 -> Total: 800 kW
    result = SmartAllocationEngine.allocate(
        grid_capacity_kw=1000.0,
        solar_generation_kw=400.0,
        critical_demand_kw=200.0,
        essential_demand_kw=300.0,
        urgent_ev_demand_kw=100.0,
        flexible_ev_demand_kw=100.0,
        optional_demand_kw=100.0
    )
    assert result["is_constrained"] is False
    assert result["deficit_kw"] == 0.0
    assert result["critical_load_kw"] == 200.0
    assert result["essential_building_kw"] == 300.0
    assert result["urgent_ev_kw"] == 100.0
    assert result["flexible_ev_kw"] == 100.0
    assert result["optional_curtailed_kw"] == 0.0
    assert result["solar_allocated_kw"] == 400.0
    assert result["grid_allocated_kw"] == 400.0

def test_smart_allocation_constrained_flex_ev_curtailment():
    # Total Supply: 600 kW (500 kW grid + 100 kW solar)
    # Demands: Crit: 250 kW, Ess: 250 kW, Urg EV: 80 kW, Flex EV: 120 kW, Opt: 100 kW -> Total: 800 kW
    # Supply = 600 kW
    # Priority:
    # 1. Critical: min(600, 250) = 250 kW (rem 350)
    # 2. Essential: min(350, 250) = 250 kW (rem 100)
    # 3. Urgent EV: min(100, 80) = 80 kW (rem 20)
    # 4. Flexible EV: min(20, 120) = 20 kW (rem 0) -> Flex shortfall = 100 kW
    # 5. Optional: min(0, 100) = 0 kW -> Curtailed = 100 kW
    result = SmartAllocationEngine.allocate(
        grid_capacity_kw=500.0,
        solar_generation_kw=100.0,
        critical_demand_kw=250.0,
        essential_demand_kw=250.0,
        urgent_ev_demand_kw=80.0,
        flexible_ev_demand_kw=120.0,
        optional_demand_kw=100.0
    )
    assert result["is_constrained"] is True
    assert result["deficit_kw"] == 200.0
    assert result["critical_load_kw"] == 250.0
    assert result["essential_building_kw"] == 250.0
    assert result["urgent_ev_kw"] == 80.0
    assert result["flexible_ev_kw"] == 20.0
    assert result["optional_curtailed_kw"] == 100.0
    # Total allocated must NEVER exceed total supply
    assert (
        result["critical_load_kw"] +
        result["essential_building_kw"] +
        result["urgent_ev_kw"] +
        result["flexible_ev_kw"] +
        (100.0 - result["optional_curtailed_kw"])
    ) <= result["total_supply_kw"]

def test_never_allocate_more_than_supply():
    grid_cap = 400.0
    solar_gen = 100.0
    total_supply = 500.0

    result = SmartAllocationEngine.allocate(
        grid_capacity_kw=grid_cap,
        solar_generation_kw=solar_gen,
        critical_demand_kw=300.0,
        essential_demand_kw=300.0,
        urgent_ev_demand_kw=200.0,
        flexible_ev_demand_kw=200.0,
        optional_demand_kw=200.0
    )
    total_allocated = result["details"]["total_allocated_kw"]
    assert total_allocated <= total_supply
    assert result["deficit_kw"] == 700.0

def test_solar_physics_temperature_derating():
    import datetime
    dt_noon = datetime.datetime(2026, 6, 21, 12, 0)
    # At 25°C standard test condition
    res_25 = SolarIntelligenceEngine.estimate_generation(650.0, dt_noon, temperature_c=25.0)
    # At 40°C heatwave condition
    res_40 = SolarIntelligenceEngine.estimate_generation(650.0, dt_noon, temperature_c=40.0)

    assert res_25["generation_kw"] > res_40["generation_kw"]
    assert res_40["thermal_efficiency_pct"] < res_25["thermal_efficiency_pct"]
