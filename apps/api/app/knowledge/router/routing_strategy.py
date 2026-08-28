"""Routing strategy abstractions for PharmaTrybe knowledge providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.knowledge.providers.base_provider import KnowledgeProvider
from app.knowledge.router.provider_registry import ProviderRegistry
from app.knowledge.router.routing_models import ProviderRouteQuery


class RoutingStrategy(ABC):
    """Abstract routing strategy for knowledge providers."""

    @abstractmethod
    def route(self, query: ProviderRouteQuery | None, registry: ProviderRegistry) -> list[KnowledgeProvider]:
        """Return ordered providers for a route query."""


class DefaultRoutingStrategy(RoutingStrategy):
    """Default routing strategy for knowledge providers."""

    def route(self, query: ProviderRouteQuery | None, registry: ProviderRegistry) -> list[KnowledgeProvider]:
        providers = registry.find_by_query(query)
        return sorted(providers, key=lambda provider: provider.metadata().priority, reverse=True)
