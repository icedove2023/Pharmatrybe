"""Security helpers for PharmaTrybe authentication scaffolding."""

from __future__ import annotations

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class BearerAuthentication(HTTPBearer):
    """Bearer token scheme for future protected endpoints."""

    def __init__(self) -> None:
        super().__init__(auto_error=False)


bearer_scheme = BearerAuthentication()


def get_bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str | None:
    """Return the bearer token from an authorization header when present."""
    if credentials is None:
        return None
    return credentials.credentials
