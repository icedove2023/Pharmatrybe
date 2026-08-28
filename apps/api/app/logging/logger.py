"""Structured logger and logging configuration for PharmaTrybe."""

from __future__ import annotations

import logging
from logging import Logger

from app.core.config import settings

LOG_LEVELS: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class StructuredLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that preserves structured key/value fields."""

    def process(self, msg: str, kwargs: dict[str, object]) -> tuple[str, dict[str, object]]:
        extra = kwargs.get("extra", {})
        if isinstance(extra, dict) and extra:
            formatted_fields = " ".join(
                f"{key}={value}" for key, value in extra.items()
            )
            msg = f"{msg} {formatted_fields}"
            kwargs["extra"] = {}
        return msg, kwargs


def configure_logging() -> None:
    """Configure root logging for the PharmaTrybe application."""
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(LOG_LEVELS.get(settings.log_level.upper(), logging.INFO))

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    root_logger.debug("Logging configured", extra={"log_level": settings.log_level})


def get_logger(name: str) -> Logger:
    """Return a structured logger for the requested module."""
    return StructuredLoggerAdapter(logging.getLogger(name), {})
