"""Structured logging placeholders for the PharmaTrybe API."""

import logging


def configure_logging() -> None:
    """Configure the default logging behaviour for the application."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def get_logger(name: str) -> logging.Logger:
    """Return a logger instance for the requested module."""
    return logging.getLogger(name)
