"""Registry describing the platform services that the backend will eventually orchestrate."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ServiceHealthStatus:
    """Simple health descriptor for a platform service."""

    name: str
    version: str
    enabled: bool = True
    healthy: bool = True
    endpoint: str = ""


SERVICE_HEALTH_REGISTRY: list[ServiceHealthStatus] = [
    ServiceHealthStatus(name="SOAR", version="0.1.0", endpoint="", enabled=True, healthy=True),
    ServiceHealthStatus(name="ARMD", version="0.1.0", endpoint="", enabled=True, healthy=True),
    ServiceHealthStatus(name="WHO", version="0.1.0", endpoint="", enabled=True, healthy=True),
    ServiceHealthStatus(name="Decision Engine", version="0.1.0", endpoint="", enabled=True, healthy=True),
    ServiceHealthStatus(name="Explainability", version="0.1.0", endpoint="", enabled=True, healthy=True),
]


def get_service_health_registry() -> list[ServiceHealthStatus]:
    """Return the service registry for future health monitoring."""
    return SERVICE_HEALTH_REGISTRY
