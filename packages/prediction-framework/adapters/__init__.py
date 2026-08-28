"""Prediction Framework Adapters.

Non-invasive adapters that wrap existing prediction engines
(SOAR, ARMD) into unified plugin interfaces.
"""

from .armd_adapter import ARMDAdapter, ARMDAdapterError

__all__ = [
    "ARMDAdapter",
    "ARMDAdapterError",
]
