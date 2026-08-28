"""Transactional outbox worker for invitation delivery."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.identity import InvitationDeliveryOutbox
from app.services.identity.delivery import InvitationDelivery
from app.services.identity.invitation_handoff import InvitationTokenHandoffService

MAX_ATTEMPTS = 3


class InvitationOutboxWorker:
    """Claim and deliver invitation outbox records without changing identity state."""

    def __init__(self, delivery: InvitationDelivery, handoff: InvitationTokenHandoffService, frontend_route: str) -> None:
        if not frontend_route.strip():
            raise ValueError("invitation frontend route is required")
        self.delivery = delivery
        self.handoff = handoff
        self.frontend_route = frontend_route.rstrip("/")

    def recover_stale(self, db: Session) -> int:
        """Return stale processing records to pending or fail exhausted records."""
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(minutes=15)
        exhausted = db.execute(
            update(InvitationDeliveryOutbox)
            .where(
                InvitationDeliveryOutbox.status == "PROCESSING",
                InvitationDeliveryOutbox.processing_started_at < threshold,
                InvitationDeliveryOutbox.attempt_count >= MAX_ATTEMPTS,
            )
            .values(status="FAILED", updated_at=now)
        )
        result = db.execute(
            update(InvitationDeliveryOutbox)
            .where(
                InvitationDeliveryOutbox.status == "PROCESSING",
                InvitationDeliveryOutbox.processing_started_at < threshold,
                InvitationDeliveryOutbox.attempt_count < MAX_ATTEMPTS,
            )
            .values(
                status="PENDING",
                available_at=now,
                processing_started_at=None,
                updated_at=now,
            )
        )
        db.commit()
        return int((result.rowcount or 0) + (exhausted.rowcount or 0))

    def process_one(self, db: Session) -> bool:
        """Claim and process one eligible delivery record."""
        now = datetime.now(timezone.utc)
        record = db.scalar(
            select(InvitationDeliveryOutbox)
            .where(
                InvitationDeliveryOutbox.status == "PENDING",
                InvitationDeliveryOutbox.available_at <= now,
                InvitationDeliveryOutbox.attempt_count < MAX_ATTEMPTS,
            )
            .with_for_update(skip_locked=True)
        )
        if record is None:
            return False
        record.status = "PROCESSING"
        record.attempt_count += 1
        record.processing_started_at = now
        record.last_attempt_at = now
        db.flush()
        payload: dict[str, Any] = record.payload
        reference = str(payload["handoff_reference"])
        try:
            token = self.handoff.retrieve(reference, record.invitation_id, record.hospital_id, record.id, db=db)
            url = f"{self.frontend_route}?{urlencode({'token': token})}"
            result = self.delivery.send_invitation(record.recipient_email, url, record.invitation_id, record.idempotency_key)
        except (TimeoutError, KeyError, PermissionError, ValueError):
            record.status = "FAILED"
            record.last_error_code = "HANDOFF_UNAVAILABLE"
            record.last_error_message = "secure invitation handoff unavailable"
            db.commit()
            return True
        except Exception:
            record.status = "PENDING" if record.attempt_count < MAX_ATTEMPTS else "FAILED"
            record.available_at = now + timedelta(minutes=1 if record.attempt_count == 1 else 5)
            record.processing_started_at = None
            record.last_error_code = "UNKNOWN_DELIVERY_ERROR"
            record.last_error_message = "unexpected delivery failure"
            db.commit()
            return True
        if result.success:
            record.status = "SENT"
            record.completed_at = datetime.now(timezone.utc)
            self.handoff.complete(reference, record.invitation_id, record.hospital_id, record.id, db=db)
        elif result.retryable and record.attempt_count < MAX_ATTEMPTS:
            record.status = "PENDING"
            record.available_at = now + timedelta(minutes=1 if record.attempt_count == 1 else 5)
            record.processing_started_at = None
            record.last_error_code = result.error_code
            record.last_error_message = result.error_message
        else:
            record.status = "FAILED"
            record.processing_started_at = None
            record.last_error_code = result.error_code
            record.last_error_message = result.error_message
        db.commit()
        return True
