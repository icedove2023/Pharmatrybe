"""Evidence bundle models for PharmaTrybe knowledge providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EvidenceBundle:
    evidence_id: str
    disease_id: str
    summary: str
    source: str
    level: str | None = None
    provenance: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
