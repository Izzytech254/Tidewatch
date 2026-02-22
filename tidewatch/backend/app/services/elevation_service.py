"""USGS National Elevation Dataset API client."""

import httpx
from cachetools import TTLCache

from app.models.schemas import ElevationData

# Cache elevation lookups for 24 hours (terrain doesn't change)
_elevation_cache: TTLCache = TTLCache(maxsize=500, ttl=86400)

USGS_ELEVATION_URL = "https://epqs.nationalmap.gov/v1/json"


async def get_elevation(latitude: float, longitude: float) -> ElevationData:
    """
    Get ground elevation for a lat/lon coordinate.
    Returns elevation in feet above sea level.
    """
    # Round to 5 decimal places for cache key (~1m precision)
    cache_key = f"{round(latitude, 5)},{round(longitude, 5)}"
    if cache_key in _elevation_cache:
        return _elevation_cache[cache_key]

    params = {
        "x": longitude,
        "y": latitude,
        "wkid": 4326,
        "units": "Feet",
        "includeDate": False,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(USGS_ELEVATION_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        elevation_ft = float(data.get("value", 0))

        result = ElevationData(
            latitude=latitude,
            longitude=longitude,
            elevation_ft=elevation_ft,
            source="USGS National Elevation Dataset",
        )
        _elevation_cache[cache_key] = result
        return result

    except Exception as e:
        print(f"[USGS] Error fetching elevation: {e}")
        # Return a conservative default (low elevation = higher risk)
        return ElevationData(
            latitude=latitude,
            longitude=longitude,
            elevation_ft=5.0,  # Conservative default for Norfolk
            source="default (API unavailable)",
        )
