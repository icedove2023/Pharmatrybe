"""Provider-neutral invitation delivery contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DeliveryResult:
    """Safe result returned by an invitation delivery adapter."""

    success: bool
    retryable: bool = False
    error_code: str | None = None
    error_message: str | None = None
    provider_reference: str | None = None


class InvitationDelivery(Protocol):
    """Provider-neutral invitation delivery interface."""

    def send_invitation(
        self,
        recipient_email: str,
        invitation_url: str,
        invitation_id: str,
        idempotency_key: str,
    ) -> DeliveryResult:
        """Send an invitation without exposing provider-specific behavior."""
        ...


class UnconfiguredInvitationDelivery:
    """Explicit development adapter when no provider is configured."""

    def send_invitation(
        self,
        recipient_email: str,
        invitation_url: str,
        invitation_id: str,
        idempotency_key: str,
    ) -> DeliveryResult:
        """Report provider unavailability without pretending delivery succeeded."""
        return DeliveryResult(
            success=False,
            retryable=True,
            error_code="PROVIDER_UNAVAILABLE",
            error_message="invitation delivery provider is not configured",
        )
