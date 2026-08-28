"""Hospital-scoped professional invitation routes."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import AuthorizationContext, AuthenticatedUser, get_current_user, require_permission
from app.auth.rbac_catalog import CANONICAL_ROLE_CODES
from app.database.session import get_db_session
from app.core.config import settings
from app.models.identity import (
    HospitalInvitation,
    HospitalMembership,
    InvitationDeliveryOutbox,
    MembershipEvent,
    MembershipRole,
    ProfessionalProfile,
    Role,
)
from app.services.identity.invitation_handoff import get_invitation_handoff_service

router = APIRouter(prefix="/professionals", tags=["professionals"])

class ProfessionalInvitationRequest(BaseModel):
    """Hospital-bound invitation request."""

    email: str = Field(..., min_length=3)
    role_code: str = Field(..., min_length=1)


class InvitationAcceptanceRequest(BaseModel):
    """Invitation token and professional profile details."""

    token: str = Field(..., min_length=16)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    professional_type: str | None = None


class MembershipUpdateRequest(BaseModel):
    """Allowed hospital membership changes made by an administrator."""

    status: Literal["ACTIVE", "SUSPENDED", "DEACTIVATED"] | None = None
    role_code: str | None = Field(default=None, min_length=1)


@router.get("", summary="List professionals in the active hospital")
async def list_professionals(
    context: Annotated[AuthorizationContext, Depends(require_permission("professionals:view"))],
    db: Annotated[Session, Depends(get_db_session)],
) -> dict[str, Any]:
    """Return active-hospital professional profiles and assigned canonical roles."""
    professionals = db.scalars(
        select(ProfessionalProfile)
        .join(HospitalMembership)
        .where(
            HospitalMembership.hospital_id == context.hospital_id,
            HospitalMembership.status == "ACTIVE",
        )
        .options(
            selectinload(ProfessionalProfile.memberships)
            .selectinload(HospitalMembership.roles)
            .selectinload(MembershipRole.role)
        )
        .order_by(ProfessionalProfile.last_name, ProfessionalProfile.first_name)
    ).unique().all()
    items = []
    for professional in professionals:
        membership = next(
            (item for item in professional.memberships if item.hospital_id == context.hospital_id),
            None,
        )
        if membership is None:
            continue
        items.append({
            "professional_id": professional.id,
            "first_name": professional.first_name,
            "last_name": professional.last_name,
            "professional_type": professional.professional_type,
            "profile_status": professional.profile_status,
            "membership_id": membership.id,
            "membership_status": membership.status,
            "roles": sorted(role.role.code for role in membership.roles),
            "joined_at": membership.joined_at.isoformat() if membership.joined_at else None,
        })
    return {"items": items}


@router.get("/invitations", summary="List invitations for the active hospital")
async def list_invitations(
    context: Annotated[AuthorizationContext, Depends(require_permission("professionals:view"))],
    db: Annotated[Session, Depends(get_db_session)],
) -> dict[str, Any]:
    """Return invitation metadata without exposing token material."""
    invitations = db.scalars(
        select(HospitalInvitation)
        .where(HospitalInvitation.hospital_id == context.hospital_id)
        .order_by(HospitalInvitation.created_at.desc())
    ).all()
    return {"items": [
        {
            "invitation_id": invitation.id,
            "email": invitation.email,
            "role_code": invitation.role_code,
            "status": invitation.status,
            "expires_at": invitation.expires_at.isoformat(),
            "created_at": invitation.created_at.isoformat() if invitation.created_at else None,
        }
        for invitation in invitations
    ]}


@router.post("/invite", status_code=status.HTTP_201_CREATED)
async def invite_professional(
    payload: ProfessionalInvitationRequest,
    context: Annotated[AuthorizationContext, Depends(require_permission("professionals:invite"))],
    db: Annotated[Session, Depends(get_db_session)],
) -> dict[str, Any]:
    """Create a pending hospital invitation for external delivery."""
    role_code = payload.role_code.strip().upper()
    if role_code not in CANONICAL_ROLE_CODES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid canonical role")

    normalized_email = payload.email.strip().lower()
    duplicate = db.scalar(
        select(HospitalInvitation).where(
            HospitalInvitation.hospital_id == context.hospital_id,
            HospitalInvitation.email == normalized_email,
            HospitalInvitation.status == "PENDING",
            HospitalInvitation.expires_at > datetime.now(timezone.utc),
        )
    )
    if duplicate is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pending invitation already exists")
    if not settings.invitation_handoff_encryption_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Invitation delivery is not configured")

    raw_token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=7)
    handoff_service = get_invitation_handoff_service()
    try:
        invitation = HospitalInvitation(
            hospital_id=context.hospital_id,
            email=normalized_email,
            invited_by=context.user_id,
            role_code=role_code,
            token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
            status="PENDING",
            expires_at=expires_at,
        )
        db.add(invitation)
        db.flush()
        outbox = InvitationDeliveryOutbox(
            hospital_id=context.hospital_id,
            invitation_id=invitation.id,
            idempotency_key=f"invitation:{invitation.id}:initial",
            delivery_type="PROFESSIONAL_INVITATION",
            recipient_email=normalized_email,
            payload={},
            status="PENDING",
            attempt_count=0,
            available_at=now,
        )
        db.add(outbox)
        db.flush()
        handoff_reference = handoff_service.create(
            raw_token=raw_token,
            invitation_id=invitation.id,
            hospital_id=context.hospital_id,
            outbox_id=outbox.id,
            expires_at=expires_at,
            db=db,
        )
        outbox.payload = {
            "invitation_id": invitation.id,
            "recipient_email": normalized_email,
            "hospital_id": context.hospital_id,
            "handoff_reference": handoff_reference,
        }
        db.commit()
    except Exception as exc:
        db.rollback()
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invitation creation failed") from exc
    return {
        "invitation_id": invitation.id,
        "hospital_id": context.hospital_id,
        "role_code": role_code,
        "status": invitation.status,
        "delivery": "queued",
    }


@router.post("/invitations/accept", status_code=status.HTTP_201_CREATED)
async def accept_professional_invitation(
    payload: InvitationAcceptanceRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
) -> dict[str, Any]:
    """Accept a hospital invitation for the authenticated Supabase user."""
    token_hash = hashlib.sha256(payload.token.encode("utf-8")).hexdigest()
    invitation = db.scalar(select(HospitalInvitation).where(HospitalInvitation.token_hash == token_hash))
    if invitation is None or invitation.status != "PENDING" or invitation.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation is invalid or expired")
    if not current_user.email or current_user.email.lower() != invitation.email.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invitation email does not match identity")

    professional = db.scalar(
        select(ProfessionalProfile).where(ProfessionalProfile.auth_user_id == current_user.user_id)
    )
    if professional is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Professional profile already exists")
    professional = ProfessionalProfile(
        auth_user_id=current_user.user_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        professional_type=payload.professional_type,
    )
    db.add(professional)
    db.flush()

    active_membership = db.scalar(
        select(HospitalMembership).where(
            HospitalMembership.professional_id == professional.id,
            HospitalMembership.status == "ACTIVE",
        )
    )
    if active_membership is not None:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Professional already has an active hospital membership")

    role = db.scalar(select(Role).where(Role.code == invitation.role_code))
    if role is None or invitation.role_code not in CANONICAL_ROLE_CODES:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid canonical role")
    try:
        membership = HospitalMembership(
            professional_id=professional.id,
            hospital_id=invitation.hospital_id,
            status="ACTIVE",
            invited_by=invitation.invited_by,
        )
        db.add(membership)
        db.flush()
        db.add(MembershipRole(membership_id=membership.id, role_id=role.id, assigned_by=invitation.invited_by))
        db.add(MembershipEvent(
            membership_id=membership.id,
            hospital_id=membership.hospital_id,
            actor_user_id=current_user.user_id,
            event_type="MEMBERSHIP_CREATED_FROM_INVITATION",
            details={
                "event": "MEMBERSHIP_CREATED_FROM_INVITATION",
                "source": "invitation_acceptance",
                "role_code": invitation.role_code,
            },
        ))
        invitation.status = "ACCEPTED"
        invitation.accepted_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invitation acceptance failed") from exc
    return {"membership_id": membership.id, "hospital_id": membership.hospital_id, "status": membership.status}


@router.patch("/{professional_id}/membership", summary="Manage a hospital professional membership")
async def update_membership(
    professional_id: str,
    payload: MembershipUpdateRequest,
    context: Annotated[AuthorizationContext, Depends(require_permission("professionals:manage"))],
    db: Annotated[Session, Depends(get_db_session)],
) -> dict[str, Any]:
    """Update membership status and, when authorized, assign a canonical role."""
    if payload.status is None and payload.role_code is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A membership status or role change is required")

    membership = db.scalar(
        select(HospitalMembership)
        .where(
            HospitalMembership.professional_id == professional_id,
            HospitalMembership.hospital_id == context.hospital_id,
        )
        .options(selectinload(HospitalMembership.roles).selectinload(MembershipRole.role))
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional membership not found")

    changes: dict[str, Any] = {}
    if payload.status is not None and payload.status != membership.status:
        previous_status = membership.status
        membership.status = payload.status
        now = datetime.now(timezone.utc)
        if payload.status == "ACTIVE":
            membership.activated_at = now
        elif payload.status == "SUSPENDED":
            membership.suspended_at = now
        else:
            membership.deactivated_at = now
        changes["status"] = {"from": previous_status, "to": payload.status}

    if payload.role_code is not None:
        role_code = payload.role_code.strip().upper()
        if "roles:assign" not in context.permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role assignment permission required")
        if role_code not in CANONICAL_ROLE_CODES:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid canonical role")
        role = db.scalar(select(Role).where(Role.code == role_code))
        if role is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Canonical role is not configured")
        if not any(item.role.code == role_code for item in membership.roles):
            db.add(MembershipRole(membership_id=membership.id, role_id=role.id, assigned_by=context.user_id))
            changes["role_code"] = role_code

    if not changes:
        return {
            "professional_id": professional_id,
            "membership_id": membership.id,
            "status": membership.status,
            "roles": sorted(item.role.code for item in membership.roles),
        }

    db.add(MembershipEvent(
        membership_id=membership.id,
        hospital_id=context.hospital_id,
        actor_user_id=context.user_id,
        event_type="MEMBERSHIP_UPDATED",
        details={"event": "MEMBERSHIP_UPDATED", "changes": changes},
    ))
    db.commit()
    return {
        "professional_id": professional_id,
        "membership_id": membership.id,
        "status": membership.status,
        "roles": sorted({*{item.role.code for item in membership.roles}, *( [payload.role_code.strip().upper()] if payload.role_code else [])}),
    }