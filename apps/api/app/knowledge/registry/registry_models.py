"""Registry data models for the Model Registry.

Small, Pydantic-backed models used by higher-level registry APIs to
represent entries and summaries. These are intentionally lightweight
and do not perform model loading or inference.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from app.knowledge.registry.model_metadata import ModelMetadata
from app.knowledge.registry.registry_types import ModelStatus


class ModelEntry(BaseModel):
    metadata: ModelMetadata
    status: ModelStatus = Field(ModelStatus.REGISTERED)
    registered_at: datetime | None = None
    loader: str | None = None

    class Config:
        frozen = True


class ModelSummary(BaseModel):
    name: str
    latest_version: str | None = None
    versions: List[str] = Field(default_factory=list)

    class Config:
        frozen = True
