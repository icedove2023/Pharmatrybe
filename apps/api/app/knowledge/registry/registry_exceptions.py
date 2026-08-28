"""Exceptions raised by the Model Registry."""

from __future__ import annotations


class ModelRegistryError(RuntimeError):
    """Base error for model registry failures."""


class ModelNotFoundError(ModelRegistryError):
    """Raised when a requested model cannot be found in the registry."""


class ModelLoadError(ModelRegistryError):
    """Raised when a model cannot be loaded or verified."""


class UnsupportedFormatError(ModelRegistryError):
    """Raised when a model artifact's serialization format is unsupported."""
