"""SOAR-specific model metadata definitions."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.knowledge.registry.model_metadata import ModelMetadata
from app.knowledge.registry.registry_types import ModelFormat, ProviderType


class SOARModelMetadata(BaseModel):
    model_name: str = Field(..., description="SOAR organism-antibiotic model name")
    model_version: str = Field(..., description="SOAR organism-antibiotic model version")
    organism: str = Field(..., description="Target organism for the prediction model")
    antibiotic: str = Field(..., description="Antibiotic agent predicted by the model")
    algorithm: str = Field(..., description="Algorithm or model family used for prediction")
    training_years: list[int] | None = Field(None, description="Years included in training data")
    validation_years: list[int] | None = Field(None, description="Years included in validation data")
    deployment_year: int | None = Field(None, description="Year when the model was deployed")
    model_format: str = Field(..., description="Serialization format of the deployed model artifact")
    artifact_uri: str = Field(..., description="URI for the deployed model artifact")
    preprocessing_pipeline_uri: str | None = Field(None, description="URI for the preprocessing pipeline artifact")
    calibration_uri: str | None = Field(None, description="URI for the calibration artifact")
    optimized_threshold: float | None = Field(None, description="Decision threshold optimized during calibration")
    calibration_method: str | None = Field(None, description="Calibration method used for the model")
    macro_f1: float | None = Field(None, description="Macro F1 score from model evaluation")
    supported_features: list[str] | None = Field(None, description="Features supported by the deployed model")
    prediction_classes: list[str] = Field(default_factory=lambda: ["S", "I", "R"], description="Prediction classes supported by the model")
    provider: Literal["SOAR"] = Field("SOAR", description="Provider name for the model")
    source_datasets: list[str] | None = Field(None, description="Datasets used to train or validate the model")
    checksum: str | None = Field(None, description="Artifact integrity checksum")
    created_at: datetime | None = Field(None, description="Metadata creation timestamp")
    updated_at: datetime | None = Field(None, description="Metadata last updated timestamp")

    model_config = {"frozen": True}

    def to_registry_metadata(self) -> ModelMetadata:
        """Convert SOAR-specific metadata to the generic registry metadata model."""
        try:
            registry_format = ModelFormat(self.model_format.lower())
        except ValueError:
            registry_format = ModelFormat.CUSTOM

        return ModelMetadata(
            name=self.model_name,
            version=self.model_version,
            provider=ProviderType.SOAR,
            format=registry_format,
            uri=self.artifact_uri,
            created_at=self.created_at,
            description=f"SOAR model for {self.organism} and {self.antibiotic}",
            tags=[self.organism, self.antibiotic, self.algorithm],
            input_spec={"supported_features": self.supported_features or []},
            artifact_checksum=self.checksum,
            extra={
                "training_years": self.training_years,
                "validation_years": self.validation_years,
                "deployment_year": self.deployment_year,
                "preprocessing_pipeline_uri": self.preprocessing_pipeline_uri,
                "calibration_uri": self.calibration_uri,
                "optimized_threshold": self.optimized_threshold,
                "calibration_method": self.calibration_method,
                "macro_f1": self.macro_f1,
                "prediction_classes": self.prediction_classes,
                "source_datasets": self.source_datasets,
                "updated_at": self.updated_at,
            },
        )
