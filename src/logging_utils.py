"""Logging setup for Weather Agent."""

import logging
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(config: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """Set up logging for the Weather Agent.

    Args:
        config: Configuration dictionary

    Returns:
        Configured logger
    """
    if config is None:
        config = {}

    log_level = config.get("logging", {}).get("level", "INFO")
    log_file = config.get("logging", {}).get("file", "logs/weather_agent.log")
    max_bytes = config.get("logging", {}).get("max_bytes", 10485760)
    backup_count = config.get("logging", {}).get("backup_count", 5)

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("weather_agent")
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(f"weather_agent.{name}")
