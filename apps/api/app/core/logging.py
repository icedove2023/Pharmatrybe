"""Structured logging helpers for the PharmaTrybe API."""

from app.logging.logger import configure_logging as configure_app_logging
from app.logging.logger import get_logger as get_app_logger


def configure_logging() -> None:
    """Configure application logging from the core bootstrap."""
    configure_app_logging()


def get_logger(name: str):
    """Return a structured logger instance for the requested module."""
    return get_app_logger(name)
