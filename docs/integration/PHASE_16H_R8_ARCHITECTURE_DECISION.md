# PHASE 16H — R8 Frontend Session Lifecycle Architecture Decision

## 1. Document Identity

**Project:** PharmaTrybe Clinical Intelligence Platform  
**Phase:** 16 / Identity, Tenant, Authentication, Authorization & Platform Integration  
**Slice:** R8  
**Title:** Frontend Session Lifecycle  
**Version:** 1.0  
**Status:** APPROVED  
**Decision Classification:** Confirmed Architecture / Security / Frontend Session Contract  
**Implementation Status:** AUTHORIZED  

This is the sole canonical R8 architecture record and implementation contract.

The legacy “Phase 8 — Explainability Engine” roadmap is a separate numbering system and does not redefine Phase 16 R8.

---

## 2. Purpose and Authority

R8 defines the complete browser/frontend authenticated-session lifecycle that consumes the approved Phase 16 identity, tenancy, authentication, RBAC, and backend authorization architecture.

R8 is the next Phase 16 slice after closed R7. It is not the legacy platform Phase 8 Explainability Engine and does not include recommendation or clinical-logic work.

R8 consumes, and does not reopen:

- Phase 16A identity and tenancy architecture;
- Phase 16B identity and tenant schema;
- Phase 16C role and permission matrix;
- Phase 16D Supabase Auth architecture;
- Phase 16E backend authentication and RBAC design;
- R7 invitation transactionality and delivery;
- R7A transactional outbox;
- R7A-11 secure invitation-token handoff.

If a genuine contradiction directly prevents R8, implementation must stop and report it. R8 must not redesign those preceding decisions by inference.

---

## 3. Scope

R8 covers:

- authoritative frontend authentication state;
- session initialization and restoration;
- access-token availability, expiry, refresh, and invalidation behavior;
- authenticated API-client credential attachment;
- 401 and 403 handling;
- logout and protected-route behavior;
- presentation-only role and permission consumption;
- canonical organisation/hospital context consumption;
- tenant-scoped cache lifecycle;
- multi-tab session changes;
- inactive-account handling;
- invitation-link acceptance handoff after the user follows an R7 delivery link;
- frontend-safe errors, observability, configuration dependencies, and tests.

---

## 4. Non-Goals

R8 does not:

- redesign identity or organisation schema;
- redesign RBAC or permissions;
- redesign Supabase Auth;
- redesign invitation creation, outbox, or token handoff;
- implement backend authorization;
- implement clinical authorization or recommendation logic;
- implement the Explainability Engine;
- change R6, R7, R7A, or R7A-11;
- make frontend role maps security boundaries;
- create a frontend JWT issuer or verifier;
- create migrations, models, backend routes, services, workers, or tests in this documentation task.

---

## 5. Current-State Baseline

The Phase 16 authentication audit records that:

- authentication lifecycle is not implemented;
- frontend login exists but is intentionally unavailable;
- no authoritative session restoration exists;
- no refresh lifecycle exists;
- logout is not authoritative session revocation;
- frontend auth state is not authoritative;
- backend authentication scaffolding is not wired into all runtime routes;
- Supabase is not yet integrated in the inspected frontend runtime.

These are observed implementation facts, not permission to invent replacement architecture.

The audit dependency graph is:

```text
identity architecture
        ↓
Supabase/Auth configuration
        ↓
JWT/session contract
        ↓
identity/membership model
        ↓
RBAC
        ↓
protected backend routes
        ↓
frontend session restore and route guards
        ↓
end-to-end security tests
```

R7 delivered the approved identity/invitation/backend foundations that precede R8.

---

## 6. Dependency Matrix

| Dependency | Source | Status | R8 action |
|---|---|---|---|
| Identity model | Phase 16B | Approved Phase 16 dependency; implemented as applicable | Consume |
| Role/permission matrix | Phase 16C | Approved Phase 16 dependency | Consume |
| Supabase Auth architecture | Phase 16D | Approved Phase 16 dependency | Consume; do not invent provider |
| Backend authentication/RBAC | Phase 16E | Approved Phase 16 dependency | Consume backend authority |
| Invitation transactionality | R7/R7A | R7 closed; R7A approved | Consume |
| Secure invitation handoff | R7A-11 | Approved | Consume acceptance handoff only |
| Frontend session adapter | R8 | New, approved here | Implement |
| Route guards | R8 | New, approved here | Implement |
| Session-aware API client | R8 | New, approved here | Implement |
| Session security tests | R8 | New, approved here | Implement |

---

## 7. Legacy Phase 8 Separation

The older [Backend Implementation Roadmap](../backend/Backend_Implementation_Roadmap.md) labels its legacy Phase 8 as the Explainability Engine. Existing `docs/frontend/PHASE_8_*` and related verification records concern recommendation/explainability contracts.

Those records are a separate legacy roadmap/workstream. They are not competing R8 authority for the Phase 16 sequence and are outside this R8 scope.

---

## 8. R8 Decision Matrix

The following decisions are approved by this contract. Inherited decisions remain owned by their source records; new R8 decisions are approved here.

| ID | Decision | State | Evidence | Approval | Implementation impact |
|---|---|---|---|---|---|
| R8-1 | Scope and authority: R8 is Frontend Session Lifecycle | INHERITED / CONFIRMED | R7 next-slice gate; Phase 16 auth audit | APPROVED | Defines R8 boundary |
| R8-2 | Authentication authority | INHERITED / CONFIRMED | Phase 16D; approved integration baseline | APPROVED | Frontend uses Supabase Auth |
| R8-3 | Session representation | NEW R8 DECISION | R8 contract | APPROVED | Defines lifecycle states |
| R8-4 | Session restoration | NEW R8 DECISION | Phase 16 audit dependency graph | APPROVED | Startup/reload behavior |
| R8-5 | Browser storage policy | INHERITED + R8 CLARIFICATION | Phase 16D; approved Supabase client baseline | APPROVED | Provider-managed; no custom token store |
| R8-6 | Access-token lifecycle | INHERITED + R8 CONTRACT | Phase 16D session authority | APPROVED | Provider-managed refresh, expiry, invalidation |
| R8-7 | API-client integration | NEW R8 DECISION | Phase 16E backend authority | APPROVED | Attach current provider token only |
| R8-8 | HTTP 401 handling | NEW R8 DECISION | R8 scope | APPROVED | Bounded provider refresh/recovery |
| R8-9 | HTTP 403 handling | INHERITED / CONFIRMED | Phase 16C/E backend RBAC | APPROVED | Forbidden state; no refresh |
| R8-10 | Logout | INHERITED + R8 CONTRACT | Phase 16D session termination | APPROVED | Provider logout plus local/cache cleanup |
| R8-11 | Route guards | NEW R8 DECISION | R8 scope | APPROVED | Restore-aware navigation |
| R8-12 | Role/permission consumption | INHERITED / CONFIRMED | Phase 16C/E | APPROVED | Presentation only; backend authority |
| R8-13 | Organisation/tenant context | INHERITED / CONFIRMED | Phase 16A/B/E | APPROVED | No browser tenant override |
| R8-14 | Session-aware cache behavior | NEW R8 DECISION | R8 scope | APPROVED | Clear protected data on transitions |
| R8-15 | Multi-tab/browser concurrency | NEW R8 DECISION | Provider-compatible R8 behavior | APPROVED | Consume provider auth-state changes |
| R8-16 | Session expiry | INHERITED + R8 CONTRACT | Phase 16D session authority | APPROVED | Fail closed |
| R8-17 | Account state | INHERITED / CONFIRMED | Phase 16 identity/account model | APPROVED | Inactive account leaves authenticated state |
| R8-18 | Invitation acceptance handoff | INHERITED / CONFIRMED | R7/R7A/R7A-11 | APPROVED | Backend-authoritative acceptance |
| R8-19 | Error boundaries | NEW R8 DECISION | R8 scope | APPROVED | Safe provider/backend errors |
| R8-20 | Security invariants | INHERITED + R8 CONTRACT | Project constitution and Phase 16 | APPROVED | Browser never authority |
| R8-21 | Testing contract | NEW R8 DECISION | R8 scope | APPROVED | Browser/session/security coverage |
| R8-22 | Observability | INHERITED + R8 CONTRACT | R7 audit principles and R8 scope | APPROVED | No credential leakage |
| R8-23 | Configuration | INHERITED + R8 CONTRACT | Phase 16D and integration baseline | APPROVED | Approved external values only |
| R8-24 | Implementation boundary | CONFIRMED INSTRUCTION | Documentation-first process | APPROVED | Implementation follows contract |
| R8-25 | Dependency matrix | NEW R8 DECISION | Phase 16A–E, R7, R7A, R7A-11 | APPROVED | Prevents dependency drift |
| R8-26 | Explicit non-changes | CONFIRMED INSTRUCTION | R7 closed and scope | APPROVED | Protects preceding slices |
| R8-27 | Approval and implementation gate | CONFIRMED INSTRUCTION | User architecture process | APPROVED | Implementation authorized |

---

## 9. Approved R8 Contract

### R8-2 — Authentication Authority

The frontend obtains authenticated state only through the approved Phase 16 authentication authority. It must not create a second provider, issue JWTs, or treat Zustand, localStorage, cached profiles, or frontend role maps as authoritative.

The client/session adapter must use `@supabase/supabase-js` and the provider-managed session lifecycle approved by Phase 16D. No custom authentication provider or parallel session authority is permitted.

### R8-3 — Session Representation

The session state must distinguish:

```text
LOADING / RESTORING
AUTHENTICATED
UNAUTHENTICATED
SESSION_EXPIRED
SESSION_INVALID
ACCOUNT_INACTIVE
AUTHENTICATED_BUT_FORBIDDEN
```

These are frontend state categories, not new identity database states.

### R8-4 — Session Restoration

On browser start or reload, the frontend must:

1. initialize the approved authentication client/session adapter;
2. restore the authoritative session;
3. resolve authenticated identity;
4. resolve canonical organisation context through the approved backend identity model;
5. consume backend-authoritative role/permission information for presentation;
6. expose authenticated state only after validation;
7. fail closed if validation fails.

Cached profile data alone must never establish authentication.

### R8-5 — Browser Storage

The browser storage mechanism is governed by the Supabase client/session architecture approved by Phase 16D. R8 does not add custom token storage, token serialization, or a parallel browser session authority.

The eventual implementation must explicitly document what may be held in localStorage, sessionStorage, cookies, and memory, and must not expose credentials through application state or logs.

### R8-6 — Access-Token Lifecycle

The frontend consumes access-token availability and refresh behavior from the approved authentication authority. It must not sign or verify JWTs locally, manufacture credentials, or continue attaching stale credentials after logout or invalidation.

Refresh success, refresh failure, concurrent refresh, invalid session, and restoration behavior are handled through the approved Supabase session adapter and exposed through the R8 state machine.

### R8-7 — API Client

Authenticated requests obtain credentials from the approved session authority and attach them only while an authenticated session exists. The client must never accept a user-supplied hospital or organisation identifier as tenant authority.

### R8-8 and R8-9 — 401 and 403

`401` means the authentication state is missing, expired, invalid, or requires approved refresh handling. The client must avoid redirect loops and infinite refresh loops.

`403` means the session may be valid but the requested operation is forbidden. The client must not refresh authentication solely because a `403` occurred.

### R8-10 — Logout

Logout must terminate the authoritative session according to Phase 16D, clear local authenticated state, invalidate protected queries/cache, and prevent protected-route access. Clearing Zustand state alone is insufficient.

### R8-11 — Route Guards

```text
LOADING / RESTORING
        → do not prematurely redirect
AUTHENTICATED
        → evaluate protected route
UNAUTHENTICATED
        → authentication entry point
AUTHENTICATED BUT FORBIDDEN
        → forbidden state
```

Frontend role maps are presentation aids, not final authorization.

### R8-12 and R8-13 — Roles and Organisation

The frontend may use approved role/permission information for navigation and presentation. Backend authorization remains authoritative.

The frontend consumes canonical organisation context and must not allow URL parameters, localStorage, sessionStorage, request bodies, query parameters, or Zustand state to override tenant authority.

The inherited one-active-hospital/organisation invariant is not redesigned as multi-tenant membership by R8.

### R8-14 — Cache Behavior

When authentication, identity, organisation, or account state changes, protected user/tenant-scoped queries and mutations must not remain accessible under the wrong session. Logout and session replacement require approved cache invalidation behavior.

### R8-15 and R8-16 — Concurrency and Expiry

The frontend must consume provider-consistent cross-tab session changes, logout, refresh, expiry, revocation, and account-state changes. Expired or revoked sessions fail closed.

### R8-17 — Account State

The frontend consumes account-active/inactive state from the approved identity authority. It must not create a second account-status authority in browser state.

### R8-18 — Invitation Handoff

After a user follows an R7 invitation link, the frontend presents the approved acceptance flow and submits acceptance to the backend-authoritative operation. It does not create invitations, persist raw tokens, or decide acceptance, membership, or role state.

### R8-19 through R8-23

Network, provider, backend, malformed-session, expired-session, and forbidden-operation failures must produce safe user-facing states without exposing credentials or sensitive backend errors. Observability must exclude access tokens, refresh tokens, invitation tokens, passwords, authorization headers, and sensitive identity data. Configuration must consume existing approved values and record missing dependencies rather than inventing new ones.

---

## 10. Security Invariants

The approved R8 contract preserves these invariants:

1. Browser state is never the source of truth for authentication.
2. Browser state is never the source of truth for tenant authority.
3. Frontend permissions never replace backend RBAC.
4. Frontend never creates JWTs.
5. Frontend never verifies authorization solely from client-controlled role state.
6. Logout terminates the authoritative session according to the approved auth architecture.
7. Expired and invalid sessions fail closed.
8. `401` and `403` remain semantically distinct.
9. Authenticated tenant data does not remain accessible after user/session transition.
10. Credentials and sensitive identity data are never logged.

---

## 11. Testing Contract

Focused tests must cover:

- initial session restoration;
- authenticated, unauthenticated, loading/restoring, expired, invalid, and inactive states;
- refresh success and failure;
- logout and authoritative session invalidation;
- 401 and 403 distinction;
- protected route guards and forbidden routes;
- tenant context consumption and browser tenant override rejection;
- role/permission presentation without treating it as security;
- protected cache clearing on logout/session replacement;
- multi-tab logout, refresh, expiry, and session replacement;
- invitation acceptance handoff;
- no fabricated credentials or local JWT authority;
- no credential/token logging.

Tests are implementation deliverables; no tests are created during this documentation reconciliation.

---

## 12. Explicit Non-Changes

This architecture pass does not:

- modify application code;
- modify migrations;
- modify database models;
- modify tests;
- modify Supabase configuration;
- modify R7;
- reopen R7A;
- reopen R7A-11;
- implement authentication;
- begin R9 or legacy Explainability Engine work.

---

## 13. Implementation Boundary

R8 architecture and R8 implementation remain separate. Implementation may begin only under this approved contract. Any implementation requirement not defined by the approved Phase 16 decisions or this R8 contract must be recorded as unresolved rather than inferred.

---

## 14. Approval Gate

```text
R8:
ARCHITECTURE STATUS: APPROVED
IMPLEMENTATION: AUTHORIZED
```

### Architectural Approval

```text
[x] APPROVED
[ ] REJECTED
[ ] APPROVED WITH AMENDMENTS
```

**Approved By:** ______________________________

**Date:** _____________________________________

**Amendments:**

```text
________________________________________________

________________________________________________

________________________________________________
```

---

## 15. Decision Record

```text
SLICE: R8
TITLE: Frontend Session Lifecycle
ARCHITECTURE STATUS: APPROVED
IMPLEMENTATION: AUTHORIZED
CANONICAL DOCUMENT: PHASE_16H_R8_ARCHITECTURE_DECISION.md

R7: CLOSED / COMPLETE
R7A: APPROVED / AUTHORIZED
R7A-11: APPROVED / AUTHORIZED

LEGACY PHASE 8 EXPLAINABILITY ENGINE:
SEPARATE ROADMAP / NOT R8 AUTHORITY

NEXT ACTION:
Implement the approved R8 Frontend Session Lifecycle contract.
```

---

**END OF R8 FRONTEND SESSION LIFECYCLE ARCHITECTURE DECISION**
