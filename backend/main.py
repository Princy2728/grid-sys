from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "gridwise-backend"
    }
