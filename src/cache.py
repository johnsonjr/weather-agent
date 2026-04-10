"""Caching layer for Weather Agent."""

import logging
from typing import Optional, Any, Dict
from cachetools import TTLCache

from .config import get_config


logger = logging.getLogger(__name__)


class WeatherCache:
    """Caching layer for weather data."""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize the cache.

        Args:
            config: Configuration dictionary
        """
        self.config = config or get_config()

        weather_ttl = self.config.get("cache.weather_ttl", 300)
        geocode_ttl = self.config.get("cache.geocode_ttl", 86400)
        max_size = self.config.get("cache.max_size", 100)

        self.weather_cache: TTLCache = TTLCache(maxsize=max_size, ttl=weather_ttl)
        self.geocode_cache: TTLCache = TTLCache(maxsize=max_size * 2, ttl=geocode_ttl)
        self.forecast_cache: TTLCache = TTLCache(maxsize=max_size, ttl=weather_ttl)

        self.enabled = self.config.get("cache.enabled", True)

        self.stats = {
            "weather_hits": 0,
            "weather_misses": 0,
            "forecast_hits": 0,
            "forecast_misses": 0,
            "geocode_hits": 0,
            "geocode_misses": 0,
        }

    def get_weather(self, city: str, units: str = "metric") -> Optional[Dict]:
        """Get cached weather data.

        Args:
            city: City name
            units: Temperature units

        Returns:
            Cached data or None
        """
        if not self.enabled:
            return None

        key = self._make_key(city, units)

        if key in self.weather_cache:
            logger.debug(f"Weather cache HIT for {key}")
            self.stats["weather_hits"] += 1
            return self.weather_cache[key]

        logger.debug(f"Weather cache MISS for {key}")
        self.stats["weather_misses"] += 1
        return None

    def set_weather(self, city: str, units: str, data: Dict) -> None:
        """Set weather data in cache.

        Args:
            city: City name
            units: Temperature units
            data: Weather data to cache
        """
        if not self.enabled:
            return

        key = self._make_key(city, units)
        self.weather_cache[key] = data
        logger.debug(f"Cached weather data for {key}")

    def get_forecast(self, city: str, units: str, days: int) -> Optional[Dict]:
        """Get cached forecast data.

        Args:
            city: City name
            units: Temperature units
            days: Number of days

        Returns:
            Cached data or None
        """
        if not self.enabled:
            return None

        key = self._make_key(city, units, days)

        if key in self.forecast_cache:
            logger.debug(f"Forecast cache HIT for {key}")
            self.stats["forecast_hits"] += 1
            return self.forecast_cache[key]

        logger.debug(f"Forecast cache MISS for {key}")
        self.stats["forecast_misses"] += 1
        return None

    def set_forecast(self, city: str, units: str, days: int, data: Dict) -> None:
        """Set forecast data in cache.

        Args:
            city: City name
            units: Temperature units
            days: Number of days
            data: Forecast data to cache
        """
        if not self.enabled:
            return

        key = self._make_key(city, units, days)
        self.forecast_cache[key] = data
        logger.debug(f"Cached forecast data for {key}")

    def get_geocode(self, city: str) -> Optional[Dict]:
        """Get cached geocoding data.

        Args:
            city: City name

        Returns:
            Cached data or None
        """
        if not self.enabled:
            return None

        key = city.lower().strip()

        if key in self.geocode_cache:
            logger.debug(f"Geocode cache HIT for {key}")
            self.stats["geocode_hits"] += 1
            return self.geocode_cache[key]

        logger.debug(f"Geocode cache MISS for {key}")
        self.stats["geocode_misses"] += 1
        return None

    def set_geocode(self, city: str, data: Dict) -> None:
        """Set geocoding data in cache.

        Args:
            city: City name
            data: Geocoding data to cache
        """
        if not self.enabled:
            return

        key = city.lower().strip()
        self.geocode_cache[key] = data
        logger.debug(f"Cached geocode data for {key}")

    def _make_key(self, *args) -> str:
        """Create a cache key from arguments.

        Args:
            *args: Key components

        Returns:
            Cache key string
        """
        return ":".join(str(arg).lower().strip() for arg in args)

    def clear(self) -> None:
        """Clear all caches."""
        self.weather_cache.clear()
        self.forecast_cache.clear()
        self.geocode_cache.clear()
        logger.info("All caches cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary of cache stats
        """
        stats = self.stats.copy()

        weather_total = stats["weather_hits"] + stats["weather_misses"]
        forecast_total = stats["forecast_hits"] + stats["forecast_misses"]
        geocode_total = stats["geocode_hits"] + stats["geocode_misses"]

        stats["weather_hit_rate"] = int(
            stats["weather_hits"] / weather_total * 100 if weather_total > 0 else 0
        )
        stats["forecast_hit_rate"] = int(
            stats["forecast_hits"] / forecast_total * 100 if forecast_total > 0 else 0
        )
        stats["geocode_hit_rate"] = int(
            stats["geocode_hits"] / geocode_total * 100 if geocode_total > 0 else 0
        )

        stats["weather_cache_size"] = len(self.weather_cache)
        stats["forecast_cache_size"] = len(self.forecast_cache)
        stats["geocode_cache_size"] = len(self.geocode_cache)

        return stats

    def invalidate(self, city: str, units: str = "metric") -> None:
        """Invalidate cached data for a city.

        Args:
            city: City name
            units: Temperature units
        """
        key = self._make_key(city, units)

        if key in self.weather_cache:
            del self.weather_cache[key]
            logger.debug(f"Invalidated weather cache for {key}")

        if key in self.geocode_cache:
            del self.geocode_cache[key]
            logger.debug(f"Invalidated geocode cache for {key}")


_global_cache: Optional[WeatherCache] = None


def get_cache() -> WeatherCache:
    """Get global cache instance.

    Returns:
        WeatherCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = WeatherCache()
    return _global_cache
