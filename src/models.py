"""Data models for Weather Agent."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class WeatherCondition(BaseModel):
    """Weather condition details."""

    main: str = Field(..., description="Main condition (Clear, Rain, etc.)")
    description: str = Field(..., description="Detailed description")
    icon: str = Field(..., description="Weather icon code")


class WeatherData(BaseModel):
    """Current weather data model."""

    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country code")
    temperature: float = Field(..., description="Current temperature")
    feels_like: float = Field(..., description="Feels like temperature")
    temp_min: float = Field(..., description="Minimum temperature")
    temp_max: float = Field(..., description="Maximum temperature")
    humidity: int = Field(..., description="Humidity percentage")
    pressure: int = Field(..., description="Pressure in hPa")
    wind_speed: float = Field(..., description="Wind speed")
    wind_direction: Optional[int] = Field(None, description="Wind direction in degrees")
    clouds: int = Field(..., description="Cloudiness percentage")
    visibility: Optional[int] = Field(None, description="Visibility in meters")
    condition: WeatherCondition
    timestamp: datetime = Field(default_factory=datetime.now)
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city": "Toronto",
                "country": "CA",
                "temperature": 22.5,
                "feels_like": 21.8,
                "temp_min": 20.0,
                "temp_max": 25.0,
                "humidity": 65,
                "pressure": 1013,
                "wind_speed": 3.5,
                "wind_direction": 180,
                "clouds": 20,
                "visibility": 10000,
                "condition": {
                    "main": "Clear",
                    "description": "clear sky",
                    "icon": "01d",
                },
            }
        }
    )


class ForecastDay(BaseModel):
    """Forecast for a single day."""

    date: datetime
    temp_min: float
    temp_max: float
    humidity: int
    condition: WeatherCondition
    precipitation_probability: Optional[float] = None


class ForecastData(BaseModel):
    """5-day weather forecast data."""

    city: str
    country: str
    forecasts: List[ForecastDay]


class GeocodingData(BaseModel):
    """Geocoding response data."""

    city: str
    country: str
    latitude: float
    longitude: float
    state: Optional[str] = None


class WeatherAlert(BaseModel):
    """Weather alert data."""

    event: str
    headline: str
    description: str
    severity: str
    start: datetime
    end: datetime


class UserPreferences(BaseModel):
    """User preferences model."""

    default_units: str = Field(
        default="metric", description="Default temperature units"
    )
    default_location: Optional[str] = Field(None, description="Default location")
    output_format: str = Field(default="plain", description="Output format")
    notifications_enabled: bool = Field(default=True)


class AgentResponse(BaseModel):
    """Agent response model."""

    message: str
    tool_used: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[str] = None
