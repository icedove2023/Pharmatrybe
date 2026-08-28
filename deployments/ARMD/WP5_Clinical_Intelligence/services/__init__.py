"""
WP5 Service Layer.

Contains application orchestration.

Services coordinate:

    API
        ↓
    Engine
        ↓
    Response

Services never implement
machine learning.

Services never perform SQL.
"""

from .prediction_service import PredictionService

__all__ = [
    "PredictionService",
]