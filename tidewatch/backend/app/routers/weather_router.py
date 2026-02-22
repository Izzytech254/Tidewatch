"""Weather data API routes."""

from fastapi import APIRouter
from app.services import weather_service

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/forecast")
async def get_forecast():
    """Get current weather forecast for Norfolk, VA area."""
    weather = await weather_service.get_weather_data()
    return {
        "precipitation_forecast_in": weather.precipitation_forecast_in,
        "wind_speed_mph": weather.wind_speed_mph,
        "wind_direction": weather.wind_direction,
        "periods": [
            {
                "name": p.name,
                "temperature": p.temperature,
                "wind_speed": p.wind_speed,
                "wind_direction": p.wind_direction,
                "short_forecast": p.short_forecast,
                "precipitation_chance": p.precipitation_chance,
            }
            for p in weather.periods
        ],
    }
