"""Model Registry package for PharmaTrybe.

This package contains lightweight skeletons for a Model Registry responsible
for discovering, loading, and exposing deployed ML assets. It purposely
contains no loading or inference implementation — only interfaces, DTOs,
exceptions, and the registry skeleton.

Public modules:
- model_registry
- model_loader
- model_metadata
- registry_types
- registry_exceptions

"""

from .model_registry import ModelRegistry
from .model_loader import BaseModelLoader
from .model_metadata import ModelMetadata
from .registry_models import ModelEntry, ModelSummary
from .registry_types import ModelFormat, ProviderType, ModelStatus
from .registry_exceptions import (
    ModelRegistryError,
    ModelNotFoundError,
    ModelLoadError,
    UnsupportedFormatError,
)

__all__ = [
    "ModelRegistry",
    "BaseModelLoader",
    "ModelMetadata",
    "ModelEntry",
    "ModelSummary",
    "ModelFormat",
    "ProviderType",
    "ModelStatus",
    "ModelRegistryError",
    "ModelNotFoundError",
    "ModelLoadError",
    "UnsupportedFormatError",
]
