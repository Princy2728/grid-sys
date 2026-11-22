import datetime
import math
import random
from backend.database.connection import SessionLocal
from backend.models.entities import (
    Campus, Building, EnergyReading, SolarReading,
    ChargingStation, EV, ChargingRequest, ChargingSession,
    DemandForecast, ResourceAllocation, Alert, SimulationScenario
)

def seed_database():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Campus).first():
            print("Database already contains data. Skipping seed.")
            return

        print("Seeding initial data...")
        now = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)

        # 1. Campus Setting
        campus = Campus(
            name="Metro Innovation Smart Campus",
            grid_capacity_kw=1200.0,
            solar_capacity_kw=650.0,
            battery_capacity_kwh=500.0,
            critical_load_ratio=0.35,
            max_ev_allocation_kw=400.0,
            alert_threshold_pct=85.0
        )
        db.add(campus)

        # 2. Buildings (Mixed critical research labs, medical, academic, dorms)
        buildings_data = [
            ("BioTech Research Center", "Laboratory", 120.0, 180.0, 155.0, True, 1),
            ("Emergency Medical Center", "Health & Medical", 60.0, 75.0, 68.0, True, 1),
            ("Central IT & Network Core", "Infrastructure", 95.0, 110.0, 102.0, True, 1),
            ("Engineering Science Hall", "Academic", 140.0, 195.0, 165.0, False, 2),
            ("Central University Library", "Academic", 75.0, 115.0, 92.0, False, 3),
            ("Student Residence North", "Dormitory", 85.0, 130.0, 105.0, False, 3),
            ("Student Residence South", "Dormitory", 80.0, 125.0, 98.0, False, 3),
            ("Campus Sports & Event Arena", "Athletic", 65.0, 120.0, 80.0, False, 4),
        ]

        buildings = []
        for name, b_type, base_load, peak_cooling, current_load, is_crit, prio in buildings_data:
            b = Building(
                name=name,
                type=b_type,
                base_load_kw=base_load,
                peak_cooling_kw=peak_cooling,
                current_load_kw=current_load,
                is_critical=is_crit,
                priority_order=prio
            )
            db.add(b)
            buildings.append(b)

        # 3. Charging Stations
        stations_data = [
            ("Station CS-01", "North Parking Hub", 50.0, "CCS Fast", "in_use", 45.0),
            ("Station CS-02", "North Parking Hub", 22.0, "Type 2", "in_use", 22.0),
            ("Station CS-03", "North Parking Hub", 11.0, "Type 2", "available", 0.0),
            ("Station CS-04", "South Parking Deck", 50.0, "CCS Fast", "in_use", 48.0),
            ("Station CS-05", "South Parking Deck", 22.0, "Type 2", "in_use", 18.0),
            ("Station CS-06", "South Parking Deck", 11.0, "Type 2", "available", 0.0),
            ("Station CS-07", "West Tech Park", 22.0, "Type 2", "in_use", 20.0),
            ("Station CS-08", "West Tech Park", 11.0, "Type 2", "faulted", 0.0),
        ]

        stations = []
        for name, loc, max_p, conn, stat, curr_p in stations_data:
            s = ChargingStation(
                name=name,
                location=loc,
                max_power_kw=max_p,
                connector_type=conn,
                status=stat,
                current_power_kw=curr_p,
                efficiency_pct=94.5
            )
            db.add(s)
            stations.append(s)

        # 4. Registered EVs
        evs_data = [
            ("MedEvac Transport 1", "Campus Health Unit", "EV-AMB-01", 68.0, 32.0, 90.0, True),
            ("Campus Security Patrol", "Security Services", "EV-SEC-09", 75.0, 38.0, 85.0, True),
            ("Facilities Logistics Van", "Operations Dept", "EV-FAC-14", 135.0, 42.0, 80.0, False),
            ("Hyundai Ioniq 5", "Dr. Aris Thorne", "EV-FAC-781", 77.0, 24.0, 80.0, False),
            ("Nissan Leaf e+", "Prof. Elena Rostova", "EV-FAC-349", 62.0, 52.0, 85.0, False),
            ("Campus North Shuttle", "Transit Authority", "EV-BUS-02", 160.0, 36.0, 90.0, False),
            ("Tesla Model 3 Long Range", "Marcus Vance", "EV-STU-440", 78.0, 19.0, 80.0, False),
            ("Chevy Bolt EV", "Sarah Jenkins", "EV-STU-882", 65.0, 58.0, 80.0, False),
            ("BMW i4 Gran Coupe", "Dean's Office", "EV-ADM-012", 83.0, 44.0, 85.0, False),
            ("Kia EV6 GT-Line", "Tech Support Team", "EV-OPS-221", 77.0, 28.0, 80.0, False),
        ]

        evs = []
        for model, owner, plate, bat_cap, cur_soc, tgt_soc, is_em in evs_data:
            ev_obj = EV(
                model=model,
                owner_name=owner,
                license_plate=plate,
                battery_capacity_kwh=bat_cap,
                current_soc_pct=cur_soc,
                target_soc_pct=tgt_soc,
                is_emergency_vehicle=is_em,
                registered_at=now - datetime.timedelta(days=random.randint(10, 90))
            )
            db.add(ev_obj)
            evs.append(ev_obj)

        db.flush()

        # 5. Charging Requests & Active Sessions
        # Assign requests to active stations
        # Station 0 (CS-01, 50kW) -> EV 0 (Ambulance, Urgent)
        req1 = ChargingRequest(
            ev_id=evs[0].id,
            station_id=stations[0].id,
            requested_energy_kwh=39.4,
            current_soc_pct=32.0,
            target_soc_pct=90.0,
            departure_time=now + datetime.timedelta(hours=2),
            priority_level="Urgent",
            status="active",
            requested_at=now - datetime.timedelta(minutes=45),
            scheduled_start_time=now - datetime.timedelta(minutes=45),
            allocated_power_kw=45.0,
            reason_notes="Emergency medical vehicle on active shift standby."
        )
        db.add(req1)
        db.flush()

        sess1 = ChargingSession(
            request_id=req1.id,
            ev_id=evs[0].id,
            station_id=stations[0].id,
            allocated_power_kw=45.0,
            energy_delivered_kwh=28.5,
            start_time=now - datetime.timedelta(minutes=45),
            estimated_end_time=now + datetime.timedelta(minutes=40),
            status="active"
        )
        db.add(sess1)

        # Station 1 (CS-02, 22kW) -> EV 1 (Security, Urgent)
        req2 = ChargingRequest(
            ev_id=evs[1].id,
            station_id=stations[1].id,
            requested_energy_kwh=35.2,
            current_soc_pct=38.0,
            target_soc_pct=85.0,
            departure_time=now + datetime.timedelta(hours=3),
            priority_level="Urgent",
            status="active",
            requested_at=now - datetime.timedelta(minutes=30),
            scheduled_start_time=now - datetime.timedelta(minutes=30),
            allocated_power_kw=22.0,
            reason_notes="Security patrol priority dispatch."
        )
        db.add(req2)
        db.flush()

        sess2 = ChargingSession(
            request_id=req2.id,
            ev_id=evs[1].id,
            station_id=stations[1].id,
            allocated_power_kw=22.0,
            energy_delivered_kwh=11.0,
            start_time=now - datetime.timedelta(minutes=30),
            estimated_end_time=now + datetime.timedelta(hours=1, minutes=30),
            status="active"
        )
        db.add(sess2)

        # Station 3 (CS-04, 50kW) -> EV 5 (Campus Shuttle, High)
        req3 = ChargingRequest(
            ev_id=evs[5].id,
            station_id=stations[3].id,
            requested_energy_kwh=86.4,
            current_soc_pct=36.0,
            target_soc_pct=90.0,
            departure_time=now + datetime.timedelta(hours=4),
            priority_level="High",
            status="active",
            requested_at=now - datetime.timedelta(minutes=50),
            scheduled_start_time=now - datetime.timedelta(minutes=50),
            allocated_power_kw=48.0,
            reason_notes="Transit bus morning route schedule."
        )
        db.add(req3)
        db.flush()

        sess3 = ChargingSession(
            request_id=req3.id,
            ev_id=evs[5].id,
            station_id=stations[3].id,
            allocated_power_kw=48.0,
            energy_delivered_kwh=38.0,
            start_time=now - datetime.timedelta(minutes=50),
            estimated_end_time=now + datetime.timedelta(hours=1, minutes=15),
            status="active"
        )
        db.add(sess3)

        # Station 4 (CS-05, 22kW) -> EV 3 (Dr. Thorne, Normal)
        req4 = ChargingRequest(
            ev_id=evs[3].id,
            station_id=stations[4].id,
            requested_energy_kwh=43.1,
            current_soc_pct=24.0,
            target_soc_pct=80.0,
            departure_time=now + datetime.timedelta(hours=6),
            priority_level="Normal",
            status="active",
            requested_at=now - datetime.timedelta(minutes=20),
            scheduled_start_time=now - datetime.timedelta(minutes=20),
            allocated_power_kw=18.0,
            reason_notes="Faculty scheduled departure at 17:00."
        )
        db.add(req4)
        db.flush()

        sess4 = ChargingSession(
            request_id=req4.id,
            ev_id=evs[3].id,
            station_id=stations[4].id,
            allocated_power_kw=18.0,
            energy_delivered_kwh=6.0,
            start_time=now - datetime.timedelta(minutes=20),
            estimated_end_time=now + datetime.timedelta(hours=2, minutes=20),
            status="active"
        )
        db.add(sess4)

        # Station 6 (CS-07, 22kW) -> EV 6 (Marcus Vance, Flexible)
        req5 = ChargingRequest(
            ev_id=evs[6].id,
            station_id=stations[6].id,
            requested_energy_kwh=47.5,
            current_soc_pct=19.0,
            target_soc_pct=80.0,
            departure_time=now + datetime.timedelta(hours=7),
            priority_level="Flexible",
            status="active",
            requested_at=now - datetime.timedelta(minutes=15),
            scheduled_start_time=now - datetime.timedelta(minutes=15),
            allocated_power_kw=20.0,
            reason_notes="Flexible overnight charging enrolled."
        )
        db.add(req5)
        db.flush()

        sess5 = ChargingSession(
            request_id=req5.id,
            ev_id=evs[6].id,
            station_id=stations[6].id,
            allocated_power_kw=20.0,
            energy_delivered_kwh=5.0,
            start_time=now - datetime.timedelta(minutes=15),
            estimated_end_time=now + datetime.timedelta(hours=2, minutes=30),
            status="active"
        )
        db.add(sess5)

        # Pending / Deferred Requests
        req6 = ChargingRequest(
            ev_id=evs[2].id,
            station_id=None,
            requested_energy_kwh=51.3,
            current_soc_pct=42.0,
            target_soc_pct=80.0,
            departure_time=now + datetime.timedelta(hours=8),
            priority_level="Flexible",
            status="deferred",
            requested_at=now - datetime.timedelta(minutes=10),
            scheduled_start_time=now + datetime.timedelta(hours=2),
            allocated_power_kw=0.0,
            reason_notes="Deferred to off-peak window (high solar / lower campus base load)."
        )
        db.add(req6)

        req7 = ChargingRequest(
            ev_id=evs[7].id,
            station_id=None,
            requested_energy_kwh=14.3,
            current_soc_pct=58.0,
            target_soc_pct=80.0,
            departure_time=now + datetime.timedelta(hours=5),
            priority_level="Normal",
            status="pending",
            requested_at=now - datetime.timedelta(minutes=5),
            scheduled_start_time=None,
            allocated_power_kw=0.0,
            reason_notes="Awaiting station assignment."
        )
        db.add(req7)

        # 6. Generate 72 hours of historical Energy and Solar Readings
        # Synthetic diurnal curves for solar and campus building loads
        for h in range(72, -1, -1):
            ts = now - datetime.timedelta(hours=h)
            hour_of_day = ts.hour
            day_of_week = ts.weekday()

            # Base building load variation: peak during 09:00 - 18:00
            is_weekend = day_of_week >= 5
            workday_factor = 0.65 if is_weekend else 1.0

            # Diurnal building curve (summing to ~600 - 950 kW)
            hour_curve = math.sin((hour_of_day - 6) * math.pi / 18) if 6 <= hour_of_day <= 22 else 0.1
            hour_curve = max(0.1, hour_curve)
            building_load = (450.0 + 380.0 * hour_curve * workday_factor) + random.uniform(-15.0, 15.0)

            # Solar curve (650 kW peak around 12:00 - 13:00)
            if 6 <= hour_of_day <= 18:
                solar_angle = math.sin((hour_of_day - 6) * math.pi / 12)
                irradiance = max(0.0, solar_angle * 950.0 + random.uniform(-40.0, 30.0))
                solar_gen = max(0.0, (campus.solar_capacity_kw * (irradiance / 1000.0) * 0.95) + random.uniform(-10.0, 10.0))
                cloud_cover = max(5.0, min(80.0, (1.0 - solar_angle) * 35.0 + random.uniform(-10, 15)))
            else:
                irradiance = 0.0
                solar_gen = 0.0
                cloud_cover = random.uniform(10.0, 30.0)

            # EV charging load
            ev_load = (120.0 + 80.0 * hour_curve) if 8 <= hour_of_day <= 20 else 30.0
            ev_load += random.uniform(-10.0, 15.0)
            ev_load = max(15.0, ev_load)

            total_consumption = building_load + ev_load
            grid_import = max(0.0, total_consumption - solar_gen)
            net_demand = total_consumption - solar_gen

            temp = 20.0 + 9.0 * math.sin((hour_of_day - 8) * math.pi / 14) + random.uniform(-1.0, 1.0)
            weather = "Partly Cloudy" if cloud_cover > 40 else "Sunny / Clear"

            # Energy Reading
            er = EnergyReading(
                timestamp=ts,
                total_consumption_kw=round(total_consumption, 2),
                building_consumption_kw=round(building_load, 2),
                ev_charging_kw=round(ev_load, 2),
                solar_generation_kw=round(solar_gen, 2),
                grid_import_kw=round(grid_import, 2),
                net_demand_kw=round(net_demand, 2),
                temperature_c=round(temp, 1),
                weather_condition=weather
            )
            db.add(er)

            # Solar Reading
            sr = SolarReading(
                timestamp=ts,
                generation_kw=round(solar_gen, 2),
                efficiency_pct=round(18.2 + random.uniform(-0.8, 0.8), 2),
                irradiance_w_m2=round(irradiance, 1),
                cloud_cover_pct=round(cloud_cover, 1),
                ambient_temp_c=round(temp, 1)
            )
            db.add(sr)

        # 7. Generate 24 hours of Demand Forecasts
        for f_h in range(1, 25):
            target_ts = now + datetime.timedelta(hours=f_h)
            target_hour = target_ts.hour
            hour_curve = math.sin((target_hour - 6) * math.pi / 18) if 6 <= target_hour <= 22 else 0.1
            hour_curve = max(0.1, hour_curve)
            pred = 560.0 + 440.0 * hour_curve + random.uniform(-15.0, 20.0)
            is_peak = pred > 900.0
            is_shortage = pred > (campus.grid_capacity_kw + 100.0)

            df = DemandForecast(
                forecast_timestamp=now,
                target_timestamp=target_ts,
                predicted_demand_kw=round(pred, 2),
                lower_bound_kw=round(pred * 0.94, 2),
                upper_bound_kw=round(pred * 1.06, 2),
                confidence_score=round(0.93 - (f_h * 0.005), 3),
                peak_flag=is_peak,
                shortage_risk_flag=is_shortage,
                model_version="Ridge-Ensemble-v1.0"
            )
            db.add(df)

        # 8. Initial Resource Allocation record
        total_curr_supply = campus.grid_capacity_kw + 420.0  # grid + current solar
        crit_load = 325.0
        ess_bldg = 460.0
        urg_ev = 115.0
        flex_ev = 38.0
        curtailed = 0.0
        deficit = 0.0

        alloc = ResourceAllocation(
            timestamp=now,
            scenario_name="Normal Campus Operations",
            total_supply_kw=total_curr_supply,
            solar_allocated_kw=420.0,
            grid_allocated_kw=518.0,
            critical_load_kw=crit_load,
            essential_building_kw=ess_bldg,
            urgent_ev_kw=urg_ev,
            flexible_ev_kw=flex_ev,
            optional_curtailed_kw=curtailed,
            deficit_kw=deficit,
            explanation="Normal daytime operating conditions. 100% of critical research and health loads fulfilled. Grid import is within standard headroom (43.2% capacity utilized). Solar contribution accounts for 44.8% of aggregate instantaneous campus demand.",
            is_constrained=False
        )
        db.add(alloc)

        # 9. Alerts
        alerts_data = [
            ("peak_demand", "warning", "Predicted Peak Demand Window at 14:00 - 16:00",
             "Forecast models predict campus demand will peak at 960 kW due to anticipated high lab activity and ambient temperature reaching 32°C. Pre-cooling optimization and EV deferral recommended.", False),
            ("station_fault", "critical", "Station CS-08 Inverter Ground Fault",
             "Charging Station CS-08 (West Tech Park) reported ground isolation error at 09:14 UTC. Station hardware automatically isolated. Maintenance ticket auto-dispatched.", False),
            ("system_info", "info", "Solar Array Optimization Online",
             "Rooftop PV array tracking efficiency operating at optimal 94.5% output. Estimated daily renewable contribution: 3,420 kWh.", False),
            ("shortage_warning", "warning", "Grid Headroom Caution Threshold",
             "Overall campus net demand is approaching 80% of local substation nominal rating during EV simultaneous charging spikes.", False),
        ]

        for a_type, sev, title, desc, is_res in alerts_data:
            alt = Alert(
                timestamp=now - datetime.timedelta(minutes=random.randint(5, 120)),
                type=a_type,
                severity=sev,
                title=title,
                description=desc,
                is_resolved=is_res
            )
            db.add(alt)

        # 10. Simulation Scenarios (Presets)
        scenarios_data = [
            ("Normal Operation", "Standard baseline weather and activity on campus.", 24.0, 1.0, 1.0, 1.0, 1.0, True),
            ("Heatwave Alert (Extreme Cooling)", "Extreme 39°C heatwave induces severe HVAC surge (+75%), slight PV thermal de-rating (-15%), and grid transmission capacity derating (-10%).", 39.0, 1.75, 0.85, 0.90, 1.30, False),
            ("Solar Drop (Cloud Cover / Smoke)", "Sudden cloud and particulates drop PV generation by 75%, forcing immediate grid reliance and peak tariff mitigation.", 26.0, 1.05, 0.25, 1.0, 1.10, False),
            ("Grid Substation Shortage", "Local substation transformer trip slashes grid import capacity to 55%, triggering aggressive load shedding on flexible EVs and non-critical HVAC.", 29.0, 1.20, 0.95, 0.55, 1.20, False),
            ("EV Fleet Demand Surge", "Simultaneous arrival of visiting conference EV fleet doubles EV charging request backlog (+120%).", 25.0, 1.10, 1.0, 1.0, 2.20, False),
        ]

        for s_name, desc, temp, cool_m, sol_m, grid_m, ev_m, active in scenarios_data:
            sc = SimulationScenario(
                name=s_name,
                description=desc,
                temperature_c=temp,
                cooling_multiplier=cool_m,
                solar_multiplier=sol_m,
                grid_capacity_multiplier=grid_m,
                ev_demand_multiplier=ev_m,
                is_active=active
            )
            db.add(sc)

        db.commit()
        print("Database successfully seeded with realistic smart campus operational data!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    from backend.database.init_db import init_database
    init_database()
    seed_database()
