"""Security helpers and placeholders for future authentication work."""

from app.core.config import settings


def get_jwt_secret() -> str:
    """Return the configured JWT secret placeholder."""
    return settings.jwt_secret
