"""Custom exceptions for Weather Agent."""

from typing import Optional


class WeatherAgentError(Exception):
    """Base exception for Weather Agent."""

    def __init__(self, message: str, user_message: Optional[str] = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(message)


class WeatherAPIError(WeatherAgentError):
    """Exception raised when weather API request fails."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code

        # User-friendly messages based on status code
        if status_code == 401:
            user_message = (
                "Weather service authentication failed. Please check your API key."
            )
        elif status_code == 404:
            user_message = "City not found. Please check the spelling and try again."
        elif status_code == 429:
            user_message = "Too many requests. Please wait a moment and try again."
        elif status_code and status_code >= 500:
            user_message = (
                "Weather service is temporarily unavailable. Please try again later."
            )
        else:
            user_message = "Unable to fetch weather data. Please try again."

        super().__init__(message, user_message)


class InvalidCityError(WeatherAgentError):
    """Exception raised when city is not found."""

    def __init__(self, city: str):
        self.city = city
        self.message = f"City not found: {city}"
        user_message = f"Sorry, I couldn't find weather information for '{city}'. Please check the spelling or try a nearby city."
        super().__init__(self.message, user_message)


class APIKeyError(WeatherAgentError):
    """Exception raised when API key is missing or invalid."""

    def __init__(self, provider: str):
        self.provider = provider
        self.message = f"Missing or invalid API key for {provider}"
        user_message = f"AI assistant service ({provider}) is not properly configured. Please contact support."
        super().__init__(self.message, user_message)


class RateLimitError(WeatherAgentError):
    """Exception raised when API rate limit is exceeded."""

    def __init__(self, message: str = "API rate limit exceeded"):
        self.message = message
        user_message = "I'm receiving too many requests right now. Please wait a minute and try again."
        super().__init__(message, user_message)


class ConfigurationError(WeatherAgentError):
    """Exception raised for configuration issues."""

    def __init__(self, message: str):
        user_message = (
            "The weather service is not properly configured. Please contact support."
        )
        super().__init__(message, user_message)


class NetworkError(WeatherAgentError):
    """Exception raised for network-related issues."""

    def __init__(self, message: str):
        self.message = message
        user_message = "I'm having trouble connecting to the weather service. Please check your internet connection and try again."
        super().__init__(message, user_message)
