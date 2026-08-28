"""Importable compatibility package for the shared prediction adapters."""

from .armd_adapter import ARMDAdapter, ARMDAdapterError

__all__ = ["ARMDAdapter", "ARMDAdapterError"]
