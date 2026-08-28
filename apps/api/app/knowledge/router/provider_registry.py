"""Provider registry for plugin-style knowledge providers."""

from __future__ import annotations

from app.knowledge.providers.base_provider import KnowledgeProvider
from app.knowledge.router.routing_models import ProviderCapability, ProviderRouteQuery


class ProviderRegistry:
    """Registry that manages knowledge provider registrations."""

    def __init__(self, providers: list[KnowledgeProvider] | None = None) -> None:
        self._providers = providers.copy() if providers is not None else []

    def register(self, provider: KnowledgeProvider) -> None:
        if provider not in self._providers:
            self._providers.append(provider)

    def unregister(self, provider: KnowledgeProvider) -> None:
        self._providers = [existing for existing in self._providers if existing is not provider]

    def list(self) -> list[KnowledgeProvider]:
        return self._providers.copy()

    def find_by_name(self, name: str) -> KnowledgeProvider | None:
        for provider in self._providers:
            if provider.metadata().name == name:
                return provider
        return None

    def find_by_query(self, query: ProviderRouteQuery | None = None) -> list[KnowledgeProvider]:
        providers = self._providers
        if query is None:
            return providers.copy()

        if query.capabilities:
            requested_capabilities = {cap.value.upper() for cap in query.capabilities}
            providers = [
                provider
                for provider in providers
                if requested_capabilities.issubset({cap.upper() for cap in provider.metadata().capabilities})
            ]

        if query.entity_type is not None:
            providers = [
                provider
                for provider in providers
                if query.entity_type in provider.metadata().supported_entities
            ]

        return providers

    def health(self) -> list[tuple[str, bool]]:
        return [(provider.metadata().name, provider.health().healthy) for provider in self._providers]
