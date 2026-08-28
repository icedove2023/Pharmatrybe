"""Provider metadata and health models for PharmaTrybe."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ProviderSourceType(str, Enum):
    DATABASE = "database"
    INFERENCE_ENGINE = "inference_engine"
    API_SERVICE = "api_service"
    VECTOR_STORE = "vector_store"
    LLM_PLUGIN = "llm_plugin"
    LOCAL_GUIDELINE_SERVICE = "local_guideline_service"


@dataclass(frozen=True)
class ProviderMetadata:
    name: str
    description: str
    version: str
    provider_type: ProviderSourceType
    supported_entities: list[str]
    capabilities: list[str]
    supported_languages: list[str]
    priority: int = 0
    effective_date: datetime | None = None


@dataclass(frozen=True)
class ProviderHealthStatus:
    healthy: bool
    checked_at: datetime
    details: str | None = None
