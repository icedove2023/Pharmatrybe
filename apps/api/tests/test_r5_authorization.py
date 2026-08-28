from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api.v1.clinical_cases import router as clinical_cases_router
from app.api.v1.recommendations import router as recommendations_router
from app.auth.current_user import AuthenticatedUser
from app.auth.dependencies import (
    AuthorizationContext,
    deny_by_default,
    get_authorization_context,
    get_current_user,
    require_permission,
    require_same_hospital,
)
from app.auth.rbac_catalog import CANONICAL_ROLE_CODES


def _request() -> Request:
    return Request({"type": "http", "method": "GET", "path": "/protected", "headers": []})


def _professional(*memberships, status: str = "ACTIVE"):
    return SimpleNamespace(
        auth_user_id="auth-user",
        profile_status=status,
        memberships=list(memberships),
    )


def _membership(role_codes: list[str], status: str = "ACTIVE"):
    roles = [SimpleNamespace(role=SimpleNamespace(code=code, role_permissions=[])) for code in role_codes]
    return SimpleNamespace(status=status, hospital_id="hospital-a", hospital=SimpleNamespace(name="Hospital A"), roles=roles)


def _resolve_context(professional):
    db = MagicMock()
    db.scalar.return_value = professional
    user = AuthenticatedUser(user_id="auth-user", email="user@example.com")
    return asyncio.run(get_authorization_context(user, db, _request()))


def test_missing_profile_fails_closed():
    with pytest.raises(HTTPException) as error:
        _resolve_context(None)
    assert error.value.status_code == 403


def test_inactive_profile_fails_closed():
    with pytest.raises(HTTPException) as error:
        _resolve_context(_professional(status="INACTIVE"))
    assert error.value.status_code == 403


def test_missing_or_inactive_membership_fails_closed():
    for memberships in ([], [_membership(["CLINICIAN"], status="SUSPENDED")]):
        with pytest.raises(HTTPException) as error:
            _resolve_context(_professional(*memberships))
        assert error.value.status_code == 403


def test_multiple_active_memberships_fail_closed():
    with pytest.raises(HTTPException) as error:
        _resolve_context(_professional(_membership(["CLINICIAN"]), _membership(["CLINICIAN"])))
    assert error.value.status_code == 403


def test_missing_or_unknown_role_fails_closed():
    for role_codes in ([], ["NOT_CANONICAL"]):
        with pytest.raises(HTTPException) as error:
            _resolve_context(_professional(_membership(role_codes)))
        assert error.value.status_code == 403


def test_context_role_resolution_uses_only_canonical_codes():
    context = _resolve_context(_professional(_membership(["CLINICIAN"])))
    assert context.roles == {"CLINICIAN"}
    assert context.hospital_id == "hospital-a"
    assert context.roles.issubset(set(CANONICAL_ROLE_CODES))


def test_missing_permission_returns_403():
    context = AuthorizationContext(
        AuthenticatedUser(user_id="auth-user"),
        SimpleNamespace(),
        SimpleNamespace(hospital_id="hospital-a", hospital=SimpleNamespace(name="Hospital A")),
        {"CLINICIAN"},
        {"cases:view"},
    )
    checker = require_permission("professionals:manage")
    with pytest.raises(HTTPException) as error:
        asyncio.run(checker(context))
    assert error.value.status_code == 403


def test_uncontracted_operation_is_denied_by_default():
    with pytest.raises(HTTPException) as error:
        asyncio.run(deny_by_default(AuthorizationContext(
            AuthenticatedUser(user_id="auth-user"),
            SimpleNamespace(),
            SimpleNamespace(hospital_id="hospital-a", hospital=SimpleNamespace(name="Hospital A")),
            {"CLINICIAN"},
            {"cases:view"},
        )))
    assert error.value.status_code == 403


def test_cross_hospital_context_is_denied():
    context = AuthorizationContext(
        AuthenticatedUser(user_id="auth-user"),
        SimpleNamespace(),
        SimpleNamespace(hospital_id="hospital-a", hospital=SimpleNamespace(name="Hospital A")),
        {"CLINICIAN"},
        {"cases:view"},
    )
    checker = require_same_hospital("hospital-b")
    with pytest.raises(HTTPException) as error:
        asyncio.run(checker(context))
    assert error.value.status_code == 403


def test_missing_bearer_token_is_401():
    credentials = SimpleNamespace(credentials=None)
    with pytest.raises(HTTPException) as error:
        asyncio.run(get_current_user(credentials, _request()))
    assert error.value.status_code == 401


def test_protected_routes_have_backend_dependencies():
    clinical_routes = {route.path: route for route in clinical_cases_router.routes if hasattr(route, "dependant")}
    recommendation_routes = {route.path: route for route in recommendations_router.routes if hasattr(route, "dependant")}

    assert any(dependency.call.__name__ == "permission_checker" for dependency in clinical_routes["/clinical-cases"].dependant.dependencies)
    assert any(dependency.call.__name__ == "permission_checker" for dependency in recommendation_routes["/recommendations/generate"].dependant.dependencies)
    assert any(dependency.call.__name__ == "deny_by_default" for dependency in clinical_routes["/clinical-cases/{case_id}"].dependant.dependencies)