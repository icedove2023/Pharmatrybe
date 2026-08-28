"""Compatibility package for the shared prediction framework.

This module exposes the same shared framework API under the importable
``packages.prediction_framework`` name while keeping the repository's
canonical source tree under ``packages/prediction-framework``.
"""

__version__ = "0.1.0"

__all__ = [
    "runtime",
    "plugin",
    "explainability",
    "exceptions",
    "contracts",
]
