# GRIDWISE AI – Predictive Smart Grid & Urban Resource Allocation Controller

**Competition Track**: Track 2 – Climate, Resource Infrastructure & Global Supply Resilience  
**Project Name**: GRIDWISE AI  
**Deployment**: Local-First Lightweight Decision Support Application (Zero Paid External API Dependencies)

---

## 1. Overview

**GRIDWISE AI** is a smart grid and urban resource allocation controller designed to solve electricity shortages, peak demand spikes, solar generation volatility, and simultaneous EV charging bottlenecks during heatwaves.

Built initially for a simulated smart campus environment (Metro Innovation Smart Campus), GRIDWISE AI combines:
- **Real-time Energy & Solar Monitoring**: High-resolution tracking of building baselines, solar PV arrays, and substation headroom.
- **Predictive Demand Forecasting**: Lightweight machine learning (Ridge autoregressive ensemble) predicting hourly loads with 95% confidence bands and peak alert detection.
- **Deterministic Priority Resource Allocation**: 5-tier constrained priority scheduling guaranteeing that total allocated power never exceeds safe physical capacity.
- **Complete EV Fleet Management**: Vehicle registration, charging station tracking, priority queuing, and automated peak-tariff deferrals.
- **Heatwave & Stress Simulation Lab**: Interactive multi-slider scenario modeling (15–48°C, HVAC surges, solar degradation, substation outages) with before-and-after audit comparisons.
- **Explainable Recommendation Assistant**: Transparent natural language explanations and peak-shaving directives without requiring paid external LLM APIs.

---

## 2. Technology Stack

- **Frontend**: React.js 18, Vite 5, Tailwind CSS, Recharts, Lucide React
- **Backend**: Python 3.14, FastAPI, Uvicorn, SQLAlchemy, Pydantic v2
- **Database**: SQLite (`gridwise.db`)
- **AI / ML & Modeling**: Scikit-Learn, Pandas, NumPy, Scipy
- **Testing**: Pytest 9.2

---

## 3. Quick Start & Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ (tested on Node 24)
- npm or pnpm

### Automated 1-Click Launch (Windows)
Double-click `start.bat` or run in terminal:
```cmd
.\start.bat
```

### Automated Launch (Linux / macOS)
```bash
chmod +x start.sh
./start.sh
```

### Manual Step-by-Step Launch

1. **Activate Python Virtual Environment & Install Dependencies**:
   ```bash
   # Windows
   .\.venv\Scripts\activate
   pip install -r backend\requirements.txt

   # Linux/macOS
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

2. **Initialize Database & Seed Demonstration Data** (automatically done on first backend startup, or run manually):
   ```bash
   python -m backend.database.seed_data
   ```

3. **Start FastAPI Backend**:
   ```bash
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```

4. **Start Vite Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the Application**:
   - **Dashboard UI**: [http://localhost:3000](http://localhost:3000)
   - **Interactive API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 4. Key Application Pages

| # | Page Name | Primary Features |
| :--- | :--- | :--- |
| **1** | **Overview Dashboard** | KPI cards (Demand, Solar, Grid, EV load), 24h AreaChart, headroom gauge, active alerts. |
| **2** | **EV Management** | Charging station network grid, active charging queue, registered fleet table, Add EV and Enqueue Request modals. |
| **3** | **Energy Intelligence** | 24-hour Ridge ML forecast with 95% confidence bands, solar physics telemetry, anomaly surveillance. |
| **4** | **Smart Allocation** | 5-tier hierarchical matrix, supply vs demand gauge, zero-deficit constraint, explainable dispatch rationale. |
| **5** | **Simulation Lab** | 5 scenario presets (Heatwave, Solar Drop, Substation Trip, EV Surge), 5 interactive sliders, before & after audit, AI recommendations. |
| **6** | **Alerts & Reports** | Filterable incident stream, severity badges (Critical, Warning, Info), one-click resolution, printable report audit. |
| **7** | **Settings** | Substation rating, PV array capacity, BESS buffer, critical ratio, and alert thresholds with reset to defaults. |

---

## 5. Verification & Testing

To execute the automated test suite:
```bash
.\.venv\Scripts\python -m pytest tests\test_allocation.py tests\test_services.py -v
```

To verify the frontend production build:
```bash
npm run build --prefix frontend
```

---

## 6. License & Attribution

Developed for Track 2 – Climate, Resource Infrastructure & Global Supply Resilience.  
GRIDWISE AI is released under the MIT Open Source License.
