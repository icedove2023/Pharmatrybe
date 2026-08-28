from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.plugin_governance import (
    GovernanceApprovalState,
    GovernanceStatus,
    GovernanceTrustLevel,
    GovernanceValidationState,
    PluginGovernanceAuditEvent,
    PluginExecutionAudit,
    PluginGovernanceRecord,
)
from app.plugins.identity import canonical_plugin_id, is_internal_plugin


ALLOWED_CAPABILITIES = frozenset({
    "READ_PATIENT_DATA",
    "READ_AMR_DATA",
    "READ_KNOWLEDGE_BASE",
    "ACCESS_GUIDELINES",
    "NETWORK_ACCESS",
    "FILE_READ",
    "FILE_WRITE",
    "DATABASE_ACCESS",
})

CAPABILITY_ALIASES = {
    "guidelines": "ACCESS_GUIDELINES",
    "prediction": "READ_AMR_DATA",
    "knowledge": "READ_KNOWLEDGE_BASE",
}


class PluginGovernanceService:
    """Service layer enforcing the R9 governance lifecycle for external plugins."""

    INTERNAL_PLUGIN_IDS = {"WHO", "SOAR", "ARMD"}

    def __init__(self, db: Session):
        self.db = db

    def register_plugin(
        self,
        *,
        hospital_id: str,
        plugin_id: str,
        plugin_name: str,
        plugin_type: str,
        plugin_version: str,
        plugin_origin: str,
        owner: str,
        publisher: str,
        artifact_hash: str | None,
        artifact_uri: str | None,
        capabilities: list[str] | None = None,
        submitted_by_user_id: str | None,
        trust_level: GovernanceTrustLevel = GovernanceTrustLevel.UNTRUSTED,
        configuration: dict[str, Any] | None = None,
        manifest_metadata: dict[str, Any] | None = None,
        security_validation: dict[str, Any] | None = None,
        artifact_size: int | None = None,
    ) -> PluginGovernanceRecord:
        plugin_id = canonical_plugin_id(plugin_id)
        if plugin_origin.lower() == "external" and is_internal_plugin(plugin_id):
            raise ValueError("External plugins cannot use platform-owned plugin IDs")
        if plugin_origin.lower() == "external" and not artifact_hash:
            raise ValueError("External plugins require a server-calculated artifact hash")
        canonical_capabilities = [CAPABILITY_ALIASES.get(capability, capability) for capability in (capabilities or [])]
        unknown_capabilities = set(canonical_capabilities) - ALLOWED_CAPABILITIES
        if unknown_capabilities:
            raise ValueError(f"Unsupported plugin capabilities: {sorted(unknown_capabilities)}")
        existing = self.db.scalar(
            select(PluginGovernanceRecord).where(
                PluginGovernanceRecord.hospital_id == hospital_id,
                PluginGovernanceRecord.plugin_id == plugin_id,
            )
        )
        if existing is not None:
            raise ValueError(f"Plugin already registered for hospital: {plugin_id}")

        record = PluginGovernanceRecord(
            hospital_id=hospital_id,
            plugin_id=plugin_id,
            plugin_name=plugin_name,
            plugin_type=plugin_type,
            plugin_version=plugin_version,
            plugin_origin=plugin_origin,
            owner=owner,
            publisher=publisher,
            artifact_hash=artifact_hash,
            artifact_hospital_id=hospital_id,
            artifact_uri=artifact_uri,
            capabilities=canonical_capabilities,
            configuration=configuration or {},
            validation_state=GovernanceValidationState.PENDING.value,
            approval_state=GovernanceApprovalState.PENDING.value,
            trust_level=trust_level.value,
            status=GovernanceStatus.REGISTERED.value,
            submitted_by_user_id=submitted_by_user_id,
            artifact_size=artifact_size,
            manifest_metadata=manifest_metadata or {},
            security_validation=security_validation or {},
        )
        self.db.add(record)
        self.db.flush()
        self._audit(record, submitted_by_user_id, "PLUGIN_REGISTERED", self._details(None, record, "registration"))
        self.db.commit()
        return record

    def validate_plugin(self, plugin_id: str, *, hospital_id: str, validated_by_user_id: str | None = None) -> PluginGovernanceRecord:
        record = self._require_record(plugin_id, hospital_id)
        self._require_state(record, {GovernanceStatus.REGISTERED.value, GovernanceStatus.PENDING_VALIDATION.value, GovernanceStatus.PENDING_APPROVAL.value})
        previous = record.status
        record.validation_state = GovernanceValidationState.VALIDATED.value
        record.status = GovernanceStatus.VALIDATED.value
        record.validated_at = datetime.now(timezone.utc)
        record.validated_by_user_id = validated_by_user_id
        self._audit(record, validated_by_user_id, "PLUGIN_VALIDATED", self._details(previous, record, "validation"))
        self.db.commit()
        return record

    def approve_plugin(self, plugin_id: str, *, hospital_id: str, approved_by_user_id: str | None) -> PluginGovernanceRecord:
        record = self._require_record(plugin_id, hospital_id)
        self._require_state(record, {GovernanceStatus.VALIDATED.value})
        previous = record.status
        if record.validation_state != GovernanceValidationState.VALIDATED.value:
            raise ValueError(f"Only validated plugins may be approved: {plugin_id}")
        record.approval_state = GovernanceApprovalState.APPROVED.value
        record.status = GovernanceStatus.APPROVED.value
        record.approved_at = datetime.now(timezone.utc)
        record.approved_by_user_id = approved_by_user_id
        self._audit(record, approved_by_user_id, "PLUGIN_APPROVED", self._details(previous, record, "approval"))
        self.db.commit()
        return record

    def activate_plugin(self, plugin_id: str, *, hospital_id: str) -> PluginGovernanceRecord:
        record = self._require_record(plugin_id, hospital_id)
        self._require_state(record, {GovernanceStatus.APPROVED.value})
        if record.approval_state != GovernanceApprovalState.APPROVED.value or not record.artifact_hash:
            raise ValueError(f"Only approved plugins may be activated: {plugin_id}")
        previous = record.status
        record.status = GovernanceStatus.ACTIVE.value
        record.activated_by_user_id = record.approved_by_user_id
        record.activated_at = datetime.now(timezone.utc)
        self._audit(record, record.approved_by_user_id, "PLUGIN_ACTIVATED", self._details(previous, record, "activation"))
        self.db.commit()
        return record

    def deactivate_plugin(self, plugin_id: str, *, hospital_id: str, actor_user_id: str | None = None) -> PluginGovernanceRecord:
        record = self._require_record(plugin_id, hospital_id)
        self._require_state(record, {GovernanceStatus.ACTIVE.value})
        previous = record.status
        record.status = GovernanceStatus.DISABLED.value
        self._audit(record, actor_user_id, "PLUGIN_DISABLED", self._details(previous, record, "deactivation"))
        self.db.commit()
        return record

    def reject_plugin(self, plugin_id: str, *, hospital_id: str, actor_user_id: str | None) -> PluginGovernanceRecord:
        record = self._require_record(plugin_id, hospital_id)
        self._require_state(record, {GovernanceStatus.REGISTERED.value, GovernanceStatus.PENDING_VALIDATION.value, GovernanceStatus.VALIDATED.value, GovernanceStatus.PENDING_APPROVAL.value})
        previous = record.status
        record.status = GovernanceStatus.REJECTED.value
        record.approval_state = GovernanceApprovalState.REJECTED.value
        record.rejected_by_user_id = actor_user_id
        record.rejected_at = datetime.now(timezone.utc)
        self._audit(record, actor_user_id, "PLUGIN_REJECTED", self._details(previous, record, "rejection"))
        self.db.commit()
        return record

    def revoke_plugin(self, plugin_id: str, *, hospital_id: str, actor_user_id: str | None) -> PluginGovernanceRecord:
        record = self._require_record(plugin_id, hospital_id)
        self._require_state(record, {GovernanceStatus.ACTIVE.value, GovernanceStatus.DISABLED.value, GovernanceStatus.APPROVED.value})
        previous = record.status
        record.status = GovernanceStatus.REVOKED.value
        record.approval_state = GovernanceApprovalState.REVOKED.value
        record.revoked_by_user_id = actor_user_id
        record.revoked_at = datetime.now(timezone.utc)
        self._audit(record, actor_user_id, "PLUGIN_REVOKED", self._details(previous, record, "revocation"))
        self.db.commit()
        return record

    def quarantine_plugin(self, plugin_id: str, *, hospital_id: str, actor_user_id: str | None) -> PluginGovernanceRecord:
        record = self._require_record(plugin_id, hospital_id)
        self._require_state(record, {GovernanceStatus.ACTIVE.value, GovernanceStatus.DISABLED.value, GovernanceStatus.APPROVED.value})
        previous = record.status
        record.status = GovernanceStatus.QUARANTINED.value
        record.quarantined_by_user_id = actor_user_id
        record.quarantined_at = datetime.now(timezone.utc)
        self._audit(record, actor_user_id, "PLUGIN_QUARANTINED", self._details(previous, record, "quarantine"))
        self.db.commit()
        return record

    def get_record(self, plugin_id: str, *, hospital_id: str) -> PluginGovernanceRecord:
        return self._require_record(plugin_id, hospital_id)

    def list_for_hospital(self, hospital_id: str) -> list[PluginGovernanceRecord]:
        return list(
            self.db.scalars(
                select(PluginGovernanceRecord).where(PluginGovernanceRecord.hospital_id == hospital_id).order_by(PluginGovernanceRecord.created_at.desc())
            ).all()
        )

    def is_runtime_eligible(self, plugin_id: str, *, hospital_id: str | None = None) -> bool:
        plugin_id = canonical_plugin_id(plugin_id)
        if is_internal_plugin(plugin_id):
            return True
        if hospital_id is None:
            return False
        record = self.db.scalar(
            select(PluginGovernanceRecord).where(
                PluginGovernanceRecord.hospital_id == hospital_id,
                PluginGovernanceRecord.plugin_id == plugin_id,
            )
        )
        if record is None:
            return False
        security_ok = (record.security_validation or {}).get("passed", True)
        return record.status == GovernanceStatus.ACTIVE.value and record.approval_state == GovernanceApprovalState.APPROVED.value and bool(record.artifact_hash) and security_ok

    def _require_state(self, record: PluginGovernanceRecord, allowed: set[str]) -> None:
        if record.status not in allowed:
            raise ValueError(f"Invalid lifecycle transition from {record.status}: {record.plugin_id}")

    @staticmethod
    def _details(previous: str | None, record: PluginGovernanceRecord, reason: str) -> dict[str, Any]:
        return {
            "plugin_id": record.plugin_id,
            "plugin_version": record.plugin_version,
            "previous_state": previous,
            "new_state": record.status,
            "reason": reason,
            "artifact_hash": record.artifact_hash,
            "trust_level": record.trust_level,
        }

    def _require_record(self, plugin_id: str, hospital_id: str) -> PluginGovernanceRecord:
        plugin_id = canonical_plugin_id(plugin_id)
        record = self.db.scalar(
            select(PluginGovernanceRecord).where(
                PluginGovernanceRecord.hospital_id == hospital_id,
                PluginGovernanceRecord.plugin_id == plugin_id,
            )
        )
        if record is None:
            raise KeyError(f"No governance record for plugin {plugin_id} in hospital {hospital_id}")
        return record

    def _audit(self, record: PluginGovernanceRecord, actor_user_id: str | None, action: str, details: dict[str, Any]) -> None:
        event = PluginGovernanceAuditEvent(
            plugin_record_id=record.id,
            hospital_id=record.hospital_id,
            actor_user_id=actor_user_id,
            action=action,
            details=details,
        )
        self.db.add(event)

    def record_execution(self, **fields: Any) -> None:
        """Persist bounded execution metadata without plugin output or secrets."""
        allowed = {column.name for column in PluginExecutionAudit.__table__.columns}
        self.db.add(PluginExecutionAudit(**{key: value for key, value in fields.items() if key in allowed}))
        self.db.commit()
