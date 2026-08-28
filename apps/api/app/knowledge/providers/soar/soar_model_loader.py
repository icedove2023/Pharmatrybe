"""SOAR model loader implementation for SOAR model artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.knowledge.registry.model_loader import BaseModelLoader
from app.knowledge.registry.registry_types import ModelFormat
from app.knowledge.providers.soar.deployment.deployment_artifact import (
    SOARCalibrationArtifact,
    SOARExplainerArtifact,
    SOARModelArtifact,
    SOARModelDeployment,
    SOARPipelineArtifact,
)
from app.knowledge.providers.soar.soar_metadata import SOARModelMetadata


@dataclass
class SOARRuntimeArtifact:
    """Runtime handle for a lazily loaded SOAR deployment artifact."""

    uri: str
    artifact_type: str
    path: Path
    size_bytes: int | None = None
    modified_at: datetime | None = None
    checksum: str | None = None
    loaded_at: datetime | None = None


class SOARRuntimeModel:
    """Runtime model container for loaded SOAR deployment artifacts."""

    def __init__(self, deployment: SOARModelDeployment) -> None:
        self.deployment = deployment
        self.artifact_metadata = deployment.artifact_metadata
        self._model_artifact: SOARRuntimeArtifact | None = None
        self._pipeline_artifact: SOARRuntimeArtifact | None = None
        self._calibration_artifact: SOARRuntimeArtifact | None = None
        self._explainer_artifact: SOARRuntimeArtifact | None = None

    @property
    def model_artifact(self) -> SOARRuntimeArtifact:
        if self._model_artifact is None:
            self._model_artifact = self._load_artifact(
                self.deployment.model_artifact.artifact_uri,
                "trained_model",
                self.deployment.model_artifact.checksum,
            )
        return self._model_artifact

    @property
    def pipeline_artifact(self) -> SOARRuntimeArtifact:
        if self._pipeline_artifact is None:
            self._pipeline_artifact = self._load_artifact(
                self.deployment.pipeline_artifact.artifact_uri,
                "preprocessing_pipeline",
                None,
            )
        return self._pipeline_artifact

    @property
    def calibration_artifact(self) -> SOARRuntimeArtifact:
        if self._calibration_artifact is None:
            self._calibration_artifact = self._load_artifact(
                self.deployment.calibration_artifact.artifact_uri,
                "calibration_object",
                None,
            )
        return self._calibration_artifact

    @property
    def explainer_artifact(self) -> SOARRuntimeArtifact:
        if self._explainer_artifact is None:
            self._explainer_artifact = self._load_artifact(
                self.deployment.explainer_artifact.artifact_uri,
                "shap_explainer",
                None,
            )
        return self._explainer_artifact

    @property
    def optimized_threshold(self) -> float | None:
        return self.deployment.calibration_artifact.optimized_threshold

    def load_all(self) -> None:
        self.model_artifact
        self.pipeline_artifact
        self.calibration_artifact
        self.explainer_artifact

    def _load_artifact(self, uri: str, artifact_type: str, checksum: str | None) -> SOARRuntimeArtifact:
        path = Path(uri)
        if not path.exists():
            raise FileNotFoundError(f"SOAR runtime artifact not found: {uri}")

        stat = path.stat()
        return SOARRuntimeArtifact(
            uri=uri,
            artifact_type=artifact_type,
            path=path,
            size_bytes=stat.st_size,
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            checksum=checksum,
            loaded_at=datetime.now(),
        )


class SOARModelLoader(BaseModelLoader):
    """Filesystem loader for deployed SOAR model artifacts.

    This loader discovers a deployment directory, validates required
    artifact presence, and constructs a deployment descriptor.
    """

    def __init__(self) -> None:
        self._metadata: SOARModelMetadata | None = None
        self._runtime_models: dict[str, SOARRuntimeModel] = {}

    @property
    def provider_name(self) -> str:
        return "SOAR"

    @property
    def supported_formats(self) -> list[ModelFormat]:
        return [
            ModelFormat.PICKLE,
            ModelFormat.TORCH,
            ModelFormat.ONNX,
            ModelFormat.SAVEDMODEL,
            ModelFormat.TF,
            ModelFormat.CUSTOM,
        ]

    @property
    def model_family(self) -> str:
        return "organism_antibiotic"

    def load_metadata(self, uri: str) -> SOARModelMetadata:
        deployment = self.discover_deployment(uri)
        self._metadata = deployment.artifact_metadata
        return deployment.artifact_metadata

    def load_runtime_model(self, deployment: SOARModelDeployment) -> SOARRuntimeModel:
        cache_key = deployment.metadata_json_uri or deployment.model_artifact.artifact_uri
        if cache_key in self._runtime_models:
            return self._runtime_models[cache_key]

        runtime_model = SOARRuntimeModel(deployment)
        self._runtime_models[cache_key] = runtime_model
        return runtime_model

    def get_runtime_model(self, deployment: SOARModelDeployment) -> SOARRuntimeModel:
        cache_key = deployment.metadata_json_uri or deployment.model_artifact.artifact_uri
        if cache_key not in self._runtime_models:
            return self.load_runtime_model(deployment)
        return self._runtime_models[cache_key]

    def discover_deployment(self, uri: str) -> SOARModelDeployment:
        deployment_directory = Path(uri)
        if not deployment_directory.exists() or not deployment_directory.is_dir():
            raise FileNotFoundError(f"SOAR deployment directory not found: {uri}")

        metadata_path = deployment_directory / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"SOAR deployment metadata.json not found in {uri}")

        metadata = self._load_metadata_json(metadata_path)
        self._validate_required_artifacts(deployment_directory, metadata)

        model_artifact = SOARModelArtifact(
            model_name=metadata.model_name,
            model_version=metadata.model_version,
            artifact_uri=self._resolve_uri(deployment_directory, metadata.artifact_uri),
            model_format=metadata.model_format,
            checksum=metadata.checksum,
            created_at=metadata.created_at,
            updated_at=metadata.updated_at,
            metadata_uri=str(metadata_path),
        )

        pipeline_artifact = SOARPipelineArtifact(
            pipeline_name=f"{metadata.model_name}-preprocessing",
            artifact_uri=self._resolve_uri(deployment_directory, metadata.preprocessing_pipeline_uri),
            checksum=None,
            created_at=None,
            updated_at=None,
            metadata_uri=None,
        )

        calibration_artifact = SOARCalibrationArtifact(
            calibration_name=f"{metadata.model_name}-calibration",
            artifact_uri=self._resolve_uri(deployment_directory, metadata.calibration_uri),
            calibration_method=metadata.calibration_method,
            optimized_threshold=metadata.optimized_threshold,
            checksum=None,
            created_at=None,
            updated_at=None,
            metadata_uri=None,
        )

        explainer_artifact = SOARExplainerArtifact(
            explainer_name=f"{metadata.model_name}-shap-explainer",
            artifact_uri=self._resolve_uri(deployment_directory, metadata.shap_explainer_uri),
            checksum=None,
            created_at=None,
            updated_at=None,
            metadata_uri=None,
        )

        deployment = SOARModelDeployment(
            model_artifact=model_artifact,
            pipeline_artifact=pipeline_artifact,
            calibration_artifact=calibration_artifact,
            explainer_artifact=explainer_artifact,
            artifact_metadata=metadata,
            metadata_json_uri=str(metadata_path),
            deployed_at=metadata.created_at,
            updated_at=metadata.updated_at,
        )

        return deployment

    def validate_artifact(self, uri: str) -> bool:
        try:
            self.discover_deployment(uri)
            return True
        except Exception:
            return False

    def _load_metadata_json(self, path: Path) -> SOARModelMetadata:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if payload.get("provider") != "SOAR":
            raise ValueError("SOARModelLoader requires provider 'SOAR' in metadata")

        return SOARModelMetadata(**payload)

    def _validate_required_artifacts(self, base_dir: Path, metadata: SOARModelMetadata) -> None:
        missing: list[str] = []

        required = {
            "trained model": metadata.artifact_uri,
            "preprocessing pipeline": metadata.preprocessing_pipeline_uri,
            "calibration object": metadata.calibration_uri,
            "optimized threshold": metadata.optimized_threshold,
            "metadata": metadata.model_name,
            "SHAP explainer": metadata.shap_explainer_uri,
        }

        if metadata.artifact_uri is None:
            missing.append("trained model artifact_uri")
        if metadata.preprocessing_pipeline_uri is None:
            missing.append("preprocessing pipeline URI")
        if metadata.calibration_uri is None:
            missing.append("calibration URI")
        if metadata.optimized_threshold is None:
            missing.append("optimized threshold")
        if metadata.shap_explainer_uri is None:
            missing.append("SHAP explainer URI")

        if missing:
            raise ValueError(f"SOAR deployment missing required metadata fields: {', '.join(missing)}")

        for name, candidate in [
            ("trained model", metadata.artifact_uri),
            ("preprocessing pipeline", metadata.preprocessing_pipeline_uri),
            ("calibration object", metadata.calibration_uri),
            ("SHAP explainer", metadata.shap_explainer_uri),
        ]:
            if candidate is not None:
                resolved = self._resolve_uri(base_dir, candidate)
                if not Path(resolved).exists():
                    missing.append(f"{name} artifact at {resolved}")

        if missing:
            raise FileNotFoundError(f"SOAR deployment missing required artifacts: {', '.join(missing)}")

    def _resolve_uri(self, base_dir: Path, uri: str | None) -> str:
        if uri is None:
            return ""

        candidate = Path(uri)
        if candidate.is_absolute():
            return str(candidate)

        return str((base_dir / uri).resolve())
