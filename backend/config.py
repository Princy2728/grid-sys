import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "GRIDWISE AI"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gridwise.db")
    DEBUG: bool = True
    DEFAULT_CAMPUS_NAME: str = "Metro Innovation Smart Campus"
    DEFAULT_GRID_CAPACITY_KW: float = 1200.0
    DEFAULT_SOLAR_CAPACITY_KW: float = 650.0
    DEFAULT_CRITICAL_PRIORITY_WEIGHT: float = 1.0

settings = Settings()
