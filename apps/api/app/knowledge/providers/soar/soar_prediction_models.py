"""Model classes for SOAR prediction requests and responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SOARPredictionRequest:
    model_name: str
    model_version: str | None = None
    payload: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class SOARPredictionResult:
    model_name: str
    model_version: str | None = None
    predictions: dict[str, Any] | None = None
    confidence: float | None = None
    metadata: dict[str, Any] | None = None
