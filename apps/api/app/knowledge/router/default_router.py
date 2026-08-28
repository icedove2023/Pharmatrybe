"""Default router builder for PharmaTrybe knowledge providers."""

from __future__ import annotations

from app.database.repositories.who_knowledge_repository import WHOKnowledgeRepository
from app.knowledge.providers.who_provider import WHOProvider
from app.knowledge.router.knowledge_router import KnowledgeRouter
from app.knowledge.router.provider_registry import ProviderRegistry
from app.knowledge.router.routing_strategy import DefaultRoutingStrategy


def build_default_router(session) -> KnowledgeRouter:
    repository = WHOKnowledgeRepository(session)
    who_provider = WHOProvider(repository)
    registry = ProviderRegistry([who_provider])
    router = KnowledgeRouter(registry=registry, strategy=DefaultRoutingStrategy())
    return router
