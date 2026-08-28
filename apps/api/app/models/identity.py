"""Identity, hospital tenancy, role, invitation, and membership models."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, Uuid, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


IDENTITY_UUID = Uuid(as_uuid=False)
DATABASE_UUID_DEFAULT = text("gen_random_uuid()")


class Hospital(Base):
    """Hospital organisation and tenant."""

    __tablename__ = "hospitals"

    id: Mapped[str] = mapped_column(IDENTITY_UUID, primary_key=True, server_default=DATABASE_UUID_DEFAULT)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    legal_name: Mapped[str | None] = mapped_column(Text)
    hospital_code: Mapped[str | None] = mapped_column(Text, unique=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    memberships: Mapped[list[HospitalMembership]] = relationship(back_populates="hospital")


class ProfessionalProfile(Base):
    """Application profile linked to a Supabase Auth user UUID."""

    __tablename__ = "professional_profiles"

    id: Mapped[str] = mapped_column(IDENTITY_UUID, primary_key=True, server_default=DATABASE_UUID_DEFAULT)
    auth_user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    professional_type: Mapped[str | None] = mapped_column(Text)
    professional_registration_number: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(Text)
    profile_status: Mapped[str] = mapped_column(Text, nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    memberships: Mapped[list[HospitalMembership]] = relationship(back_populates="professional")


class Role(Base):
    """Canonical application role from the approved role matrix."""

    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(IDENTITY_UUID, primary_key=True, server_default=DATABASE_UUID_DEFAULT)
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    membership_roles: Mapped[list[MembershipRole]] = relationship(back_populates="role")
    role_permissions: Mapped[list[RolePermission]] = relationship(back_populates="role")


class Permission(Base):
    """Canonical resource-action permission."""

    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(IDENTITY_UUID, primary_key=True, server_default=DATABASE_UUID_DEFAULT)
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    role_permissions: Mapped[list[RolePermission]] = relationship(back_populates="permission")


class RolePermission(Base):
    """Role-to-permission assignment."""

    __tablename__ = "role_permissions"

    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[str] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)

    role: Mapped[Role] = relationship(back_populates="role_permissions")
    permission: Mapped[Permission] = relationship(back_populates="role_permissions")


class HospitalMembership(Base):
    """Historical professional-to-hospital membership with one active row."""

    __tablename__ = "hospital_memberships"
    __table_args__ = (
        Index(
            "idx_one_active_membership_per_professional",
            "professional_id",
            unique=True,
            sqlite_where=text("status = 'ACTIVE'"),
            postgresql_where=text("status = 'ACTIVE'"),
        ),
    )

    id: Mapped[str] = mapped_column(IDENTITY_UUID, primary_key=True, server_default=DATABASE_UUID_DEFAULT)
    professional_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("professional_profiles.id", ondelete="CASCADE"), nullable=False)
    hospital_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="INVITED")
    invited_by: Mapped[str | None] = mapped_column(Uuid(as_uuid=False))
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    professional: Mapped[ProfessionalProfile] = relationship(back_populates="memberships")
    hospital: Mapped[Hospital] = relationship(back_populates="memberships")
    roles: Mapped[list[MembershipRole]] = relationship(back_populates="membership")


class MembershipRole(Base):
    """Role assigned within a hospital membership."""

    __tablename__ = "membership_roles"
    membership_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("hospital_memberships.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    assigned_by: Mapped[str | None] = mapped_column(Uuid(as_uuid=False))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    membership: Mapped[HospitalMembership] = relationship(back_populates="roles")
    role: Mapped[Role] = relationship(back_populates="membership_roles")


class HospitalInvitation(Base):
    """Hospital-bound invitation used for controlled professional onboarding."""

    __tablename__ = "hospital_invitations"

    id: Mapped[str] = mapped_column(IDENTITY_UUID, primary_key=True, server_default=DATABASE_UUID_DEFAULT)
    hospital_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    invited_by: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False)
    role_code: Mapped[str] = mapped_column(Text, nullable=False)
    token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="PENDING")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class InvitationDeliveryOutbox(Base):
    """Backend-owned invitation delivery intent."""

    __tablename__ = "invitation_delivery_outbox"
    __table_args__ = (
        CheckConstraint("status IN ('PENDING', 'PROCESSING', 'SENT', 'FAILED')", name="ck_invitation_outbox_status"),
        CheckConstraint("attempt_count >= 0 AND attempt_count <= 3", name="ck_invitation_outbox_attempt_count"),
        Index("idx_invitation_outbox_pending_available", "status", "available_at"),
        Index("idx_invitation_outbox_processing_started", "status", "processing_started_at"),
        Index("idx_invitation_outbox_invitation", "invitation_id"),
    )

    id: Mapped[str] = mapped_column(IDENTITY_UUID, primary_key=True, server_default=DATABASE_UUID_DEFAULT)
    hospital_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    invitation_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("hospital_invitations.id", ondelete="CASCADE"), nullable=False, unique=True)
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    delivery_type: Mapped[str] = mapped_column(Text, nullable=False)
    recipient_email: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="PENDING")
    attempt_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default=text("0"))
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processing_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error_code: Mapped[str | None] = mapped_column(Text)
    last_error_message: Mapped[str | None] = mapped_column(Text)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class InvitationTokenHandoff(Base):
    """Encrypted, bounded-lifetime token material for backend delivery only."""

    __tablename__ = "invitation_token_handoffs"

    reference: Mapped[str] = mapped_column(Text, primary_key=True)
    invitation_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("hospital_invitations.id", ondelete="CASCADE"), nullable=False)
    hospital_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    outbox_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("invitation_delivery_outbox.id", ondelete="CASCADE"), nullable=False, unique=True)
    encrypted_token: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MembershipEvent(Base):
    """Immutable membership lifecycle event."""

    __tablename__ = "membership_events"

    id: Mapped[str] = mapped_column(IDENTITY_UUID, primary_key=True, server_default=DATABASE_UUID_DEFAULT)
    membership_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("hospital_memberships.id", ondelete="CASCADE"), nullable=False)
    hospital_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    actor_user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)