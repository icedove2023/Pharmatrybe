"""Reusable authentication dependencies for the PharmaTrybe backend scaffold."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth.current_user import AuthenticatedUser
from app.auth.jwt import TokenVerificationError, verify_token
from app.auth.rbac_catalog import CANONICAL_ROLE_CODES
from app.auth.security import bearer_scheme, get_bearer_token
from app.auth.tenant_context import TenantContext
from app.database.session import get_db_session
from app.models.identity import HospitalMembership, MembershipRole, ProfessionalProfile, Role, RolePermission


class AuthorizationContext:
    """Resolved application identity, tenant, roles, and permissions."""

    def __init__(
        self,
        user: AuthenticatedUser,
        professional: ProfessionalProfile,
        membership: HospitalMembership,
        roles: set[str],
        permissions: set[str],
    ) -> None:
        self.user = user
        self.professional = professional
        self.membership = membership
        self.hospital = membership.hospital
        self.roles = roles
        self.permissions = permissions

    @property
    def user_id(self) -> str:
        """Return the Supabase Auth user UUID."""
        return self.user.user_id

    @property
    def hospital_id(self) -> str:
        """Return the resolved active hospital UUID."""
        return self.membership.hospital_id

    @property
    def tenant_context(self) -> TenantContext:
        """Return the immutable runtime tenant context derived from membership."""
        primary_role = sorted(self.roles)[0] if self.roles else None
        return TenantContext(
            hospital_id=self.hospital_id,
            authenticated_user_id=self.user_id,
            professional_id=self.professional.id,
            role=primary_role,
            permissions=frozenset(self.permissions),
        )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    request: Request,
) -> AuthenticatedUser:
    """Return the authenticated user context for future protected endpoints."""
    token = get_bearer_token(credentials)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        claims = verify_token(token)
    except TokenVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = AuthenticatedUser(
        user_id=str(claims["sub"]),
        email=str(claims.get("email") or ""),
    )
    request.state.user_id = user.user_id
    request.state.user_role = "authenticated"
    return user


async def get_authorization_context(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    request: Request,
) -> AuthorizationContext:
    """Resolve the active PharmaTrybe membership for a verified identity."""
    professional = db.scalar(
        select(ProfessionalProfile)
        .where(ProfessionalProfile.auth_user_id == current_user.user_id)
        .options(
            selectinload(ProfessionalProfile.memberships)
            .selectinload(HospitalMembership.roles)
            .selectinload(MembershipRole.role)
            .selectinload(Role.role_permissions)
            .selectinload(RolePermission.permission)
        )
    )
    if professional is None or professional.profile_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_INACTIVE", "message": "Application profile is not active"},
        )

    active_memberships = [membership for membership in professional.memberships if membership.status == "ACTIVE"]
    if len(active_memberships) != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Active hospital membership required")

    membership = active_memberships[0]
    roles = {membership_role.role.code for membership_role in membership.roles}
    if not roles or not roles.issubset(set(CANONICAL_ROLE_CODES)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Canonical application role required")
    permissions = {
        role_permission.permission.code
        for membership_role in membership.roles
        for role_permission in membership_role.role.role_permissions
    }
    context = AuthorizationContext(current_user, professional, membership, roles, permissions)
    request.state.hospital_id = context.hospital_id
    request.state.user_role = ",".join(sorted(context.roles))
    return context


def require_permission(permission_name: str):
    """Create a dependency enforcing an approved resource-action permission."""

    async def permission_checker(
        context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
    ) -> AuthorizationContext:
        if permission_name not in context.permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return context

    return permission_checker


def require_same_hospital(resource_hospital_id: str):
    """Create a dependency enforcing the resolved hospital boundary."""

    async def hospital_checker(
        context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
    ) -> AuthorizationContext:
        if context.hospital_id != resource_hospital_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-hospital access forbidden")
        return context

    return hospital_checker


async def deny_by_default(
    _context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> None:
    """Deny operations that have no approved static permission contract."""
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation is not authorized")


async def require_clinician(
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> AuthorizationContext:
    """Require the caller to have the clinician role."""
    if "CLINICIAN" not in context.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed")
    return context


async def require_admin(
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> AuthorizationContext:
    """Require the caller to have the administrator role."""
    if "HOSPITAL_ADMIN" not in context.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed")
    return context


async def require_steward(
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> AuthorizationContext:
    """Require the caller to have the stewardship team role."""
    if "PHARMACIST" not in context.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed")
    return context


async def require_lab_scientist(
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
) -> AuthorizationContext:
    """Require the caller to have the laboratory scientist role."""
    if "LABORATORY_SCIENTIST" not in context.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed")
    return context
