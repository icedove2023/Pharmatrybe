from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models.identity import Hospital
from app.models.plugin_governance import (
    GovernanceApprovalState,
    GovernanceStatus,
    GovernanceTrustLevel,
    GovernanceValidationState,
    PluginGovernanceAuditEvent,
    PluginGovernanceRecord,
)
from app.services.plugin_governance import PluginGovernanceService


def _build_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            Hospital.__table__,
            PluginGovernanceRecord.__table__,
            PluginGovernanceAuditEvent.__table__,
        ],
    )
    return Session(engine)


def test_register_plugin_sets_pending_approval_and_hospital_scope():
    session = _build_session()
    hospital = Hospital(id="h-1", name="Test Hospital")
    session.add(hospital)
    session.commit()

    service = PluginGovernanceService(session)
    record = service.register_plugin(
        hospital_id="h-1",
        plugin_id="local_guidelines",
        plugin_name="Local Guidelines",
        plugin_type="knowledge",
        plugin_version="1.2.0",
        plugin_origin="external",
        owner="Test Hospital",
        publisher="Test Hospital",
        artifact_hash="abc123",
        artifact_uri="https://example.invalid/plugin.zip",
        capabilities=["guidelines"],
        submitted_by_user_id="u-1",
    )

    assert record.plugin_id == "local_guidelines"
    assert record.hospital_id == "h-1"
    assert record.status == GovernanceStatus.REGISTERED
    assert record.validation_state == GovernanceValidationState.PENDING


def test_approve_and_activate_plugin_makes_runtime_eligible():
    session = _build_session()
    hospital = Hospital(id="h-1", name="Test Hospital")
    session.add(hospital)
    session.commit()

    service = PluginGovernanceService(session)
    service.register_plugin(
        hospital_id="h-1",
        plugin_id="local_predictor",
        plugin_name="Local Predictor",
        plugin_type="prediction",
        plugin_version="2.0.0",
        plugin_origin="external",
        owner="Test Hospital",
        publisher="Test Hospital",
        artifact_hash="hash-2",
        artifact_uri="https://example.invalid/model.zip",
        capabilities=["prediction"],
        submitted_by_user_id="u-1",
    )
    service.validate_plugin("local_predictor", hospital_id="h-1")
    service.approve_plugin("local_predictor", hospital_id="h-1", approved_by_user_id="u-1")
    service.activate_plugin("local_predictor", hospital_id="h-1")

    record = service.get_record("local_predictor", hospital_id="h-1")
    assert record.status == GovernanceStatus.ACTIVE
    assert record.approval_state == GovernanceApprovalState.APPROVED
    assert service.is_runtime_eligible("local_predictor", hospital_id="h-1") is True


def test_revocation_blocks_runtime_and_cross_hospital_isolation():
    session = _build_session()
    hospital_a = Hospital(id="h-1", name="Hosp A")
    hospital_b = Hospital(id="h-2", name="Hosp B")
    session.add_all([hospital_a, hospital_b])
    session.commit()

    service = PluginGovernanceService(session)
    service.register_plugin(
        hospital_id="h-1",
        plugin_id="a_plugin",
        plugin_name="A Plugin",
        plugin_type="knowledge",
        plugin_version="1.0.0",
        plugin_origin="external",
        owner="Hosp A",
        publisher="Hosp A",
        artifact_hash="hash-a",
        artifact_uri="https://example.invalid/a.zip",
        capabilities=["guidelines"],
        submitted_by_user_id="u-1",
    )
    service.validate_plugin("a_plugin", hospital_id="h-1")
    service.approve_plugin("a_plugin", hospital_id="h-1", approved_by_user_id="u-1")
    service.activate_plugin("a_plugin", hospital_id="h-1")
    service.revoke_plugin("a_plugin", hospital_id="h-1", actor_user_id="u-1")

    assert service.is_runtime_eligible("a_plugin", hospital_id="h-1") is False
    assert service.is_runtime_eligible("a_plugin", hospital_id="h-2") is False
    assert service.list_for_hospital("h-2") == []


def test_internal_plugins_are_allowed_without_governance_record():
    session = _build_session()
    service = PluginGovernanceService(session)
    assert service.is_runtime_eligible("WHO", hospital_id="h-1") is True
    assert service.is_runtime_eligible("SOAR", hospital_id="h-1") is True


def test_external_plugin_cannot_register_with_platform_owned_id():
    session = _build_session()
    session.add(Hospital(id="h-1", name="Hosp A"))
    session.commit()

    with pytest.raises(ValueError, match="platform-owned plugin IDs"):
        PluginGovernanceService(session).register_plugin(
            hospital_id="h-1",
            plugin_id="SOAR",
            plugin_name="Imposter",
            plugin_type="prediction",
            plugin_version="1.0.0",
            plugin_origin="external",
            owner="Hosp A",
            publisher="Hosp A",
            artifact_hash="hash-imposter",
            artifact_uri="https://example.invalid/imposter.zip",
            capabilities=[],
            submitted_by_user_id="u-1",
        )


def test_trust_levels_and_audit_records_are_preserved():
    session = _build_session()
    hospital = Hospital(id="h-1", name="Hosp A")
    session.add(hospital)
    session.commit()

    service = PluginGovernanceService(session)
    record = service.register_plugin(
        hospital_id="h-1",
        plugin_id="trusted_plugin",
        plugin_name="Trusted Plugin",
        plugin_type="knowledge",
        plugin_version="3.0.0",
        plugin_origin="external",
        owner="Hosp A",
        publisher="Hosp A",
        artifact_hash="hash-a",
        artifact_uri="https://example.invalid/trusted.zip",
        capabilities=["knowledge"],
        submitted_by_user_id="u-1",
        trust_level=GovernanceTrustLevel.TRUSTED,
    )

    assert record.trust_level == GovernanceTrustLevel.TRUSTED
    assert record.audit_events is not None
    assert len(record.audit_events) >= 1
