"""Model metadata DTO for the Model Registry.

This module provides a compact, validated representation of a model
artifact's metadata. We use Pydantic (v2) here so callers can depend on
basic validation and serialization for registry operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, validator

from app.knowledge.registry.registry_types import ModelFormat, ProviderType


class ModelMetadata(BaseModel):
    name: str = Field(..., description="Stable model name")
    version: str = Field(..., description="Model semantic version or tag")
    provider: ProviderType = Field(..., description="Source provider of model")
    format: ModelFormat = Field(..., description="Serialization/format of artifact")
    uri: str | None = Field(None, description="Location where the artifact can be fetched")
    created_at: datetime | None = Field(None, description="Artifact creation timestamp")
    description: str | None = Field(None, description="Optional short description")
    tags: list[str] | None = Field(None, description="Optional tags for filtering/search")
    input_spec: dict[str, Any] | None = Field(None, description="Input schema/shape description")
    artifact_checksum: str | None = Field(None, description="Optional artifact checksum")
    extra: dict[str, Any] | None = Field(None, description="Freeform extra metadata")

    model_config = {"frozen": True}

    @validator("version")
    @classmethod
    def _clean_version(cls, v: str) -> str:
        return v.strip()

