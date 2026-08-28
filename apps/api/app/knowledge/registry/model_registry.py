"""Model Registry skeleton for discovering and exposing ML assets."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from app.knowledge.registry.model_loader import BaseModelLoader
from app.knowledge.registry.model_metadata import ModelMetadata
from app.knowledge.registry.registry_types import ModelFormat, ProviderType
from app.knowledge.registry.registry_exceptions import ModelNotFoundError


class ModelRegistry:
    """Lightweight registry for model metadata and loader registration.

    Responsibilities:
    - register/unregister `BaseModelLoader` implementations
    - discover metadata for known model URIs
    - list available models

    This class explicitly does NOT perform model instantiation, inference,
    scoring, explainability, or clinical decision logic.
    """

    def __init__(self, loaders: Iterable[BaseModelLoader] | None = None) -> None:
        self._loaders: list[BaseModelLoader] = list(loaders) if loaders is not None else []
        self._metadata_index: dict[str, ModelMetadata] = {}
        self._uri_index: dict[str, ModelMetadata] = {}

    def register_loader(self, loader: BaseModelLoader) -> None:
        if loader not in self._loaders:
            self._loaders.append(loader)

    def unregister_loader(self, loader: BaseModelLoader) -> None:
        self._loaders = [l for l in self._loaders if l is not loader]

    def list_loaders(self) -> list[BaseModelLoader]:
        return self._loaders.copy()

    def list_models(self) -> list[ModelMetadata]:
        return list(self._metadata_index.values())

    def list_models_by_provider(self, provider: ProviderType) -> list[ModelMetadata]:
        return [m for m in self._metadata_index.values() if m.provider == provider]

    def list_models_by_format(self, model_format: ModelFormat) -> list[ModelMetadata]:
        return [m for m in self._metadata_index.values() if m.format == model_format]

    def register_model_metadata(self, metadata: ModelMetadata, uri: str | None = None) -> None:
        key = f"{metadata.name}:{metadata.version}"
        self._metadata_index[key] = metadata
        if uri is not None:
            self._uri_index[uri] = metadata

    def get_model(self, name: str, version: str | None = None) -> ModelMetadata:
        key = f"{name}:{version or 'latest'}"
        if key in self._metadata_index:
            return self._metadata_index[key]

        candidates = [m for m in self._metadata_index.values() if m.name == name]
        if not candidates:
            raise ModelNotFoundError(f"Model {name} not found")

        candidates.sort(
            key=lambda m: (m.created_at.timestamp() if m.created_at is not None else 0),
            reverse=True,
        )
        return candidates[0]

    def get_model_by_uri(self, uri: str) -> ModelMetadata:
        if uri in self._uri_index:
            return self._uri_index[uri]
        raise ModelNotFoundError(f"Model metadata for URI {uri} not found")

    def find_models_by_provider(self, provider: ProviderType) -> list[ModelMetadata]:
        return self.list_models_by_provider(provider)

    def discover_metadata(self, uri: str) -> ModelMetadata:
        """Discover metadata for a remote/local artifact URI using available loaders.

        This method only queries loaders for metadata and returns a `ModelMetadata`.
        Actual model instantiation is intentionally out of scope.
        """
        for loader in self._loaders:
            try:
                # loaders are expected to raise or return metadata
                metadata = loader.load_metadata(uri)
                self.register_model_metadata(metadata, uri=uri)
                return metadata
            except Exception:
                continue
        raise ModelNotFoundError(f"No loader could discover metadata for {uri}")

    def discover_models(self, uris: Iterable[str]) -> list[ModelMetadata]:
        """Discover and cache metadata for multiple deployed model URIs."""
        discovered: list[ModelMetadata] = []
        for uri in uris:
            try:
                discovered.append(self.discover_metadata(uri))
            except ModelNotFoundError:
                continue
        return discovered

    def resolve_loader_for_format(self, model_format: ModelFormat) -> list[BaseModelLoader]:
        return [loader for loader in self._loaders if model_format in loader.supported_formats]
