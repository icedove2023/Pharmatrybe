"""
Logging configuration.

Provides a single logger used across the
Clinical Intelligence API.
"""

import logging
import sys

from pathlib import Path

from .config import LOG_DIRECTORY
from .config import LOG_FORMAT
from .config import LOG_LEVEL

LOG_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


def setup_logging() -> logging.Logger:
    """
    Configure application logging.
    """

    logger = logging.getLogger("WP5")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")

    # ----------------------------
    # Console
    # ----------------------------

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # ----------------------------
    # File
    # ----------------------------

    log_file = LOG_DIRECTORY / "WP5.log"

    file_handler = logging.FileHandler(log_file)

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    logger.info("Logging initialised.")

    return logger