"""Explicit adapters from canonical backend requests to plugin requests."""

from .clinical import AdapterValidationError, adapt_prediction_request

__all__ = ["AdapterValidationError", "adapt_prediction_request"]
