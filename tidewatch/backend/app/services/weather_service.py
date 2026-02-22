"""National Weather Service API client for Norfolk, VA area."""

import re
import httpx
from typing import Optional
from cachetools import TTLCache

from app.config import settings
from app.models.schemas import WeatherPeriod, WeatherData

# Cache weather data for 30 minutes
_weather_cache: TTLCache = TTLCache(maxsize=10, ttl=1800)

NWS_HEADERS = {
    "User-Agent": "(TideWatch, tidewatch@example.com)",
    "Accept": "application/geo+json",
}


def _parse_wind_speed(wind_str: str) -> float:
    """Extract numeric wind speed from strings like '15 mph' or '10 to 20 mph'."""
    numbers = re.findall(r"\d+", wind_str)
    if numbers:
        return max(float(n) for n in numbers)
    return 0.0


def _parse_precip_chance(period_data: dict) -> int:
    """Extract precipitation probability from forecast period."""
    prob = period_data.get("probabilityOfPrecipitation", {})
    if prob and prob.get("value") is not None:
        return int(prob["value"])
    return 0


async def get_forecast() -> Optional[WeatherData]:
    """Fetch weather forecast from NWS for Norfolk grid point."""
    cache_key = "nws_forecast"
    if cache_key in _weather_cache:
        return _weather_cache[cache_key]

    url = f"{settings.nws_base_url}/gridpoints/{settings.nws_office}/{settings.nws_grid_x},{settings.nws_grid_y}/forecast"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=NWS_HEADERS)
            resp.raise_for_status()
            data = resp.json()

        periods = []
        max_precip = 0
        max_wind = 0.0
        wind_dir = ""

        for p in data.get("properties", {}).get("periods", [])[:6]:
            precip = _parse_precip_chance(p)
            wind = _parse_wind_speed(p.get("windSpeed", "0 mph"))

            period = WeatherPeriod(
                name=p.get("name", ""),
                temperature=p.get("temperature", 0),
                temperature_unit=p.get("temperatureUnit", "F"),
                wind_speed=p.get("windSpeed", ""),
                wind_direction=p.get("windDirection", ""),
                short_forecast=p.get("shortForecast", ""),
                detailed_forecast=p.get("detailedForecast", ""),
                precipitation_chance=precip,
            )
            periods.append(period)

            if precip > max_precip:
                max_precip = precip
            if wind > max_wind:
                max_wind = wind
                wind_dir = p.get("windDirection", "")

        # Estimate precipitation in inches from probability
        # Rough heuristic: 80%+ chance ≈ 1-2in, 50-80% ≈ 0.5-1in, etc.
        precip_estimate = 0.0
        if max_precip >= 80:
            precip_estimate = 1.5
        elif max_precip >= 60:
            precip_estimate = 1.0
        elif max_precip >= 40:
            precip_estimate = 0.5
        elif max_precip >= 20:
            precip_estimate = 0.2

        weather = WeatherData(
            periods=periods,
            precipitation_forecast_in=precip_estimate,
            wind_speed_mph=max_wind,
            wind_direction=wind_dir,
        )
        _weather_cache[cache_key] = weather
        return weather

    except Exception as e:
        print(f"[NWS] Error fetching forecast: {e}")
        return None


async def get_weather_data() -> WeatherData:
    """Get weather data with fallback defaults."""
    result = await get_forecast()
    if result is None:
        return WeatherData()
    return result
