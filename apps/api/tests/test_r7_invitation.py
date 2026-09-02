from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from cryptography.fernet import Fernet
from types import SimpleNamespace

from app.services.identity.delivery import DeliveryResult
from app.services.identity.outbox_worker import InvitationOutboxWorker
from app.services.identity.invitation_handoff import InvitationTokenHandoffService
from app.models.identity import InvitationTokenHandoff
from app.core.config import Settings
from app.api.v1.professionals import InvitationAcceptanceRequest, accept_professional_invitation
from app.auth.current_user import AuthenticatedUser
from app.core import config as app_config
from app.models.identity import HospitalInvitation, HospitalMembership, MembershipEvent, ProfessionalProfile, Role
from app.services.identity import supabase_auth


def test_backend_settings_resolve_env_file_from_workspace_root() -> None:
    expected_root = Path(__file__).resolve().parents[4]
    assert app_config.PROJECT_ROOT == expected_root
    assert app_config.PROJECT_ROOT / ".env" == expected_root / ".env"
    assert (app_config.PROJECT_ROOT / ".env").exists()


def test_handoff_is_replayable_until_successful_delivery() -> None:
    service = InvitationTokenHandoffService(encryption_key=Fernet.generate_key().decode())
    invitation_id = str(uuid4())
    hospital_id = str(uuid4())
    outbox_id = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    reference = service.create(
        raw_token="opaque-token",
        invitation_id=invitation_id,
        hospital_id=hospital_id,
        outbox_id=outbox_id,
        expires_at=expires_at,
    )

    assert service.retrieve(reference, invitation_id, hospital_id, outbox_id) == "opaque-token"
    assert service.retrieve(reference, invitation_id, hospital_id, outbox_id) == "opaque-token"

    service.complete(reference, invitation_id, hospital_id, outbox_id)

    with pytest.raises(KeyError):
        service.retrieve(reference, invitation_id, hospital_id, outbox_id)


def test_handoff_rejects_cross_tenant_or_cross_outbox_retrieval() -> None:
    service = InvitationTokenHandoffService(encryption_key=Fernet.generate_key().decode())
    invitation_id = str(uuid4())
    hospital_id = str(uuid4())
    outbox_id = str(uuid4())
    reference = service.create(
        raw_token="opaque-token",
        invitation_id=invitation_id,
        hospital_id=hospital_id,
        outbox_id=outbox_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    with pytest.raises(PermissionError):
        service.retrieve(reference, invitation_id, str(uuid4()), outbox_id)
    with pytest.raises(PermissionError):
        service.retrieve(reference, invitation_id, hospital_id, str(uuid4()))


def test_handoff_expires_at_invitation_expiry() -> None:
    service = InvitationTokenHandoffService(encryption_key=Fernet.generate_key().decode())
    invitation_id = str(uuid4())
    hospital_id = str(uuid4())
    outbox_id = str(uuid4())
    reference = service.create(
        raw_token="opaque-token",
        invitation_id=invitation_id,
        hospital_id=hospital_id,
        outbox_id=outbox_id,
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )

    with pytest.raises(TimeoutError):
        service.retrieve(reference, invitation_id, hospital_id, outbox_id)


class _WorkerSession:
    def __init__(self, record, handoff_service: InvitationTokenHandoffService) -> None:
        self.record = record
        self.commit_count = 0
        self.handoff_service = handoff_service

    def scalar(self, _statement):
        return self.record

    def get(self, entity_type, reference):
        if entity_type is not InvitationTokenHandoff:
            return None
        invitation_id, hospital_id, outbox_id, expires_at, encrypted_token = self.handoff_service._records[reference]
        return InvitationTokenHandoff(
            reference=reference,
            invitation_id=invitation_id,
            hospital_id=hospital_id,
            outbox_id=outbox_id,
            expires_at=expires_at,
            encrypted_token=encrypted_token,
        )

    def delete(self, entity) -> None:
        self.handoff_service._records.pop(entity.reference, None)

    def flush(self) -> None:
        return None

    def commit(self) -> None:
        self.commit_count += 1


def _worker_record(service: InvitationTokenHandoffService):
    invitation_id = str(uuid4())
    hospital_id = str(uuid4())
    outbox_id = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    reference = service.create(
        raw_token="opaque-token",
        invitation_id=invitation_id,
        hospital_id=hospital_id,
        outbox_id=outbox_id,
        expires_at=expires_at,
    )
    return SimpleNamespace(
        id=outbox_id,
        invitation_id=invitation_id,
        hospital_id=hospital_id,
        idempotency_key=f"invitation:{invitation_id}:initial",
        recipient_email="invitee@example.com",
        payload={"handoff_reference": reference},
        status="PENDING",
        attempt_count=0,
        available_at=datetime.now(timezone.utc),
        processing_started_at=None,
        last_attempt_at=None,
        last_error_code=None,
        last_error_message=None,
        completed_at=None,
    )


def test_worker_marks_success_sent_and_destroys_handoff() -> None:
    handoff = InvitationTokenHandoffService(encryption_key=Fernet.generate_key().decode())
    record = _worker_record(handoff)

    class SuccessfulDelivery:
        def send_invitation(self, *_args):
            return DeliveryResult(success=True)

    assert InvitationOutboxWorker(SuccessfulDelivery(), handoff, "/invite").process_one(_WorkerSession(record, handoff))
    assert record.status == "SENT"
    assert record.attempt_count == 1
    with pytest.raises(KeyError):
        handoff.retrieve(record.payload["handoff_reference"], record.invitation_id, record.hospital_id, record.id)


def test_worker_uses_approved_first_retry_delay() -> None:
    handoff = InvitationTokenHandoffService(encryption_key=Fernet.generate_key().decode())
    record = _worker_record(handoff)

    class RetryableDelivery:
        def send_invitation(self, *_args):
            return DeliveryResult(success=False, retryable=True, error_code="PROVIDER_UNAVAILABLE", error_message="temporary")

    before = datetime.now(timezone.utc)
    assert InvitationOutboxWorker(RetryableDelivery(), handoff, "/invite").process_one(_WorkerSession(record, handoff))
    assert record.status == "PENDING"
    assert record.attempt_count == 1
    assert record.available_at >= before + timedelta(minutes=1)


def test_worker_marks_non_retryable_failure_terminal() -> None:
    handoff = InvitationTokenHandoffService(encryption_key=Fernet.generate_key().decode())
    record = _worker_record(handoff)

    class PermanentDelivery:
        def send_invitation(self, *_args):
            return DeliveryResult(success=False, retryable=False, error_code="INVALID_RECIPIENT", error_message="invalid recipient")

    assert InvitationOutboxWorker(PermanentDelivery(), handoff, "/invite").process_one(_WorkerSession(record, handoff))
    assert record.status == "FAILED"
    assert record.attempt_count == 1


def test_worker_exhausts_retryable_failures_on_third_attempt() -> None:
    handoff = InvitationTokenHandoffService(encryption_key=Fernet.generate_key().decode())
    record = _worker_record(handoff)
    delivered_urls: list[str] = []

    class RetryableDelivery:
        def send_invitation(self, _recipient, invitation_url, _invitation_id, _idempotency_key):
            delivered_urls.append(invitation_url)
            return DeliveryResult(success=False, retryable=True, error_code="PROVIDER_UNAVAILABLE", error_message="temporary")

    worker = InvitationOutboxWorker(RetryableDelivery(), handoff, "/invite")
    session = _WorkerSession(record, handoff)
    worker.process_one(session)
    first_available = record.available_at
    worker.process_one(session)
    second_available = record.available_at
    worker.process_one(session)

    assert record.status == "FAILED"
    assert record.attempt_count == 3
    assert second_available > first_available
    assert delivered_urls == ["/invite?token=opaque-token"] * 3


class _RecoveryResult:
    def __init__(self, rowcount: int) -> None:
        self.rowcount = rowcount


class _RecoverySession:
    def __init__(self, rowcounts: list[int]) -> None:
        self.rowcounts = iter(rowcounts)
        self.commits = 0

    def execute(self, _statement):
        return _RecoveryResult(next(self.rowcounts))

    def commit(self) -> None:
        self.commits += 1


def test_worker_recovers_stale_processing_records_with_attempt_limit() -> None:
    handoff = InvitationTokenHandoffService(encryption_key=Fernet.generate_key().decode())
    worker = InvitationOutboxWorker(lambda: None, handoff, "/invite")

    session = _RecoverySession([1, 0])
    assert worker.recover_stale(session) == 1
    assert session.commits == 1

    exhausted_session = _RecoverySession([1, 0])
    assert worker.recover_stale(exhausted_session) == 1
    assert exhausted_session.commits == 1


def test_production_configuration_requires_handoff_key_and_route(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("INVITATION_HANDOFF_ENCRYPTION_KEY", raising=False)
    monkeypatch.delenv("INVITATION_FRONTEND_ROUTE", raising=False)
    key = Fernet.generate_key().decode()
    configured = Settings(
        environment="production",
        invitation_handoff_encryption_key=key,
        invitation_frontend_route="/invite",
    )
    assert configured.invitation_frontend_route == "/invite"

    with pytest.raises(ValueError, match="INVITATION_HANDOFF_ENCRYPTION_KEY"):
        Settings(_env_file=None, environment="production", invitation_frontend_route="/invite")

    with pytest.raises(ValueError, match="INVITATION_FRONTEND_ROUTE"):
        Settings(_env_file=None, environment="production", invitation_handoff_encryption_key=key)


def test_supabase_invitation_preserves_provider_error_detail(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(supabase_auth.settings, "supabase_url", "https://project.supabase.co")
    monkeypatch.setattr(supabase_auth.settings, "supabase_service_role_key", "service-role-key")
    monkeypatch.setattr(supabase_auth.settings, "invitation_frontend_route", "http://localhost:3000/")
    response = supabase_auth.httpx.Response(
        422,
        json={"error": "email_address_invalid", "error_description": "Invalid email address"},
    )
    request = {}

    def fake_post(*args, **kwargs):
        request["url"] = args[0]
        return response

    monkeypatch.setattr(supabase_auth.httpx, "post", fake_post)

    with pytest.raises(supabase_auth.SupabaseAuthError, match="Invalid email address"):
        supabase_auth.invite_user_by_email("invalid")
    assert request["url"] == "https://project.supabase.co/auth/v1/invite"


class _AcceptanceSession:
    def __init__(self, results, *, fail_on_event: bool = False) -> None:
        self.results = list(results)
        self.added: list[object] = []
        self.commit_count = 0
        self.rollback_count = 0
        self.fail_on_event = fail_on_event

    def scalar(self, _statement):
        return self.results.pop(0)

    def add(self, entity) -> None:
        if self.fail_on_event and isinstance(entity, MembershipEvent):
            raise RuntimeError("event insert failed")
        self.added.append(entity)

    def flush(self) -> None:
        for entity in self.added:
            if isinstance(entity, (ProfessionalProfile, HospitalMembership)) and entity.id is None:
                entity.id = str(uuid4())

    def commit(self) -> None:
        self.commit_count += 1

    def rollback(self) -> None:
        self.rollback_count += 1


def _acceptance_payload() -> InvitationAcceptanceRequest:
    return InvitationAcceptanceRequest(first_name="Ada", last_name="Lovelace")


def _invitation(*, status: str = "PENDING") -> HospitalInvitation:
    return HospitalInvitation(
        id=str(uuid4()),
        hospital_id=str(uuid4()),
        email="invitee@example.com",
        invited_by=str(uuid4()),
        role_code="CLINICIAN",
        token_hash=None,
        status=status,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )


def test_acceptance_creates_one_approved_event_atomically() -> None:
    invitation = _invitation()
    role = Role(id=str(uuid4()), code="CLINICIAN", name="Clinician")
    session = _AcceptanceSession([invitation, None, None, role])

    result = asyncio.run(accept_professional_invitation(
        _acceptance_payload(),
        AuthenticatedUser(user_id=str(uuid4()), email="invitee@example.com"),
        session,
    ))

    events = [entity for entity in session.added if isinstance(entity, MembershipEvent)]
    assert result["status"] == "ACTIVE"
    assert invitation.status == "ACCEPTED"
    assert len(events) == 1
    assert events[0].event_type == "MEMBERSHIP_CREATED_FROM_INVITATION"
    assert events[0].details["source"] == "invitation_acceptance"
    assert session.commit_count == 1
    assert session.rollback_count == 0


def test_acceptance_rejects_wrong_identity_and_already_accepted_invitation() -> None:
    wrong_identity_session = _AcceptanceSession([_invitation()])
    with pytest.raises(Exception):
        asyncio.run(accept_professional_invitation(
            _acceptance_payload(),
            AuthenticatedUser(user_id=str(uuid4()), email="other@example.com"),
            wrong_identity_session,
        ))
    assert wrong_identity_session.commit_count == 0

    accepted_session = _AcceptanceSession([_invitation(status="ACCEPTED")])
    with pytest.raises(Exception):
        asyncio.run(accept_professional_invitation(
            _acceptance_payload(),
            AuthenticatedUser(user_id=str(uuid4()), email="invitee@example.com"),
            accepted_session,
        ))
    assert accepted_session.commit_count == 0


def test_acceptance_rejects_existing_profile_without_writes() -> None:
    session = _AcceptanceSession([_invitation(), ProfessionalProfile(auth_user_id="existing")])

    with pytest.raises(Exception):
        asyncio.run(accept_professional_invitation(
            _acceptance_payload(),
            AuthenticatedUser(user_id="existing", email="invitee@example.com"),
            session,
        ))

    assert session.added == []
    assert session.commit_count == 0


def test_acceptance_rolls_back_when_membership_event_insert_fails() -> None:
    invitation = _invitation()
    role = Role(id=str(uuid4()), code="CLINICIAN", name="Clinician")
    session = _AcceptanceSession([invitation, None, None, role], fail_on_event=True)

    with pytest.raises(Exception):
        asyncio.run(accept_professional_invitation(
            _acceptance_payload(),
            AuthenticatedUser(user_id=str(uuid4()), email="invitee@example.com"),
            session,
        ))

    assert session.commit_count == 0
    assert session.rollback_count == 1
    assert invitation.status == "PENDING"
