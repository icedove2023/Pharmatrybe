"""
Global configuration.

This module centralises project paths used by WP5.

No business logic should exist here.
"""

from pathlib import Path

# --------------------------------------------------------
# PROJECT ROOT
# --------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------------
# WP4
# --------------------------------------------------------

WP4_DIRECTORY = PROJECT_ROOT

WP4_ENGINE = PROJECT_ROOT / "WP4_Decision_Engine.py"

# --------------------------------------------------------
# OUTPUTS
# --------------------------------------------------------

OUTPUT_DIRECTORY = PROJECT_ROOT / "output"

WP5_OUTPUT_DIRECTORY = OUTPUT_DIRECTORY / "WP5"

LOG_DIRECTORY = WP5_OUTPUT_DIRECTORY / "Logs"

# --------------------------------------------------------
# API
# --------------------------------------------------------

API_NAME = "ARMD Clinical Intelligence API"

API_VERSION = "1.0.0"

# --------------------------------------------------------
# SHAP
# --------------------------------------------------------

DEFAULT_BACKGROUND_SIZE = 200

# --------------------------------------------------------
# Logging
# --------------------------------------------------------

LOG_LEVEL = "INFO"

LOG_FORMAT = (
    "[%(asctime)s] "
    "[%(levelname)s] "
    "%(message)s"
)