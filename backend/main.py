import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.config import settings
from backend.database.init_db import init_database
from backend.database.seed_data import seed_database
from backend.api.routes_energy import router as energy_router
from backend.api.routes_ev import router as ev_router
from backend.api.routes_allocation import router as allocation_router
from backend.api.routes_simulation import router as simulation_router
from backend.api.routes_alerts import router as alerts_router
from backend.api.routes_settings import router as settings_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables and initial data
    init_database()
    seed_database()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Predictive Smart Grid & Urban Resource Allocation Controller API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware (allowing development origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all route groups under /api
app.include_router(energy_router, prefix=settings.API_V1_STR)
app.include_router(ev_router, prefix=settings.API_V1_STR)
app.include_router(allocation_router, prefix=settings.API_V1_STR)
app.include_router(simulation_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "gridwise-backend"
    }

# Unified Full-Stack Static Frontend Serving (for Cloud Deployments like Render, Railway, Docker)
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
assets_dir = os.path.join(frontend_dist, "assets")

if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

if os.path.exists(frontend_dist):
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Do not intercept API or documentation routes
        if full_path.startswith("api") or full_path in ["docs", "redoc", "openapi.json", "health"]:
            return None
        target_file = os.path.join(frontend_dist, full_path)
        if full_path and os.path.exists(target_file) and os.path.isfile(target_file):
            return FileResponse(target_file)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "system": settings.PROJECT_NAME,
            "status": "online",
            "version": "1.0.0",
            "docs_url": "/docs"
        }
