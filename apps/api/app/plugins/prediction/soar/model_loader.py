from __future__ import annotations

import csv
import json
import pickle
import joblib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger
from app.plugins.prediction.soar.artifact_registry import Artifact, ArtifactCategoryConfig, ArtifactRegistry
from app.plugins.prediction.soar.deployment_scanner import DeploymentInfo

logger = get_logger(__name__)


class ModelLoadError(Exception):
    """Raised when a deployed SOAR model cannot be loaded."""


@dataclass
class LoadedModel:
    """In-memory representation of loaded SOAR deployment artifacts."""

    deployment_info: DeploymentInfo
    artifact_registry: ArtifactRegistry
    loaded_timestamp: datetime
    model: Any
    label_encoder: Optional[Any]
    preprocessor: Optional[Any]
    optimal_threshold: Optional[Any]


class ModelLoader:
    """Loads deployed SOAR model artifacts lazily and caches them in memory."""

    def __init__(self, category_config: Optional[ArtifactCategoryConfig] = None) -> None:
        self._cache: Dict[str, LoadedModel] = {}
        self.category_config = category_config or ArtifactCategoryConfig.load_default()

    def load(self, deployment_info: DeploymentInfo) -> LoadedModel:
        """Prepare lazy artifact handles for the specified deployment.

        If the deployment is already loaded, the cached LoadedModel is returned.
        """
        deployment_id = deployment_info.deployment_id
        if self.is_loaded(deployment_id):
            logger.info("Using cached model", extra={"deployment_id": deployment_id})
            return self._cache[deployment_id]

        logger.info("Registering deployment artifacts", extra={"deployment_id": deployment_id})
        try:
            artifact_registry = deployment_info.artifact_registry
            model = self._load_artifact_by_category(artifact_registry, "MODEL")
            label_encoder = self._load_artifact_by_category(artifact_registry, "ENCODER")
            preprocessor = None
            try:
                preprocessor = self._load_artifact_by_category(artifact_registry, "PREPROCESSOR")
            except ModelLoadError:
                preprocessor = None
            optimal_threshold = self._load_artifact_by_category(artifact_registry, "THRESHOLD")

            loaded_model = LoadedModel(
                deployment_info=deployment_info,
                artifact_registry=artifact_registry,
                loaded_timestamp=datetime.utcnow(),
                model=model,
                label_encoder=label_encoder,
                preprocessor=preprocessor,
                optimal_threshold=optimal_threshold,
            )
            self._cache[deployment_id] = loaded_model
            logger.info("Registered artifacts successfully", extra={"deployment_id": deployment_id})
            return loaded_model
        except Exception as exc:
            logger.error("Artifact registration failed", extra={"deployment_id": deployment_id, "error": str(exc)})
            raise ModelLoadError(f"Failed to load deployment {deployment_id}: {exc}") from exc

    def load_artifact(self, artifact: Artifact) -> Any:
        try:
            if artifact.extension in {".pkl", ".joblib"}:
                return self._load_pickle(artifact.absolute_path)
            if artifact.extension == ".json":
                return self._load_json(artifact.absolute_path)
            if artifact.extension == ".csv":
                return self._load_metrics(artifact.absolute_path)
            return artifact.absolute_path
        except Exception as exc:
            raise ModelLoadError(f"Failed to load artifact {artifact.absolute_path}: {exc}") from exc

    def get_artifact(self, deployment_id: str, category: str) -> Optional[Artifact]:
        loaded = self.get(deployment_id)
        if loaded is None:
            return None
        return loaded.artifact_registry.find_first(category)

    def load_model(self, deployment_id: str) -> Any:
        artifact = self.get_artifact(deployment_id, "MODEL")
        if artifact is None:
            raise ModelLoadError(f"Model artifact not found for deployment: {deployment_id}")
        return self.load_artifact(artifact)

    def load_encoder(self, deployment_id: str) -> Any:
        artifact = self.get_artifact(deployment_id, "ENCODER")
        if artifact is None:
            raise ModelLoadError(f"Encoder artifact not found for deployment: {deployment_id}")
        return self.load_artifact(artifact)

    def load_preprocessor(self, deployment_id: str) -> Any:
        artifact = self.get_artifact(deployment_id, "PREPROCESSOR")
        if artifact is None:
            raise ModelLoadError(f"Preprocessor artifact not found for deployment: {deployment_id}")
        return self.load_artifact(artifact)

    def load_threshold(self, deployment_id: str) -> Any:
        artifact = self.get_artifact(deployment_id, "THRESHOLD")
        if artifact is None:
            raise ModelLoadError(f"Threshold artifact not found for deployment: {deployment_id}")
        return self.load_artifact(artifact)

    def get(self, deployment_id: str) -> Optional[LoadedModel]:
        """Return an already loaded model, or None if not loaded."""
        return self._cache.get(deployment_id)

    def is_loaded(self, deployment_id: str) -> bool:
        """Return whether the specified deployment is loaded."""
        return deployment_id in self._cache

    def unload(self, deployment_id: str) -> None:
        """Unload a loaded deployment from the cache."""
        if deployment_id not in self._cache:
            return
        logger.info("Unloading model", extra={"deployment_id": deployment_id})
        self._cache.pop(deployment_id, None)

    def unload_all(self) -> None:
        """Unload all cached models."""
        for deployment_id in list(self._cache.keys()):
            logger.info("Unloading model", extra={"deployment_id": deployment_id})
            self._cache.pop(deployment_id, None)

    def loaded_models(self) -> List[LoadedModel]:
        """Return all currently loaded models."""
        return list(self._cache.values())

    def _load_artifact_by_category(self, artifact_registry: ArtifactRegistry, category: str) -> Any:
        artifact = artifact_registry.find_first(category)
        if artifact is None:
            raise ModelLoadError(f"Artifact of category '{category}' not found in deployment {artifact_registry.deployment_path.name}.")
        return self.load_artifact(artifact)

    def _load_pickle(self, path: Path) -> Any:
        try:
            return joblib.load(path)
        except Exception as exc:
            raise ModelLoadError(f"Failed to load pickle artifact at {path}: {exc}") from exc

    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as file_obj:
                return json.load(file_obj)
        except Exception as exc:
            raise ModelLoadError(f"Failed to load JSON artifact at {path}: {exc}") from exc

    def _load_metrics(self, path: Path) -> List[Dict[str, Any]]:
        try:
            with path.open("r", encoding="utf-8") as file_obj:
                reader = csv.DictReader(file_obj)
                return [dict(row) for row in reader]
        except Exception as exc:
            raise ModelLoadError(f"Failed to load metrics artifact at {path}: {exc}") from exc
