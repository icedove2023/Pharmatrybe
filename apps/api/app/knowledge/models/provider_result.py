"""Standard provider result model for PharmaTrybe knowledge orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.knowledge.models.knowledge_bundle import KnowledgePackage
from app.knowledge.models.provenance import Provenance
from app.knowledge.providers.provider_types import ProviderMetadata


@dataclass(frozen=True)
class ProviderResult:
    provider_metadata: ProviderMetadata
    knowledge_package: KnowledgePackage | list[KnowledgePackage] | None
    provenance: Provenance | None
    execution_time_ms: float
    status: str
    warnings: list[str] | None = None
    errors: list[str] | None = None
    query: Any | None = None
