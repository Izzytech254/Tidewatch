"""Tide data API routes."""

from fastapi import APIRouter
from app.services import noaa_service
from app.models.schemas import TideData

router = APIRouter(prefix="/api/tides", tags=["tides"])


@router.get("/current", response_model=TideData)
async def get_current_tides():
    """Get current water level and 48-hour tide predictions for Sewells Point."""
    return await noaa_service.get_tide_data()


@router.get("/predictions")
async def get_predictions(hours: int = 48):
    """Get tide predictions for the next N hours."""
    predictions = await noaa_service.get_tide_predictions(hours=min(hours, 168))
    return {
        "station": "Sewells Point, VA",
        "station_id": "8638610",
        "predictions": [
            {
                "timestamp": p.timestamp.isoformat(),
                "prediction_ft": p.prediction_ft,
            }
            for p in predictions
        ],
    }
