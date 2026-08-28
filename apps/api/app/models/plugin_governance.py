from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class GovernanceStatus(str, Enum):
    """Primary lifecycle state for a governed plugin."""

    REGISTERED = "REGISTERED"
    PENDING_VALIDATION = "PENDING_VALIDATION"
    SUBMITTED = "SUBMITTED"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"
    QUARANTINED = "QUARANTINED"


class GovernanceValidationState(str, Enum):
    """Validation sub-state for a submitted plugin."""

    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"


class GovernanceApprovalState(str, Enum):
    """Approval sub-state for a governed plugin."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"


class GovernanceTrustLevel(str, Enum):
    """Trust classification for plugin provenance and security."""

    UNTRUSTED = "UNTRUSTED"
    VERIFIED = "VERIFIED"
    TRUSTED = "TRUSTED"


class PluginGovernanceRecord(Base):
    """Persistent governance record for hospital-scoped plugin lifecycle management."""

    __tablename__ = "plugin_governance_records"
    __table_args__ = (
        UniqueConstraint("hospital_id", "plugin_id", "plugin_version", "artifact_hash", name="uq_plugin_governance_artifact"),
        Index("idx_plugin_governance_hospital_status", "hospital_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(__import__("uuid").uuid4()))
    hospital_id: Mapped[str] = mapped_column(String(64), nullable=False)
    plugin_id: Mapped[str] = mapped_column(String(255), nullable=False)
    plugin_name: Mapped[str] = mapped_column(String(255), nullable=False)
    plugin_type: Mapped[str] = mapped_column(String(64), nullable=False)
    plugin_version: Mapped[str] = mapped_column(String(64), nullable=False)
    plugin_origin: Mapped[str] = mapped_column(String(64), nullable=False, default="external")
    owner: Mapped[str | None] = mapped_column(String(255))
    publisher: Mapped[str | None] = mapped_column(String(255))
    artifact_hash: Mapped[str | None] = mapped_column(String(255))
    artifact_hospital_id: Mapped[str | None] = mapped_column(String(64))
    artifact_size: Mapped[int | None] = mapped_column(nullable=True)
    artifact_uri: Mapped[str | None] = mapped_column(Text)
    capabilities: Mapped[list[str]] = mapped_column(JSON, default=list)
    configuration: Mapped[dict | None] = mapped_column(JSON, default=dict)
    manifest_metadata: Mapped[dict | None] = mapped_column(JSON, default=dict)
    security_validation: Mapped[dict | None] = mapped_column(JSON, default=dict)
    validation_state: Mapped[str] = mapped_column(String(32), nullable=False, default=GovernanceValidationState.PENDING.value)
    approval_state: Mapped[str] = mapped_column(String(32), nullable=False, default=GovernanceApprovalState.PENDING.value)
    trust_level: Mapped[str] = mapped_column(String(32), nullable=False, default=GovernanceTrustLevel.UNTRUSTED.value)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=GovernanceStatus.SUBMITTED.value)
    submitted_by_user_id: Mapped[str | None] = mapped_column(String(64))
    approved_by_user_id: Mapped[str | None] = mapped_column(String(64))
    validated_by_user_id: Mapped[str | None] = mapped_column(String(64))
    rejected_by_user_id: Mapped[str | None] = mapped_column(String(64))
    revoked_by_user_id: Mapped[str | None] = mapped_column(String(64))
    quarantined_by_user_id: Mapped[str | None] = mapped_column(String(64))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    quarantined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    activated_by_user_id: Mapped[str | None] = mapped_column(String(64))
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    audit_events: Mapped[list[PluginGovernanceAuditEvent]] = relationship(back_populates="plugin_record", cascade="all, delete-orphan")


class PluginGovernanceAuditEvent(Base):
    """Immutable audit event tied to a governance lifecycle transition."""

    __tablename__ = "plugin_governance_audit_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(__import__("uuid").uuid4()))
    plugin_record_id: Mapped[str] = mapped_column(ForeignKey("plugin_governance_records.id", ondelete="CASCADE"), nullable=False)
    hospital_id: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    details: Mapped[dict | None] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    plugin_record: Mapped[PluginGovernanceRecord] = relationship(back_populates="audit_events")


class PluginExecutionAudit(Base):
    """Bounded, non-clinical audit record for an external runtime attempt."""

    __tablename__ = "plugin_execution_audits"
    __table_args__ = (Index("idx_plugin_execution_audit_hospital_started", "hospital_id", "started_at"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(__import__("uuid").uuid4()))
    hospital_id: Mapped[str] = mapped_column(String(64), nullable=False)
    authenticated_user_id: Mapped[str | None] = mapped_column(String(64))
    professional_id: Mapped[str | None] = mapped_column(String(64))
    plugin_id: Mapped[str] = mapped_column(String(255), nullable=False)
    plugin_version: Mapped[str | None] = mapped_column(String(64))
    artifact_hash: Mapped[str | None] = mapped_column(String(255))
    governance_record_id: Mapped[str | None] = mapped_column(String(64))
    execution_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    isolation_mode: Mapped[str] = mapped_column(String(64), nullable=False)
    trust_level: Mapped[str | None] = mapped_column(String(32))
    requested_capabilities: Mapped[list[str]] = mapped_column(JSON, default=list)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    execution_status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_ms: Mapped[float] = mapped_column(nullable=False)
    timed_out: Mapped[bool] = mapped_column(nullable=False, default=False)
    denial_reason: Mapped[str | None] = mapped_column(String(255))
    failure_reason: Mapped[str | None] = mapped_column(String(255))
    isolation_level: Mapped[str | None] = mapped_column(String(64))
    cpu_enforced: Mapped[bool] = mapped_column(nullable=False, default=False)
    memory_enforced: Mapped[bool] = mapped_column(nullable=False, default=False)
    network_enforced: Mapped[bool] = mapped_column(nullable=False, default=False)
    filesystem_enforced: Mapped[bool] = mapped_column(nullable=False, default=False)
    identity_enforced: Mapped[bool] = mapped_column(nullable=False, default=False)
    resource_policy_status: Mapped[str | None] = mapped_column(String(32))
