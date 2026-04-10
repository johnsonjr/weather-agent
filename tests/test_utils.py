"""Tests for utility functions."""

import pytest
from src.utils import (
    format_temperature,
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    kmh_to_mph,
    mph_to_kmh,
    convert_units,
    sanitize_city_input,
    format_wind_direction,
    get_clothing_recommendation,
    get_activity_recommendation,
)


class TestTemperatureConversion:
    """Test temperature conversion functions."""

    def test_celsius_to_fahrenheit(self):
        """Test Celsius to Fahrenheit conversion."""
        assert celsius_to_fahrenheit(0) == 32
        assert celsius_to_fahrenheit(100) == 212
        assert abs(celsius_to_fahrenheit(37) - 98.6) < 0.1

    def test_fahrenheit_to_celsius(self):
        """Test Fahrenheit to Celsius conversion."""
        assert fahrenheit_to_celsius(32) == 0
        assert fahrenheit_to_celsius(212) == 100
        assert abs(fahrenheit_to_celsius(98.6) - 37) < 0.1

    def test_format_temperature_metric(self):
        """Test formatting temperature in Celsius."""
        result = format_temperature(22.5, "metric")
        assert "22.5" in result
        assert "°C" in result

    def test_format_temperature_imperial(self):
        """Test formatting temperature in Fahrenheit."""
        result = format_temperature(72.5, "imperial")
        assert "72.5" in result
        assert "°F" in result


class TestSpeedConversion:
    """Test speed conversion functions."""

    def test_kmh_to_mph(self):
        """Test km/h to mph conversion."""
        assert abs(kmh_to_mph(100) - 62.137) < 0.01

    def test_mph_to_kmh(self):
        """Test mph to km/h conversion."""
        assert abs(mph_to_kmh(60) - 96.56) < 0.01


class TestUnitConversion:
    """Test general unit conversion."""

    def test_celsius_to_fahrenheit_conversion(self):
        """Test convert_units for temperature."""
        result = convert_units(0, "celsius", "fahrenheit")
        assert result == 32

    def test_kmh_to_mph_conversion(self):
        """Test convert_units for speed."""
        result = convert_units(100, "kmh", "mph")
        assert abs(result - 62.137) < 0.01

    def test_same_unit_conversion(self):
        """Test conversion when units are the same."""
        result = convert_units(50, "celsius", "celsius")
        assert result == 50

    def test_unsupported_conversion(self):
        """Test unsupported conversion raises error."""
        with pytest.raises(ValueError):
            convert_units(50, "celsius", "kmh")


class TestSanitizeInput:
    """Test input sanitization."""

    def test_sanitize_city(self):
        """Test city name sanitization."""
        assert sanitize_city_input("Toronto") == "Toronto"
        assert sanitize_city_input("New York") == "New York"
        assert (
            sanitize_city_input("São Paulo") == "São Paulo"
        )  # Keep accented characters

    def test_sanitize_removes_special_chars(self):
        """Test special character removal."""
        assert sanitize_city_input("Tokyo<script>") == "Tokyoscript"
        assert sanitize_city_input("City;DROP TABLE") == "CityDROP TABLE"

    def test_sanitize_truncates_length(self):
        """Test input truncation."""
        long_name = "A" * 200
        result = sanitize_city_input(long_name)
        assert len(result) <= 100


class TestWindDirection:
    """Test wind direction formatting."""

    def test_cardinal_directions(self):
        """Test cardinal direction conversion."""
        assert format_wind_direction(0) == "N"
        assert format_wind_direction(90) == "E"
        assert format_wind_direction(180) == "S"
        assert format_wind_direction(270) == "W"

    def test_intermediate_directions(self):
        """Test intermediate direction conversion."""
        assert format_wind_direction(45) == "NE"
        assert format_wind_direction(135) == "SE"

    def test_none_direction(self):
        """Test None input handling."""
        assert format_wind_direction(None) == "N/A"


class TestClothingRecommendation:
    """Test clothing recommendations."""

    def test_cold_weather(self):
        """Test recommendation for cold weather."""
        result = get_clothing_recommendation(-5, "Clear", "metric")
        assert "Bundle" in result or "winter" in result.lower()

    def test_mild_weather(self):
        """Test recommendation for mild weather."""
        result = get_clothing_recommendation(20, "Clear", "metric")
        assert "jacket" in result.lower() or "light" in result.lower()

    def test_hot_weather(self):
        """Test recommendation for hot weather."""
        result = get_clothing_recommendation(35, "Clear", "metric")
        assert "light" in result.lower() or "cool" in result.lower()


class TestActivityRecommendation:
    """Test activity recommendations."""

    def test_rainy_weather(self):
        """Test recommendation for rainy weather."""
        result = get_activity_recommendation("rain", 3)
        assert "indoor" in result.lower()

    def test_clear_weather(self):
        """Test recommendation for clear weather."""
        result = get_activity_recommendation("clear", 2)
        assert "outdoor" in result.lower()

    def test_windy_weather(self):
        """Test recommendation for windy weather."""
        result = get_activity_recommendation("clear", 15)
        assert "wind" in result.lower()
