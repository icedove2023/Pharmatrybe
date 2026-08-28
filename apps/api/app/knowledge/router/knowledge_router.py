"""Router for PharmaTrybe knowledge providers."""

from __future__ import annotations

from app.knowledge.providers.base_provider import KnowledgeProvider
from app.knowledge.router.provider_registry import ProviderRegistry
from app.knowledge.router.routing_models import ProviderRouteQuery
from app.knowledge.router.routing_strategy import RoutingStrategy, DefaultRoutingStrategy


class KnowledgeRouter:
    """Router that delegates provider selection to a registry and strategy."""

    def __init__(
        self,
        registry: ProviderRegistry | None = None,
        strategy: RoutingStrategy | None = None,
    ) -> None:
        self.registry = registry or ProviderRegistry()
        self.strategy = strategy or DefaultRoutingStrategy()

    def register_provider(self, provider: KnowledgeProvider) -> None:
        self.registry.register(provider)

    def unregister_provider(self, provider: KnowledgeProvider) -> None:
        self.registry.unregister(provider)

    def get_providers(self, query: ProviderRouteQuery | None = None) -> list[KnowledgeProvider]:
        return self.strategy.route(query, self.registry)

    def get_provider_by_name(self, name: str) -> KnowledgeProvider | None:
        return self.registry.find_by_name(name)

    def health(self) -> list[tuple[str, bool]]:
        return self.registry.health()
