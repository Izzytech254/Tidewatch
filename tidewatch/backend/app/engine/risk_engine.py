"""
TideWatch Risk Scoring Engine

Computes a composite flood risk score (0-100) from four factors:
  R = w1*(T/Tmax) + w2*(1 - E/Eref) + w3*(P/Pthresh) + w4*S_wind

Where:
  T = current tidal water level (ft above MLLW)
  Tmax = historical max tide at station
  E = ground elevation at address (ft)
  Eref = reference "safe" elevation
  P = forecast precipitation (inches)
  Pthresh = precipitation threshold for concern
  S_wind = wind surge factor (0-1)
"""

from app.config import settings
from app.models.schemas import (
    RiskScore,
    RiskGrade,
    RiskFactors,
    TideData,
    WeatherData,
    ElevationData,
)

# Weights for each risk factor (must sum to 1.0)
W_TIDAL = 0.35
W_ELEVATION = 0.30
W_PRECIPITATION = 0.20
W_WIND = 0.15


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _compute_tidal_factor(tide: TideData) -> float:
    """Normalize current water level against historical max."""
    if tide.current is None:
        return 0.3  # Moderate default if data unavailable
    level = tide.current.water_level_ft
    return _clamp(level / settings.tidal_max_ft)


def _compute_elevation_factor(elevation: ElevationData) -> float:
    """Lower elevation = higher risk. Inverted and normalized."""
    elev = elevation.elevation_ft
    if elev <= 0:
        return 1.0  # At or below sea level = maximum risk
    factor = 1.0 - (elev / settings.reference_elevation_ft)
    return _clamp(factor)


def _compute_precipitation_factor(weather: WeatherData) -> float:
    """Normalize forecast precipitation against threshold."""
    precip = weather.precipitation_forecast_in
    return _clamp(precip / settings.precip_threshold_in)


def _compute_wind_surge_factor(weather: WeatherData) -> float:
    """
    Estimate wind surge contribution.
    Norfolk is most vulnerable to NE and E winds pushing water up the Chesapeake.
    Wind surge factor increases with speed and onshore direction.
    """
    wind_mph = weather.wind_speed_mph
    direction = weather.wind_direction.upper()

    # Base factor from wind speed (tropical storm force = 1.0)
    speed_factor = _clamp(wind_mph / 60.0)

    # Direction multiplier - NE/E winds are worst for Norfolk
    direction_multipliers = {
        "NE": 1.0,
        "ENE": 0.95,
        "E": 0.9,
        "N": 0.7,
        "NNE": 0.85,
        "ESE": 0.7,
        "SE": 0.5,
        "S": 0.3,
        "SSE": 0.4,
        "SSW": 0.2,
        "SW": 0.2,
        "W": 0.1,
        "NW": 0.3,
        "NNW": 0.4,
        "WNW": 0.15,
        "WSW": 0.15,
    }
    dir_mult = direction_multipliers.get(direction, 0.5)

    return _clamp(speed_factor * dir_mult)


def _score_to_grade(score: float) -> RiskGrade:
    if score <= 20:
        return RiskGrade.A
    elif score <= 40:
        return RiskGrade.B
    elif score <= 60:
        return RiskGrade.C
    elif score <= 80:
        return RiskGrade.D
    else:
        return RiskGrade.F


def _generate_summary(grade: RiskGrade, factors: RiskFactors) -> str:
    summaries = {
        RiskGrade.A: "Low flood risk. Conditions are favorable with no significant threats.",
        RiskGrade.B: "Minor flood risk. Some elevated conditions but no immediate concern.",
        RiskGrade.C: "Moderate flood risk. Pay attention to conditions — low-lying areas may see water.",
        RiskGrade.D: "High flood risk. Flooding likely in vulnerable areas. Take precautions.",
        RiskGrade.F: "Severe flood risk. Significant flooding expected. Protect property and consider evacuation routes.",
    }
    return summaries.get(grade, "Unable to determine risk level.")


def _generate_recommendations(grade: RiskGrade, factors: RiskFactors) -> list[str]:
    recs = []

    if grade in (RiskGrade.D, RiskGrade.F):
        recs.append("Move vehicles to higher ground")
        recs.append("Avoid driving through flooded streets")
        recs.append("Know your evacuation route")

    if factors.tidal_factor > 0.6:
        recs.append("High tide contributing to risk — avoid waterfront areas")

    if factors.precipitation_factor > 0.5:
        recs.append("Heavy rain expected — storm drains may back up in low areas")

    if factors.wind_surge_factor > 0.5:
        recs.append("Onshore winds increasing tidal surge risk")

    if factors.elevation_factor > 0.7:
        recs.append("Your location is in a low-elevation zone — stay alert during high water events")

    if grade == RiskGrade.A:
        recs.append("No action needed — conditions are normal")

    if grade == RiskGrade.B:
        recs.append("Monitor conditions if you're in a flood-prone area")

    return recs


def _estimate_confidence(tide: TideData, weather: WeatherData, elevation: ElevationData) -> float:
    """Estimate confidence based on data availability and quality."""
    confidence = 1.0

    if tide.current is None:
        confidence -= 0.25
    if len(weather.periods) == 0:
        confidence -= 0.20
    if elevation.source.startswith("default"):
        confidence -= 0.20

    # Elevation precision adds uncertainty for borderline cases
    if 3.0 <= elevation.elevation_ft <= 7.0:
        confidence -= 0.10  # Borderline elevations have more uncertainty

    return _clamp(confidence, 0.3, 1.0)


def calculate_risk(
    tide: TideData,
    weather: WeatherData,
    elevation: ElevationData,
) -> RiskScore:
    """
    Calculate composite flood risk score.

    R = w1*(T/Tmax) + w2*(1 - E/Eref) + w3*(P/Pthresh) + w4*S_wind
    """
    tidal_factor = _compute_tidal_factor(tide)
    elevation_factor = _compute_elevation_factor(elevation)
    precipitation_factor = _compute_precipitation_factor(weather)
    wind_surge_factor = _compute_wind_surge_factor(weather)

    # Weighted composite score (0-1) → scale to 0-100
    raw_score = (
        W_TIDAL * tidal_factor
        + W_ELEVATION * elevation_factor
        + W_PRECIPITATION * precipitation_factor
        + W_WIND * wind_surge_factor
    )
    score = round(_clamp(raw_score) * 100, 1)

    grade = _score_to_grade(score)
    factors = RiskFactors(
        tidal_factor=round(tidal_factor, 3),
        elevation_factor=round(elevation_factor, 3),
        precipitation_factor=round(precipitation_factor, 3),
        wind_surge_factor=round(wind_surge_factor, 3),
    )

    summary = _generate_summary(grade, factors)
    recommendations = _generate_recommendations(grade, factors)
    confidence = _estimate_confidence(tide, weather, elevation)

    return RiskScore(
        score=score,
        grade=grade,
        factors=factors,
        summary=summary,
        recommendations=recommendations,
        confidence=round(confidence, 2),
    )
