import datetime
import math
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

class EnergyForecastingEngine:
    """
    Lightweight, high-accuracy machine learning forecasting model.
    Trains on historical consumption, diurnal cycles, temperature, EV demands, and solar availability.
    Outputs point forecast, 95% confidence intervals, peak detection, and shortage risk warnings.
    """

    def __init__(self):
        self.model = Ridge(alpha=1.0)
        self.is_trained = False
        self.feature_names = [
            "hour", "hour_sin", "hour_cos", "day_of_week",
            "is_weekend", "temperature_c", "solar_generation_kw",
            "ev_charging_kw", "lag_1h", "lag_24h"
        ]

    def _extract_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Engineers cyclic temporal and meteorological features."""
        df = df.copy()
        df["hour"] = df["timestamp"].dt.hour
        df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24.0)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24.0)
        df["day_of_week"] = df["timestamp"].dt.dayofweek
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(float)
        
        # Lags
        df["lag_1h"] = df["total_consumption_kw"].shift(1).bfill()
        df["lag_24h"] = df["total_consumption_kw"].shift(24).bfill()

        X = df[self.feature_names].values
        y = df["total_consumption_kw"].values
        return X, y

    def train_on_history(self, history_records: List[Dict[str, Any]]) -> Dict[str, float]:
        """Trains the Ridge regression forecasting model on historical data."""
        if len(history_records) < 24:
            self.is_trained = False
            return {"r2": 0.0, "mae": 0.0, "samples": len(history_records)}

        df = pd.DataFrame(history_records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        X, y = self._extract_features(df)
        self.model.fit(X, y)
        self.is_trained = True

        predictions = self.model.predict(X)
        mae = mean_absolute_error(y, predictions)
        r2 = r2_score(y, predictions)

        return {
            "r2": round(float(r2), 4),
            "mae": round(float(mae), 2),
            "samples": len(df)
        }

    def predict_horizon(
        self,
        current_reading: Dict[str, Any],
        horizon_hours: int = 24,
        grid_capacity_kw: float = 1200.0,
        temp_modifier: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Generates future hourly demand forecasts with confidence intervals and peak warnings."""
        forecasts = []
        base_time = pd.to_datetime(current_reading["timestamp"])
        curr_load = current_reading["total_consumption_kw"]
        curr_temp = current_reading.get("temperature_c", 25.0) + temp_modifier

        # Expected baseline std dev for error bands (~5% of nominal demand)
        error_margin = 35.0

        for h in range(1, horizon_hours + 1):
            target_time = base_time + datetime.timedelta(hours=h)
            target_hour = target_time.hour
            is_weekend = target_time.weekday() >= 5
            workday_scale = 0.70 if is_weekend else 1.0

            # Diurnal temperature expectation
            hour_temp = curr_temp + 6.0 * math.sin((target_hour - 8) * math.pi / 14)

            # Simulated solar profile for feature vector
            solar_est = 0.0
            if 6 <= target_hour <= 18:
                solar_angle = math.sin((target_hour - 6) * math.pi / 12)
                solar_est = max(0.0, solar_angle * 600.0)

            # EV profile
            ev_est = 120.0 if (8 <= target_hour <= 19) else 35.0

            if self.is_trained:
                feat = np.array([[
                    target_hour,
                    np.sin(2 * np.pi * target_hour / 24.0),
                    np.cos(2 * np.pi * target_hour / 24.0),
                    target_time.weekday(),
                    1.0 if is_weekend else 0.0,
                    hour_temp,
                    solar_est,
                    ev_est,
                    curr_load,  # approx lag
                    curr_load   # approx 24h lag
                ]])
                pred = float(self.model.predict(feat)[0])
            else:
                # Statistical baseline fallback
                hour_curve = math.sin((target_hour - 6) * math.pi / 18) if 6 <= target_hour <= 22 else 0.1
                hour_curve = max(0.1, hour_curve)
                pred = (480.0 + 420.0 * hour_curve * workday_scale) + (max(0.0, hour_temp - 24.0) * 18.0)

            pred = max(200.0, pred)
            lower = max(150.0, pred - error_margin * 1.96)
            upper = pred + error_margin * 1.96

            peak_flag = pred > 900.0
            shortage_risk = pred > (grid_capacity_kw + solar_est * 0.8)

            forecasts.append({
                "target_timestamp": target_time.isoformat(),
                "predicted_demand_kw": round(pred, 2),
                "lower_bound_kw": round(lower, 2),
                "upper_bound_kw": round(upper, 2),
                "confidence_score": round(max(0.75, 0.95 - (h * 0.007)), 3),
                "peak_flag": peak_flag,
                "shortage_risk_flag": shortage_risk,
                "hour": target_hour,
                "solar_estimated_kw": round(solar_est, 2),
                "temperature_c": round(hour_temp, 1)
            })

            # Roll current load forward
            curr_load = pred

        return forecasts


class SolarIntelligenceEngine:
    """
    Physical-statistical Solar Generation Intelligence Model.
    Models PV array physics:
      - Sun position & clear-sky irradiance
      - Cloud cover attenuation
      - Temperature derating coefficient: P_derated = P_stc * [1 - gamma * (T_cell - 25°C)]
    """

    @classmethod
    def estimate_generation(
        cls,
        capacity_kw: float,
        timestamp: datetime.datetime,
        temperature_c: float = 25.0,
        cloud_cover_pct: float = 10.0,
        panel_efficiency: float = 0.20
    ) -> Dict[str, Any]:
        hour = timestamp.hour + (timestamp.minute / 60.0)

        # Solar elevation angle approximation
        if 6.0 <= hour <= 18.0:
            solar_sin = math.sin((hour - 6.0) * math.pi / 12.0)
            clearsky_irradiance = 1000.0 * solar_sin  # W/m2 at standard peak
            cloud_attenuation = max(0.1, 1.0 - (cloud_cover_pct / 100.0) * 0.75)
            actual_irradiance = clearsky_irradiance * cloud_attenuation

            # Temperature derating: -0.4% per °C above 25°C
            temp_derate_factor = 1.0 - max(0.0, (temperature_c - 25.0) * 0.004)
            power_kw = capacity_kw * (actual_irradiance / 1000.0) * temp_derate_factor * 0.95
        else:
            actual_irradiance = 0.0
            power_kw = 0.0
            temp_derate_factor = 1.0

        return {
            "timestamp": timestamp.isoformat(),
            "generation_kw": round(max(0.0, power_kw), 2),
            "irradiance_w_m2": round(actual_irradiance, 1),
            "temperature_c": temperature_c,
            "cloud_cover_pct": cloud_cover_pct,
            "thermal_efficiency_pct": round(temp_derate_factor * 100.0, 1),
            "renewable_fraction_kw": round(max(0.0, power_kw), 2)
        }
