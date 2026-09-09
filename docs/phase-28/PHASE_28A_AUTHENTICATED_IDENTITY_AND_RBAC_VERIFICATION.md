# Phase 28A Authenticated Identity and RBAC Verification

## Authentication flow
The frontend uses the provider-backed `authApi.login` path and the auth store tracks authenticated, unauthenticated, expired, forbidden, and recovery states. The login form is present at the application boundary.

`AUTHENTICATED_WORKFLOW: NOT_VERIFIED`

No interactive browser-control capability was available in this execution, so credentials were not entered, transmitted, stored, logged, or reported.

## Tenant and role resolution
Backend `get_authorization_context` requires a verified bearer token, an active professional profile, exactly one active hospital membership, canonical roles, and derived permissions. `AuthorizationContext.tenant_context` binds hospital, authenticated user, professional, role, and permissions.

Static/test evidence passes for governed plugin admission, tenant matching, governance, security, and external execution: 15 focused tests.

## RBAC
The catalogue defines `CLINICIAN`, `HOSPITAL_ADMIN`, `PHARMACIST`, laboratory, infectious-disease, and researcher roles with deterministic permissions. `require_clinician`, `require_admin`, `require_permission`, and `deny_by_default` enforce role/permission boundaries.

Interactive authorized and unauthorized browser actions were not executed.

## Session/sign-out
The frontend auth store and Supabase adapter contain local session restoration and sign-out handling; R8 session lifecycle tests cover sign-out and expiry behavior. Browser sign-out verification was not performed.

## Status
`PARTIAL`: identity, tenant, and RBAC code/test boundaries are evidenced; authenticated browser acceptance remains `NOT_VERIFIED`.
