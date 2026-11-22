from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Campus & Settings
class CampusBase(BaseModel):
    name: str
    grid_capacity_kw: float
    solar_capacity_kw: float
    battery_capacity_kwh: float
    critical_load_ratio: float
    max_ev_allocation_kw: float
    alert_threshold_pct: float

class CampusUpdate(BaseModel):
    name: Optional[str] = None
    grid_capacity_kw: Optional[float] = None
    solar_capacity_kw: Optional[float] = None
    battery_capacity_kwh: Optional[float] = None
    critical_load_ratio: Optional[float] = None
    max_ev_allocation_kw: Optional[float] = None
    alert_threshold_pct: Optional[float] = None

class CampusOut(CampusBase):
    id: int
    updated_at: datetime
    class Config:
        from_attributes = True

# Buildings
class BuildingBase(BaseModel):
    name: str
    type: str
    base_load_kw: float
    peak_cooling_kw: float
    current_load_kw: float
    is_critical: bool
    priority_order: int

class BuildingOut(BuildingBase):
    id: int
    class Config:
        from_attributes = True

# Energy Readings
class EnergyReadingBase(BaseModel):
    timestamp: datetime
    total_consumption_kw: float
    building_consumption_kw: float
    ev_charging_kw: float
    solar_generation_kw: float
    grid_import_kw: float
    net_demand_kw: float
    temperature_c: float
    weather_condition: str

class EnergyReadingOut(EnergyReadingBase):
    id: int
    class Config:
        from_attributes = True

# Solar Readings
class SolarReadingBase(BaseModel):
    timestamp: datetime
    generation_kw: float
    efficiency_pct: float
    irradiance_w_m2: float
    cloud_cover_pct: float
    ambient_temp_c: float

class SolarReadingOut(SolarReadingBase):
    id: int
    class Config:
        from_attributes = True

# EV Management
class EVBase(BaseModel):
    model: str
    owner_name: str
    license_plate: str
    battery_capacity_kwh: float
    current_soc_pct: float
    target_soc_pct: float
    is_emergency_vehicle: bool = False

class EVCreate(EVBase):
    pass

class EVUpdate(BaseModel):
    model: Optional[str] = None
    owner_name: Optional[str] = None
    current_soc_pct: Optional[float] = None
    target_soc_pct: Optional[float] = None
    battery_capacity_kwh: Optional[float] = None
    is_emergency_vehicle: Optional[bool] = None

class EVOut(EVBase):
    id: int
    registered_at: datetime
    class Config:
        from_attributes = True

# Charging Station
class ChargingStationBase(BaseModel):
    name: str
    location: str
    max_power_kw: float
    connector_type: str
    status: str
    current_power_kw: float
    efficiency_pct: float

class ChargingStationUpdate(BaseModel):
    status: Optional[str] = None
    current_power_kw: Optional[float] = None
    max_power_kw: Optional[float] = None

class ChargingStationOut(ChargingStationBase):
    id: int
    class Config:
        from_attributes = True

# Charging Request
class ChargingRequestCreate(BaseModel):
    ev_id: int
    station_id: Optional[int] = None
    requested_energy_kwh: float
    current_soc_pct: float
    target_soc_pct: float
    departure_time: datetime
    priority_level: str = "Normal"  # Urgent, High, Normal, Flexible

class ChargingRequestUpdate(BaseModel):
    status: Optional[str] = None
    priority_level: Optional[str] = None
    allocated_power_kw: Optional[float] = None
    reason_notes: Optional[str] = None

class ChargingRequestOut(BaseModel):
    id: int
    ev_id: int
    station_id: Optional[int]
    requested_energy_kwh: float
    current_soc_pct: float
    target_soc_pct: float
    departure_time: datetime
    priority_level: str
    status: str
    requested_at: datetime
    scheduled_start_time: Optional[datetime]
    allocated_power_kw: float
    reason_notes: Optional[str]
    ev: Optional[EVOut] = None
    class Config:
        from_attributes = True

# Charging Session
class ChargingSessionOut(BaseModel):
    id: int
    request_id: int
    ev_id: int
    station_id: int
    allocated_power_kw: float
    energy_delivered_kwh: float
    start_time: datetime
    estimated_end_time: Optional[datetime]
    status: str
    class Config:
        from_attributes = True

# Demand Forecast
class DemandForecastOut(BaseModel):
    id: int
    forecast_timestamp: datetime
    target_timestamp: datetime
    predicted_demand_kw: float
    lower_bound_kw: float
    upper_bound_kw: float
    confidence_score: float
    peak_flag: bool
    shortage_risk_flag: bool
    model_version: str
    class Config:
        from_attributes = True

# Resource Allocation
class AllocationRequest(BaseModel):
    scenario_name: Optional[str] = "Live Manual Allocation"
    custom_temperature_c: Optional[float] = None
    custom_solar_multiplier: Optional[float] = None
    custom_grid_multiplier: Optional[float] = None
    custom_ev_demand_multiplier: Optional[float] = None

class AllocationOut(BaseModel):
    id: Optional[int] = None
    timestamp: datetime
    scenario_name: str
    total_supply_kw: float
    solar_allocated_kw: float
    grid_allocated_kw: float
    critical_load_kw: float
    essential_building_kw: float
    urgent_ev_kw: float
    flexible_ev_kw: float
    optional_curtailed_kw: float
    deficit_kw: float
    explanation: str
    is_constrained: bool
    details: Optional[Dict[str, Any]] = None

# Alert
class AlertBase(BaseModel):
    type: str
    severity: str
    title: str
    description: str

class AlertCreate(AlertBase):
    pass

class AlertOut(AlertBase):
    id: int
    timestamp: datetime
    is_resolved: bool
    resolved_at: Optional[datetime]
    class Config:
        from_attributes = True

# Simulation Scenario
class SimulationScenarioBase(BaseModel):
    name: str
    description: str
    temperature_c: float
    cooling_multiplier: float
    solar_multiplier: float
    grid_capacity_multiplier: float
    ev_demand_multiplier: float
    is_active: bool

class SimulationScenarioCreate(SimulationScenarioBase):
    pass

class SimulationScenarioOut(SimulationScenarioBase):
    id: int
    class Config:
        from_attributes = True

class SimulationRunRequest(BaseModel):
    preset_name: Optional[str] = None
    temperature_c: Optional[float] = None
    cooling_multiplier: Optional[float] = None
    solar_multiplier: Optional[float] = None
    grid_capacity_multiplier: Optional[float] = None
    ev_demand_multiplier: Optional[float] = None

class SimulationRunResponse(BaseModel):
    scenario_name: str
    baseline: Dict[str, Any]
    simulated: Dict[str, Any]
    allocation_result: AllocationOut
    explanation: str
    recommendations: List[str]
    impact_summary: Dict[str, Any]
