"""Abstract model loader interface for the Model Registry.

Loaders are responsible for knowing how to load metadata and optionally
instantiate model artifacts. For this task we only define the interface
and minimal helpers; actual loading is intentionally not implemented yet.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.knowledge.registry.model_metadata import ModelMetadata
from app.knowledge.registry.registry_types import ModelFormat


class BaseModelLoader(ABC):
    """Abstract loader for a specific provider and format."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider this loader supports (e.g. 'soar', 'armd')."""

    @property
    @abstractmethod
    def supported_formats(self) -> list[ModelFormat]:
        """Return a list of ModelFormat values this loader can handle."""

    @abstractmethod
    def load_metadata(self, uri: str) -> ModelMetadata:
        """Load and return ModelMetadata for the artifact at `uri`.

        Implementations should NOT perform heavy IO in constructors; this
        method is intentionally the place to implement retrieval.
        """

    def health_check(self) -> dict[str, Any] | None:
        """Optional lightweight health check for loader dependencies.

        Default implementation returns `None` to indicate no health data.
        """
        return None

    # Note: No `load_model` method is defined here on purpose — model
    # instantiation and inference are out of scope for the registry skeleton.
