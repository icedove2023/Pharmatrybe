"""Routing models for PharmaTrybe knowledge providers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ProviderCapability(str, Enum):
    SEARCH = "SEARCH"
    GUIDELINES = "GUIDELINES"
    RECOMMENDATIONS = "RECOMMENDATIONS"
    MONITORING = "MONITORING"
    PATHOGENS = "PATHOGENS"
    EVIDENCE = "EVIDENCE"
    STEWARDSHIP = "STEWARDSHIP"
    FOLLOW_UP = "FOLLOW_UP"
    REFERRAL = "REFERRAL"


@dataclass(frozen=True)
class ProviderRouteQuery:
    entity_type: str | None = None
    identifier: str | None = None
    filters: dict[str, Any] | None = None
    capabilities: list[ProviderCapability] | None = None
