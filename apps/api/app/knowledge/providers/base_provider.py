"""Knowledge provider base interfaces for PharmaTrybe."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.knowledge.models.knowledge_bundle import KnowledgePackage
from app.knowledge.providers.provider_types import ProviderHealthStatus, ProviderMetadata
from app.knowledge.providers.query_models import KnowledgeQuery, SearchQuery


class KnowledgeProvider(ABC):
    """Abstract contract for generic knowledge providers."""

    @abstractmethod
    def retrieve(self, query: KnowledgeQuery) -> KnowledgePackage:
        """Retrieve structured knowledge for a provider query."""

    @abstractmethod
    def search(self, query: SearchQuery) -> list[KnowledgePackage]:
        """Search knowledge within a provider."""

    @abstractmethod
    def supports(self, query: Any) -> bool:
        """Determine whether the provider can fulfill the query."""

    @abstractmethod
    def metadata(self) -> ProviderMetadata:
        """Return provider metadata."""

    @abstractmethod
    def health(self) -> ProviderHealthStatus:
        """Return a health snapshot for the provider."""

    @abstractmethod
    def version(self) -> str:
        """Return the provider version identifier."""
