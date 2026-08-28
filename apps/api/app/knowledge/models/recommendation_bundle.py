"""Recommendation bundle models for PharmaTrybe knowledge providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RecommendationBundle:
    recommendation_id: str
    disease_id: str
    drug_id: str
    population: str | None = None
    severity: str | None = None
    evidence: Any | None = None
    provenance: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
