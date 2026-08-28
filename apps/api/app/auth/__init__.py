"""Authentication infrastructure for the PharmaTrybe backend scaffold."""

from app.auth.current_user import AuthenticatedUser
from app.auth.dependencies import (
    AuthorizationContext,
    deny_by_default,
    get_authorization_context,
    get_current_user,
    require_admin,
    require_clinician,
    require_lab_scientist,
    require_permission,
    require_same_hospital,
    require_steward,
)
from app.auth.jwt import TokenVerificationError, verify_token
from app.auth.permissions import Permission, get_required_permission
from app.auth.roles import PharmaTrybeRole, normalize_role
from app.auth.security import bearer_scheme, get_bearer_token

__all__ = [
    "AuthenticatedUser",
    "AuthorizationContext",
    "deny_by_default",
    "Permission",
    "PharmaTrybeRole",
    "TokenVerificationError",
    "bearer_scheme",
    "get_bearer_token",
    "get_authorization_context",
    "get_current_user",
    "get_required_permission",
    "normalize_role",
    "require_admin",
    "require_clinician",
    "require_lab_scientist",
    "require_permission",
    "require_same_hospital",
    "require_steward",
    "verify_token",
]
