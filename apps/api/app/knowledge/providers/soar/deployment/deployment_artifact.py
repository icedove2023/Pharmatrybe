"""Deployment artifact definitions for SOAR provider."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SOARModelArtifact:
    """Represents a deployed SOAR trained model artifact."""

    model_name: str
    model_version: str
    artifact_uri: str
    model_format: str
    checksum: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata_uri: str | None = None


@dataclass(frozen=True)
class SOARPipelineArtifact:
    """Represents the deployed preprocessing pipeline artifact."""

    pipeline_name: str
    artifact_uri: str
    checksum: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata_uri: str | None = None


@dataclass(frozen=True)
class SOARCalibrationArtifact:
    """Represents a deployed probability calibration artifact."""

    calibration_name: str
    artifact_uri: str
    calibration_method: str | None = None
    optimized_threshold: float | None = None
    checksum: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata_uri: str | None = None


@dataclass(frozen=True)
class SOARExplainerArtifact:
    """Represents a deployed SHAP explainer artifact for SOAR models."""

    explainer_name: str
    artifact_uri: str
    checksum: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata_uri: str | None = None


@dataclass(frozen=True)
class SOARArtifactMetadata:
    """Structured metadata for a deployed SOAR model artifact."""

    model_name: str
    model_version: str
    organism: str
    antibiotic: str
    algorithm: str
    training_years: list[int] | None = None
    validation_years: list[int] | None = None
    deployment_year: int | None = None
    model_format: str | None = None
    artifact_uri: str | None = None
    preprocessing_pipeline_uri: str | None = None
    calibration_uri: str | None = None
    optimized_threshold: float | None = None
    calibration_method: str | None = None
    macro_f1: float | None = None
    supported_features: list[str] | None = None
    prediction_classes: list[str] | None = None
    provider: str = "SOAR"
    source_datasets: list[str] | None = None
    checksum: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    shap_explainer_uri: str | None = None
    metadata_json_uri: str | None = None


@dataclass(frozen=True)
class SOARModelDeployment:
    """Describes a deployed SOAR organism–antibiotic model package."""

    model_artifact: SOARModelArtifact
    pipeline_artifact: SOARPipelineArtifact | None = None
    calibration_artifact: SOARCalibrationArtifact | None = None
    explainer_artifact: SOARExplainerArtifact | None = None
    artifact_metadata: SOARArtifactMetadata | None = None
    metadata_json_uri: str | None = None
    deployed_at: datetime | None = None
    updated_at: datetime | None = None
    notes: str | None = None
