from __future__ import annotations

from types import SimpleNamespace
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session

from app.auth.dependencies import AuthorizationContext, get_authorization_context
from app.database.base import Base
from app.database.session import get_db_session
from app.main import app
from app.models.identity import Hospital
from app.models.plugin_governance import PluginGovernanceAuditEvent, PluginGovernanceRecord


def _session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine, tables=[Hospital.__table__, PluginGovernanceRecord.__table__, PluginGovernanceAuditEvent.__table__])
    session = Session(engine)
    session.add(Hospital(id="00000000-0000-0000-0000-000000000001", name="Hospital"))
    session.commit()
    return session


def _context(roles: set[str], permissions: set[str]) -> AuthorizationContext:
    context = object.__new__(AuthorizationContext)
    context.user = SimpleNamespace(user_id="u-1")
    context.membership = SimpleNamespace(hospital_id="00000000-0000-0000-0000-000000000001")
    context.roles = roles
    context.permissions = permissions
    context._hospital_id = "h-1"
    context._user_id = "u-1"
    return context


def test_governance_api_rejects_unauthenticated_request() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/plugins")
    assert response.status_code == 401


def test_governance_api_requires_role_and_permission() -> None:
    session = _session()
    app.dependency_overrides[get_db_session] = lambda: session
    try:
        for context in (_context({"CLINICIAN"}, set()), _context({"HOSPITAL_ADMIN"}, set())):
            app.dependency_overrides[get_authorization_context] = lambda context=context: context
            response = TestClient(app).get("/api/v1/plugins")
            assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()
        session.close()


def test_governance_api_accepts_authorized_registration() -> None:
    session = _session()
    app.dependency_overrides[get_db_session] = lambda: session
    app.dependency_overrides[get_authorization_context] = lambda: _context({"HOSPITAL_ADMIN"}, {"plugins:configure"})
    try:
        response = TestClient(app).post(
            "/api/v1/plugins",
            json={
                "plugin_id": "external",
                "plugin_name": "External",
                "plugin_type": "knowledge",
                "plugin_version": "1.0.0",
                "owner": "Hospital",
                "publisher": "Hospital",
                "artifact_hash": "a" * 64,
                "capabilities": [],
            },
        )
        assert response.status_code == 201
        assert response.json()["status"] == "REGISTERED"
    finally:
        app.dependency_overrides.clear()
        session.close()
