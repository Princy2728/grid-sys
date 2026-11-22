import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database.connection import Base

class Campus(Base):
    __tablename__ = "campuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Metro Innovation Smart Campus")
    grid_capacity_kw = Column(Float, default=1200.0)
    solar_capacity_kw = Column(Float, default=650.0)
    battery_capacity_kwh = Column(Float, default=500.0)
    critical_load_ratio = Column(Float, default=0.35)
    max_ev_allocation_kw = Column(Float, default=400.0)
    alert_threshold_pct = Column(Float, default=85.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String)  # Academic, Laboratory, Dormitory, Administration, Health & Medical
    base_load_kw = Column(Float, default=50.0)
    peak_cooling_kw = Column(Float, default=80.0)
    current_load_kw = Column(Float, default=70.0)
    is_critical = Column(Boolean, default=False)
    priority_order = Column(Integer, default=3)  # 1: Most critical, 5: Lowest

class EnergyReading(Base):
    __tablename__ = "energy_readings"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    total_consumption_kw = Column(Float, nullable=False)
    building_consumption_kw = Column(Float, nullable=False)
    ev_charging_kw = Column(Float, default=0.0)
    solar_generation_kw = Column(Float, default=0.0)
    grid_import_kw = Column(Float, default=0.0)
    net_demand_kw = Column(Float, default=0.0)
    temperature_c = Column(Float, default=24.0)
    weather_condition = Column(String, default="Clear")

class SolarReading(Base):
    __tablename__ = "solar_readings"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    generation_kw = Column(Float, nullable=False)
    efficiency_pct = Column(Float, default=18.5)
    irradiance_w_m2 = Column(Float, default=750.0)
    cloud_cover_pct = Column(Float, default=10.0)
    ambient_temp_c = Column(Float, default=26.0)

class ChargingStation(Base):
    __tablename__ = "charging_stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(String, default="North Parking Lot")
    max_power_kw = Column(Float, default=22.0)
    connector_type = Column(String, default="Type 2 / CCS")
    status = Column(String, default="available")  # available, in_use, faulted, offline
    current_power_kw = Column(Float, default=0.0)
    efficiency_pct = Column(Float, default=94.0)

    sessions = relationship("ChargingSession", back_populates="station")

class EV(Base):
    __tablename__ = "electric_vehicles"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    license_plate = Column(String, unique=True, index=True)
    battery_capacity_kwh = Column(Float, default=60.0)
    current_soc_pct = Column(Float, default=40.0)
    target_soc_pct = Column(Float, default=85.0)
    is_emergency_vehicle = Column(Boolean, default=False)
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)

    requests = relationship("ChargingRequest", back_populates="ev")

class ChargingRequest(Base):
    __tablename__ = "charging_requests"

    id = Column(Integer, primary_key=True, index=True)
    ev_id = Column(Integer, ForeignKey("electric_vehicles.id"))
    station_id = Column(Integer, ForeignKey("charging_stations.id"), nullable=True)
    requested_energy_kwh = Column(Float, nullable=False)
    current_soc_pct = Column(Float, default=30.0)
    target_soc_pct = Column(Float, default=80.0)
    departure_time = Column(DateTime, nullable=False)
    priority_level = Column(String, default="Normal")  # Urgent, High, Normal, Flexible
    status = Column(String, default="pending")  # pending, scheduled, active, completed, deferred, rejected
    requested_at = Column(DateTime, default=datetime.datetime.utcnow)
    scheduled_start_time = Column(DateTime, nullable=True)
    allocated_power_kw = Column(Float, default=0.0)
    reason_notes = Column(Text, nullable=True)

    ev = relationship("EV", back_populates="requests")
    session = relationship("ChargingSession", back_populates="request", uselist=False)

class ChargingSession(Base):
    __tablename__ = "charging_sessions"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("charging_requests.id"), unique=True)
    ev_id = Column(Integer, ForeignKey("electric_vehicles.id"))
    station_id = Column(Integer, ForeignKey("charging_stations.id"))
    allocated_power_kw = Column(Float, default=11.0)
    energy_delivered_kwh = Column(Float, default=0.0)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    estimated_end_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    status = Column(String, default="active")  # active, completed, throttled, paused

    station = relationship("ChargingStation", back_populates="sessions")
    request = relationship("ChargingRequest", back_populates="session")

class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    forecast_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    target_timestamp = Column(DateTime, nullable=False, index=True)
    predicted_demand_kw = Column(Float, nullable=False)
    lower_bound_kw = Column(Float, nullable=False)
    upper_bound_kw = Column(Float, nullable=False)
    confidence_score = Column(Float, default=0.92)
    peak_flag = Column(Boolean, default=False)
    shortage_risk_flag = Column(Boolean, default=False)
    model_version = Column(String, default="Ridge-Ensemble-v1.0")

class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    scenario_name = Column(String, default="Normal Operation")
    total_supply_kw = Column(Float, nullable=False)
    solar_allocated_kw = Column(Float, default=0.0)
    grid_allocated_kw = Column(Float, default=0.0)
    critical_load_kw = Column(Float, default=0.0)
    essential_building_kw = Column(Float, default=0.0)
    urgent_ev_kw = Column(Float, default=0.0)
    flexible_ev_kw = Column(Float, default=0.0)
    optional_curtailed_kw = Column(Float, default=0.0)
    deficit_kw = Column(Float, default=0.0)
    explanation = Column(Text, nullable=False)
    is_constrained = Column(Boolean, default=False)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    type = Column(String, nullable=False)  # shortage_warning, abnormal_consumption, station_fault, peak_demand, system_info
    severity = Column(String, default="warning")  # critical, warning, info
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)

class SimulationScenario(Base):
    __tablename__ = "simulation_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    temperature_c = Column(Float, default=25.0)
    cooling_multiplier = Column(Float, default=1.0)
    solar_multiplier = Column(Float, default=1.0)
    grid_capacity_multiplier = Column(Float, default=1.0)
    ev_demand_multiplier = Column(Float, default=1.0)
    is_active = Column(Boolean, default=False)
