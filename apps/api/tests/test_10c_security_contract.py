from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.auth.dependencies import AuthorizationContext, get_authorization_context, require_permission, require_same_hospital
from app.auth.current_user import AuthenticatedUser


def _request() -> Request:
    return Request({"type": "http", "method": "GET", "path": "/protected", "headers": []})


def _membership(role_codes: list[str], *, status: str = "ACTIVE"):
    roles = [
        SimpleNamespace(
            role=SimpleNamespace(
                code=code,
                role_permissions=[
                    SimpleNamespace(permission=SimpleNamespace(code="cases:view" if code == "CLINICIAN" else "guidelines:view"))
                ],
            )
        )
        for code in role_codes
    ]
    return SimpleNamespace(
        status=status,
        hospital_id="hospital-a",
        hospital=SimpleNamespace(name="Hospital A"),
        roles=roles,
    )


def _professional(*memberships, profile_status: str = "ACTIVE"):
    return SimpleNamespace(
        auth_user_id="auth-user",
        profile_status=profile_status,
        id="professional-1",
        memberships=list(memberships),
    )


def test_10c_authentication_requires_verified_supabase_identity():
    db = SimpleNamespace(scalar=lambda _query: None)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_authorization_context(AuthenticatedUser(user_id="auth-user"), db, _request()))
    assert exc.value.status_code == 403


def test_10c_rbac_resolves_permissions_through_membership_roles_then_role_permissions():
    professional = _professional(_membership(["CLINICIAN"]))
    db = SimpleNamespace(scalar=lambda _query: professional)
    context = asyncio.run(get_authorization_context(AuthenticatedUser(user_id="auth-user", email="user@example.com"), db, _request()))

    assert context.hospital_id == "hospital-a"
    assert context.roles == {"CLINICIAN"}
    assert "cases:view" in context.permissions
    assert "cases:create" not in context.permissions


def test_10c_client_supplied_hospital_id_cannot_override_authoritative_tenant():
    context = AuthorizationContext(
        AuthenticatedUser(user_id="auth-user"),
        SimpleNamespace(id="professional-1"),
        SimpleNamespace(hospital_id="hospital-a", hospital=SimpleNamespace(name="Hospital A")),
        {"CLINICIAN"},
        {"cases:view"},
    )

    with pytest.raises(HTTPException):
        asyncio.run(require_same_hospital("hospital-b")(context))


def test_10c_missing_permission_is_rejected_even_for_authenticated_user():
    context = AuthorizationContext(
        AuthenticatedUser(user_id="auth-user"),
        SimpleNamespace(id="professional-1"),
        SimpleNamespace(hospital_id="hospital-a", hospital=SimpleNamespace(name="Hospital A")),
        {"CLINICIAN"},
        {"cases:view"},
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(require_permission("roles:assign")(context))
    assert exc.value.status_code == 403


def test_10c_inactive_membership_and_inactive_profile_fail_closed():
    inactive_profile = _professional(_membership(["CLINICIAN"], status="SUSPENDED"), profile_status="ACTIVE")
    db = SimpleNamespace(scalar=lambda _query: inactive_profile)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_authorization_context(AuthenticatedUser(user_id="auth-user"), db, _request()))
    assert exc.value.status_code == 403

    inactive_profile_state = _professional(_membership(["CLINICIAN"]), profile_status="INACTIVE")
    db = SimpleNamespace(scalar=lambda _query: inactive_profile_state)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_authorization_context(AuthenticatedUser(user_id="auth-user"), db, _request()))
    assert exc.value.status_code == 403
