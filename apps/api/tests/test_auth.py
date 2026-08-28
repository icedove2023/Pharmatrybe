from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
import jwt
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request

from app.auth.current_user import AuthenticatedUser
from app.auth.dependencies import (
    get_current_user,
    require_permission,
)
from app.auth.jwt import TokenVerificationError, verify_token
from app.auth.roles import PharmaTrybeRole, normalize_role
from app.auth.security import get_bearer_token
from app.core.config import settings
from cryptography.hazmat.primitives.asymmetric import rsa


ISSUER = "https://auth.example.test"
AUDIENCE = "authenticated"
JWKS_URL = "https://auth.example.test/.well-known/jwks.json"
USER_ID = "user-123"


@pytest.fixture(scope="module")
def rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


@pytest.fixture
def configured_verifier(monkeypatch):
    monkeypatch.setattr(settings, "supabase_jwt_issuer", ISSUER)
    monkeypatch.setattr(settings, "supabase_jwt_audience", AUDIENCE)
    monkeypatch.setattr(settings, "supabase_jwks_url", JWKS_URL)
    monkeypatch.setattr(settings, "supabase_jwt_algorithms", "RS256")
    return settings


def _claims(**overrides):
    claims = {
        "sub": USER_ID,
        "email": "user@example.com",
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }
    claims.update(overrides)
    return claims


def _token(private_key, **overrides):
    return jwt.encode(_claims(**overrides), private_key, algorithm="RS256", headers={"kid": "test-key"})


def _patch_jwks(monkeypatch, public_key):
    monkeypatch.setattr(
        "app.auth.jwt._jwks_client",
        lambda _url: SimpleNamespace(get_signing_key_from_jwt=lambda _token: SimpleNamespace(key=public_key)),
    )


def test_role_enum_values_are_expected():
    assert PharmaTrybeRole.CLINICIAN.value == "Clinician"
    assert PharmaTrybeRole.ADMINISTRATOR.value == "Administrator"
    assert PharmaTrybeRole.LABORATORY_SCIENTIST.value == "Laboratory Scientist"
    assert PharmaTrybeRole.STEWARDSHIP_TEAM.value == "Stewardship Team"


def test_normalize_role_returns_enum_for_text():
    assert normalize_role("clinician") == PharmaTrybeRole.CLINICIAN
    assert normalize_role("ADMINISTRATOR") == PharmaTrybeRole.ADMINISTRATOR
    assert normalize_role("unknown") is None


def test_permission_helpers_attach_and_retrieve_markers():
    def sample_function():
        pass

    from app.auth.permissions import require_permission, get_required_permission, Permission

    decorated = require_permission(Permission.READ_API)(sample_function)

    assert get_required_permission(decorated) == Permission.READ_API.value
    assert get_required_permission(sample_function) is None


def test_verify_token_rejects_missing_token():
    with pytest.raises(TokenVerificationError):
        verify_token("")


def test_verify_token_fails_closed_when_configuration_is_missing(monkeypatch):
    monkeypatch.setattr(settings, "supabase_jwt_issuer", "")
    monkeypatch.setattr(settings, "supabase_jwt_audience", AUDIENCE)
    monkeypatch.setattr(settings, "supabase_jwks_url", JWKS_URL)

    with pytest.raises(TokenVerificationError, match="SUPABASE_JWT_ISSUER"):
        verify_token("malformed")


def test_verify_token_rejects_malformed_token(configured_verifier, rsa_keys, monkeypatch):
    _patch_jwks(monkeypatch, rsa_keys[1])

    with pytest.raises(TokenVerificationError):
        verify_token("not-a-jwt")


def test_verify_token_rejects_missing_subject(configured_verifier, rsa_keys, monkeypatch):
    _patch_jwks(monkeypatch, rsa_keys[1])
    token = _token(rsa_keys[0], sub=None)

    with pytest.raises(TokenVerificationError):
        verify_token(token)


def test_verify_token_rejects_expired_token(configured_verifier, rsa_keys, monkeypatch):
    _patch_jwks(monkeypatch, rsa_keys[1])
    token = _token(rsa_keys[0], exp=datetime.now(timezone.utc) - timedelta(minutes=1))

    with pytest.raises(TokenVerificationError):
        verify_token(token)


@pytest.mark.parametrize("claim, value", [("iss", "https://wrong.example.test"), ("aud", "wrong-audience")])
def test_verify_token_rejects_invalid_registered_claims(configured_verifier, rsa_keys, monkeypatch, claim, value):
    _patch_jwks(monkeypatch, rsa_keys[1])
    token = _token(rsa_keys[0], **{claim: value})

    with pytest.raises(TokenVerificationError):
        verify_token(token)


def test_verify_token_rejects_invalid_signature(configured_verifier, rsa_keys, monkeypatch):
    other_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    _patch_jwks(monkeypatch, rsa_keys[1])
    token = _token(other_private_key)

    with pytest.raises(TokenVerificationError):
        verify_token(token)


def test_verify_token_rejects_unsupported_algorithm(configured_verifier, rsa_keys, monkeypatch):
    _patch_jwks(monkeypatch, rsa_keys[1])
    token = jwt.encode(_claims(), rsa_keys[0], algorithm="RS512", headers={"kid": "test-key"})

    with pytest.raises(TokenVerificationError):
        verify_token(token)


def test_verify_token_accepts_valid_jwks_signature(configured_verifier, rsa_keys, monkeypatch):
    _patch_jwks(monkeypatch, rsa_keys[1])
    token = _token(rsa_keys[0])

    claims = verify_token(token)

    assert claims["sub"] == USER_ID


def test_get_current_user_uses_subject_only_and_ignores_role_claim(configured_verifier, rsa_keys, monkeypatch):
    token = _token(rsa_keys[0], role="HOSPITAL_ADMIN")
    request = Request({"type": "http", "method": "GET", "path": "/auth/me", "headers": []})

    monkeypatch.setattr("app.auth.dependencies.get_bearer_token", lambda credentials: token)
    monkeypatch.setattr("app.auth.dependencies.verify_token", lambda _token: _claims(role="HOSPITAL_ADMIN"))

    user = asyncio.run(
        get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token), request)
    )

    assert isinstance(user, AuthenticatedUser)
    assert user.user_id == USER_ID
    assert user.email == "user@example.com"
    assert user.role is None
    assert user.active is True


def test_permission_dependency_is_backend_context_based():
    assert callable(require_permission("cases:view"))
    assert PharmaTrybeRole.CLINICIAN.value == "Clinician"


def test_dependency_objects_import_correctly():
    assert callable(get_current_user)
    assert callable(get_bearer_token)
