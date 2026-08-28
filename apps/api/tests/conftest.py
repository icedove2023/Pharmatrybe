"""Shared pytest fixtures for PharmaTrybe backend tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.schemas.clinical_case import ClinicalCaseRequest


@pytest.fixture(scope="session")
def test_app() -> TestClient:
    """Create a shared FastAPI TestClient for the backend application."""
    from app.main import app

    return TestClient(app)


@pytest.fixture
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Return a generic mock settings object for configuration overrides."""
    mock_settings = MagicMock(name="MockSettings")
    monkeypatch.setattr("app.core.config.settings", mock_settings, raising=False)
    return mock_settings


@pytest.fixture
def mock_db_session() -> MagicMock:
    """Return a reusable mock database session for repository tests."""
    return MagicMock(name="MockDatabaseSession")


@pytest.fixture
def mock_repository(mock_db_session: MagicMock) -> MagicMock:
    """Return a generic mock repository bound to a mock database session."""
    repository = MagicMock(name="MockRepository")
    repository.session = mock_db_session
    return repository


@pytest.fixture
def mock_service(mock_repository: MagicMock) -> MagicMock:
    """Return a generic mock service bound to a mock repository."""
    service = MagicMock(name="MockService")
    service.repository = mock_repository
    return service


@pytest.fixture
def mock_authenticated_user() -> MagicMock:
    """Return a generic authenticated user context object."""
    return MagicMock(
        name="AuthenticatedUser",
        user_id="user-123",
        email="user@example.com",
        role="clinician",
        active=True,
    )


@pytest.fixture
def sample_clinical_case_payload() -> dict[str, Any]:
    """Return a reusable sample clinical case payload for backend tests."""
    return {
        "request_id": str(uuid.uuid4()),
        "case_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "schema_version": "1.0.0",
        "demographics": {
            "age": 35,
            "sex": "female",
            "weight": 70.0,
            "pregnancy_status": False,
            "ethnicity": "not specified",
        },
        "presentation": {
            "syndrome": "respiratory infection",
            "severity": "moderate",
            "acquisition": "community",
            "symptoms": ["cough", "fever"],
            "duration_days": 3,
        },
        "resistance_status": "none",
    }


@pytest.fixture
def sample_clinical_case_request(sample_clinical_case_payload: dict[str, Any]) -> ClinicalCaseRequest:
    """Return a `ClinicalCaseRequest` model instance derived from the payload."""
    return ClinicalCaseRequest.model_validate(sample_clinical_case_payload)
