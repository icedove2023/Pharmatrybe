"""WHO provider implementation for PharmaTrybe."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.database.repositories.who_knowledge_repository import WHOKnowledgeRepository
from app.knowledge.models.knowledge_bundle import KnowledgePackage
from app.knowledge.models.knowledge_objects import (
    BaseKnowledgeObject,
    DiseaseKnowledge,
    DiagnosticKnowledge,
    EvidenceKnowledge,
    FollowUpKnowledge,
    MonitoringKnowledge,
    PathogenKnowledge,
    RecommendationKnowledge,
    ReferralKnowledge,
    StewardshipKnowledge,
)
from app.knowledge.models.provenance import Provenance
from app.knowledge.providers.base_provider import KnowledgeProvider
from app.knowledge.providers.provider_types import ProviderHealthStatus, ProviderMetadata, ProviderSourceType
from app.knowledge.providers.query_models import KnowledgeQuery, SearchQuery


class WHOProvider(KnowledgeProvider):
    """WHO knowledge provider implementation backed by a repository."""

    def __init__(self, repository: WHOKnowledgeRepository) -> None:
        self.repository = repository
        self._metadata = ProviderMetadata(
            name="WHOProvider",
            description="WHO clinical knowledge provider for PharmaTrybe.",
            version="1.0.0",
            provider_type=ProviderSourceType.DATABASE,
            supported_entities=[
                "disease",
                "recommendation",
                "diagnostic",
                "monitoring",
                "pathogen",
                "evidence",
                "stewardship",
                "follow_up",
                "referral",
            ],
            capabilities=[
                "SEARCH",
                "GUIDELINES",
                "RECOMMENDATIONS",
                "MONITORING",
                "PATHOGENS",
                "EVIDENCE",
                "STEWARDSHIP",
                "FOLLOW_UP",
                "REFERRAL",
            ],
            supported_languages=["en"],
            priority=100,
        )

    def retrieve(self, query: KnowledgeQuery) -> KnowledgePackage:
        if query.entity_type in {"disease", "guideline"}:
            return self._retrieve_disease_package(query)

        if query.entity_type == "recommendation" and query.identifier is not None:
            return self._retrieve_recommendation_package(query.identifier)

        raise ValueError(f"WHOProvider does not support retrieval for entity_type={query.entity_type}")

    def search(self, query: SearchQuery) -> list[KnowledgePackage]:
        query_text = query.query_text or ""
        disease_results = self.repository.search_diseases(query_text)
        return [self._build_package_from_disease(disease) for disease in disease_results]

    def supports(self, query: Any) -> bool:
        if isinstance(query, KnowledgeQuery):
            return query.entity_type in {"disease", "guideline", "recommendation"}
        if isinstance(query, SearchQuery):
            return True
        return False

    def metadata(self) -> ProviderMetadata:
        return self._metadata

    def health(self) -> ProviderHealthStatus:
        return ProviderHealthStatus(
            healthy=True,
            checked_at=datetime.now(timezone.utc),
            details="WHO repository access is available.",
        )

    def version(self) -> str:
        return self._metadata.version

    def _retrieve_disease_package(self, query: KnowledgeQuery) -> KnowledgePackage:
        if query.identifier is None:
            disease_list = self.repository.list_diseases()
            packages = [self._build_package_from_disease(disease) for disease in disease_list]
            return KnowledgePackage(
                source="WHO",
                version=self.version(),
                provenance=self._build_provenance(query),
                diseases=[pkg.diseases for pkg in packages],
                metadata={"query": query},
            )

        disease = self.repository.get_complete_guideline(query.identifier)
        if disease is None:
            return KnowledgePackage(
                source="WHO",
                version=self.version(),
                provenance=self._build_provenance(query),
            )

        return self._build_package_from_disease(disease, query)

    def _retrieve_recommendation_package(self, recommendation_id: str) -> KnowledgePackage:
        recommendation = self.repository.get_recommendation_by_id(recommendation_id)
        if recommendation is None:
            return KnowledgePackage(
                source="WHO",
                version=self.version(),
                provenance=self._build_provenance(KnowledgeQuery(entity_type="recommendation", identifier=recommendation_id)),
            )

        disease_id = recommendation.disease_id
        disease = self.repository.get_complete_guideline(disease_id)
        knowledge_package = self._build_package_from_disease(disease) if disease else KnowledgePackage(
            source="WHO",
            version=self.version(),
            provenance=self._build_provenance(KnowledgeQuery(entity_type="recommendation", identifier=recommendation_id)),
        )
        return knowledge_package

    def _build_package_from_disease(self, disease: Any, query: KnowledgeQuery | None = None) -> KnowledgePackage:
        provenance = self._build_provenance(query if query is not None else KnowledgeQuery(entity_type="disease", identifier=disease.disease_id))
        recommendations = [
            RecommendationKnowledge(
                id=recommendation.recommendation_id,
                title=getattr(recommendation, "title", None),
                description=getattr(recommendation, "description", None),
                provenance=provenance,
                metadata={"drug_id": recommendation.drug_id, "population": recommendation.population, "severity": recommendation.severity},
                recommendation_id=recommendation.recommendation_id,
                disease_id=recommendation.disease_id,
                drug_id=recommendation.drug_id,
                population=recommendation.population,
                severity=recommendation.severity,
                evidence=[
                    EvidenceKnowledge(
                        id=evidence.evidence_id,
                        title=getattr(evidence, "title", None),
                        description=getattr(evidence, "description", None),
                        provenance=provenance,
                        metadata={"level": evidence.level if hasattr(evidence, "level") else None},
                        evidence_id=evidence.evidence_id,
                        disease_id=evidence.disease_id,
                        source=getattr(evidence, "source", "WHO"),
                        level=getattr(evidence, "level", None),
                    )
                    for evidence in getattr(disease, "evidence", []) or []
                ],
            )
            for recommendation in getattr(disease, "recommendations", []) or []
        ]

        return KnowledgePackage(
            source="WHO",
            version=self.version(),
            provenance=provenance,
            diseases=[
                DiseaseKnowledge(
                    id=disease.disease_id,
                    title=disease.name,
                    description=disease.description,
                    provenance=provenance,
                    metadata={"chapter_number": disease.chapter_number, "care_level": disease.care_level},
                    disease_id=disease.disease_id,
                    severity=None,
                    category=getattr(disease, "category", None),
                )
            ],
            recommendations=recommendations,
            diagnostics=[
                DiagnosticKnowledge(
                    id=diagnostic.diagnostic_id,
                    title=getattr(diagnostic, "title", None),
                    description=getattr(diagnostic, "description", None),
                    provenance=provenance,
                    metadata={},
                    disease_id=diagnostic.disease_id,
                    diagnostic_type=getattr(diagnostic, "diagnostic_type", None),
                    criteria=getattr(diagnostic, "criteria", None),
                )
                for diagnostic in getattr(disease, "diagnostics", []) or []
            ],
            pathogens=[
                PathogenKnowledge(
                    id=pathogen.pathogen_id,
                    title=pathogen.name,
                    description=getattr(pathogen, "description", None),
                    provenance=provenance,
                    metadata={},
                    pathogen_id=pathogen.pathogen_id,
                    taxonomy=getattr(pathogen, "taxonomy", None),
                    resistance_patterns={},
                )
                for pathogen in getattr(disease, "pathogens", []) or []
            ],
            evidence=[
                EvidenceKnowledge(
                    id=evidence.evidence_id,
                    title=getattr(evidence, "title", None),
                    description=getattr(evidence, "description", None),
                    provenance=provenance,
                    metadata={"level": evidence.level if hasattr(evidence, "level") else None},
                    evidence_id=evidence.evidence_id,
                    disease_id=evidence.disease_id,
                    source=getattr(evidence, "source", "WHO"),
                    level=getattr(evidence, "level", None),
                )
                for evidence in getattr(disease, "evidence", []) or []
            ],
            stewardship=[
                StewardshipKnowledge(
                    id=stewardship.stewardship_id,
                    title=getattr(stewardship, "title", None),
                    description=getattr(stewardship, "description", None),
                    provenance=provenance,
                    metadata={},
                    disease_id=stewardship.disease_id,
                    policy=getattr(stewardship, "policy", None),
                    guidance={"notes": getattr(stewardship, "notes", None)},
                )
                for stewardship in getattr(disease, "stewardship", []) or []
            ],
            monitoring=[
                MonitoringKnowledge(
                    id=monitoring.monitoring_id,
                    title=getattr(monitoring, "title", None),
                    description=getattr(monitoring, "description", None),
                    provenance=provenance,
                    metadata={},
                    disease_id=monitoring.disease_id,
                    monitoring_type=getattr(monitoring, "monitoring_type", None),
                    parameters={"instructions": getattr(monitoring, "instructions", None)},
                )
                for monitoring in getattr(disease, "monitoring", []) or []
            ],
            follow_up=[
                FollowUpKnowledge(
                    id=follow_up.follow_up_id,
                    title=getattr(follow_up, "title", None),
                    description=getattr(follow_up, "description", None),
                    provenance=provenance,
                    metadata={},
                    disease_id=follow_up.disease_id,
                    follow_up_type=getattr(follow_up, "follow_up_type", None),
                    instructions={"notes": getattr(follow_up, "instructions", None)},
                )
                for follow_up in getattr(disease, "follow_up", []) or []
            ],
            referral=[
                ReferralKnowledge(
                    id=referral.referral_id,
                    title=getattr(referral, "title", None),
                    description=getattr(referral, "description", None),
                    provenance=provenance,
                    metadata={},
                    disease_id=referral.disease_id,
                    criteria={"notes": getattr(referral, "criteria", None)},
                    referral_path=getattr(referral, "referral_path", None),
                )
                for referral in getattr(disease, "referral", []) or []
            ],
        )

    def _build_provenance(self, query: KnowledgeQuery | None = None) -> Provenance:
        return Provenance(
            source_name="WHO Knowledge Base",
            provider_name=self._metadata.name,
            provider_type=self._metadata.provider_type.value,
            version=self._metadata.version,
            publication_date=None,
            retrieval_timestamp=datetime.now(timezone.utc),
            confidence=1.0,
            citation="WHO AWaRe Knowledge Base",
            license="WHO License",
            trace_id=None,
            checksum=None,
            details={"entity_type": query.entity_type if query is not None else None, "identifier": query.identifier if query is not None else None},
        )
