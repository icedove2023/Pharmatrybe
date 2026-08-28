"""Importable compatibility wrapper for the shared ARMD adapter."""

from importlib import import_module

_module = import_module("packages.prediction-framework.adapters.armd_adapter")

ARMDAdapter = _module.ARMDAdapter
ARMDAdapterError = _module.ARMDAdapterError

__all__ = ["ARMDAdapter", "ARMDAdapterError"]
