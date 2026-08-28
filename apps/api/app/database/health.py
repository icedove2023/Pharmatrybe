"""Database health helpers for the PharmaTrybe backend scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass(slots=True)
class DatabaseHealthStatus:
    """Simple descriptor for the current database integration state."""

    configured: bool
    healthy: bool
    detail: str


def check_database_health() -> DatabaseHealthStatus:
    """Return a placeholder health status for the database integration layer."""
    configured = bool(settings.database_url)
    return DatabaseHealthStatus(
        configured=configured,
        healthy=configured,
        detail="Database integration scaffold is ready for future connections" if configured else "Database URL is not configured",
    )
