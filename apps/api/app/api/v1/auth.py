"""Authentication and application-identity routes for the PharmaTrybe v1 API."""

from datetime import date, datetime, timezone
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import AuthorizationContext, AuthenticatedUser, get_authorization_context, get_current_user
from app.database.session import get_db_session
from app.models.identity import (
    Hospital,
    HospitalMembership,
    MembershipEvent,
    MembershipRole,
    ProfessionalProfile,
    Role,
)
from app.services.identity.supabase_auth import SupabaseAuthError, is_email_confirmed

router = APIRouter(prefix="/auth", tags=["auth"])


class ProfileUpdateRequest(BaseModel):
    """Self-service profile fields editable from the Settings screen."""

    first_name: str | None = Field(default=None, min_length=1)
    last_name: str | None = Field(default=None, min_length=1)
    phone: str | None = None
    professional_type: str | None = None
    professional_registration_number: str | None = None
    date_of_birth: date | None = None


class HospitalRegistrationRequest(BaseModel):
    """Validated hospital registration data after Supabase account creation."""

    hospital_name: str = Field(..., min_length=2)
    country: str = Field(..., min_length=2)
    admin_name: str = Field(..., min_length=2)
    admin_phone: str | None = Field(None, min_length=5)
    admin_professional_number: str | None = Field(None, min_length=2)


@router.get("", summary="Authentication service status")
async def auth_status() -> dict[str, str]:
    """Return the public authentication service status payload."""
    return {"service": "Authentication Service", "status": "available"}


@router.get("/me")
async def current_application_user(
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> dict[str, Any]:
    """Return the verified application identity and resolved tenant context."""
    role_codes = context.roles
    role_label = {
        "HOSPITAL_ADMIN": "Admin",
        "CLINICIAN": "General Practitioner",
        "PHARMACIST": "Pharmacist",
        "LABORATORY_SCIENTIST": "Laboratory Scientist",
        "INFECTIOUS_DISEASE_SPECIALIST": "Infectious Disease Specialist",
        "RESEARCHER": "Researcher",
    }
    primary_role = next((role_label[code] for code in role_label if code in role_codes), "Researcher")
    permission_codes = context.permissions
    professional = context.professional
    age = None
    if professional.date_of_birth is not None:
        today = datetime.now(timezone.utc).date()
        dob = professional.date_of_birth
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return {
        "id": context.user_id,
        "professionalId": str(context.professional.id),
        "membershipId": str(context.membership.id),
        "hospitalId": str(context.hospital_id),
        "roles": sorted(role_codes),
        "permissionCodes": sorted(permission_codes),
        "name": f"{context.professional.first_name} {context.professional.last_name}".strip(),
        "email": context.user.email,
        "role": primary_role,
        "organization": context.hospital.name,
        "department": context.professional.professional_type or "",
        "licenseNumber": context.professional.professional_registration_number,
        "phone": professional.phone,
        "dateOfBirth": professional.date_of_birth.isoformat() if professional.date_of_birth else None,
        "age": age,
        "forcePasswordReset": professional.force_password_reset,
        "memberSince": professional.created_at.isoformat() if professional.created_at else None,
        "permissions": {
            "canSubmitAssessment": "cases:create" in permission_codes,
            "canViewRecommendations": "recommendations:view" in permission_codes,
            "canSignPrescription": False,
            "canOverrideStewardship": "stewardship:manage" in permission_codes,
            "canViewExplainability": "recommendations:review" in permission_codes,
            "canAccessKnowledgeExplorer": "guidelines:view" in permission_codes,
            "canViewPatientDirectory": "patients:view" in permission_codes,
            "canManagePlugins": "plugins:configure" in permission_codes,
            "canViewSystemHealth": "hospital:view" in permission_codes,
            "canManageUsers": "professionals:manage" in permission_codes,
            "canViewAuditLogs": "audit:view" in permission_codes,
        },
    }


@router.post("/register-hospital", status_code=status.HTTP_201_CREATED)
async def register_hospital(
    payload: HospitalRegistrationRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
) -> dict[str, Any]:
    """Create a hospital and its first administrator transactionally. Idempotent: returns existing membership if already registered."""
    # Check if profile already exists. Some concurrent or repeated registration flows
    # can hit this path before the relationship is fully loaded; treat it as a
    # duplicate registration instead of a 500 crash.
    existing_profile = db.scalar(
        select(ProfessionalProfile).where(ProfessionalProfile.auth_user_id == current_user.user_id)
    )

    if existing_profile is not None:
        memberships = list(getattr(existing_profile, "memberships", []) or [])
        active_memberships = [m for m in memberships if getattr(m, "status", None) == "ACTIVE"]
        if active_memberships:
            membership = active_memberships[0]
            return {
                "id": current_user.user_id,
                "hospital_id": str(membership.hospital_id),
                "status": "ACTIVE",
                "idempotent": True,
            }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "PROFILE_EXISTS_NO_MEMBERSHIP",
                "message": "Hospital profile already exists for this user.",
            },
        )

    # Require a verified email before completing registration. This is enforced
    # here regardless of the Supabase project's "Confirm email" dashboard
    # setting, so hospital + admin records are never created for an
    # unverified address even if that setting is ever accidentally disabled.
    try:
        email_confirmed = is_email_confirmed(current_user.user_id)
    except SupabaseAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "EMAIL_VERIFICATION_CHECK_FAILED", "message": f"Could not verify your email status: {str(exc)[:150]}"},
        ) from exc
    if not email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "EMAIL_NOT_VERIFIED",
                "message": "Please verify your email address before completing hospital registration. Check your inbox (including spam) for the confirmation link we sent, then try again.",
            },
        )

    # Create new registration
    try:
        first_name, _, last_name = payload.admin_name.partition(" ")
        hospital = Hospital(
            name=payload.hospital_name,
            legal_name=payload.hospital_name,
            country=payload.country,
        )
        profile = ProfessionalProfile(
            auth_user_id=current_user.user_id,
            first_name=first_name or payload.admin_name,
            last_name=last_name or first_name or payload.admin_name,
            professional_type="Hospital Administrator",
            phone=payload.admin_phone,
            professional_registration_number=payload.admin_professional_number,
        )
        role = db.scalar(select(Role).where(Role.code == "HOSPITAL_ADMIN"))
        if role is None:
            role = Role(code="HOSPITAL_ADMIN", name="Hospital Administrator")
            db.add(role)
            db.flush()

        db.add_all([hospital, profile])
        db.flush()
        membership = HospitalMembership(
            professional_id=profile.id,
            hospital_id=hospital.id,
            status="ACTIVE",
        )
        db.add(membership)
        db.flush()
        db.add(MembershipRole(membership_id=membership.id, role_id=role.id, assigned_by=current_user.user_id))
        db.add(
            MembershipEvent(
                membership_id=membership.id,
                hospital_id=hospital.id,
                actor_user_id=current_user.user_id,
                event_type="MEMBERSHIP_CREATED",
                details={
                    "event": "MEMBERSHIP_CREATED",
                    "source": "hospital_registration",
                    "role_code": "HOSPITAL_ADMIN",
                },
            )
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "REGISTRATION_FAILED", "message": f"Hospital registration failed: {str(exc)[:100]}"},
        ) from exc

    return {"id": current_user.user_id, "hospital_id": str(hospital.id), "status": "ACTIVE"}


@router.patch("/me", summary="Update the caller's own profile")
async def update_my_profile(
    payload: ProfileUpdateRequest,
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
    db: Annotated[Session, Depends(get_db_session)],
) -> dict[str, Any]:
    """Update the authenticated professional's own self-service profile fields.

    Used by the Settings screen. Every user can update their own name,
    phone, professional type, license/registration number, and date of
    birth - this never touches hospital, role, or membership data.
    """
    professional = db.get(ProfessionalProfile, context.professional.id)
    if professional is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional profile not found")

    if payload.first_name is not None:
        professional.first_name = payload.first_name
    if payload.last_name is not None:
        professional.last_name = payload.last_name
    if payload.phone is not None:
        professional.phone = payload.phone
    if payload.professional_type is not None:
        professional.professional_type = payload.professional_type
    if payload.professional_registration_number is not None:
        professional.professional_registration_number = payload.professional_registration_number
    if payload.date_of_birth is not None:
        professional.date_of_birth = payload.date_of_birth

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "PROFILE_UPDATE_FAILED", "message": f"Profile update failed: {str(exc)[:100]}"},
        ) from exc

    return {
        "id": context.user_id,
        "firstName": professional.first_name,
        "lastName": professional.last_name,
        "phone": professional.phone,
        "professionalType": professional.professional_type,
        "licenseNumber": professional.professional_registration_number,
        "dateOfBirth": professional.date_of_birth.isoformat() if professional.date_of_birth else None,
    }


@router.post("/me/password-changed", summary="Acknowledge that the caller has set their own password")
async def acknowledge_password_changed(
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
    db: Annotated[Session, Depends(get_db_session)],
) -> dict[str, Any]:
    """Clear the forced-password-reset flag once the user sets their own password.

    The password itself is changed directly against Supabase Auth from the
    frontend (supabase.auth.updateUser) using the caller's own session -
    this endpoint only updates our own bookkeeping flag afterward.
    """
    professional = db.get(ProfessionalProfile, context.professional.id)
    if professional is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professional profile not found")
    professional.force_password_reset = False
    db.commit()
    return {"forcePasswordReset": False}
