"""Generic normalized knowledge package models for PharmaTrybe."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.knowledge.models.provenance import Provenance


@dataclass(frozen=True)
class KnowledgePackage:
    source: str
    version: str
    provenance: Provenance | None
    diseases: list[Any] | None = None
    recommendations: list[Any] | None = None
    diagnostics: list[Any] | None = None
    pathogens: list[Any] | None = None
    evidence: list[Any] | None = None
    stewardship: list[Any] | None = None
    monitoring: list[Any] | None = None
    follow_up: list[Any] | None = None
    referral: list[Any] | None = None
    metadata: dict[str, Any] | None = None
