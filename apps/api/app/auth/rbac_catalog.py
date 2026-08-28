"""Canonical static RBAC catalogue from the approved Phase 16C matrix."""

from __future__ import annotations

CANONICAL_ROLE_CODES = (
    "HOSPITAL_ADMIN",
    "CLINICIAN",
    "PHARMACIST",
    "LABORATORY_SCIENTIST",
    "INFECTIOUS_DISEASE_SPECIALIST",
    "RESEARCHER",
)

# Permission rows marked Policy, Limited, Approved, or Controlled in 16C are
# catalogue entries but require later contextual enforcement; they are not
# static role grants in this slice.
CANONICAL_PERMISSION_CODES = (
    "hospital:view",
    "hospital:update",
    "professionals:invite",
    "professionals:view",
    "professionals:manage",
    "roles:assign",
    "patients:view",
    "patients:create",
    "cases:view",
    "cases:create",
    "cases:update",
    "laboratory:view",
    "laboratory:create",
    "recommendations:view",
    "recommendations:request",
    "recommendations:review",
    "guidelines:view",
    "guidelines:manage",
    "stewardship:view",
    "stewardship:manage",
    "plugins:view",
    "plugins:configure",
    "workflows:manage",
    "workflows:execute",
    "audit:view",
    "data:export",
)

ROLE_PERMISSION_GRANTS: dict[str, frozenset[str]] = {
    "HOSPITAL_ADMIN": frozenset(
        {
            "hospital:view",
            "hospital:update",
            "professionals:invite",
            "professionals:view",
            "professionals:manage",
            "roles:assign",
            "guidelines:view",
            "guidelines:manage",
            "stewardship:view",
            "plugins:view",
            "plugins:configure",
            "workflows:manage",
            "audit:view",
        }
    ),
    "CLINICIAN": frozenset(
        {
            "hospital:view",
            "professionals:view",
            "patients:view",
            "patients:create",
            "cases:view",
            "cases:create",
            "cases:update",
            "laboratory:view",
            "recommendations:view",
            "recommendations:request",
            "recommendations:review",
            "guidelines:view",
            "stewardship:view",
            "workflows:execute",
        }
    ),
    "PHARMACIST": frozenset(
        {
            "hospital:view",
            "professionals:view",
            "patients:view",
            "cases:view",
            "cases:create",
            "laboratory:view",
            "recommendations:view",
            "recommendations:request",
            "recommendations:review",
            "guidelines:view",
            "stewardship:view",
            "workflows:execute",
        }
    ),
    "LABORATORY_SCIENTIST": frozenset(
        {
            "hospital:view",
            "professionals:view",
            "cases:view",
            "laboratory:view",
            "laboratory:create",
            "guidelines:view",
            "stewardship:view",
            "workflows:execute",
        }
    ),
    "INFECTIOUS_DISEASE_SPECIALIST": frozenset(
        {
            "hospital:view",
            "professionals:view",
            "patients:view",
            "patients:create",
            "cases:view",
            "cases:create",
            "cases:update",
            "laboratory:view",
            "recommendations:view",
            "recommendations:request",
            "recommendations:review",
            "guidelines:view",
            "stewardship:view",
            "workflows:execute",
        }
    ),
    "RESEARCHER": frozenset({"guidelines:view"}),
}

HOSPITAL_ADMIN_PERMISSION_CODES = tuple(sorted(ROLE_PERMISSION_GRANTS["HOSPITAL_ADMIN"]))


def validate_catalogue() -> None:
    """Fail fast if the checked-in RBAC catalogue is internally inconsistent."""
    if len(CANONICAL_ROLE_CODES) != len(set(CANONICAL_ROLE_CODES)):
        raise ValueError("Canonical role codes must be unique")
    if len(CANONICAL_PERMISSION_CODES) != len(set(CANONICAL_PERMISSION_CODES)):
        raise ValueError("Canonical permission codes must be unique")
    if set(ROLE_PERMISSION_GRANTS) != set(CANONICAL_ROLE_CODES):
        raise ValueError("Every canonical role must have a deterministic mapping")
    unknown_permissions = {
        permission
        for permissions in ROLE_PERMISSION_GRANTS.values()
        for permission in permissions
        if permission not in CANONICAL_PERMISSION_CODES
    }
    if unknown_permissions:
        raise ValueError(f"Unknown permissions in role grants: {sorted(unknown_permissions)}")


validate_catalogue()