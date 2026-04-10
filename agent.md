# Weather Information Agent - Project Plan

## Project Overview
A simple AI agent that fetches real-time weather data for specified locations and provides intelligent, conversational responses about weather conditions, forecasts, and recommendations.

## Core Objectives
- Demonstrate basic agentic design patterns (perception, reasoning, action)
- Integrate external API tool calls (weather APIs)
- Maintain conversation context and memory
- Provide natural language weather insights

## Architecture

### Components
1. **Agent Core** - Main orchestration loop with LLM
2. **Weather Tool** - Function to fetch weather data from external API
3. **Memory Store** - Conversation history management
4. **Response Generator** - Natural language output formatting
5. **Configuration Manager** - Environment and settings management
6. **Cache Layer** - Response caching for performance
7. **CLI Interface** - Command-line user interaction

### Technology Stack
- **Language**: Python 3.10+
- **LLM Provider**: Anthropic Claude or OpenAI GPT
- **Weather API**: OpenWeatherMap API (free tier)
- **Dependencies**: 
  - `anthropic` or `openai`
  - `requests` or `httpx` (async HTTP)
  - `python-dotenv`
  - `pydantic` (data validation)
  - `click` or `argparse` (CLI)
  - `cachetools` (caching)
  - `pyyaml` (configuration)
  - `logging` (built-in)
  - `pytest` (testing)
  - `pytest-cov` (coverage)
  - `responses` or `aioresponses` (mocking)

## Data Models

### Weather Response Model
```python
from pydantic import BaseModel
from typing import Optional

class WeatherCondition(BaseModel):
    main: str
    description: str
    icon: str

class WeatherData(BaseModel):
    city: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    condition: WeatherCondition
    timestamp: Optional[str] = None
```

### User Preferences Model
```python
class UserPreferences(BaseModel):
    default_units: str = "metric"
    default_location: Optional[str] = None
    output_format: str = "plain"
    notifications_enabled: bool = True
```

## Environment Setup

### Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### requirements.txt Structure
```
anthropic>=0.18.0
requests>=2.31.0
python-dotenv>=1.0.0
pydantic>=2.0.0
click>=8.1.0
cachetools>=5.3.0
pyyaml>=6.0
pytest>=7.4.0
pytest-cov>=4.1.0
responses>=0.23.0
```

## Features

### MVP (Minimum Viable Product)
- [x] Current weather lookup by city name
- [x] Temperature, humidity, conditions
- [x] Multi-turn conversation support
- [x] Natural language responses

### Enhanced Features
- [ ] 5-day weather forecast
- [ ] Weather alerts and warnings
- [ ] Multiple location comparison
- [ ] Weather-based recommendations (clothing, activities)
- [ ] Unit conversion (Celsius/Fahrenheit)
- [ ] Location geocoding (coordinates to city)

### Enhanced Feature Details

#### 5-Day Weather Forecast
- **Endpoint**: `/forecast` 
- **Tool**: `get_forecast`
- **Features**: Daily summaries, hourly breakdowns, precipitation probability
- **UI**: Formatted table or ASCII chart output

#### Weather Alerts
- **Endpoint**: `/alerts` (via OneCall API)
- **Tool**: `get_alerts`
- **Severity Levels**: Extreme, Severe, Moderate, Minor
- **Features**: Push notifications, alert summary

#### Unit Conversion
- **Tool**: `convert_units`
- **Supports**: Celsius ↔ Fahrenheit, km/h ↔ mph, hPa ↔ inHg
- **Persistence**: Remember user preference in config

#### Geocoding
- **Tool**: `geocode_location`
- **Features**: City name → coordinates, coordinates → city name
- **Use Case**: Location-based weather without city name

## Implementation Steps

### Phase 1: Setup (30 minutes)
1. Create project directory structure
2. Set up virtual environment
3. Install dependencies
4. Obtain API keys:
   - OpenWeatherMap API key (free)
   - Anthropic/OpenAI API key
5. Create `.env` file for secrets

### Phase 2: Weather Tool (45 minutes)
1. Create `WeatherTool` class
2. Implement API call to OpenWeatherMap
3. Parse and structure response data
4. Add error handling (invalid city, API failures)
5. Test tool independently

### Phase 3: Agent Core (60 minutes)
1. Create `WeatherAgent` class
2. Implement conversation memory
3. Add tool schema definition
4. Build agentic loop (think → act → observe)
5. Handle tool use and responses

### Phase 4: Testing & Refinement (30 minutes)
1. Test various weather queries
2. Handle edge cases
3. Improve response quality
4. Add logging for debugging

### Phase 5: Configuration & Logging (20 minutes)
1. Create `config.py` for settings management
2. Implement YAML config file support
3. Set up structured logging with levels
4. Add file rotation for logs
5. Create debug mode toggle

### Phase 6: CLI Enhancement (25 minutes)
1. Design CLI with `click` or `argparse`
2. Implement interactive mode (REPL)
3. Add single-query mode
4. Support output formats (JSON, table, plain)
5. Add colored output support

### Phase 7: Caching (15 minutes)
1. Implement `cache.py` with TTL support
2. Cache weather responses (5-minute TTL)
3. Cache geocoding results (24-hour TTL)
4. Add cache invalidation commands
5. Monitor cache hit rate

## Project Structure

```
weather-agent/
├── .env                    # API keys (gitignored)
├── .gitignore
├── README.md
├── agent.md               # This file
├── requirements.txt       # Dependencies
├── config.yaml            # Configuration settings
├── pyproject.toml        # Project metadata (optional)
├── src/
│   ├── __init__.py
│   ├── agent.py           # Main agent class
│   ├── tools.py           # Weather tool implementation
│   ├── utils.py           # Helper functions
│   ├── config.py          # Configuration loader
│   ├── cache.py           # Caching layer
│   ├── cli.py             # CLI interface
│   ├── models.py          # Pydantic data models
│   └── exceptions.py      # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_weather.py    # Weather tool tests
│   ├── test_agent.py      # Agent tests
│   ├── test_tools.py      # Tool tests
│   ├── test_cache.py      # Cache tests
│   └── test_cli.py        # CLI tests
├── logs/                  # Log files directory
│   └── .gitkeep
└── main.py                # Entry point / CLI
```

## Async Support (Optional Enhancement)

For improved performance, consider using async/await:

```python
import httpx
import asyncio

class AsyncWeatherTool:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_weather(self, city: str, units: str = "metric"):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/weather",
                params={"q": city, "appid": self.api_key, "units": units}
            )
            return response.json()

# Usage
async def main():
    tool = AsyncWeatherTool(api_key)
    weather = await tool.get_weather("Toronto")
```

## Code Quality Standards

### Type Hints
```python
from typing import Optional, List, Dict, Any

def get_weather(city: str, units: str = "metric") -> Dict[str, Any]:
    """Fetch weather data for a city.
    
    Args:
        city: Name of the city
        units: Temperature units (metric/imperial)
    
    Returns:
        Dictionary containing weather data
    
    Raises:
        WeatherAPIError: If API request fails
    """
    pass
```

### Docstrings (Google Style)
```python
def format_temperature(temp: float, units: str) -> str:
    """Format temperature with unit symbol.
    
    Args:
        temp: Temperature value
        units: Unit system (metric/imperial)
    
    Returns:
        Formatted temperature string (e.g., "22°C")
    """
    symbol = "°C" if units == "metric" else "°F"
    return f"{temp:.1f}{symbol}"
```

### Code Organization
- Keep functions small and focused (< 50 lines)
- Use meaningful variable names
- Group related functions into modules
- Separate business logic from I/O operations

## API Integration

### OpenWeatherMap API
**Endpoint**: `https://api.openweathermap.org/data/2.5/weather`

**Parameters**:
- `q`: City name (e.g., "Toronto")
- `appid`: API key
- `units`: metric or imperial

**Response Structure**:
```json
{
  "weather": [{"main": "Clear", "description": "clear sky"}],
  "main": {
    "temp": 22.5,
    "feels_like": 21.8,
    "humidity": 65
  },
  "wind": {"speed": 3.5},
  "name": "Toronto"
}
```

### Forecast API
**Endpoint**: `https://api.openweathermap.org/data/2.5/forecast`

**Parameters**:
- `q`: City name
- `appid`: API key
- `units`: metric or imperial
- `cnt`: Number of timestamps (optional)

### OneCall API (Alerts)
**Endpoint**: `https://api.openweathermap.org/data/3.0/onecall`

**Parameters**:
- `lat`: Latitude
- `lon`: Longitude
- `appid`: API key
- `exclude`: Parts to exclude

## Tool Schema Definitions

### get_weather
```python
{
    "name": "get_weather",
    "description": "Retrieves current weather information for a specified city",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name (e.g., 'Toronto', 'New York')"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "description": "Temperature units (metric=Celsius, imperial=Fahrenheit)",
                "default": "metric"
            }
        },
        "required": ["city"]
    }
}
```

### get_forecast
```python
{
    "name": "get_forecast",
    "description": "Retrieves 5-day weather forecast for a specified city",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "default": "metric"
            },
            "days": {
                "type": "integer",
                "description": "Number of days (1-5)",
                "default": 5
            }
        },
        "required": ["city"]
    }
}
```

### get_alerts
```python
{
    "name": "get_alerts",
    "description": "Retrieves weather alerts for a specified location",
    "input_schema": {
        "type": "object",
        "properties": {
            "lat": {
                "type": "number",
                "description": "Latitude"
            },
            "lon": {
                "type": "number",
                "description": "Longitude"
            }
        },
        "required": ["lat", "lon"]
    }
}
```

### convert_units
```python
{
    "name": "convert_units",
    "description": "Converts temperature, speed, or pressure units",
    "input_schema": {
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "Value to convert"
            },
            "from_unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit", "kmh", "mph", "hpa", "inhg"]
            },
            "to_unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit", "kmh", "mph", "hpa", "inhg"]
            }
        },
        "required": ["value", "from_unit", "to_unit"]
    }
}
```

### geocode_location
```python
{
    "name": "geocode_location",
    "description": "Converts between city names and coordinates",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name to geocode"
            },
            "lat": {
                "type": "number",
                "description": "Latitude for reverse geocoding"
            },
            "lon": {
                "type": "number",
                "description": "Longitude for reverse geocoding"
            }
        }
    }
}
```

## Configuration Management

### config.yaml Structure
```yaml
app:
  name: "Weather Agent"
  version: "1.0.0"
  debug: false

api:
  weather_provider: "openweathermap"
  cache_ttl_seconds: 300
  timeout_seconds: 10
  max_retries: 3

llm:
  provider: "anthropic"  # or "openai"
  model: "claude-3-sonnet"
  max_tokens: 1024
  temperature: 0.7

cache:
  enabled: true
  weather_ttl: 300      # 5 minutes
  geocode_ttl: 86400    # 24 hours
  max_size: 100

logging:
  level: "INFO"
  file: "logs/weather_agent.log"
  max_bytes: 10485760   # 10MB
  backup_count: 5

cli:
  default_units: "metric"
  output_format: "table"  # table, json, plain
  color_output: true
```

### Environment Variables (.env)
```bash
OPENWEATHER_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
# OR
OPENAI_API_KEY=your_key_here
```

## Logging Strategy

### Log Levels
| Level | Use Case |
|-------|----------|
| DEBUG | Detailed API requests/responses, tool execution |
| INFO | Session start/end, user queries, cache hits |
| WARNING | API rate limits, degraded performance |
| ERROR | API failures, invalid inputs, exceptions |

### Log Format
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Implementation
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(config):
    logger = logging.getLogger('weather_agent')
    logger.setLevel(getattr(logging, config['logging']['level']))
    
    handler = RotatingFileHandler(
        config['logging']['file'],
        maxBytes=config['logging']['max_bytes'],
        backupCount=config['logging']['backup_count']
    )
    logger.addHandler(handler)
    return logger
```

## CLI Interface Design

### Commands
```bash
# Interactive mode
weather-agent

# Single query
weather-agent "What's the weather in Toronto?"

# With options
weather-agent "Weather in Paris" --units imperial --format json

# Forecast
weather-agent forecast Toronto --days 3

# Compare locations
weather-agent compare Toronto Vancouver

# Configure
weather-agent config set default_units imperial
weather-agent config get api.timeout_seconds
```

### CLI Options
| Option | Description |
|--------|-------------|
| `--units, -u` | Temperature units (metric/imperial) |
| `--format, -f` | Output format (table/json/plain) |
| `--debug, -d` | Enable debug logging |
| `--no-cache` | Disable caching |
| `--version, -v` | Show version |

## Caching Layer

### Cache Strategy
```python
from cachetools import TTLCache

class WeatherCache:
    def __init__(self):
        self.weather_cache = TTLCache(maxsize=100, ttl=300)  # 5 min
        self.geocode_cache = TTLCache(maxsize=200, ttl=86400)  # 24 hrs
    
    def get_weather(self, city: str, units: str):
        key = f"{city}:{units}"
        return self.weather_cache.get(key)
    
    def set_weather(self, city: str, units: str, data: dict):
        key = f"{city}:{units}"
        self.weather_cache[key] = data
```

### Cache Statistics
- Track hit/miss ratio
- Monitor cache size
- Log evictions

## Rate Limiting

### Implementation
```python
import time
from threading import Lock

class RateLimiter:
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.timestamps = []
        self.lock = Lock()
    
    def acquire(self):
        with self.lock:
            now = time.time()
            self.timestamps = [t for t in self.timestamps if t > now - self.period]
            if len(self.timestamps) >= self.calls:
                sleep_time = self.timestamps[0] - (now - self.period)
                time.sleep(sleep_time)
            self.timestamps.append(now)
```

### OpenWeatherMap Limits
- Free tier: 60 calls/minute
- Monitor usage with `X-RateLimit-Remaining` header

## Security Considerations

### API Key Protection
- Store in `.env` file (never commit)
- Use environment variables
- Mask in logs

### Input Sanitization
```python
def sanitize_city_input(city: str) -> str:
    # Remove special characters, limit length
    return re.sub(r'[^a-zA-Z\s,-]', '', city)[:100]
```

### Secure Error Messages
- Don't expose internal paths
- Don't leak API keys in errors
- Generic messages for users, detailed for logs

## Example Interactions

### Simple Query
**User**: "What's the weather in Toronto?"
**Agent**: Uses `get_weather` tool → Responds with current conditions

### Multi-turn Conversation
**User**: "What's the weather in Toronto?"
**Agent**: "It's currently 22°C with clear skies..."
**User**: "Should I bring an umbrella?"
**Agent**: (References previous query) "No need! The weather is clear with no rain expected."

### Comparison Query
**User**: "Compare weather in Toronto and Vancouver"
**Agent**: Calls `get_weather` twice → Provides comparative analysis

### Forecast Query
**User**: "What's the forecast for London this weekend?"
**Agent**: Uses `get_forecast` → Returns weekend summary

### Alert Query
**User**: "Any weather alerts for my location?"
**Agent**: Uses `geocode_location` + `get_alerts` → Returns active alerts

## Error Handling

### Scenarios to Handle
1. **Invalid city name**: Graceful error message with suggestions
2. **API rate limits**: Inform user, implement caching
3. **Network failures**: Retry logic with exponential backoff
4. **Missing API key**: Clear setup instructions
5. **Ambiguous locations**: Ask for clarification (e.g., "Paris, France" vs "Paris, Texas")

### API Error Codes
| Code | Meaning | Action |
|------|---------|--------|
| 401 | Invalid API key | Prompt user to check .env |
| 404 | City not found | Suggest similar cities |
| 429 | Rate limited | Enable caching, wait |
| 500+ | Server error | Retry with backoff |

### Retry Logic
```python
import time
from functools import wraps

def retry(max_attempts=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(backoff_factor ** attempt)
        return wrapper
    return decorator
```

## Success Metrics

### Technical
- Response time < 3 seconds
- API success rate > 95%
- Zero unhandled exceptions
- Cache hit rate > 40%

### User Experience
- Natural, conversational responses
- Accurate weather data
- Context-aware follow-up handling

## Testing Strategy

### Unit Tests
| Component | Tests |
|-----------|-------|
| WeatherTool | API parsing, error handling |
| Cache | Get/set, TTL expiration |
| Config | Load, validate, defaults |
| Utils | Unit conversion, sanitization |

### Integration Tests
| Component | Tests |
|-----------|-------|
| Agent | Full conversation flow |
| API | Real API calls (mocked) |
| CLI | Command parsing, output |

### End-to-End Tests
| Scenario | Validation |
|----------|------------|
| Weather query | Correct response format |
| Multi-turn | Context maintained |
| Error cases | Graceful degradation |
| Caching | Performance improvement |

### Test Commands
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_tools.py -v
```

## Future Enhancements

### Advanced Features
1. **Historical weather data** - Trends and patterns
2. **Weather alerts integration** - Severe weather warnings
3. **Voice interface** - Speech-to-text integration
4. **Multi-language support** - International users
5. **Redis caching** - Distributed cache for scale
6. **Webhook integration** - Daily weather briefings via email/Slack

### SRE/DevOps Integration Ideas
- **Infrastructure monitoring agent** - Weather-based capacity planning
- **Datacenter environmental monitoring** - Temperature/humidity tracking
- **Incident correlation** - Weather events vs service disruptions
- **On-call scheduling** - Weather-based shift adjustments

## Learning Outcomes

By completing this project, you will understand:
- ✅ Agentic loop patterns (ReAct framework)
- ✅ Tool/function calling with LLMs
- ✅ External API integration
- ✅ Conversation memory management
- ✅ Error handling in AI systems
- ✅ Prompt engineering for tool use
- ✅ Configuration management
- ✅ Logging best practices
- ✅ CLI design patterns
- ✅ Caching strategies

## Resources

### Documentation
- [OpenWeatherMap API Docs](https://openweathermap.org/api)
- [Anthropic Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Click CLI Documentation](https://click.palletsprojects.com/)
- [Cachetools Documentation](https://cachetools.readthedocs.io/)

### References
- ReAct: Reasoning and Acting paper
- LangChain documentation (for comparison)
- Building AI agents from scratch tutorials

## Timeline

**Total Estimated Time**: 3.5-4 hours for full implementation

| Phase | Duration |
|-------|----------|
| Setup | 30 min |
| Weather Tool | 45 min |
| Agent Core | 60 min |
| Testing | 30 min |
| Config & Logging | 20 min |
| CLI Enhancement | 25 min |
| Caching | 15 min |
| Documentation | 15 min |

## Next Steps
1. [ ] Create project directory
2. [ ] Set up virtual environment
3. [ ] Install dependencies
4. [ ] Obtain API keys
5. [ ] Implement weather tool
6. [ ] Build agent core
7. [ ] Add configuration management
8. [ ] Implement caching
9. [ ] Create CLI interface
10. [ ] Test and iterate
11. [ ] Deploy (optional)

---

## What We've Done So Far

This section tracks our progress in planning the Weather Agent project.

### Completed Planning Items
1. **Initial Plan Created** - Basic agent architecture with 4 components
2. **Enhanced Plan** - Added 7 components, 7 implementation phases
3. **Tool Schemas** - Defined 5 tools (get_weather, get_forecast, get_alerts, convert_units, geocode_location)
4. **Configuration System** - YAML config + environment variables
5. **Logging Strategy** - Structured logging with rotation
6. **CLI Design** - Interactive and single-query modes
7. **Caching Layer** - TTL-based caching implementation
8. **Rate Limiting** - Request throttling implementation
9. **Security Considerations** - API key protection, input sanitization
10. **Testing Strategy** - Unit, integration, and E2E tests

### Recent Optimizations Added
- **Data Models** - Pydantic models for type-safe data handling
- **Environment Setup** - Virtual environment and requirements.txt structure
- **API Error Codes** - Table mapping error codes to actions
- **Async Support** - Optional async/await implementation
- **Code Quality Standards** - Type hints, docstrings, code organization

---

**Last Updated**: February 17, 2026
**Status**: Enhanced Planning Phase
**Complexity**: Beginner to Intermediate
