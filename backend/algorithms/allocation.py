from typing import Dict, List, Any, Tuple
import datetime

class SmartAllocationEngine:
    """
    Deterministic Constrained Priority Scheduling Engine.
    Allocates available energy across hierarchical tiers:
      Tier 1: Critical Campus Loads (Medical, Labs, IT Data Center, Life Safety)
      Tier 2: Essential Building Loads (Academic baseline, Dormitory baseline)
      Tier 3: Urgent EV Charging (Emergency responders, security, low SoC near deadline)
      Tier 4: Flexible EV Charging (Students, standard staff, delayed departure)
      Tier 5: Optional Consumption (Athletic complex, decorative lighting, auxiliary HVAC)
    
    Guarantees:
      - Never allocates more power than Available Capacity (Grid + Solar).
      - If supply < demand, curtails lower tiers strictly and computes deficit.
      - Provides full human-readable and structured mathematical explanation.
    """

    @classmethod
    def allocate(
        cls,
        grid_capacity_kw: float,
        solar_generation_kw: float,
        critical_demand_kw: float,
        essential_demand_kw: float,
        urgent_ev_demand_kw: float,
        flexible_ev_demand_kw: float,
        optional_demand_kw: float,
        scenario_name: str = "Standard Allocation"
    ) -> Dict[str, Any]:
        total_supply = grid_capacity_kw + solar_generation_kw
        total_demand = (
            critical_demand_kw +
            essential_demand_kw +
            urgent_ev_demand_kw +
            flexible_ev_demand_kw +
            optional_demand_kw
        )

        remaining_supply = total_supply

        # Tier 1: Critical Campus Loads
        allocated_critical = min(remaining_supply, critical_demand_kw)
        remaining_supply -= allocated_critical
        critical_shortfall = critical_demand_kw - allocated_critical

        # Tier 2: Essential Building Requirements
        allocated_essential = min(remaining_supply, essential_demand_kw)
        remaining_supply -= allocated_essential
        essential_shortfall = essential_demand_kw - allocated_essential

        # Tier 3: Urgent EV Charging
        allocated_urgent_ev = min(remaining_supply, urgent_ev_demand_kw)
        remaining_supply -= allocated_urgent_ev
        urgent_ev_shortfall = urgent_ev_demand_kw - allocated_urgent_ev

        # Tier 4: Flexible EV Charging
        allocated_flexible_ev = min(remaining_supply, flexible_ev_demand_kw)
        remaining_supply -= allocated_flexible_ev
        flexible_ev_shortfall = flexible_ev_demand_kw - allocated_flexible_ev

        # Tier 5: Optional Consumption
        allocated_optional = min(remaining_supply, optional_demand_kw)
        remaining_supply -= allocated_optional
        curtailed_optional = optional_demand_kw - allocated_optional

        # Total allocated power
        total_allocated = (
            allocated_critical +
            allocated_essential +
            allocated_urgent_ev +
            allocated_flexible_ev +
            allocated_optional
        )

        # Deficit calculation
        deficit = max(0.0, total_demand - total_supply)
        is_constrained = deficit > 0.0 or curtailed_optional > 0.0 or flexible_ev_shortfall > 0.0

        # Allocation of source power (Solar first, then Grid)
        solar_allocated = min(total_allocated, solar_generation_kw)
        grid_allocated = total_allocated - solar_allocated

        # Solar coverage percentage
        solar_coverage_pct = round((solar_allocated / total_allocated * 100.0), 1) if total_allocated > 0 else 0.0
        grid_utilization_pct = round((grid_allocated / grid_capacity_kw * 100.0), 1) if grid_capacity_kw > 0 else 0.0

        # Generate transparent, deterministic explanation
        explanation_lines = []
        if not is_constrained:
            explanation_lines.append(
                f"Optimal supply balance: Total available power of {total_supply:.1f} kW safely exceeds aggregate campus demand of {total_demand:.1f} kW."
            )
            explanation_lines.append(
                f"Solar generation provides {solar_allocated:.1f} kW ({solar_coverage_pct}% of total consumption), reducing peak grid draw to {grid_allocated:.1f} kW ({grid_utilization_pct}% of substation limit)."
            )
            explanation_lines.append(
                "All 5 priority tiers (100% Critical, 100% Essential, 100% EV Charging, 100% Auxiliary) are fully supplied without curtailment."
            )
        else:
            explanation_lines.append(
                f"CONSTRAINED DISPATCH ACTIVE: Aggregate campus demand ({total_demand:.1f} kW) exceeds safe instantaneous supply capacity ({total_supply:.1f} kW) by {deficit:.1f} kW."
            )
            if critical_shortfall > 0:
                explanation_lines.append(
                    f"CRITICAL DEFICIT ALERT: Insufficient capacity to fully satisfy Tier 1 Critical Loads. Unmet critical load: {critical_shortfall:.1f} kW."
                )
            elif essential_shortfall > 0:
                explanation_lines.append(
                    f"ESSENTIAL DEFICIT: Tier 1 Critical loads 100% satisfied ({allocated_critical:.1f} kW), but Tier 2 Essential building services have an unmet shortfall of {essential_shortfall:.1f} kW."
                )
            elif urgent_ev_shortfall > 0:
                explanation_lines.append(
                    f"EV DISPATCH DEFICIT: Tier 1 & 2 fully satisfied. Urgent/emergency EV charging throttled by {urgent_ev_shortfall:.1f} kW."
                )
            elif flexible_ev_shortfall > 0:
                explanation_lines.append(
                    f"SMART EV CURTAILMENT: Prioritized Tier 1 Critical ({allocated_critical:.1f} kW), Tier 2 Essential ({allocated_essential:.1f} kW), and Tier 3 Urgent EV ({allocated_urgent_ev:.1f} kW). Flexible EV charging deferred by {flexible_ev_shortfall:.1f} kW to prevent grid overload."
                )
            if curtailed_optional > 0:
                explanation_lines.append(
                    f"Optional/auxiliary loads (athletic facilities and decorative lighting) curtailed by {curtailed_optional:.1f} kW to maintain grid stability."
                )

        return {
            "scenario_name": scenario_name,
            "timestamp": datetime.datetime.utcnow(),
            "total_supply_kw": round(total_supply, 2),
            "solar_allocated_kw": round(solar_allocated, 2),
            "grid_allocated_kw": round(grid_allocated, 2),
            "critical_load_kw": round(allocated_critical, 2),
            "essential_building_kw": round(allocated_essential, 2),
            "urgent_ev_kw": round(allocated_urgent_ev, 2),
            "flexible_ev_kw": round(allocated_flexible_ev, 2),
            "optional_curtailed_kw": round(curtailed_optional, 2),
            "deficit_kw": round(deficit, 2),
            "is_constrained": is_constrained,
            "explanation": " ".join(explanation_lines),
            "details": {
                "total_demand_kw": round(total_demand, 2),
                "total_allocated_kw": round(total_allocated, 2),
                "solar_coverage_pct": solar_coverage_pct,
                "grid_utilization_pct": grid_utilization_pct,
                "headroom_kw": round(max(0.0, total_supply - total_allocated), 2),
                "shortfalls": {
                    "critical": round(critical_shortfall, 2),
                    "essential": round(essential_shortfall, 2),
                    "urgent_ev": round(urgent_ev_shortfall, 2),
                    "flexible_ev": round(flexible_ev_shortfall, 2),
                    "curtailed_optional": round(curtailed_optional, 2),
                }
            }
        }
