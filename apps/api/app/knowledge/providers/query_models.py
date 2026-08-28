"""Generic query models for knowledge provider operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PaginationParams:
    limit: int | None = None
    offset: int | None = None


@dataclass(frozen=True)
class SortParams:
    sort_by: str | None = None
    sort_order: str = "asc"


@dataclass(frozen=True)
class FilterParams:
    field: str
    value: Any


@dataclass(frozen=True)
class KnowledgeQuery:
    entity_type: str | None = None
    identifier: str | None = None
    filters: list[FilterParams] | None = None
    pagination: PaginationParams | None = None
    sort: SortParams | None = None
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class EntityQuery:
    entity_type: str
    identifier: str | None = None
    filters: list[FilterParams] | None = None
    pagination: PaginationParams | None = None
    sort: SortParams | None = None
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class SearchQuery:
    query_text: str
    entity_type: str | None = None
    pagination: PaginationParams | None = None
    sort: SortParams | None = None
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class ProviderCapabilityQuery:
    operation: str
    entity_type: str | None = None
    parameters: dict[str, Any] | None = None
