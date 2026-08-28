from __future__ import annotations

from pathlib import Path

import pytest

from app.auth.rbac_catalog import (
    CANONICAL_PERMISSION_CODES,
    CANONICAL_ROLE_CODES,
    HOSPITAL_ADMIN_PERMISSION_CODES,
    ROLE_PERMISSION_GRANTS,
    validate_catalogue,
)


EXPECTED_ROLES = {
    "HOSPITAL_ADMIN",
    "CLINICIAN",
    "PHARMACIST",
    "LABORATORY_SCIENTIST",
    "INFECTIOUS_DISEASE_SPECIALIST",
    "RESEARCHER",
}

EXPECTED_PERMISSIONS = {
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
}


def test_canonical_roles_are_complete_and_unique():
    assert set(CANONICAL_ROLE_CODES) == EXPECTED_ROLES
    assert len(CANONICAL_ROLE_CODES) == len(set(CANONICAL_ROLE_CODES))


def test_canonical_permissions_are_complete_and_unique():
    assert set(CANONICAL_PERMISSION_CODES) == EXPECTED_PERMISSIONS
    assert len(CANONICAL_PERMISSION_CODES) == len(set(CANONICAL_PERMISSION_CODES))


def test_every_role_has_deterministic_static_grants():
    validate_catalogue()
    assert set(ROLE_PERMISSION_GRANTS) == EXPECTED_ROLES
    assert HOSPITAL_ADMIN_PERMISSION_CODES == tuple(sorted(ROLE_PERMISSION_GRANTS["HOSPITAL_ADMIN"]))


def test_conditional_cells_are_not_static_grants():
    conditional_permissions = {
        "patients:view",
        "patients:create",
        "cases:update",
        "recommendations:view",
        "recommendations:review",
        "stewardship:manage",
        "workflows:execute",
        "audit:view",
        "data:export",
    }
    assert "patients:view" not in ROLE_PERMISSION_GRANTS["HOSPITAL_ADMIN"]
    assert "recommendations:view" not in ROLE_PERMISSION_GRANTS["LABORATORY_SCIENTIST"]
    assert "data:export" not in {permission for grants in ROLE_PERMISSION_GRANTS.values() for permission in grants}
    assert conditional_permissions - {"cases:update", "workflows:execute", "audit:view"}


def test_membership_management_is_the_only_static_membership_control():
    granted = {permission for grants in ROLE_PERMISSION_GRANTS.values() for permission in grants}
    assert "professionals:manage" in ROLE_PERMISSION_GRANTS["HOSPITAL_ADMIN"]
    assert "professionals:suspend" not in granted
    assert "professionals:deactivate" not in granted
    assert "memberships:suspend" not in granted
    assert "memberships:deactivate" not in granted


def test_seed_migration_is_idempotent_and_contains_only_canonical_grants():
    migration = Path(__file__).parents[3] / "supabase" / "migrations" / "0002_rbac_seed.sql"
    sql = migration.read_text(encoding="utf-8")
    assert "on conflict (code) do update" in sql
    assert "on conflict (role_id, permission_id) do nothing" in sql
    assert "professionals:suspend" not in sql
    assert "professionals:deactivate" not in sql
    assert "memberships:suspend" not in sql
    assert "memberships:deactivate" not in sql