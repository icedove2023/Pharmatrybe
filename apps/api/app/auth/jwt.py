"""Supabase JWT verification helpers for the FastAPI authentication boundary."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKClientError

from app.core.config import settings


class TokenVerificationError(ValueError):
    """Raised when an incoming token is malformed or cannot be trusted."""


def _required_auth_configuration() -> tuple[str, str, str, list[str]]:
    """Return required Supabase verification settings or fail closed."""
    missing = [
        name
        for name, value in (
            ("SUPABASE_JWT_ISSUER", settings.supabase_jwt_issuer),
            ("SUPABASE_JWT_AUDIENCE", settings.supabase_jwt_audience),
            ("SUPABASE_JWKS_URL", settings.supabase_jwks_url),
        )
        if not value
    ]
    algorithms = [item.strip() for item in settings.supabase_jwt_algorithms.split(",") if item.strip()]
    if not algorithms:
        missing.append("SUPABASE_JWT_ALGORITHMS")
    if missing:
        raise TokenVerificationError(f"Supabase JWT configuration is incomplete: {', '.join(missing)}")
    return settings.supabase_jwt_issuer, settings.supabase_jwt_audience, settings.supabase_jwks_url, algorithms


@lru_cache(maxsize=4)
def _jwks_client(jwks_url: str) -> PyJWKClient:
    """Cache the JWKS client while allowing deployment URL changes in tests."""
    return PyJWKClient(jwks_url)


def verify_token(token: str) -> dict[str, Any]:
    """Verify a Supabase JWT signature and required registered claims."""
    if not token:
        raise TokenVerificationError("Token is required")

    issuer, audience, jwks_url, algorithms = _required_auth_configuration()
    try:
        signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=algorithms,
            issuer=issuer,
            audience=audience,
            options={"require": ["exp", "iat", "iss", "aud", "sub"]},
        )
    except (InvalidTokenError, PyJWKClientError, ValueError) as exc:
        raise TokenVerificationError("Token verification failed") from exc

    if not claims.get("sub"):
        raise TokenVerificationError("Token subject is required")
    return claims
