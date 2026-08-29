"""Authentication and application-identity routes for the PharmaTrybe v1 API."""

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

router = APIRouter(prefix="/auth", tags=["auth"])


class HospitalRegistrationRequest(BaseModel):
    """Validated hospital registration data after Supabase account creation."""

    hospital_name: str = Field(..., min_length=2)
    country: str = Field(..., min_length=2)
    admin_name: str = Field(..., min_length=2)


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
    """Create a hospital and its first administrator transactionally."""
    existing_profile = db.scalar(
        select(ProfessionalProfile).where(ProfessionalProfile.auth_user_id == current_user.user_id)
    )
    if existing_profile is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Application profile already exists")

    first_name, _, last_name = payload.admin_name.partition(" ")
    hospital = Hospital(name=payload.hospital_name, legal_name=payload.hospital_name, country=payload.country)
    profile = ProfessionalProfile(
        auth_user_id=current_user.user_id,
        first_name=first_name,
        last_name=last_name or first_name,
        professional_type="Hospital Administrator",
    )
    role = db.scalar(select(Role).where(Role.code == "HOSPITAL_ADMIN"))
    if role is None:
        role = Role(code="HOSPITAL_ADMIN", name="Hospital Administrator")
        db.add(role)
        db.flush()

    try:
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Hospital registration failed") from exc

    return {"id": current_user.user_id, "hospital_id": hospital.id, "status": "ACTIVE"}
