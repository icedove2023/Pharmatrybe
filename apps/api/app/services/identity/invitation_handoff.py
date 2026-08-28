"""Backend-only temporary invitation-token handoff."""

from __future__ import annotations

from datetime import datetime, timezone
from secrets import token_urlsafe
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.orm import Session

from app.models.identity import InvitationTokenHandoff


class InvitationTokenHandoffService:
    """Keep raw invitation tokens outside persistent invitation and outbox records."""

    def __init__(self, encryption_key: str) -> None:
        if not encryption_key:
            raise ValueError("handoff encryption key is required")
        self._cipher = Fernet(encryption_key.encode())
        self._records: dict[str, tuple[str, str, str, datetime, str]] = {}

    def create(
        self,
        *,
        raw_token: str,
        invitation_id: str,
        hospital_id: str,
        outbox_id: str,
        expires_at: datetime,
        db: Session | None = None,
    ) -> str:
        """Create an opaque handoff reference for a trusted backend worker."""
        reference = token_urlsafe(32)
        record = (
            invitation_id,
            hospital_id,
            outbox_id,
            expires_at,
            self._protect(raw_token),
        )
        if db is None:
            self._records[reference] = record
        else:
            db.add(InvitationTokenHandoff(
                reference=reference,
                invitation_id=invitation_id,
                hospital_id=hospital_id,
                outbox_id=outbox_id,
                encrypted_token=record[4],
                expires_at=expires_at,
            ))
            db.flush()
        return reference

    def retrieve(self, reference: str, invitation_id: str, hospital_id: str, outbox_id: str, db: Session | None = None) -> str:
        """Replay a handoff for the bound worker until completion or expiry."""
        if db is None:
            record = self._records.get(reference)
        else:
            handoff = db.get(InvitationTokenHandoff, reference)
            record = None if handoff is None else (
                handoff.invitation_id,
                handoff.hospital_id,
                handoff.outbox_id,
                handoff.expires_at,
                handoff.encrypted_token,
            )
        if record is None:
            raise KeyError("handoff not found")
        record_invitation_id, record_hospital_id, record_outbox_id, expires_at, encrypted_token = record
        if record_invitation_id != invitation_id or record_hospital_id != hospital_id or record_outbox_id != outbox_id:
            raise PermissionError("handoff binding mismatch")
        if datetime.now(timezone.utc) >= expires_at:
            if db is None:
                self._records.pop(reference, None)
            else:
                db.delete(handoff)
                db.flush()
            raise TimeoutError("handoff expired")
        return self._unprotect(encrypted_token)

    def complete(self, reference: str, invitation_id: str, hospital_id: str, outbox_id: str, db: Session | None = None) -> None:
        """Destroy a handoff after successful external delivery."""
        self.retrieve(reference, invitation_id, hospital_id, outbox_id, db=db)
        if db is None:
            self._records.pop(reference, None)
        else:
            handoff = db.get(InvitationTokenHandoff, reference)
            if handoff is not None:
                db.delete(handoff)
                db.flush()

    def _protect(self, raw_token: str) -> str:
        """Represent protected temporary material without exposing plaintext to callers."""
        return self._cipher.encrypt(raw_token.encode()).decode()

    def _unprotect(self, encrypted_token: str) -> str:
        try:
            return self._cipher.decrypt(encrypted_token.encode()).decode()
        except InvalidToken as exc:
            raise ValueError("handoff material is invalid") from exc


def get_invitation_handoff_service() -> InvitationTokenHandoffService:
    """Build the trusted handoff service from deployment-provided key material."""
    from app.core.config import settings

    return InvitationTokenHandoffService(settings.invitation_handoff_encryption_key)
