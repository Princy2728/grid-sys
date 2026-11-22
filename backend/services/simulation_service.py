import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.entities import (
    Campus, Building, EnergyReading, SolarReading,
    ChargingRequest, ChargingSession, SimulationScenario,
    ResourceAllocation
)
from backend.algorithms.allocation import SmartAllocationEngine
from backend.schemas.schemas import SimulationRunRequest

class SimulationService:
    @staticmethod
    def run_simulation(db: Session, req: SimulationRunRequest) -> Dict[str, Any]:
        campus = db.query(Campus).first()
        grid_cap = campus.grid_capacity_kw if campus else 1200.0
        solar_cap = campus.solar_capacity_kw if campus else 650.0

        # Baseline conditions
        baseline_temp = 24.0
        baseline_cooling_mult = 1.0
        baseline_solar_mult = 1.0
        baseline_grid_mult = 1.0
        baseline_ev_mult = 1.0

        scenario_name = req.preset_name or "Custom Simulation Scenario"

        # Check preset scenario if preset_name passed
        if req.preset_name:
            preset = db.query(SimulationScenario).filter(SimulationScenario.name == req.preset_name).first()
            if preset:
                sim_temp = preset.temperature_c
                sim_cooling = preset.cooling_multiplier
                sim_solar = preset.solar_multiplier
                sim_grid = preset.grid_capacity_multiplier
                sim_ev = preset.ev_demand_multiplier
            else:
                sim_temp = req.temperature_c or 38.0
                sim_cooling = req.cooling_multiplier or 1.6
                sim_solar = req.solar_multiplier or 0.85
                sim_grid = req.grid_capacity_multiplier or 0.90
                sim_ev = req.ev_demand_multiplier or 1.3
        else:
            sim_temp = req.temperature_c if req.temperature_c is not None else 32.0
            sim_cooling = req.cooling_multiplier if req.cooling_multiplier is not None else 1.4
            sim_solar = req.solar_multiplier if req.solar_multiplier is not None else 0.9
            sim_grid = req.grid_capacity_multiplier if req.grid_capacity_multiplier is not None else 1.0
            sim_ev = req.ev_demand_multiplier if req.ev_demand_multiplier is not None else 1.2

        # Campus building baseline loads
        buildings = db.query(Building).all()
        crit_base = sum(b.base_load_kw for b in buildings if b.is_critical)
        crit_peak_cool = sum(b.peak_cooling_kw - b.base_load_kw for b in buildings if b.is_critical)

        ess_base = sum(b.base_load_kw for b in buildings if not b.is_critical and b.priority_order <= 3)
        ess_peak_cool = sum(b.peak_cooling_kw - b.base_load_kw for b in buildings if not b.is_critical and b.priority_order <= 3)

        opt_base = sum(b.base_load_kw for b in buildings if b.priority_order > 3)
        opt_peak_cool = sum(b.peak_cooling_kw - b.base_load_kw for b in buildings if b.priority_order > 3)

        # Baseline EV loads
        urgent_ev_base = 70.0
        flex_ev_base = 80.0

        # Baseline Solar & Grid
        baseline_solar_gen = 450.0
        baseline_grid_avail = grid_cap

        # 1. Compute Baseline Allocation
        base_crit_demand = crit_base + crit_peak_cool * 0.4
        base_ess_demand = ess_base + ess_peak_cool * 0.4
        base_opt_demand = opt_base + opt_peak_cool * 0.4

        baseline_result = SmartAllocationEngine.allocate(
            grid_capacity_kw=baseline_grid_avail,
            solar_generation_kw=baseline_solar_gen,
            critical_demand_kw=base_crit_demand,
            essential_demand_kw=base_ess_demand,
            urgent_ev_demand_kw=urgent_ev_base,
            flexible_ev_demand_kw=flex_ev_base,
            optional_demand_kw=base_opt_demand,
            scenario_name="Baseline (Normal Operations)"
        )

        # 2. Compute Simulated Loads under Stress / Multipliers
        sim_grid_avail = grid_cap * sim_grid
        # Solar PV thermal de-rating above 25°C: -0.4% per degree + multiplier
        temp_loss = max(0.0, (sim_temp - 25.0) * 0.005)
        sim_solar_gen = max(0.0, (baseline_solar_gen * sim_solar * (1.0 - temp_loss)))

        # Cooling surge scales with temperature & cooling multiplier
        sim_crit_demand = crit_base + crit_peak_cool * sim_cooling
        sim_ess_demand = ess_base + ess_peak_cool * sim_cooling
        sim_opt_demand = opt_base + opt_peak_cool * sim_cooling

        sim_urg_ev_demand = urgent_ev_base * sim_ev
        sim_flex_ev_demand = flex_ev_base * sim_ev

        simulated_result = SmartAllocationEngine.allocate(
            grid_capacity_kw=sim_grid_avail,
            solar_generation_kw=sim_solar_gen,
            critical_demand_kw=sim_crit_demand,
            essential_demand_kw=sim_ess_demand,
            urgent_ev_demand_kw=sim_urg_ev_demand,
            flexible_ev_demand_kw=sim_flex_ev_demand,
            optional_demand_kw=sim_opt_demand,
            scenario_name=scenario_name
        )

        # 3. Generate Actionable Recommendations (Module H - Energy Recommendation Assistant)
        recommendations = []
        if simulated_result["is_constrained"]:
            deficit = simulated_result["deficit_kw"]
            flex_cut = simulated_result["details"]["shortfalls"]["flexible_ev"]
            opt_cut = simulated_result["details"]["shortfalls"]["curtailed_optional"]

            recommendations.append(
                f"Peak Shaving Directive: Activate dynamic pre-cooling protocols across non-critical academic halls to curb aggregate chiller load."
            )
            if flex_cut > 0:
                recommendations.append(
                    f"EV Smart Deferral: Defer {flex_cut:.1f} kW of flexible commuter vehicle charging to off-peak nocturnal window (22:00 - 05:00)."
                )
            if opt_cut > 0:
                recommendations.append(
                    f"Auxiliary Load Curtailment: Shed {opt_cut:.1f} kW of non-essential campus loads (sports arena HVAC and decorative architectural lighting)."
                )
            if sim_grid < 1.0:
                recommendations.append(
                    f"Substation Protection: Grid import constrained to {sim_grid_avail:.1f} kW ({sim_grid*100:.0f}% capacity). Battery ESS discharge recommended."
                )
        else:
            recommendations.append(
                "Grid stability optimal: Substation headroom is sufficient to absorb current simulated loads. No immediate load shedding required."
            )
            recommendations.append(
                "Green Energy Utilization: Maximize daytime EV charging to directly capture available renewable solar generation."
            )

        # Impact Summary
        demand_delta = (
            (sim_crit_demand + sim_ess_demand + sim_opt_demand + sim_urg_ev_demand + sim_flex_ev_demand) -
            (base_crit_demand + base_ess_demand + base_opt_demand + urgent_ev_base + flex_ev_base)
        )
        supply_delta = (sim_grid_avail + sim_solar_gen) - (baseline_grid_avail + baseline_solar_gen)

        impact_summary = {
            "temperature_delta_c": round(sim_temp - baseline_temp, 1),
            "demand_increase_kw": round(demand_delta, 1),
            "demand_increase_pct": round((demand_delta / baseline_result["details"]["total_demand_kw"]) * 100.0, 1),
            "supply_change_kw": round(supply_delta, 1),
            "solar_generation_change_kw": round(sim_solar_gen - baseline_solar_gen, 1),
            "grid_capacity_kw": round(sim_grid_avail, 1),
            "deficit_kw": simulated_result["deficit_kw"],
            "deferred_flexible_ev_kw": simulated_result["details"]["shortfalls"]["flexible_ev"],
            "curtailed_optional_kw": simulated_result["details"]["shortfalls"]["curtailed_optional"]
        }

        # Save record to ResourceAllocation
        alloc_record = ResourceAllocation(
            timestamp=datetime.datetime.utcnow(),
            scenario_name=scenario_name,
            total_supply_kw=simulated_result["total_supply_kw"],
            solar_allocated_kw=simulated_result["solar_allocated_kw"],
            grid_allocated_kw=simulated_result["grid_allocated_kw"],
            critical_load_kw=simulated_result["critical_load_kw"],
            essential_building_kw=simulated_result["essential_building_kw"],
            urgent_ev_kw=simulated_result["urgent_ev_kw"],
            flexible_ev_kw=simulated_result["flexible_ev_kw"],
            optional_curtailed_kw=simulated_result["optional_curtailed_kw"],
            deficit_kw=simulated_result["deficit_kw"],
            explanation=simulated_result["explanation"],
            is_constrained=simulated_result["is_constrained"]
        )
        db.add(alloc_record)
        db.commit()

        return {
            "scenario_name": scenario_name,
            "baseline": baseline_result,
            "simulated": simulated_result,
            "allocation_result": simulated_result,
            "explanation": simulated_result["explanation"],
            "recommendations": recommendations,
            "impact_summary": impact_summary
        }
