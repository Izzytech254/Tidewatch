from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "TideWatch"
    app_env: str = "development"
    cors_origins: str = "*"

    # NOAA - Sewells Point, Norfolk VA
    noaa_station_id: str = "8638610"
    noaa_base_url: str = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

    # National Weather Service
    nws_base_url: str = "https://api.weather.gov"
    # Norfolk, VA grid point
    nws_office: str = "AKQ"
    nws_grid_x: int = 89
    nws_grid_y: int = 76

    # USGS Elevation
    usgs_elevation_url: str = "https://epqs.nationalmap.gov/v1/json"

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # Norfolk reference values
    norfolk_lat: float = 36.8508
    norfolk_lon: float = -76.2859
    reference_elevation_ft: float = 12.0  # Reference "safe" elevation in feet
    tidal_max_ft: float = 7.5  # Historical max tide level at Sewells Point
    precip_threshold_in: float = 3.0  # Inches of rain that cause concern

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
