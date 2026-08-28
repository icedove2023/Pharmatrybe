"""Provenance model for PharmaTrybe knowledge providers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Provenance:
    source_name: str
    provider_name: str
    provider_type: str
    version: str
    publication_date: datetime | None = None
    retrieval_timestamp: datetime | None = None
    confidence: float | None = None
    citation: str | None = None
    license: str | None = None
    trace_id: str | None = None
    checksum: str | None = None
    details: dict[str, str] | None = None
