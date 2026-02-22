"""Risk assessment API routes."""

from fastapi import APIRouter, HTTPException
from app.models.schemas import AddressRequest, RiskAssessment
from app.services import noaa_service, weather_service, elevation_service
from app.engine.risk_engine import calculate_risk

router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.post("/assess", response_model=RiskAssessment)
async def assess_risk(request: AddressRequest):
    """
    Assess flood risk for a specific address/location.

    Combines real-time tide data, weather forecast, and ground elevation
    to compute a composite risk score.
    """
    # Validate coordinates are roughly in Norfolk area
    if not (36.7 <= request.latitude <= 37.1 and -76.5 <= request.longitude <= -76.1):
        raise HTTPException(
            status_code=400,
            detail="Coordinates must be within the Norfolk, VA area.",
        )

    # Fetch all data sources concurrently
    import asyncio

    tide_data, weather_data, elevation_data = await asyncio.gather(
        noaa_service.get_tide_data(),
        weather_service.get_weather_data(),
        elevation_service.get_elevation(request.latitude, request.longitude),
    )

    # Calculate risk score
    risk = calculate_risk(tide_data, weather_data, elevation_data)

    return RiskAssessment(
        address=request.address,
        latitude=request.latitude,
        longitude=request.longitude,
        risk=risk,
        tide=tide_data,
        weather=weather_data,
        elevation=elevation_data,
    )


@router.get("/sample")
async def sample_locations():
    """Return sample Norfolk locations for quick testing."""
    return {
        "locations": [
            {
                "name": "Ghent / The Hague",
                "address": "Ghent, Norfolk, VA",
                "latitude": 36.8695,
                "longitude": -76.2960,
                "note": "Historically flood-prone neighborhood",
            },
            {
                "name": "Larchmont",
                "address": "Larchmont, Norfolk, VA",
                "latitude": 36.8760,
                "longitude": -76.2890,
                "note": "Low-lying residential area near Lafayette River",
            },
            {
                "name": "Downtown Norfolk",
                "address": "Downtown Norfolk, VA",
                "latitude": 36.8468,
                "longitude": -76.2852,
                "note": "Waterfront area near Town Point Park",
            },
            {
                "name": "Ocean View",
                "address": "Ocean View, Norfolk, VA",
                "latitude": 36.9260,
                "longitude": -76.2530,
                "note": "Chesapeake Bay waterfront community",
            },
            {
                "name": "757 Startup Studios (Hackathon Venue)",
                "address": "Assembly, Norfolk, VA",
                "latitude": 36.8562,
                "longitude": -76.2590,
                "note": "The Assembly campus",
            },
        ]
    }
