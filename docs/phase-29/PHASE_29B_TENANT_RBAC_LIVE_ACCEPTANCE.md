# Phase 29B Tenant/RBAC Live Acceptance

## Backend authority
`get_authorization_context` requires a verified identity, active profile, exactly one active hospital membership, canonical role, and derived permissions. Tenant context is derived server-side from membership; it is not client-controlled.

## Evidence
Governance, plugin admission, security, and external execution tests passed. Role catalogue tests cover clinician/admin and permission boundaries. A live authenticated tenant/role display was not performed.

## Status
`PARTIAL`: backend tenant/RBAC enforcement is tested; live authenticated tenant and role confirmation is `NOT_VERIFIED`.
