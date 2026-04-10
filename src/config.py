"""Configuration loader for Weather Agent."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from .exceptions import ConfigurationError


class Config:
    """Configuration manager for Weather Agent."""

    _instance: Optional["Config"] = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._config:
            self.load()

    def load(self, config_path: Optional[str] = None) -> None:
        """Load configuration from YAML file and environment variables."""
        load_dotenv()

        if config_path is None:
            config_path = os.getenv("CONFIG_PATH", "config.yaml")

        config_file = Path(config_path)

        if config_file.exists():
            with open(config_file, "r") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = self._get_defaults()

        self._override_from_env()

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "app": {"name": "Weather Agent", "version": "1.0.0", "debug": False},
            "api": {
                "weather_provider": "openweathermap",
                "base_url": "https://api.openweathermap.org/data/2.5",
                "cache_ttl_seconds": 300,
                "timeout_seconds": 10,
                "max_retries": 3,
            },
            "llm": {
                "provider": "anthropic",
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1024,
                "temperature": 0.7,
            },
            "cache": {
                "enabled": True,
                "weather_ttl": 300,
                "geocode_ttl": 86400,
                "max_size": 100,
            },
            "logging": {
                "level": "INFO",
                "file": "logs/weather_agent.log",
                "max_bytes": 10485760,
                "backup_count": 5,
            },
            "cli": {
                "default_units": "metric",
                "output_format": "plain",
                "color_output": True,
                "interactive_mode": True,
            },
        }

    def _override_from_env(self) -> None:
        """Override config with environment variables."""
        env_mappings = {
            "OPENWEATHER_API_KEY": ("api", "openweather_api_key"),
            "ANTHROPIC_API_KEY": ("llm", "anthropic_api_key"),
            "OPENAI_API_KEY": ("llm", "openai_api_key"),
            "DEFAULT_UNITS": ("cli", "default_units"),
            "DEBUG": ("app", "debug"),
        }

        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                if section not in self._config:
                    self._config[section] = {}
                self._config[section][key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value using dot notation."""
        keys = key.split(".")
        current = self._config

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    def get_api_key(self, provider: Optional[str] = None) -> str:
        """Get API key for specified provider."""
        if provider is None:
            provider = self.get("llm.provider", "anthropic")

        if provider == "anthropic":
            key = self.get("llm.anthropic_api_key") or os.getenv("ANTHROPIC_API_KEY")
        elif provider == "openai":
            key = self.get("llm.openai_api_key") or os.getenv("OPENAI_API_KEY")
        else:
            key = None

        if not key:
            raise ConfigurationError(f"API key not found for provider: {provider}")

        # Validate key format
        assert provider is not None, "Provider should not be None at this point"
        self._validate_api_key(key, provider)

        return key

    def _validate_api_key(self, key: str, provider: str) -> None:
        """Validate API key format and basic properties.

        Args:
            key: API key to validate
            provider: Provider name

        Raises:
            ConfigurationError: If key format is invalid
        """
        if not key or not key.strip():
            raise ConfigurationError(f"API key for {provider} is empty")

        key = key.strip()

        # Basic length checks
        if len(key) < 10:
            raise ConfigurationError(f"API key for {provider} is too short")

        if len(key) > 200:
            raise ConfigurationError(f"API key for {provider} is too long")

        # Provider-specific validation
        if provider == "anthropic":
            # Anthropic keys start with "sk-ant-"
            if not key.startswith("sk-ant-"):
                raise ConfigurationError("Invalid Anthropic API key format")

        elif provider == "openai":
            # OpenAI keys start with "sk-" or "sk-proj-" or "sk-svcacct-"
            if not (
                key.startswith("sk-")
                or key.startswith("sk-proj-")
                or key.startswith("sk-svcacct-")
            ):
                raise ConfigurationError("Invalid OpenAI API key format")

        # Check for obviously invalid patterns
        if any(char in key for char in [" ", "\t", "\n"]):
            raise ConfigurationError(
                f"API key for {provider} contains invalid characters"
            )

    def get_weather_api_key(self) -> str:
        """Get OpenWeatherMap API key."""
        key = self.get("api.openweather_api_key") or os.getenv("OPENWEATHER_API_KEY")
        if not key:
            raise ConfigurationError("OpenWeatherMap API key not found")

        # Basic validation for weather API key
        key = key.strip()
        if len(key) < 20 or len(key) > 50:
            raise ConfigurationError("Invalid OpenWeatherMap API key format")

        return key

    @property
    def config(self) -> Dict[str, Any]:
        """Get full config dictionary."""
        return self._config


def get_config() -> Config:
    """Get global config instance."""
    return Config()
