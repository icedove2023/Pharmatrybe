"""Base class for PharmaTrybe platform service clients."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.config import settings


@dataclass(slots=True)
class ServiceMetadata:
    """Structural metadata describing a backend service client."""

    name: str
    version: str
    endpoint: str
    enabled: bool = True
    healthy: bool = True


class BaseService:
    """Common foundation for all PharmaTrybe service clients.

    This class intentionally defines only architectural placeholders for timeout,
    retry, metadata, and availability state. No transport or business logic is
    implemented here.
    """

    def __init__(self, name: str, version: str = "0.1.0", endpoint: str = "") -> None:
        self.name = name
        self.version = version
        self.endpoint = endpoint or ""
        self.timeout_seconds = 5.0
        self.retry_count = 0
        self.retry_backoff_seconds = 0.0
        self.enabled = True
        self.healthy = True
        self.metadata = ServiceMetadata(
            name=name,
            version=version,
            endpoint=endpoint,
            enabled=self.enabled,
            healthy=self.healthy,
        )
        self.settings = settings

    def get_metadata(self) -> ServiceMetadata:
        """Return the metadata for the current service client."""
        return ServiceMetadata(
            name=self.name,
            version=self.version,
            endpoint=self.endpoint,
            enabled=self.enabled,
            healthy=self.healthy,
        )

    def set_availability(self, healthy: bool) -> None:
        """Update the service availability state."""
        self.healthy = healthy
        self.metadata.healthy = healthy

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Placeholder request execution interface for future transport layers."""
        raise NotImplementedError("Transport execution is not implemented in the architecture bootstrap")
