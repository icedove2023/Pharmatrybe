"""Base knowledge objects for PharmaTrybe providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.knowledge.models.provenance import Provenance


@dataclass(frozen=True)
class BaseKnowledgeObject:
    id: str
    title: str | None = None
    description: str | None = None
    provenance: Provenance | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class DiseaseKnowledge(BaseKnowledgeObject):
    disease_id: str | None = None
    severity: str | None = None
    category: str | None = None


@dataclass(frozen=True)
class RecommendationKnowledge(BaseKnowledgeObject):
    recommendation_id: str | None = None
    disease_id: str | None = None
    drug_id: str | None = None
    population: str | None = None
    severity: str | None = None
    evidence: list[EvidenceKnowledge] | None = None


@dataclass(frozen=True)
class EvidenceKnowledge(BaseKnowledgeObject):
    evidence_id: str | None = None
    disease_id: str | None = None
    source: str | None = None
    level: str | None = None


@dataclass(frozen=True)
class DiagnosticKnowledge(BaseKnowledgeObject):
    disease_id: str | None = None
    diagnostic_type: str | None = None
    criteria: dict[str, Any] | None = None


@dataclass(frozen=True)
class MonitoringKnowledge(BaseKnowledgeObject):
    disease_id: str | None = None
    monitoring_type: str | None = None
    parameters: dict[str, Any] | None = None


@dataclass(frozen=True)
class PathogenKnowledge(BaseKnowledgeObject):
    pathogen_id: str | None = None
    taxonomy: str | None = None
    resistance_patterns: dict[str, Any] | None = None


@dataclass(frozen=True)
class StewardshipKnowledge(BaseKnowledgeObject):
    disease_id: str | None = None
    policy: str | None = None
    guidance: dict[str, Any] | None = None


@dataclass(frozen=True)
class FollowUpKnowledge(BaseKnowledgeObject):
    disease_id: str | None = None
    follow_up_type: str | None = None
    instructions: dict[str, Any] | None = None


@dataclass(frozen=True)
class ReferralKnowledge(BaseKnowledgeObject):
    disease_id: str | None = None
    criteria: dict[str, Any] | None = None
    referral_path: str | None = None
