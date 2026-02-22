from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# --- Enums ---

class RiskGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


# --- Tide Models ---

class TideReading(BaseModel):
    timestamp: datetime
    water_level_ft: float
    prediction_ft: float
    station_id: str


class TideData(BaseModel):
    current: Optional[TideReading] = None
    predictions: List[TideReading] = []
    station_name: str = "Sewells Point, VA"


# --- Weather Models ---

class WeatherPeriod(BaseModel):
    name: str
    temperature: int
    temperature_unit: str = "F"
    wind_speed: str
    wind_direction: str
    short_forecast: str
    detailed_forecast: str
    precipitation_chance: int = 0


class WeatherData(BaseModel):
    periods: List[WeatherPeriod] = []
    precipitation_forecast_in: float = 0.0
    wind_speed_mph: float = 0.0
    wind_direction: str = ""


# --- Elevation Models ---

class ElevationData(BaseModel):
    latitude: float
    longitude: float
    elevation_ft: float
    source: str = "USGS"


# --- Risk Models ---

class RiskFactors(BaseModel):
    tidal_factor: float = Field(ge=0, le=1, description="Normalized tidal contribution")
    elevation_factor: float = Field(ge=0, le=1, description="Normalized elevation vulnerability")
    precipitation_factor: float = Field(ge=0, le=1, description="Normalized precipitation risk")
    wind_surge_factor: float = Field(ge=0, le=1, description="Normalized wind surge risk")


class RiskScore(BaseModel):
    score: float = Field(ge=0, le=100, description="Composite risk score 0-100")
    grade: RiskGrade
    factors: RiskFactors
    summary: str
    recommendations: List[str] = []
    confidence: float = Field(ge=0, le=1, default=0.7)


class RiskAssessment(BaseModel):
    address: str
    latitude: float
    longitude: float
    risk: RiskScore
    tide: Optional[TideData] = None
    weather: Optional[WeatherData] = None
    elevation: Optional[ElevationData] = None
    assessed_at: datetime = Field(default_factory=datetime.utcnow)


# --- Alert Models ---

class AlertSubscription(BaseModel):
    phone_number: str
    address: str
    latitude: float
    longitude: float
    threshold_grade: RiskGrade = RiskGrade.C  # Alert when risk >= this grade


class AlertNotification(BaseModel):
    subscription: AlertSubscription
    risk: RiskScore
    message: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)


# --- API Request/Response ---

class AddressRequest(BaseModel):
    address: str
    latitude: float
    longitude: float


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str = "TideWatch"
    version: str = "1.0.0"
