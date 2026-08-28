"""
Dependency Injection

Provides singleton services for the API.

Services are instantiated once and reused
throughout the application lifetime.
"""

from functools import lru_cache

from ..services import PredictionService


@lru_cache(maxsize=1)
def get_prediction_service() -> PredictionService:
    """
    Return the singleton PredictionService.

    Using lru_cache ensures that expensive WP4
    artifacts (registry, models, preprocessors)
    are loaded only once.
    """
    return PredictionService()