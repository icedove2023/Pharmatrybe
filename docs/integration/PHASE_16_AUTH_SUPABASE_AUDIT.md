# Phase 16 Authentication and Supabase Audit

**Audit date:** 2026-08-19  
**Scope:** Read-only repository audit  
**Implementation performed:** None  
**Authoritative runtime:** `from app.main import app; app.openapi()`

## 1. Executive Summary

The repository contains frontend authentication screens, a Zustand auth store, frontend role/permission mappings, and backend JWT/bearer verification scaffolding. It does **not** contain a working authentication lifecycle.

Confirmed current state:

- The frontend login and hospital-registration calls explicitly reject with `Authentication backend integration pending.`
- The frontend does not create or restore a real authenticated session.
- The backend exposes only `GET /api/v1/auth`, a status placeholder.
- No login, registration, refresh, logout, session, user, organisation, or hospital API is registered.
- Backend JWT verification helpers exist for future protected endpoints, but no current application route uses the dependency.
- Database/schema files contain WHO knowledge entities only; no users, organisations, memberships, invitations, profiles, or account-status tables were found.
- No Supabase client import, Supabase migration directory, generated Supabase types, RLS policy, or `auth.users` reference was found.
- Frontend role and permission definitions are UI-only and cannot provide authorization.
- Clinical cases, recommendations, WHO data, and audit metadata have no organisation ownership boundary in the inspected models/schema.

**Audit conclusion:** Phase 16 implementation prerequisites are not yet present. Authentication, hospital onboarding, identity persistence, tenant isolation, backend RBAC, and Supabase integration require separate design and implementation decisions.

## 2. Current Authentication Architecture

### Confirmed backend scaffolding

| Area | File | Current behaviour | Authoritative source | Status |
|---|---|---|---|---|
| Bearer extraction | `apps/api/app/auth/security.py` | Extracts an HTTP Bearer credential when supplied | Backend source | `backend_authoritative`, scaffolding only |
| JWT decoding | `apps/api/app/auth/jwt.py` | Decodes three-part tokens, checks expiry, and verifies an HS256-style signature using `settings.jwt_secret` | Backend source | `backend_authoritative`, not an issuance system |
| Current-user dependency | `apps/api/app/auth/dependencies.py` | Verifies a token and creates `AuthenticatedUser` from claims | Backend source | `backend_authoritative`, unused by current API routes |
| Role normalization | `apps/api/app/auth/roles.py` | Defines four backend scaffold roles and normalizes text | Backend source | `backend_authoritative`, not exposed through identity APIs |
| Permission marker | `apps/api/app/auth/permissions.py` | Decorator attaches a marker to a callable; wrapper does not enforce authorization | Backend source | `backend_authoritative`, scaffold only |
| Request identity context | `apps/api/app/api/middleware/request_context.py` | Sets `user_id` and `user_role` to `anonymous` for every request | Backend source | `backend_authoritative`, no token-to-context integration |
| Auth router | `apps/api/app/api/v1/auth.py` | Returns `{"service": "Authentication Service", "status": "available"}` from a GET status route | Runtime/source | `backend_authoritative`, placeholder |
| Admin router | `apps/api/app/api/v1/admin.py` | Returns an administration service status payload from GET | Runtime/source | `backend_authoritative`, placeholder |

### Important implementation observations

- `get_current_user` is a dependency available for future routes, not evidence of an active protected API.
- `require_admin`, `require_clinician`, `require_steward`, and `require_lab_scientist` exist but are not attached to the registered clinical/auth/admin routes inspected.
- `Permission` values exist, but `require_permission` only records metadata; it does not enforce the permission.
- `jwt_secret` defaults to `change-me` in backend configuration. This is a critical implementation prerequisite, not a production secret.
- Backend configuration includes `SUPABASE_URL` and `SUPABASE_KEY` fields as placeholders, but no Supabase integration was found.

## 3. Frontend Authentication Audit

### Frontend files inspected

- `src/api/authApi.ts`
- `src/stores/authStore.ts`
- `src/api/client.ts`
- `src/components/auth/LoginForm.tsx`
- `src/components/auth/HospitalRegistrationForm.tsx`
- `src/components/auth/AuthGuard.tsx`
- `src/App.tsx`
- `src/types/auth.ts`
- related header/session/role components

| Question | Finding | Classification |
|---|---|---|
| How does login work? | `authApi.login()` rejects with `Authentication backend integration pending.` | `unavailable` |
| Are real credentials submitted? | No. The frontend method does not call `fetch` or an auth endpoint. | `frontend_only` / `unavailable` |
| Are sessions persisted? | No authoritative session persistence. `getCurrentSession()` returns `null`. | `unavailable` |
| Are tokens created locally? | No. Previous local token generation was removed. | `frontend_only` history; current state `unavailable` |
| Are tokens stored? | `src/api/client.ts` no longer reads or attaches a browser token. | `backend_authoritative` boundary absent |
| Are tokens attached to requests? | No Authorization header is added by the current client. | `unavailable` |
| How does logout work? | Clears frontend Zustand state; `authApi.logout()` is a no-op. No backend revocation call exists. | `frontend_only` |
| How is state restored after refresh? | Store calls `getCurrentSession()`, which returns `null`; app becomes unauthenticated. | `frontend_only` |
| How are unauthenticated users handled? | `App.tsx` renders landing/login/registration screens; `AuthGuard` renders an authentication-required state. | `frontend_only` |
| How are roles represented? | `src/types/auth.ts` defines frontend roles and `ROLE_PERMISSIONS_MAP`. | `frontend_only` |
| Are roles authoritative? | No. They are only client-side UI state and are not sourced from a backend identity. | `frontend_only` |
| Do demo personas remain? | Demo login controls and persona session generation were removed from the active auth path. | `dead_code` removed |
| Does fabricated user identity remain? | No active auth identity is created. Any names in test fixtures or UI labels are not authenticated users. | `test_only` / `static_configuration` |
| Can auth state be forged in the browser? | The current store is not authoritative, but UI permission state is inherently client-controlled and no backend route enforces it. | `critical security gap` |

The frontend registration form remains visible as a UI flow, but submission reaches the unavailable auth adapter and does not create an organisation or user.

## 4. Backend Authentication Audit

### Runtime route registration

`apps/api/app/main.py` includes the aggregated `/api/v1` router. `apps/api/app/api/router.py` includes the auth and admin routers. Their active runtime routes are status endpoints only.

### Requested route matrix

| Requested route | Registered? | Runtime method(s) | Implementation file | Auth required? | Authorization required? | Database interaction? | Tested? | Frontend usable? |
|---|---:|---|---|---|---|---|---|---|
| `POST /api/v1/auth/login` | No | None | No implementation | Not applicable | Not applicable | No | No | No |
| `POST /api/v1/auth/register` | No | None | No implementation | Not applicable | Not applicable | No | No | No |
| `POST /api/v1/auth/register-hospital` | No | None | Requirements only | Not applicable | Not applicable | No | No | No |
| `POST /api/v1/auth/refresh` | No | None | No implementation | Not applicable | Not applicable | No | No | No |
| `POST /api/v1/auth/logout` | No | None | No implementation | Not applicable | Not applicable | No | No | No |
| `GET /api/v1/auth/me` | No | None | No implementation | Not applicable | Not applicable | No | No | No |
| `GET /api/v1/auth/session` | No | None | No implementation | Not applicable | Not applicable | No | No | No |
| `GET /api/v1/admin/users` | No | Only `GET /api/v1/admin` status | `apps/api/app/api/v1/admin.py` | No | No | No | No | No |
| `POST /api/v1/admin/users` | No | None | No implementation | Not applicable | Not applicable | No | No | No |
| `PUT /api/v1/admin/users/{user_id}` | No | None | No implementation | Not applicable | Not applicable | No | No | No |
| `DELETE /api/v1/admin/users/{user_id}` | No | None | No implementation | Not applicable | Not applicable | No | No | No |
| `GET /api/v1/organisations` | No | None | No implementation | Not applicable | Not applicable | No | No | No |
| `POST /api/v1/organisations` | No | None | No implementation | Not applicable | Not applicable | No | No | No |
| `GET /api/v1/organisations/{organisation_id}` | No | None | No implementation | Not applicable | Not applicable | No | No | No |

### Currently registered related routes

| Runtime path | Method | Behaviour |
|---|---|---|
| `/api/v1/auth` | GET | Authentication service status placeholder |
| `/api/v1/admin` | GET | Administration service status placeholder |
| `/api/v1/patients` | GET | Patient service status/placeholder route; no verified identity lifecycle |
| `/api/v1/clinical-cases` | GET, POST | Clinical case API; no auth dependency observed |
| `/api/v1/clinical-cases/{case_id}` | GET, PUT, DELETE | Clinical case CRUD; no tenant/auth dependency observed |
| `/api/v1/recommendations/generate` | POST | Canonical recommendation endpoint; no auth dependency observed |

## 5. Runtime OpenAPI Authentication Matrix

Runtime inspection from `apps/api` produced **28 paths**. Relevant runtime paths include:

```text
/api/v1/auth                         GET
/api/v1/admin                        GET
/api/v1/patients                     GET
/api/v1/clinical-cases               GET, POST
/api/v1/clinical-cases/{case_id}     GET, PUT, DELETE
/api/v1/recommendations              GET
/api/v1/recommendations/generate     POST
/api/v1/who/...                      GET routes
/api/v1/soar                         GET
/api/v1/armd                         GET
/api/v1/decision                     GET
/api/v1/explainability               GET
```

No requested authentication lifecycle, organisation, or admin-user CRUD path appears in OpenAPI.

**Runtime conclusion:** No frontend authentication operation is currently usable against the FastAPI API.

## 6. Requirements vs Runtime Gap

| Capability | Requirements specify | Runtime exposes | Frontend expects | Gap |
|---|---|---|---|---|
| Hospital registration | `POST /api/v1/auth/register-hospital`, transactionally creates organisation/admin | No route | Registration form exists | Full gap |
| Login | `POST /api/v1/auth/login` with generic 401/403 handling | No route | Login form exists | Full gap |
| Email verification | Recommended/considered requirement | No route or workflow | No active verified flow | Full gap |
| Password reset | Not specified as a concrete endpoint in the requirements excerpt | No route | No verified flow | Gap / requires decision |
| Sessions | Access/refresh tokens and server-side sessions | No route or session store | AuthSession type only | Full gap |
| Refresh | `POST /api/v1/auth/refresh` | No route | No active call | Full gap |
| Logout | `POST /api/v1/auth/logout` | No route | Local state clear only | Full gap |
| Organisation membership | `organization_id` and invited-by lineage required | No identity tables/routes | User type has organization string | Full gap |
| User provisioning | Admin user list/create/role/status endpoints | No route | Admin UI/client method surface exists but unavailable | Full gap |
| Roles | Five frontend/requirements roles | Backend scaffold defines four different role names | Frontend has five roles | Contract mismatch; requires decision |
| RBAC | Server-side role authorization required | Dependency helpers exist but are not wired to routes | Client permission map exists | Full enforcement gap |
| Audit logging | Immutable audit record for auth/admin mutations | Pydantic audit model and in-memory/service logging scaffolding; no identity mutation events | Admin audit UI exists but data client unavailable | Full persistence gap |
| Account deactivation | Admin status endpoint and last-admin invariant | No route or identity model | Admin UI method unavailable | Full gap |

## 7. Database Identity Audit

### Database artifacts

- `apps/api/app/database/schema.sql` is a WHO knowledge-base schema.
- No `supabase/migrations` directory exists in the inspected repository.
- No database migration set defining identity tables was found.
- SQLAlchemy models under `apps/api/app/models/` are WHO knowledge entities: diseases, drugs, evidence, recommendations, pathogens, diagnostics, monitoring, follow-up, referral, stewardship, metadata, and junctions.

| Entity/concept | Exists? | File/table evidence | Primary key | Relationships | Used by application? |
|---|---:|---|---|---|---|
| Users | No | No user model/table | None | None | No |
| Profiles | No | No profile model/table | None | None | No |
| Hospitals | No | No hospital model/table | None | None | No |
| Organisations | No | No organisation model/table | None | None | No |
| Facilities | No | No facility model/table | None | None | No |
| Memberships | No | No membership model/table | None | None | No |
| Roles table | No | Backend enum only in `app/auth/roles.py` | None | None | Scaffold only |
| Permissions table | No | Backend enum/marker only in `app/auth/permissions.py` | None | None | Scaffold only |
| Invitations | No | No model/table | None | None | No |
| Audit events | Partial | `app/models/audit_log.py` Pydantic schema; audit service/logging scaffolding | `event_id` in schema | No DB relationship | Logging/scaffold only |
| Account status | No | `AuthenticatedUser.active` claim field only | None | None | Token-claim scaffold |
| Verification status | No | No model/table | None | None | No |

## 8. Multi-Tenant Boundary Audit

No organisation or hospital ownership boundary was found in the inspected clinical data model.

| Entity | Organisation identifier? | Backend ownership enforcement? | SQL/database enforcement? | Current conclusion |
|---|---:|---:|---:|---|
| Clinical cases | No verified organisation field/model | No | No | No tenant boundary verified |
| Recommendations | WHO recommendation table links disease/evidence/drug only | No | No | No tenant boundary verified |
| WHO data | No; global knowledge entities | Not organisation-owned | No | Shared/global knowledge, not tenant-scoped |
| Audit records | `user_id`/`user_role` fields in Pydantic schema only; no organisation ID | No | No | No tenant boundary verified |
| Patient records | No verified patient identity model/table in backend models | No | No | No tenant boundary verified |
| SOAR/ARMD records | No standalone persistence/API contract | No | No | Not exposed; no tenant boundary verified |

Because no backend identity and ownership layer is present, the repository does not currently establish whether one hospital could query another hospital’s clinical records. The correct audit result is **NOT VERIFIED / no tenant enforcement demonstrated**, not an assumption of isolation.

## 9. RBAC Audit

### Existing roles

| Role | Existing? | Source | Current permissions | Authoritative? | Phase 16 target |
|---|---:|---|---|---|---|
| Infectious Disease Specialist | Yes, frontend | `src/types/auth.ts` | Clinical assessment/recommendation/explainability/knowledge UI permissions | No | Requires backend mapping decision |
| General Practitioner | Yes, frontend | `src/types/auth.ts` | Clinical assessment/recommendation/knowledge UI permissions | No | Requires backend mapping decision |
| Pharmacist | Yes, frontend | `src/types/auth.ts` | Clinical assessment/recommendation/knowledge/stewardship UI permissions | No | Requires backend mapping decision |
| Admin | Yes, frontend | `src/types/auth.ts` | UI admin/plugin/system/audit permissions | No | Requires backend mapping decision |
| Researcher | Yes, frontend | `src/types/auth.ts` | UI research/knowledge/read permissions | No | Requires backend mapping decision |
| Clinician | Yes, backend scaffold | `apps/api/app/auth/roles.py` | `require_clinician` checks normalized token claim | Only for a future protected route | Requires role taxonomy decision |
| Laboratory Scientist | Yes, backend scaffold | `apps/api/app/auth/roles.py` | `require_lab_scientist` checks normalized token claim | Only for a future protected route | Requires role taxonomy decision |
| Stewardship Team | Yes, backend scaffold | `apps/api/app/auth/roles.py` | `require_steward` checks normalized token claim | Only for a future protected route | Requires role taxonomy decision |
| Administrator | Yes, backend scaffold | `apps/api/app/auth/roles.py` | `require_admin` checks normalized token claim | Only for a future protected route | Requires role taxonomy decision |

The frontend and backend role vocabularies do not match exactly. No authenticated backend endpoint currently resolves, persists, or enforces either vocabulary.

### Browser mutability risk

The frontend permission map and Zustand state are client-controlled presentation state. They must never be treated as authorization. The backend dependency functions are not currently attached to the clinical/admin routes in runtime OpenAPI.

## 10. Supabase Readiness Audit

| Supabase capability | Current state | Classification |
|---|---|---|
| `@supabase/supabase-js` import | No import found | `unavailable` |
| `VITE_SUPABASE_URL` | No frontend configuration found | `unavailable` |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | No frontend configuration found | `unavailable` |
| Backend `SUPABASE_URL`/`SUPABASE_KEY` fields | Placeholder settings fields exist in `apps/api/app/core/config.py` | `supabase_candidate`, not integration |
| Supabase client configuration | None found | `unavailable` |
| Supabase migrations | None found | `unavailable` |
| Supabase-generated types | None found | `unavailable` |
| Supabase auth hooks | None found | `unavailable` |
| Database triggers | None found | `unavailable` |
| RLS policies | None found | `unavailable` |
| `auth.users` references | None found | `unavailable` |
| Supabase service-role key in frontend | None found | Not observed |

The repository is **not Supabase-integrated**. It has placeholder backend environment fields only.

## 11. Supabase Architecture Fit

This section is an audit assessment, not an implementation decision.

| Proposed boundary | Assessment | Evidence / prerequisite |
|---|---|---|
| Supabase owns signup/login/email verification/password recovery/sessions/JWT | Compatible candidate | No current client/project/configuration exists; requires project and identity design |
| FastAPI verifies Supabase JWTs | Compatible candidate | Existing bearer/JWT scaffolding can be adapted, but current verifier is custom HS256-oriented and not wired to routes |
| FastAPI resolves organisation/membership/RBAC | Missing prerequisite | No identity, membership, organisation, or role persistence exists |
| Postgres stores organisation/profile/membership/clinical data | Architecturally plausible | Current schema is WHO-only and has no tenant keys or migration plan |
| Supabase RLS protects tenant data | Missing prerequisite / requires decision | No Supabase migrations, policies, tenant claims, or ownership columns exist |
| Frontend uses Supabase session client | Missing prerequisite | No Supabase dependency or frontend environment variables exist |
| FastAPI remains business-rule authority | Compatible with project principles | Existing backend owns clinical routes and recommendation synthesis |
| Supabase directly replaces FastAPI clinical authorization | Incompatible with current boundary | Project requirements place RBAC/application authority in backend; this would require an explicit architectural decision |

**Requires Decision:** whether Supabase Auth JWTs are verified directly by FastAPI, whether tenant claims are embedded in tokens, and whether RLS is authoritative, defense-in-depth, or not used for clinical APIs.

## 12. Security Findings

| Severity | Finding | Evidence | Classification |
|---|---|---|---|
| Critical | Clinical and case endpoints have no verified authentication dependency in runtime routes | Runtime OpenAPI and route source | `critical` |
| Critical | No organisation isolation or tenant ownership boundary exists | Models/schema inspection | `critical` |
| Critical | Frontend role/permission state is browser-controlled | `src/types/auth.ts`, Zustand store, AuthGuard | `critical` |
| High | No login, refresh, logout, registration, or session revocation lifecycle | Runtime OpenAPI | `high` |
| High | Backend `jwt_secret` default is `change-me` | `app/core/config.py` | `high` |
| High | Permission decorator attaches metadata without enforcing it | `app/auth/permissions.py` | `high` |
| High | AuditLog is a Pydantic record shape, not verified immutable database persistence | `app/models/audit_log.py`, audit service usage | `high` |
| High | No email verification or password recovery flow | Runtime/source search | `high` |
| Medium | Frontend registration/login screens can imply availability despite pending backend integration | Auth components and unavailable adapter | `medium` |
| Medium | Backend and frontend role vocabularies differ | `app/auth/roles.py` vs `src/types/auth.ts` | `medium` |
| Medium | CORS allows all origins with credentials in `app/main.py` | `CORSMiddleware` configuration | `medium` |
| Informational | JWT scaffolding is documented as future-protected-endpoint support | Auth module docstrings | `informational` |

No frontend service-role key exposure was observed. No Supabase client exists to expose one.

## 13. Authentication Test Audit

### Existing tests

`apps/api/tests/test_auth.py` tests the backend scaffold:

- backend role enum values and normalization;
- permission marker attachment/retrieval;
- JWT payload decoding;
- missing/invalid/expired token rejection;
- `get_current_user` claim mapping;
- role dependency rejection;
- dependency importability.

These tests validate helper behavior, not an end-to-end authentication API.

### Tests to retain

- JWT signature/expiry rejection tests;
- claim normalization tests;
- dependency authorization tests;
- future endpoint 401/403 tests once routes exist;
- generic invalid-credential response tests;
- last-admin and self-deactivation invariants once persistence exists.

### Tests to eventually replace or extend

- Frontend auth tests should not treat client permission maps or local state as backend authorization.
- Requirements-only registration/login UI tests should become integration tests against real routes after implementation.
- No current end-to-end multi-tenant tests exist.

### Missing security tests

- Login success/failure with generic credential errors;
- inactive-account 403;
- refresh-token rotation and revocation;
- logout invalidation;
- email verification and password recovery;
- hospital registration transactionality;
- duplicate email 409;
- admin-only provisioning;
- last-active-admin protection;
- self-deactivation rejection;
- organisation isolation at API and database/RLS levels;
- cross-tenant access denial;
- audit event persistence and immutability;
- secret/configuration validation.

## 14. Phase 16 Dependency Graph

Derived dependency order:

```text
Identity architecture decision
        |
        +--> Supabase project and Auth configuration
        |          |
        |          +--> Frontend Supabase/session client configuration
        |          +--> JWT claim and verification contract
        |
        +--> Identity data model decision
                   |
                   +--> organisations / users / profiles / memberships
                   +--> role and permission mapping
                   +--> invitations / account status / verification state
                   +--> audit event persistence
                              |
                              +--> FastAPI authentication dependency wiring
                              +--> FastAPI organisation resolution
                              +--> FastAPI server-side RBAC
                              +--> tenant ownership columns and query enforcement
                              +--> RLS policy decision/configuration
                                         |
                                         +--> protected clinical-case APIs
                                         +--> protected recommendation APIs
                                         +--> protected admin/provisioning APIs
                                         +--> hospital registration transaction
                                         +--> user invitation/provisioning workflow
                                         +--> frontend session restore and route guards
                                         +--> end-to-end security tests
```

## 15. Required Architectural Decisions

These are recommendations/questions, not existing architecture:

1. Select the canonical role vocabulary and map frontend clinical roles to backend roles.
2. Decide whether the identity source is Supabase Auth exclusively or a separately managed identity service.
3. Define the JWT algorithm, issuer, audience, key rotation, and JWKS/secret verification contract.
4. Define organisation membership semantics: one organisation per user versus multiple memberships.
5. Define tenant ownership for clinical cases, recommendations, audit events, and future prediction records.
6. Decide whether PostgreSQL RLS is required, defense-in-depth, or outside the first implementation boundary.
7. Define whether FastAPI or Supabase is authoritative for role/membership authorization.
8. Define immutable audit storage and retention requirements.
9. Define email verification, password recovery, invitation, inactive-account, and session-revocation behavior.
10. Define the browser token/session storage policy and CSRF strategy.

## 16. Implementation Prerequisites

Before Phase 16 implementation begins, the repository needs:

- approved identity and tenant data model;
- approved role mapping and permission matrix;
- Supabase project/configuration decision;
- environment-variable contract without secrets committed to source;
- JWT verification contract between Supabase and FastAPI;
- migrations for identity, organisation, membership, invitation, account status, and audit data;
- repository/service boundaries for identity and tenant resolution;
- protected route dependency plan;
- frontend API/session adapter plan;
- end-to-end security and tenant-isolation test plan.

## 17. Explicit Non-Changes

This audit made no implementation changes.

```text
NO APPLICATION CODE CHANGED
NO FRONTEND CODE CHANGED
NO BACKEND CODE CHANGED
NO DATABASE MIGRATIONS CHANGED
NO SUPABASE PROJECT CREATED
NO PACKAGES INSTALLED
NO AUTHENTICATION IMPLEMENTED
```

The only intended artifact from this Phase 16 audit is this document:

`docs/integration/PHASE_16_AUTH_SUPABASE_AUDIT.md`

## 18. Audit Conclusion

### Confirmed

- Auth/JWT/RBAC helper scaffolding exists in the backend.
- Frontend auth UI/store/role presentation exists.
- Runtime exposes no authentication lifecycle or identity-management routes.
- WHO database schema and clinical knowledge APIs exist without identity ownership.
- Supabase is not integrated.

### Observed

- Frontend authentication is explicitly unavailable rather than silently simulated.
- Backend request context defaults identity to anonymous.
- Frontend roles and permissions remain client-side presentation state.
- Backend configuration contains placeholder Supabase and JWT settings.

### Gaps

- Identity persistence, sessions, refresh/revocation, organisation membership, tenant isolation, backend RBAC, admin provisioning, email verification, password recovery, and audit persistence.

### Recommendation

Treat Phase 16 as a new identity/tenant/security implementation phase. Begin with the architectural decisions and prerequisites above, then implement backend authority and tests before enabling the frontend authentication screens.

### Final status

**PHASE 16 AUDIT COMPLETE — NO IMPLEMENTATION PERFORMED**
