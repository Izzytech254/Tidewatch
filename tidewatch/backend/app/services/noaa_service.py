"""NOAA Tides & Currents API client for Sewells Point station."""

import httpx
from datetime import datetime, timedelta
from typing import Optional
from cachetools import TTLCache

from app.config import settings
from app.models.schemas import TideReading, TideData

# Cache tide data for 6 minutes (NOAA updates every 6 min)
_tide_cache: TTLCache = TTLCache(maxsize=10, ttl=360)


async def get_current_water_level() -> Optional[TideReading]:
    """Fetch the latest observed water level from NOAA."""
    cache_key = "current_water_level"
    if cache_key in _tide_cache:
        return _tide_cache[cache_key]

    now = datetime.utcnow()
    params = {
        "begin_date": (now - timedelta(hours=1)).strftime("%Y%m%d %H:%M"),
        "end_date": now.strftime("%Y%m%d %H:%M"),
        "station": settings.noaa_station_id,
        "product": "water_level",
        "datum": "MLLW",
        "units": "english",
        "time_zone": "gmt",
        "format": "json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(settings.noaa_base_url, params=params)
            resp.raise_for_status()
            data = resp.json()

        if "data" in data and len(data["data"]) > 0:
            latest = data["data"][-1]
            reading = TideReading(
                timestamp=datetime.strptime(latest["t"], "%Y-%m-%d %H:%M"),
                water_level_ft=float(latest["v"]),
                prediction_ft=0.0,
                station_id=settings.noaa_station_id,
            )
            _tide_cache[cache_key] = reading
            return reading
    except Exception as e:
        print(f"[NOAA] Error fetching water level: {e}")

    return None


async def get_tide_predictions(hours: int = 48) -> list[TideReading]:
    """Fetch tide predictions for the next N hours."""
    cache_key = f"predictions_{hours}"
    if cache_key in _tide_cache:
        return _tide_cache[cache_key]

    now = datetime.utcnow()
    params = {
        "begin_date": now.strftime("%Y%m%d %H:%M"),
        "end_date": (now + timedelta(hours=hours)).strftime("%Y%m%d %H:%M"),
        "station": settings.noaa_station_id,
        "product": "predictions",
        "datum": "MLLW",
        "units": "english",
        "time_zone": "gmt",
        "interval": "h",
        "format": "json",
    }

    predictions = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(settings.noaa_base_url, params=params)
            resp.raise_for_status()
            data = resp.json()

        if "predictions" in data:
            for p in data["predictions"]:
                predictions.append(
                    TideReading(
                        timestamp=datetime.strptime(p["t"], "%Y-%m-%d %H:%M"),
                        water_level_ft=0.0,
                        prediction_ft=float(p["v"]),
                        station_id=settings.noaa_station_id,
                    )
                )
            _tide_cache[cache_key] = predictions
    except Exception as e:
        print(f"[NOAA] Error fetching predictions: {e}")

    return predictions


async def get_tide_data() -> TideData:
    """Get combined current water level and predictions."""
    current = await get_current_water_level()
    predictions = await get_tide_predictions(hours=48)

    return TideData(
        current=current,
        predictions=predictions,
        station_name="Sewells Point, VA",
    )
