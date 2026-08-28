"""Placeholder fusion models for PharmaTrybe knowledge architecture."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FusionResult:
    bundles: list[Any]
    fused_payload: Any | None = None
    provenance: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
