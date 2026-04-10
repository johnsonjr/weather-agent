"""Tests for Weather Tool."""

import pytest
from unittest.mock import Mock, patch

from src.tools import WeatherTool, get_tool_schemas
from src.models import WeatherData
from src.exceptions import (
    InvalidCityError
)


class TestWeatherTool:
    """Test cases for WeatherTool class."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock config."""
        config = Mock()
        config.get.side_effect = lambda key, default=None: {
            'api.base_url': 'https://api.openweathermap.org/data/2.5',
            'api.timeout_seconds': 10,
            'api.max_retries': 3
        }.get(key, default)
        config.get_weather_api_key.return_value = 'test_api_key'
        return config
    
    @pytest.fixture
    def weather_tool(self, mock_config):
        """Create WeatherTool instance."""
        return WeatherTool(api_key='test_api_key', config=mock_config)
    
    def test_init(self, mock_config):
        """Test WeatherTool initialization."""
        tool = WeatherTool(api_key='test_key', config=mock_config)
        assert tool.api_key == 'test_key'
        assert tool.base_url == 'https://api.openweathermap.org/data/2.5'
    
    def test_get_weather_success(self, weather_tool):
        """Test successful weather fetch."""
        mock_response = {
            'name': 'Toronto',
            'sys': {'country': 'CA', 'sunrise': 1700000000, 'sunset': 1700030000},
            'main': {
                'temp': 22.5,
                'feels_like': 21.0,
                'temp_min': 20.0,
                'temp_max': 25.0,
                'humidity': 65,
                'pressure': 1013
            },
            'weather': [{'main': 'Clear', 'description': 'clear sky', 'icon': '01d'}],
            'wind': {'speed': 3.5, 'deg': 180},
            'clouds': {'all': 20},
            'visibility': 10000
        }
        
        with patch.object(weather_tool, '_make_request', return_value=mock_response):
            result = weather_tool.get_weather('Toronto')
            
            assert isinstance(result, WeatherData)
            assert result.city == 'Toronto'
            assert result.country == 'CA'
            assert result.temperature == 22.5
    
    def test_get_weather_invalid_city(self, weather_tool):
        """Test handling of invalid city."""
        
        with patch.object(weather_tool, '_make_request') as mock_request:
            mock_request.side_effect = InvalidCityError('InvalidCity')
            
            with pytest.raises(InvalidCityError):
                weather_tool.get_weather('InvalidCity')
    
    def test_get_forecast(self, weather_tool):
        """Test forecast fetching."""
        mock_response = {
            'city': {'name': 'Toronto', 'country': 'CA'},
            'list': [
                {
                    'dt': 1700000000,
                    'main': {'temp': 20.0, 'humidity': 70},
                    'weather': [{'main': 'Clear', 'description': 'clear', 'icon': '01d'}]
                },
                {
                    'dt': 1700080000,
                    'main': {'temp': 22.0, 'humidity': 65},
                    'weather': [{'main': 'Clouds', 'description': 'cloudy', 'icon': '03d'}]
                }
            ]
        }
        
        with patch.object(weather_tool, '_make_request', return_value=mock_response):
            result = weather_tool.get_forecast('Toronto', days=2)
            
            assert result.city == 'Toronto'
            assert result.country == 'CA'
            assert len(result.forecasts) >= 1
    
    def test_geocode(self, weather_tool):
        """Test geocoding."""
        mock_response = [
            {'name': 'Toronto', 'country': 'CA', 'lat': 43.6532, 'lon': -79.3832, 'state': 'Ontario'}
        ]
        
        with patch.object(weather_tool, '_make_request', return_value=mock_response):
            result = weather_tool.geocode('Toronto')
            
            assert len(result) == 1
            assert result[0].city == 'Toronto'
            assert result[0].latitude == 43.6532


class TestToolSchemas:
    """Test tool schema definitions."""
    
    def test_get_tool_schemas(self):
        """Test tool schema generation."""
        schemas = get_tool_schemas()
        
        assert len(schemas) >= 3
        assert any(s['name'] == 'get_weather' for s in schemas)
        assert any(s['name'] == 'get_forecast' for s in schemas)
        assert any(s['name'] == 'geocode_location' for s in schemas)
    
    def test_weather_schema_structure(self):
        """Test get_weather schema structure."""
        schemas = get_tool_schemas()
        weather_schema = next(s for s in schemas if s['name'] == 'get_weather')
        
        assert 'description' in weather_schema
        assert 'input_schema' in weather_schema
        assert 'properties' in weather_schema['input_schema']
        assert 'city' in weather_schema['input_schema']['properties']
