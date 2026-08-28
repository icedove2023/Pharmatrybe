"""Placeholder provenance models for PharmaTrybe knowledge fusion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProvenanceRecord:
    source_name: str
    source_type: str
    version: str
    details: dict[str, Any] | None = None
