"""Tests for caching layer."""

import pytest
from unittest.mock import Mock

from src.cache import WeatherCache, get_cache


class TestWeatherCache:
    """Test cases for WeatherCache class."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock config."""
        config = Mock()
        config.get.side_effect = lambda key, default=None: {
            'cache.enabled': True,
            'cache.weather_ttl': 300,
            'cache.geocode_ttl': 86400,
            'cache.max_size': 100
        }.get(key, default)
        return config
    
    @pytest.fixture
    def cache(self, mock_config):
        """Create cache instance."""
        return WeatherCache(config=mock_config)
    
    def test_init(self, mock_config):
        """Test cache initialization."""
        cache = WeatherCache(config=mock_config)
        assert cache.enabled is True
    
    def test_weather_cache_set_get(self, cache):
        """Test setting and getting weather cache."""
        test_data = {'temp': 22, 'humidity': 65}
        
        cache.set_weather('Toronto', 'metric', test_data)
        result = cache.get_weather('Toronto', 'metric')
        
        assert result == test_data
    
    def test_weather_cache_miss(self, cache):
        """Test cache miss."""
        result = cache.get_weather('Nonexistent', 'metric')
        assert result is None
    
    def test_cache_stats(self, cache):
        """Test cache statistics."""
        cache.get_weather('Toronto', 'metric')
        cache.set_weather('Toronto', 'metric', {'temp': 22})
        cache.get_weather('Toronto', 'metric')
        
        stats = cache.get_stats()
        
        assert 'weather_hits' in stats
        assert 'weather_misses' in stats
    
    def test_cache_clear(self, cache):
        """Test cache clearing."""
        cache.set_weather('Toronto', 'metric', {'temp': 22})
        cache.clear()
        
        result = cache.get_weather('Toronto', 'metric')
        assert result is None
    
    def test_cache_invalidate(self, cache):
        """Test cache invalidation."""
        cache.set_weather('Toronto', 'metric', {'temp': 22})
        cache.invalidate('Toronto', 'metric')
        
        result = cache.get_weather('Toronto', 'metric')
        assert result is None
    
    def test_geocode_cache(self, cache):
        """Test geocode caching."""
        test_data = {'lat': 43.65, 'lon': -79.38}
        
        cache.set_geocode('Toronto', test_data)
        result = cache.get_geocode('Toronto')
        
        assert result == test_data
    
    def test_forecast_cache(self, cache):
        """Test forecast caching."""
        test_data = {'forecasts': []}
        
        cache.set_forecast('Toronto', 'metric', 5, test_data)
        result = cache.get_forecast('Toronto', 'metric', 5)
        
        assert result == test_data


class TestGetCache:
    """Test get_cache function."""
    
    def test_global_cache(self):
        """Test global cache singleton."""
        cache1 = get_cache()
        cache2 = get_cache()
        
        assert cache1 is cache2
