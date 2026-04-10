"""Weather tool implementation for Weather Agent."""

import time
import logging
from typing import Optional, Dict, Any, List
from collections import defaultdict
from datetime import datetime
import requests

from .config import get_config
from .cache import get_cache
from .models import (
    WeatherData,
    WeatherCondition,
    ForecastData,
    ForecastDay,
    GeocodingData,
)
from .exceptions import (
    WeatherAPIError,
    InvalidCityError,
    APIKeyError,
    RateLimitError,
    NetworkError,
)
from .utils import format_timestamp, sanitize_city_input


logger = logging.getLogger(__name__)


class WeatherTool:
    """Tool for fetching weather data from OpenWeatherMap API."""

    def __init__(self, api_key: Optional[str] = None, config=None):
        """Initialize WeatherTool.

        Args:
            api_key: OpenWeatherMap API key
            config: Configuration object
        """
        self.config = config or get_config()
        self.api_key = api_key or self.config.get_weather_api_key()
        self.base_url = self.config.get(
            "api.base_url", "https://api.openweathermap.org/data/2.5"
        )
        self.timeout = self.config.get("api.timeout_seconds", 10)
        self.max_retries = self.config.get("api.max_retries", 3)
        self.cache = get_cache()

    def _make_request(
        self, endpoint: str, params: Dict[str, Any], retries: int = 3
    ) -> Dict:
        """Make API request with retry logic.

        Args:
            endpoint: API endpoint
            params: Query parameters
            retries: Number of retries left

        Returns:
            API response as dictionary

        Raises:
            WeatherAPIError: If request fails
        """
        max_retries = self.max_retries if self.max_retries else 3

        if retries is None:
            retries = max_retries

        url = f"{self.base_url}/{endpoint}"
        params["appid"] = self.api_key

        try:
            logger.debug(f"Making request to {endpoint} with params: {params}")
            response = requests.get(url, params=params, timeout=self.timeout)

            if response.status_code == 401:
                raise APIKeyError("OpenWeatherMap")
            elif response.status_code == 404:
                raise InvalidCityError(params.get("q", "Unknown"))
            elif response.status_code == 429:
                raise RateLimitError("API rate limit exceeded")
            elif response.status_code >= 500:
                if retries > 0:
                    wait_time = (max_retries - retries + 1) * 2
                    logger.warning(
                        f"Server error, retrying in {wait_time}s. Retries left: {retries - 1}"
                    )
                    time.sleep(wait_time)
                    return self._make_request(endpoint, params, retries - 1)
                raise WeatherAPIError("Weather API server error", response.status_code)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise NetworkError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Connection error - check your internet")
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Request failed: {str(e)}")

    def get_weather(self, city: str, units: str = "metric") -> WeatherData:
        """Get current weather for a city.

        Args:
            city: City name
            units: Temperature units (metric/imperial)

        Returns:
            WeatherData object

        Raises:
            InvalidCityError: If city not found
            APIKeyError: If API key is invalid
            WeatherAPIError: For other API errors
        """
        city = sanitize_city_input(city)
        logger.info(f"Fetching weather for {city} with units={units}")

        # Check cache first
        cached_data = self.cache.get_weather(city, units)
        if cached_data:
            logger.info(f"Using cached weather data for {city}")
            data = cached_data
        else:
            params = {"q": city, "units": units}
            data = self._make_request("weather", params)
            # Cache the raw API response
            self.cache.set_weather(city, units, data)

        weather_data = data.get("weather", [{}])[0]
        main = data.get("main", {})
        wind = data.get("wind", {})
        sys = data.get("sys", {})
        clouds = data.get("clouds", {})

        condition = WeatherCondition(
            main=weather_data.get("main", ""),
            description=weather_data.get("description", ""),
            icon=weather_data.get("icon", ""),
        )

        sunrise = None
        sunset = None
        if sys.get("sunrise"):
            sunrise = format_timestamp(sys["sunrise"])
        if sys.get("sunset"):
            sunset = format_timestamp(sys["sunset"])

        return WeatherData(
            city=data.get("name", city),
            country=sys.get("country", ""),
            temperature=main.get("temp", 0),
            feels_like=main.get("feels_like", 0),
            temp_min=main.get("temp_min", 0),
            temp_max=main.get("temp_max", 0),
            humidity=main.get("humidity", 0),
            pressure=main.get("pressure", 0),
            wind_speed=wind.get("speed", 0),
            wind_direction=wind.get("deg"),
            clouds=clouds.get("all", 0),
            visibility=data.get("visibility"),
            condition=condition,
            timestamp=datetime.now(),
            sunrise=sunrise,
            sunset=sunset,
        )

    def get_forecast(
        self, city: str, units: str = "metric", days: int = 5
    ) -> ForecastData:
        """Get weather forecast for a city.

        Args:
            city: City name
            units: Temperature units (metric/imperial)
            days: Number of days (1-5)

        Returns:
            ForecastData object
        """
        city = sanitize_city_input(city)
        days = min(max(days, 1), 5)
        logger.info(f"Fetching {days}-day forecast for {city}")

        # Check cache first
        cached_data = self.cache.get_forecast(city, units, days)
        if cached_data:
            logger.info(f"Using cached forecast data for {city}")
            data = cached_data
        else:
            params = {"q": city, "units": units, "cnt": days * 8}
            data = self._make_request("forecast", params)
            # Cache the raw API response
            self.cache.set_forecast(city, units, days, data)

        city_info = data.get("city", {})
        forecasts = []

        daily_forecasts: Dict[Any, List[Dict[str, Any]]] = defaultdict(list)
        for item in data.get("list", []):
            dt = format_timestamp(item["dt"])
            date_key = dt.date()

            if date_key not in daily_forecasts:
                daily_forecasts[date_key] = []
            daily_forecasts[date_key].append(item)

        for date_key, items in list(daily_forecasts.items())[:days]:
            temps = [x["main"]["temp"] for x in items]
            humidity_sum = sum(x["main"]["humidity"] for x in items)

            condition_data = items[0].get("weather", [{}])[0]
            condition = WeatherCondition(
                main=condition_data.get("main", ""),
                description=condition_data.get("description", ""),
                icon=condition_data.get("icon", ""),
            )

            forecast_day = ForecastDay(
                date=date_key,
                temp_min=min(temps),
                temp_max=max(temps),
                humidity=int(humidity_sum / len(items)),
                condition=condition,
            )
            forecasts.append(forecast_day)

        return ForecastData(
            city=city_info.get("name", city),
            country=city_info.get("country", ""),
            forecasts=forecasts,
        )

    def geocode(self, city: str) -> List[GeocodingData]:
        """Get coordinates for a city.

        Args:
            city: City name

        Returns:
            List of GeocodingData objects
        """
        city = sanitize_city_input(city)
        logger.info(f"Geocoding {city}")

        # Check cache first
        cached_data = self.cache.get_geocode(city)
        if cached_data:
            logger.info(f"Using cached geocode data for {city}")
            data = cached_data
        else:
            params = {"q": city, "limit": 5}
            data = self._make_request("geo/1.0/direct", params)
            # Cache the raw API response
            self.cache.set_geocode(city, data)

        results = []
        for item in data:
            results.append(
                GeocodingData(
                    city=item.get("name", city),
                    country=item.get("country", ""),
                    latitude=item.get("lat", 0),
                    longitude=item.get("lon", 0),
                    state=item.get("state"),
                )
            )

        return results

    def reverse_geocode(self, lat: float, lon: float) -> Optional[GeocodingData]:
        """Get city name from coordinates.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            GeocodingData object or None
        """
        logger.info(f"Reverse geocoding {lat}, {lon}")

        params = {"lat": lat, "lon": lon}

        data = self._make_request("geo/1.0/reverse", params)

        if data:
            item = data[0]
            return GeocodingData(
                city=item.get("name", "Unknown"),
                country=item.get("country", ""),
                latitude=item.get("lat", lat),
                longitude=item.get("lon", lon),
                state=item.get("state"),
            )
        return None


def get_tool_schemas() -> List[Dict]:
    """Get tool schema definitions for LLM function calling.

    Returns:
        List of tool schemas
    """
    return [
        {
            "name": "get_weather",
            "description": "Retrieves current weather information for a specified city",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., 'Toronto', 'New York')",
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "Temperature units (metric=Celsius, imperial=Fahrenheit)",
                        "default": "metric",
                    },
                },
                "required": ["city"],
            },
        },
        {
            "name": "get_forecast",
            "description": "Retrieves weather forecast for a specified city",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "default": "metric",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days (1-5)",
                        "default": 5,
                    },
                },
                "required": ["city"],
            },
        },
        {
            "name": "geocode_location",
            "description": "Converts city name to coordinates or vice versa",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name to geocode"},
                    "lat": {
                        "type": "number",
                        "description": "Latitude for reverse geocoding",
                    },
                    "lon": {
                        "type": "number",
                        "description": "Longitude for reverse geocoding",
                    },
                },
            },
        },
    ]
