"""Audit service infrastructure for PharmaTrybe."""

from __future__ import annotations

from typing import Any
from app.core.logging import get_logger
from app.logging.audit import build_audit_event
from app.models.audit_log import AuditLog, AuditStatus

logger = get_logger("pharmatrybe.api.audit")


class AuditService:
    """Reusable audit infrastructure service for platform event logging."""

    def __init__(self, source_service: str = "pharmatrybe.api") -> None:
        self.source_service = source_service

    def log_event(
        self,
        request_id: str,
        user_id: str,
        user_role: str,
        action: str,
        resource: str | None = None,
        resource_id: str | None = None,
        status: AuditStatus = AuditStatus.INFO,
        details: dict[str, Any] | None = None,
        hospital_id: str | None = None,
    ) -> AuditLog:
        """Log a generic audit event using structured audit metadata."""
        event = build_audit_event(
            request_id=request_id,
            user_id=user_id,
            hospital_id=hospital_id,
            user_role=user_role,
            action=action,
            resource=resource,
            resource_id=resource_id,
            status=status,
            details=details,
            source_service=self.source_service,
        )
        logger.info("audit.event", extra=event.model_dump())
        return event

    def log_case_created(
        self,
        request_id: str,
        user_id: str,
        user_role: str,
        resource_id: str,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        return self.log_event(
            request_id=request_id,
            user_id=user_id,
            user_role=user_role,
            action="CLINICAL_CASE_CREATED",
            resource="clinical_case",
            resource_id=resource_id,
            status=AuditStatus.SUCCESS,
            details=details,
        )

    def log_case_updated(
        self,
        request_id: str,
        user_id: str,
        user_role: str,
        resource_id: str,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        return self.log_event(
            request_id=request_id,
            user_id=user_id,
            user_role=user_role,
            action="CLINICAL_CASE_UPDATED",
            resource="clinical_case",
            resource_id=resource_id,
            status=AuditStatus.SUCCESS,
            details=details,
        )

    def log_case_deleted(
        self,
        request_id: str,
        user_id: str,
        user_role: str,
        resource_id: str,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        return self.log_event(
            request_id=request_id,
            user_id=user_id,
            user_role=user_role,
            action="CLINICAL_CASE_DELETED",
            resource="clinical_case",
            resource_id=resource_id,
            status=AuditStatus.SUCCESS,
            details=details,
        )

    def log_service_call(
        self,
        request_id: str,
        user_id: str,
        user_role: str,
        source_service: str,
        action: str,
        status: AuditStatus,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        return self.log_event(
            request_id=request_id,
            user_id=user_id,
            user_role=user_role,
            action=action,
            resource=source_service,
            resource_id=None,
            status=status,
            details=details,
        )

    def log_authentication(
        self,
        request_id: str,
        user_id: str,
        user_role: str,
        action: str,
        status: AuditStatus,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        return self.log_event(
            request_id=request_id,
            user_id=user_id,
            user_role=user_role,
            action=action,
            resource="authentication",
            resource_id=None,
            status=status,
            details=details,
        )

    def log_error(
        self,
        request_id: str,
        user_id: str,
        user_role: str,
        action: str,
        resource: str | None = None,
        resource_id: str | None = None,
        error_message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        error_details = {"error_message": error_message, **(details or {})}
        return self.log_event(
            request_id=request_id,
            user_id=user_id,
            user_role=user_role,
            action=action,
            resource=resource,
            resource_id=resource_id,
            status=AuditStatus.FAILURE,
            details=error_details,
        )
