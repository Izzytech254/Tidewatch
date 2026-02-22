"""TideWatch API - FastAPI application entry point."""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.schemas import HealthResponse
from app.routers import risk_router, tide_router, weather_router, alert_router


async def _warmup_caches():
    """Pre-fetch API data on startup so first user request is fast."""
    from app.services.noaa_service import get_current_water_level, get_tide_predictions
    from app.services.weather_service import get_weather_data
    from app.services.elevation_service import get_elevation

    try:
        await asyncio.gather(
            get_current_water_level(),
            get_tide_predictions(48),
            get_weather_data(),
            get_elevation(36.8508, -76.2859),   # Norfolk center
            return_exceptions=True,
        )
        print("[TideWatch] Cache warmup complete")
    except Exception as e:
        print(f"[TideWatch] Cache warmup partial: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: warm caches in background
    asyncio.create_task(_warmup_caches())
    yield
    # Shutdown: nothing to clean up


app = FastAPI(
    title="TideWatch API",
    description="Real-time flood risk assessment for Norfolk, VA",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(risk_router.router)
app.include_router(tide_router.router)
app.include_router(weather_router.router)
app.include_router(alert_router.router)


@app.get("/", response_model=HealthResponse)
async def health_check():
    return HealthResponse()


@app.get("/api/info")
async def api_info():
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "station": {
            "id": settings.noaa_station_id,
            "name": "Sewells Point, VA",
        },
        "coverage_area": "Norfolk, VA (36.7-37.1°N, 76.1-76.5°W)",
        "data_sources": [
            "NOAA Tides & Currents",
            "National Weather Service",
            "USGS National Elevation Dataset",
        ],
    }
