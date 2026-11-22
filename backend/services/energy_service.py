import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from backend.models.entities import (
    Campus, Building, EnergyReading, SolarReading,
    DemandForecast, ChargingSession, ChargingRequest
)
from backend.algorithms.forecasting import EnergyForecastingEngine, SolarIntelligenceEngine
from backend.algorithms.anomaly import AnomalyDetectionEngine

forecasting_engine = EnergyForecastingEngine()

class EnergyService:
    @staticmethod
    def get_kpi_overview(db: Session) -> Dict[str, Any]:
        campus = db.query(Campus).first()
        latest_reading = db.query(EnergyReading).order_by(desc(EnergyReading.timestamp)).first()
        latest_solar = db.query(SolarReading).order_by(desc(SolarReading.timestamp)).first()

        # If no readings, generate a nominal fallback
        if not latest_reading:
            total_kw = 720.0
            bldg_kw = 580.0
            ev_kw = 140.0
            solar_kw = 320.0
            grid_kw = 400.0
            temp = 24.5
        else:
            total_kw = latest_reading.total_consumption_kw
            bldg_kw = latest_reading.building_consumption_kw
            ev_kw = latest_reading.ev_charging_kw
            solar_kw = latest_reading.solar_generation_kw
            grid_kw = latest_reading.grid_import_kw
            temp = latest_reading.temperature_c

        grid_cap = campus.grid_capacity_kw if campus else 1200.0
        solar_cap = campus.solar_capacity_kw if campus else 650.0

        solar_share = round((solar_kw / total_kw * 100.0), 1) if total_kw > 0 else 0.0
        grid_load_pct = round((grid_kw / grid_cap * 100.0), 1) if grid_cap > 0 else 0.0
        available_cap = round((grid_cap + solar_kw), 1)
        headroom_kw = round(max(0.0, available_cap - total_kw), 1)

        # 24h peak consumption
        since_24h = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        peak_24h_record = db.query(func.max(EnergyReading.total_consumption_kw)).filter(
            EnergyReading.timestamp >= since_24h
        ).scalar() or total_kw

        # Critical vs non-critical building loads
        crit_bldg_load = db.query(func.sum(Building.current_load_kw)).filter(Building.is_critical == True).scalar() or 280.0
        non_crit_bldg_load = db.query(func.sum(Building.current_load_kw)).filter(Building.is_critical == False).scalar() or 380.0

        return {
            "campus_name": campus.name if campus else "Metro Innovation Smart Campus",
            "timestamp": latest_reading.timestamp.isoformat() if latest_reading else datetime.datetime.utcnow().isoformat(),
            "total_consumption_kw": round(total_kw, 1),
            "building_consumption_kw": round(bldg_kw, 1),
            "critical_building_load_kw": round(crit_bldg_load, 1),
            "non_critical_building_load_kw": round(non_crit_bldg_load, 1),
            "ev_charging_kw": round(ev_kw, 1),
            "solar_generation_kw": round(solar_kw, 1),
            "grid_import_kw": round(grid_kw, 1),
            "net_demand_kw": round(max(0.0, total_kw - solar_kw), 1),
            "solar_capacity_kw": solar_cap,
            "grid_capacity_kw": grid_cap,
            "available_capacity_kw": available_cap,
            "grid_utilization_pct": grid_load_pct,
            "solar_share_pct": solar_share,
            "headroom_kw": headroom_kw,
            "peak_today_kw": round(peak_24h_record, 1),
            "temperature_c": temp,
            "weather": latest_reading.weather_condition if latest_reading else "Clear"
        }

    @staticmethod
    def get_history(db: Session, hours: int = 24) -> List[Dict[str, Any]]:
        since = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        readings = db.query(EnergyReading).filter(
            EnergyReading.timestamp >= since
        ).order_by(EnergyReading.timestamp).all()

        result = []
        for r in readings:
            result.append({
                "id": r.id,
                "timestamp": r.timestamp.isoformat(),
                "time_label": r.timestamp.strftime("%H:%M"),
                "total_consumption_kw": r.total_consumption_kw,
                "building_consumption_kw": r.building_consumption_kw,
                "ev_charging_kw": r.ev_charging_kw,
                "solar_generation_kw": r.solar_generation_kw,
                "grid_import_kw": r.grid_import_kw,
                "net_demand_kw": r.net_demand_kw,
                "temperature_c": r.temperature_c,
                "weather_condition": r.weather_condition
            })
        return result

    @staticmethod
    def get_solar_analytics(db: Session) -> Dict[str, Any]:
        campus = db.query(Campus).first()
        solar_cap = campus.solar_capacity_kw if campus else 650.0

        latest = db.query(SolarReading).order_by(desc(SolarReading.timestamp)).first()
        since_24h = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        readings_24h = db.query(SolarReading).filter(
            SolarReading.timestamp >= since_24h
        ).order_by(SolarReading.timestamp).all()

        daily_kwh = sum(r.generation_kw for r in readings_24h)
        peak_gen = max([r.generation_kw for r in readings_24h], default=0.0)

        history = [{
            "timestamp": r.timestamp.isoformat(),
            "time_label": r.timestamp.strftime("%H:%M"),
            "generation_kw": r.generation_kw,
            "irradiance_w_m2": r.irradiance_w_m2,
            "cloud_cover_pct": r.cloud_cover_pct,
            "efficiency_pct": r.efficiency_pct
        } for r in readings_24h]

        return {
            "capacity_kw": solar_cap,
            "current_generation_kw": latest.generation_kw if latest else 0.0,
            "current_irradiance_w_m2": latest.irradiance_w_m2 if latest else 0.0,
            "current_efficiency_pct": latest.efficiency_pct if latest else 18.5,
            "cloud_cover_pct": latest.cloud_cover_pct if latest else 10.0,
            "estimated_daily_yield_kwh": round(daily_kwh, 1),
            "peak_generation_kw": round(peak_gen, 1),
            "history": history
        }

    @staticmethod
    def get_demand_forecast(db: Session) -> Dict[str, Any]:
        campus = db.query(Campus).first()
        grid_cap = campus.grid_capacity_kw if campus else 1200.0

        # Retrieve saved forecast or train engine dynamically
        latest_reading = db.query(EnergyReading).order_by(desc(EnergyReading.timestamp)).first()
        history = db.query(EnergyReading).order_by(desc(EnergyReading.timestamp)).limit(72).all()

        hist_records = [{
            "timestamp": r.timestamp,
            "total_consumption_kw": r.total_consumption_kw,
            "solar_generation_kw": r.solar_generation_kw,
            "ev_charging_kw": r.ev_charging_kw,
            "temperature_c": r.temperature_c
        } for r in reversed(history)]

        train_metrics = forecasting_engine.train_on_history(hist_records)

        current_dict = {
            "timestamp": latest_reading.timestamp if latest_reading else datetime.datetime.utcnow(),
            "total_consumption_kw": latest_reading.total_consumption_kw if latest_reading else 700.0,
            "temperature_c": latest_reading.temperature_c if latest_reading else 24.0
        }

        forecasts = forecasting_engine.predict_horizon(
            current_reading=current_dict,
            horizon_hours=24,
            grid_capacity_kw=grid_cap
        )

        # Calculate peak period
        peak_period = max(forecasts, key=lambda f: f["predicted_demand_kw"])
        shortage_warnings = [f for f in forecasts if f["shortage_risk_flag"]]

        return {
            "model_type": "Ridge-Autoregressive Ensemble",
            "evaluation_metrics": train_metrics,
            "horizon_hours": 24,
            "peak_period": {
                "target_timestamp": peak_period["target_timestamp"],
                "hour": peak_period["hour"],
                "predicted_demand_kw": peak_period["predicted_demand_kw"]
            },
            "shortage_risk_count": len(shortage_warnings),
            "forecast_series": forecasts
        }
