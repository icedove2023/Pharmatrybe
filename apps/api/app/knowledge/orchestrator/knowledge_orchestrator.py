"""Knowledge orchestrator layer for PharmaTrybe."""

from __future__ import annotations

import time
from typing import Any

from app.knowledge.models.provider_result import ProviderResult
from app.knowledge.providers.base_provider import KnowledgeProvider
from app.knowledge.providers.query_models import KnowledgeQuery, ProviderCapabilityQuery, SearchQuery
from app.knowledge.router.knowledge_router import KnowledgeRouter
from app.knowledge.router.routing_models import ProviderCapability, ProviderRouteQuery


class KnowledgeOrchestrator:
    """Orchestrates provider query execution through the knowledge router."""

    def __init__(self, router: KnowledgeRouter) -> None:
        self.router = router

    def retrieve(self, query: KnowledgeQuery) -> list[ProviderResult]:
        route_query = self._build_route_query(query)
        providers = self.router.get_providers(route_query)
        return [self._execute_provider(provider, query) for provider in providers]

    def search(self, query: SearchQuery) -> list[ProviderResult]:
        route_query = self._build_route_query(query)
        providers = self.router.get_providers(route_query)
        return [self._execute_provider(provider, query) for provider in providers]

    def _build_route_query(self, query: KnowledgeQuery | SearchQuery) -> ProviderRouteQuery:
        if isinstance(query, KnowledgeQuery):
            capability = self._capability_for_entity_type(query.entity_type)
            return ProviderRouteQuery(entity_type=query.entity_type, capabilities=[capability] if capability else None)

        if isinstance(query, SearchQuery):
            capabilities = [ProviderCapability.SEARCH]
            return ProviderRouteQuery(entity_type=query.entity_type, capabilities=capabilities)

        raise ValueError(f"Unsupported query type: {type(query).__name__}")

    def _capability_for_entity_type(self, entity_type: str | None) -> ProviderCapability | None:
        if entity_type is None:
            return ProviderCapability.SEARCH

        mapping: dict[str, ProviderCapability] = {
            "disease": ProviderCapability.GUIDELINES,
            "guideline": ProviderCapability.GUIDELINES,
            "recommendation": ProviderCapability.RECOMMENDATIONS,
            "monitoring": ProviderCapability.MONITORING,
            "pathogen": ProviderCapability.PATHOGENS,
            "evidence": ProviderCapability.EVIDENCE,
            "stewardship": ProviderCapability.STEWARDSHIP,
            "follow_up": ProviderCapability.FOLLOW_UP,
            "referral": ProviderCapability.REFERRAL,
        }
        return mapping.get(entity_type.lower())

    def _execute_provider(self, provider: KnowledgeProvider, query: Any) -> ProviderResult:
        start = time.monotonic()
        try:
            if isinstance(query, KnowledgeQuery):
                package = provider.retrieve(query)
            elif isinstance(query, SearchQuery):
                package = provider.search(query)
            else:
                raise ValueError(f"Unsupported query type: {type(query).__name__}")

            status = "success"
            errors: list[str] | None = None
            warnings: list[str] | None = None
        except Exception as exc:
            package = None
            status = "failure"
            errors = [str(exc)]
            warnings = None

        elapsed_ms = (time.monotonic() - start) * 1000.0

        provenance = None
        if package is not None and not isinstance(package, list):
            provenance = package.provenance

        return ProviderResult(
            provider_metadata=provider.metadata(),
            knowledge_package=package,
            provenance=provenance,
            execution_time_ms=elapsed_ms,
            status=status,
            warnings=warnings,
            errors=errors,
            query=query,
        )
