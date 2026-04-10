# Weather Agent

AI-powered weather information agent with CLI support, caching, and LLM-assisted responses.

## Features

- Current weather lookup by city
- Forecast lookup
- Geocoding support
- Conversation-style weather assistant
- Configurable LLM provider (Anthropic/OpenAI)
- TTL caching for weather/forecast/geocode data
- Input sanitization and API key validation
- Structured error handling with user-friendly messages

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and provide keys:

```bash
OPENWEATHER_API_KEY=your_openweather_key
ANTHROPIC_API_KEY=your_anthropic_key
# OR
OPENAI_API_KEY=your_openai_key
```

Optional app configuration is in `config.yaml`.

## Usage

Run via module:

```bash
python -m src.cli --help
```

Common commands:

```bash
python -m src.cli weather "Toronto"
python -m src.cli forecast "London" --days 3
python -m src.cli geocode "Paris"
python -m src.cli chat --prompt "What's the weather in Tokyo?"
```

Or use entrypoint:

```bash
python main.py
```

## Development

Run checks locally:

```bash
ruff check src tests
mypy src --ignore-missing-imports
pytest tests -q
```

## Release Checklist

- Lint passes
- Type checks pass
- Tests pass
- CLI smoke test passes
- README/config examples updated
