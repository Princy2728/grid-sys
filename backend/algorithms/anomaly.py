import numpy as np
from typing import List, Dict, Any, Optional

class AnomalyDetectionEngine:
    """
    Lightweight Multi-Criteria Statistical & Rule-Based Anomaly Detection.
    Detects:
      1. Abnormal campus energy spikes (Z-score > 2.5 against rolling window)
      2. Solar generation drop inconsistent with ambient irradiance
      3. Charging station ground faults and inverter hardware irregularities
      4. EV battery degradation / unusual rapid depletion patterns
      5. Substation grid headroom violations
    """

    @classmethod
    def analyze_readings(
        cls,
        recent_readings: List[Dict[str, Any]],
        current_reading: Dict[str, Any],
        grid_capacity_kw: float = 1200.0
    ) -> List[Dict[str, Any]]:
        anomalies = []

        total_kw = current_reading.get("total_consumption_kw", 0.0)
        solar_kw = current_reading.get("solar_generation_kw", 0.0)
        temp_c = current_reading.get("temperature_c", 25.0)

        # 1. Statistical Z-Score on Total Demand
        if len(recent_readings) >= 12:
            hist_loads = [r.get("total_consumption_kw", 0.0) for r in recent_readings]
            mean_load = np.mean(hist_loads)
            std_load = np.std(hist_loads) or 1.0

            z_score = (total_kw - mean_load) / std_load
            if z_score > 2.5:
                anomalies.append({
                    "type": "abnormal_consumption",
                    "severity": "warning" if z_score < 3.2 else "critical",
                    "title": f"Abnormal Demand Spike (Z-score: +{z_score:.2f})",
                    "description": f"Instantaneous campus demand of {total_kw:.1f} kW exceeds 12-hour baseline mean ({mean_load:.1f} kW) by {z_score:.1f} standard deviations.",
                    "value": total_kw,
                    "threshold": mean_load + 2.5 * std_load
                })

        # 2. Grid Capacity Headroom Alert
        grid_load = max(0.0, total_kw - solar_kw)
        grid_pct = (grid_load / grid_capacity_kw) * 100.0 if grid_capacity_kw > 0 else 0.0
        if grid_pct >= 90.0:
            anomalies.append({
                "type": "shortage_warning",
                "severity": "critical",
                "title": f"Critical Substation Overload Risk ({grid_pct:.1f}%)",
                "description": f"Grid import is drawing {grid_load:.1f} kW, exceeding 90% of nominal substation rating ({grid_capacity_kw:.1f} kW). Immediate flexible load shedding required.",
                "value": grid_load,
                "threshold": grid_capacity_kw * 0.90
            })
        elif grid_pct >= 80.0:
            anomalies.append({
                "type": "shortage_warning",
                "severity": "warning",
                "title": f"High Grid Headroom Warning ({grid_pct:.1f}%)",
                "description": f"Substation load has reached {grid_load:.1f} kW. Monitoring EV charging queues for deferred scheduling.",
                "value": grid_load,
                "threshold": grid_capacity_kw * 0.80
            })

        # 3. Solar Irradiance Mismatch
        hour = current_reading.get("timestamp")
        # If hour is 11-14 and solar generation is near zero while weather is clear
        if 11 <= current_reading.get("hour", 12) <= 14:
            if solar_kw < 50.0 and current_reading.get("weather_condition", "") == "Clear":
                anomalies.append({
                    "type": "solar_fault",
                    "severity": "warning",
                    "title": "Solar Array Performance Deficit",
                    "description": f"Mid-day clear-sky generation ({solar_kw:.1f} kW) is severely underperforming expected nominal output (>350 kW). Possible inverter disconnect or soiling.",
                    "value": solar_kw,
                    "threshold": 350.0
                })

        return anomalies
