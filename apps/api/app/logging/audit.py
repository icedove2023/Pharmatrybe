"""Audit event build helpers for PharmaTrybe."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

import logging

from app.models.audit_log import AuditLog, AuditStatus


def build_audit_event(
    request_id: str,
    user_id: str,
    user_role: str,
    action: str,
    resource: str | None = None,
    resource_id: str | None = None,
    status: AuditStatus = AuditStatus.INFO,
    details: dict[str, Any] | None = None,
    source_service: str | None = "pharmatrybe.api",
    hospital_id: str | None = None,
) -> AuditLog:
    """Build a reusable audit event model for the PharmaTrybe platform."""
    # Normalize integer logging levels (e.g., `logging.INFO`) to AuditStatus.
    if isinstance(status, int):
        if status >= logging.ERROR:
            status = AuditStatus.FAILURE
        elif status >= logging.WARNING:
            status = AuditStatus.WARNING
        else:
            status = AuditStatus.INFO

    return AuditLog(
        event_id=str(uuid.uuid4()),
        request_id=request_id,
        timestamp=datetime.now(timezone.utc),
        user_id=user_id,
        hospital_id=hospital_id,
        user_role=user_role,
        action=action,
        resource=resource,
        resource_id=resource_id,
        status=status,
        details=details,
        source_service=source_service,
    )
