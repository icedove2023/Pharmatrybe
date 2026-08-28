"""Configuration helpers for the Supabase authentication boundary."""

from app.core.config import settings


def get_jwt_verification_config() -> dict[str, str]:
    """Return non-secret Supabase JWT verification configuration."""
    return {
        "issuer": settings.supabase_jwt_issuer,
        "audience": settings.supabase_jwt_audience,
        "jwks_url": settings.supabase_jwks_url,
        "algorithms": settings.supabase_jwt_algorithms,
    }
