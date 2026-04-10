"""Utility functions for Weather Agent."""

import time
from datetime import datetime
from typing import Dict
from typing import Optional


def format_temperature(temp: float, units: str = "metric") -> str:
    """Format temperature with unit symbol.

    Args:
        temp: Temperature value
        units: Unit system (metric/imperial)

    Returns:
        Formatted temperature string (e.g., "22°C")
    """
    symbol = "°C" if units == "metric" else "°F"
    return f"{temp:.1f}{symbol}"


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5 / 9


def kmh_to_mph(kmh: float) -> float:
    """Convert km/h to mph."""
    return kmh * 0.621371


def mph_to_kmh(mph: float) -> float:
    """Convert mph to km/h."""
    return mph * 1.60934


def hpa_to_inhg(hpa: float) -> float:
    """Convert hPa to inHg."""
    return hpa * 0.02953


def inhg_to_hpa(inhg: float) -> float:
    """Convert inHg to hPa."""
    return inhg * 33.8639


def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between units.

    Args:
        value: Value to convert
        from_unit: Source unit
        to_unit: Target unit

    Returns:
        Converted value
    """
    conversions = {
        ("celsius", "fahrenheit"): celsius_to_fahrenheit,
        ("fahrenheit", "celsius"): fahrenheit_to_celsius,
        ("kmh", "mph"): kmh_to_mph,
        ("mph", "kmh"): mph_to_kmh,
        ("hpa", "inhg"): hpa_to_inhg,
        ("inhg", "hpa"): inhg_to_hpa,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        return conversions[key](value)
    elif from_unit == to_unit:
        return value
    else:
        raise ValueError(f"Unsupported conversion: {from_unit} to {to_unit}")


def sanitize_city_input(city: str) -> str:
    """Sanitize city input to prevent injection attacks.

    Args:
        city: Raw city input

    Returns:
        Sanitized city name

    Raises:
        ValueError: If input is empty or too long after sanitization
    """
    import re

    if not city or not city.strip():
        raise ValueError("City name cannot be empty")

    # Remove potentially dangerous characters but allow common city name characters
    # Keep letters, numbers, spaces, and common punctuation used in city names
    sanitized = re.sub(r"[^\w\s,\-\.'()&\u00C0-\u017F]", "", city)

    # Remove excessive whitespace
    sanitized = re.sub(r"\s+", " ", sanitized).strip()

    # Check length constraints
    if len(sanitized) < 2:
        raise ValueError("City name must be at least 2 characters long")
    if len(sanitized) > 100:
        sanitized = sanitized[:100]  # Truncate long names

    # Check for obviously malicious patterns (HTML/script injection)
    malicious_patterns = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",
        r"<style",
        r"alert\s*\(",
        r"eval\s*\(",
        r"document\.",
        r"window\.",
    ]

    for pattern in malicious_patterns:
        if re.search(pattern, sanitized, re.IGNORECASE):
            raise ValueError("Invalid city name format")

    return sanitized


def format_wind_direction(degrees: Optional[int]) -> str:
    """Convert wind direction degrees to cardinal direction.

    Args:
        degrees: Wind direction in degrees

    Returns:
        Cardinal direction (e.g., "N", "NE", "SW")
    """
    if degrees is None:
        return "N/A"

    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    index = round(degrees / 22.5) % 16
    return directions[index]


def format_timestamp(timestamp: int) -> datetime:
    """Convert Unix timestamp to datetime.

    Args:
        timestamp: Unix timestamp

    Returns:
        datetime object
    """
    return datetime.fromtimestamp(timestamp)


def format_time(dt: datetime) -> str:
    """Format datetime as time string.

    Args:
        dt: datetime object

    Returns:
        Formatted time string (e.g., "06:30 AM")
    """
    return dt.strftime("%I:%M %p")


def get_clothing_recommendation(
    temp: float, condition: str, units: str = "metric"
) -> str:
    """Get clothing recommendation based on weather.

    Args:
        temp: Temperature
        condition: Weather condition
        units: Unit system

    Returns:
        Clothing recommendation
    """
    temp_f = temp if units == "fahrenheit" else celsius_to_fahrenheit(temp)

    if temp_f < 32:
        return "Bundle up! Heavy winter coat, gloves, scarf, and hat recommended."
    elif temp_f < 50:
        return "Wear a warm coat and layers."
    elif temp_f < 65:
        return "A light jacket or sweater is recommended."
    elif temp_f < 80:
        return "Perfect weather for light clothing."
    else:
        return "Stay cool with light, breathable fabrics."


def get_activity_recommendation(condition: str, wind_speed: float) -> str:
    """Get activity recommendation based on weather.

    Args:
        condition: Weather condition
        wind_speed: Wind speed in m/s

    Returns:
        Activity recommendation
    """
    condition_lower = condition.lower()

    if "rain" in condition_lower or "thunder" in condition_lower:
        return "Indoor activities recommended today."
    elif "snow" in condition_lower:
        return "Great for skiing or building a snowman!"
    elif "wind" in condition_lower or wind_speed > 10:
        return "Windy conditions - maybe avoid cycling or sailing."
    elif "clear" in condition_lower or "sun" in condition_lower:
        return "Perfect for outdoor activities and sightseeing!"
    else:
        return "Check local conditions for outdoor plans."


def format_weather_response(data: dict, units: str = "metric") -> str:
    """Format weather data as readable string.

    Args:
        data: Weather data dictionary
        units: Unit system

    Returns:
        Formatted weather response
    """
    main = data.get("main", {})
    weather = data.get("weather", [{}])[0] if data.get("weather") else {}
    wind = data.get("wind", {})

    temp = main.get("temp", 0)
    feels_like = main.get("feels_like", 0)
    humidity = main.get("humidity", 0)
    condition = weather.get("description", "Unknown")
    wind_speed = wind.get("speed", 0)

    temp_str = format_temperature(temp, units)
    feels_str = format_temperature(feels_like, units)

    return (
        f"Weather in {data.get('name', 'Unknown')}: "
        f"{condition}. Temperature: {temp_str}, "
        f"Feels like: {feels_str}. Humidity: {humidity}%. "
        f"Wind: {wind_speed} m/s"
    )


class SimpleRateLimiter:
    """Simple rate limiter for API requests."""

    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, list] = {}

    def is_allowed(self, key: str = "default") -> bool:
        """Check if request is allowed.

        Args:
            key: Identifier for the rate limit (e.g., IP address, user ID)

        Returns:
            True if request is allowed, False if rate limited
        """
        current_time = time.time()

        if key not in self.requests:
            self.requests[key] = []

        # Clean old requests outside the time window
        self.requests[key] = [
            req_time
            for req_time in self.requests[key]
            if current_time - req_time < self.time_window
        ]

        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(current_time)
            return True

        return False

    def get_remaining_requests(self, key: str = "default") -> int:
        """Get remaining requests allowed in current window.

        Args:
            key: Identifier for the rate limit

        Returns:
            Number of remaining requests
        """
        current_time = time.time()

        if key not in self.requests:
            return self.max_requests

        # Clean old requests
        valid_requests = [
            req_time
            for req_time in self.requests[key]
            if current_time - req_time < self.time_window
        ]

        return max(0, self.max_requests - len(valid_requests))
