"""TideWatch API - FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.schemas import HealthResponse
from app.routers import risk_router, tide_router, weather_router, alert_router

app = FastAPI(
    title="TideWatch API",
    description="Real-time flood risk assessment for Norfolk, VA",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
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
