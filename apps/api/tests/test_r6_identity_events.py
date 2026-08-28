from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1.auth import HospitalRegistrationRequest, register_hospital
from app.auth.current_user import AuthenticatedUser
from app.auth.rbac_catalog import HOSPITAL_ADMIN_PERMISSION_CODES
from app.models.identity import (
    Hospital,
    HospitalMembership,
    MembershipEvent,
    MembershipRole,
    Permission,
    ProfessionalProfile,
    Role,
    RolePermission,
)


class RegistrationSession:
    """Small transaction-aware fake for the registration unit contract."""

    def __init__(self, *, fail_on_event: bool = False, existing_profile=None) -> None:
        self.fail_on_event = fail_on_event
        self.existing_profile = existing_profile
        self.added: list[object] = []
        self.flush_count = 0
        self.commit_count = 0
        self.rollback_count = 0
        self._scalar_calls = 0
        self.role = Role(id=str(uuid4()), code="HOSPITAL_ADMIN", name="Hospital Administrator")
        self.permissions = {
            code: Permission(id=str(uuid4()), code=code)
            for code in HOSPITAL_ADMIN_PERMISSION_CODES
        }

    def scalar(self, _statement):
        self._scalar_calls += 1
        if self._scalar_calls == 1:
            return self.existing_profile
        if self._scalar_calls == 2:
            return self.role
        permission_index = self._scalar_calls - 3
        return self.permissions[HOSPITAL_ADMIN_PERMISSION_CODES[permission_index]]

    def add_all(self, entities):
        for entity in entities:
            self.add(entity)

    def add(self, entity):
        if self.fail_on_event and isinstance(entity, MembershipEvent):
            raise RuntimeError("membership event insert failed")
        self.added.append(entity)

    def flush(self):
        self.flush_count += 1
        for entity in self.added:
            if isinstance(entity, (Hospital, ProfessionalProfile, HospitalMembership)) and entity.id is None:
                entity.id = str(uuid4())

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1


def _registration_payload() -> HospitalRegistrationRequest:
    return HospitalRegistrationRequest(
        hospital_name="Hospital A",
        country="NG",
        admin_name="Ada Lovelace",
    )


def _actor() -> AuthenticatedUser:
    return AuthenticatedUser(user_id="auth-user-id", email="ada@example.com")


def _added(session, entity_type):
    return [entity for entity in session.added if isinstance(entity, entity_type)]


def test_registration_creates_one_membership_event_with_trusted_actor_and_details():
    session = RegistrationSession()

    result = asyncio.run(register_hospital(_registration_payload(), _actor(), session))

    hospitals = _added(session, Hospital)
    profiles = _added(session, ProfessionalProfile)
    memberships = _added(session, HospitalMembership)
    roles = _added(session, MembershipRole)
    events = _added(session, MembershipEvent)

    assert result["status"] == "ACTIVE"
    assert len(hospitals) == 1
    assert len(profiles) == 1
    assert len(memberships) == 1
    assert len(roles) == 1
    assert len(events) == 1
    assert memberships[0].status == "ACTIVE"
    assert memberships[0].hospital_id == hospitals[0].id
    assert memberships[0].professional_id == profiles[0].id
    assert roles[0].role_id == session.role.id
    assert events[0].event_type == "MEMBERSHIP_CREATED"
    assert events[0].membership_id == memberships[0].id
    assert events[0].hospital_id == hospitals[0].id
    assert events[0].actor_user_id == "auth-user-id"
    assert events[0].details == {
        "event": "MEMBERSHIP_CREATED",
        "source": "hospital_registration",
        "role_code": "HOSPITAL_ADMIN",
    }
    assert sum(isinstance(entity, MembershipEvent) for entity in session.added) == 1
    assert session.commit_count == 1
    assert session.rollback_count == 0


def test_event_failure_rolls_back_entire_registration_without_commit():
    session = RegistrationSession(fail_on_event=True)

    with pytest.raises(HTTPException) as error:
        asyncio.run(register_hospital(_registration_payload(), _actor(), session))

    assert error.value.status_code == 500
    assert session.commit_count == 0
    assert session.rollback_count == 1
    assert len(_added(session, MembershipEvent)) == 0
    assert len(_added(session, Hospital)) == 1
    assert len(_added(session, ProfessionalProfile)) == 1
    assert len(_added(session, HospitalMembership)) == 1


def test_existing_profile_rejects_duplicate_registration_without_writes():
    existing_profile = SimpleNamespace(auth_user_id="auth-user-id")
    session = RegistrationSession(existing_profile=existing_profile)

    with pytest.raises(HTTPException) as error:
        asyncio.run(register_hospital(_registration_payload(), _actor(), session))

    assert error.value.status_code == 409
    assert session.added == []
    assert session.commit_count == 0
    assert session.rollback_count == 0