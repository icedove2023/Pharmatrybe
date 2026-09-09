
# PharmaTrybe — Phase 6F Implementation Authorization Prompt

## STATUS: ARCHITECTURAL DECISIONS APPROVED

You are now authorized to begin implementation of **Phase 6F — Authentication, Identity, Tenant, RBAC and Supabase Integration** for the PharmaTrybe platform.

Before writing code, you MUST read and understand all relevant documentation under:

```text
docs/integration/
docs/architecture/
````

You must also cross-reference the existing implementation in:

```text
apps/api/
src/
packages/
```

The integration documentation and approved architectural decisions below are the implementation baseline.

---

# 1. CRITICAL INSTRUCTION — DO NOT REINTERPRET APPROVED DECISIONS

The following architectural decisions have now been explicitly approved.

> **THESE DECISIONS ARE APPROVED AND MUST NOT BE REINTERPRETED, OVERRIDDEN, REPLACED, OR "IMPROVED" BY YOU.**

You must implement against them exactly as specified.

Do NOT:

* propose an alternative architecture;
* reopen an already-approved decision;
* substitute another authentication provider;
* introduce a different tenant model;
* invent a different RBAC model;
* introduce multi-organisation membership;
* move authorization into plugins;
* make the frontend authoritative for permissions;
* replace FastAPI authorization with Supabase-only authorization;
* introduce an alternative session architecture;
* silently modify the approved database ownership model;
* silently change the approved RLS strategy;
* invent missing architectural decisions.

If implementation details are genuinely undefined, STOP at that specific decision point and report:

```text
IMPLEMENTATION DETAIL NOT DEFINED BY APPROVED ARCHITECTURE
```

Do not silently invent a security-sensitive decision.

---

# 2. APPROVED ARCHITECTURAL BASELINE

## 2.1 Authentication Provider

### APPROVED

```text
Supabase Auth
```

Supabase Auth is the platform's identity and authentication/session authority.

Supabase is responsible for authentication lifecycle functionality including:

* account creation;
* login;
* logout;
* email verification;
* password recovery;
* session management;
* access tokens;
* refresh tokens;
* authentication state.

Do not introduce another identity provider.

---

# 3. Application Authorization Authority

### APPROVED

```text
FastAPI
```

Supabase authenticates the identity.

FastAPI determines whether the authenticated identity is authorized to perform an operation.

The architectural boundary is:

```text
Supabase Auth
      │
      │ authenticated identity/session
      ▼
Frontend
      │
      │ Bearer access token
      ▼
FastAPI
      │
      ├── JWT verification
      ├── professional identity resolution
      ├── hospital membership resolution
      ├── role resolution
      ├── permission resolution
      ├── tenant authorization
      └── route authorization
      │
      ▼
PharmaTrybe Platform
```

A valid Supabase session does NOT automatically grant PharmaTrybe authorization.

---

# 4. Identity Authority

### APPROVED

The canonical authenticated identity is:

```text
Supabase auth.users.id
```

The application identity is resolved from that identity.

The intended relationship is:

```text
auth.users
    │
    ▼
professional_profiles
    │
    ▼
hospital_memberships
    │
    ▼
hospital
    │
    ▼
roles
    │
    ▼
permissions
```

Do not replace this identity model with a separate application authentication system.

---

# 5. Tenant Model

### APPROVED

A:

```text
Hospital / Organisation
```

is a PharmaTrybe tenant.

For the first implementation:

> **One professional may have only ONE active hospital membership at a time.**

This is an approved architectural decision.

Do NOT implement:

```text
professional → many active hospitals
```

for Phase 6F.

Historical memberships may remain for:

* audit;
* history;
* organisational transfer;
* governance.

But only one membership may be active at a time.

The database must enforce this invariant.

---

# 6. Organisation Context Model

### APPROVED

Use the approved **Hybrid identity/organisation context model**.

The JWT establishes authenticated identity.

The database establishes the authoritative current organisation membership.

Conceptually:

```text
JWT
 │
 └── user_id / sub
          │
          ▼
professional_profiles
          │
          ▼
active hospital_membership
          │
          ▼
hospital / tenant
```

Do NOT assume that an organisation identifier supplied by the frontend is authoritative.

Do NOT trust arbitrary client-supplied:

```text
hospital_id
organisation_id
tenant_id
```

for authorization.

The backend must resolve and validate the active membership.

---

# 7. RBAC

### APPROVED

The **Phase 16C Role & Permission Matrix is the canonical authorization model.**

Treat the approved 16C role taxonomy and permission catalogue as authoritative.

Do not invent another role system.

Do not create arbitrary permissions.

Do not use frontend role labels as the backend authorization authority.

The backend must enforce permissions.

The frontend may use roles/permissions for:

* UI visibility;
* navigation;
* presentation;
* user experience.

But frontend checks are NOT security boundaries.

The security boundary is:

```text
FastAPI authorization
```

---

# 8. Authorization Model

The backend authorization chain must follow:

```text
Authenticated User
       ↓
Professional Profile
       ↓
Active Hospital Membership
       ↓
Role(s)
       ↓
Permissions
       ↓
Tenant Scope
       ↓
Requested Resource
       ↓
Authorization Decision
```

Failure at any required stage must fail closed.

Examples:

```text
No JWT
      → 401

Invalid JWT
      → 401

Authenticated but no professional profile
      → deny

No active hospital membership
      → deny

Inactive membership
      → deny

Insufficient permission
      → 403

Cross-hospital resource access
      → deny
```

Do not weaken these boundaries.

---

# 9. JWT Verification

### APPROVED ARCHITECTURAL DIRECTION

FastAPI must verify Supabase-issued JWTs.

Verification must cover the approved JWT security requirements, including:

* signature;
* issuer;
* audience;
* expiration;
* subject;
* required authentication claims;
* signing-key validation.

Use the Supabase signing-key/JWKS mechanism required by the approved Supabase configuration.

IMPORTANT:

If the repository does not yet contain the final concrete values for:

```text
SUPABASE_URL
JWT issuer
JWT audience
JWKS configuration
```

do NOT invent production values.

Use configuration/environment variables and document the required values.

Never hardcode secrets.

Never use:

```text
change-me
```

as a production authentication secret.

---

# 10. Frontend Authentication

### APPROVED

The frontend will use:

```text
@supabase/supabase-js
```

for Supabase authentication/session management.

The frontend must:

* initialize the Supabase client;
* authenticate users through Supabase;
* restore sessions;
* observe authentication state changes;
* obtain the current access token;
* attach the token to FastAPI requests;
* handle logout;
* handle expired sessions;
* handle `401`;
* handle `403`.

The API client must send:

```http
Authorization: Bearer <access_token>
```

when an authenticated session exists.

Do not create a second independent authentication/session system.

---

# 11. Frontend Framework Decision

### APPROVED IMPLEMENTATION BASELINE

The active frontend implementation is:

```text
Vite + React
```

If an older architecture document references Next.js, treat that as a documentation/version discrepancy.

DO NOT migrate the frontend to Next.js as part of Phase 6F.

Do not introduce a framework migration into this phase.

---

# 12. RLS

### APPROVED

PostgreSQL/Supabase Row Level Security is:

```text
DEFENCE-IN-DEPTH
```

It does not replace FastAPI authorization.

The security model is therefore:

```text
                 FastAPI
                   │
          Primary authorization
                   │
                   ▼
             Application
                   │
                   ▼
              PostgreSQL
                   │
                   ▼
                  RLS
          Defence-in-depth
```

FastAPI remains responsible for:

* authentication;
* authorization;
* RBAC;
* tenant resolution;
* application-level ownership checks.

RLS provides an additional database-level security boundary.

Do not remove FastAPI authorization because RLS exists.

Do not make the frontend responsible for tenant security.

---

# 13. Platform-Core Security Boundary

The following remain PLATFORM CORE responsibilities:

```text
Authentication
Authorization
Plugin Manager
Decision Fusion Engine
Explainability Engine
Clinical Rules Engine
Clinical Response Engine
Audit Engine
API Gateway
UI
```

This is consistent with the Plugin Framework.

Plugins are capability providers.

Plugins do NOT own:

* authentication;
* authorization;
* tenant authorization;
* RBAC;
* audit security;
* platform security policy.

---

# 14. Plugin Security

Plugins must remain inside the established platform boundary.

The approved architecture is:

```text
Frontend
   ↓
FastAPI
   ↓
Platform Core
   ↓
Plugin Manager
   ↓
Selected Plugin
```

Plugins must not:

```text
authenticate users
authorize users
bypass FastAPI
communicate directly with unrelated plugins
modify platform audit logs
modify platform security policy
access unrelated tenant data
```

Authentication and authorization context must be established by the platform before protected plugin execution.

Do not move RBAC logic into SOAR, ARMD, WHO, or other plugins.

---

# 15. FastAPI Orchestration Boundary

The official orchestration architecture states:

> All clinical requests pass through the FastAPI Backend.

Therefore:

```text
Frontend
    ↓
FastAPI
    ↓
Authentication
    ↓
Authorization
    ↓
Tenant resolution
    ↓
Validation
    ↓
Audit context
    ↓
Workflow / Plugin Manager
    ↓
Clinical services
    ↓
Decision Engine
    ↓
Explainability
    ↓
FastAPI
    ↓
Frontend
```

No service may bypass the FastAPI orchestration boundary.

This includes:

* SOAR;
* ARMD;
* WHO;
* Decision Engine;
* Explainability Engine;
* future plugins.

---

# 16. Audit

Audit remains a platform-core responsibility.

Every authenticated clinical request must be capable of being associated with:

```text
request_id
timestamp
authenticated user
hospital / tenant
executed services
model versions
knowledge version
recommendation version
explanation version
```

Do not allow plugins to independently modify the authoritative audit trail.

Audit must remain consistent with the official Data Flow and Orchestration architecture.

---

# 17. Clinical Safety

The authentication implementation must preserve PharmaTrybe's fundamental safety principles.

The system is:

```text
Clinical Decision SUPPORT
```

not:

```text
Autonomous prescribing
```

Security implementation must never introduce a path that allows:

* unauthenticated clinical recommendations;
* unauthorized clinical access;
* cross-hospital clinical data access;
* bypassing explainability;
* bypassing audit;
* bypassing the Decision Engine.

---

# 18. Approved Implementation Sequence

Implement Phase 6F incrementally in the following order.

## 16F-0 — Architectural Baseline Verification

Before modifying code:

1. Read all relevant `docs/integration/*.md`.
2. Read the relevant architecture documents.
3. Inspect the existing authentication scaffolding.
4. Inspect frontend authentication code.
5. Inspect database models/schema.
6. Inspect route protection.
7. Inspect audit implementation.
8. Produce a concise implementation gap report.

Do not modify code during this verification step.

---

# 19. 16F-1 — Supabase Configuration Contract

Establish the configuration contract.

Required configuration should be environment-based.

Examples:

```text
SUPABASE_URL
SUPABASE_ANON_KEY
SUPABASE_JWT_ISSUER
SUPABASE_JWT_AUDIENCE
```

Use the exact configuration names already defined by the project documentation where available.

Do not invent conflicting names.

Do not hardcode secrets.

Document any configuration values that must be supplied externally.

---

# 20. 16F-2 — Identity + Tenant Database Schema

Implement the approved identity/tenant schema from Phase 16B.

This includes the documented entities such as:

```text
hospitals
professional_profiles
hospital_memberships
roles
membership_roles
hospital_invitations
membership_events
```

Implement the approved relationships.

Implement the database invariant:

```text
one professional
      ↓
maximum one active hospital membership
```

Use a database-level constraint/index to enforce this.

Do NOT add RLS policies in this slice unless the approved RLS implementation has already been defined.

---

# 21. 16F-3 — Backend Authentication Context

Implement the approved FastAPI authentication architecture.

The backend should establish an authorization context equivalent to:

```text
AuthorizationContext
```

containing the information required by downstream authorization.

Conceptually:

```text
user
professional
hospital
membership
roles
permissions
```

Implement:

```text
get_current_user
get_authorization_context
require_permission
require_same_hospital
```

or the exact documented equivalent.

Replace the current unused JWT scaffold rather than creating a parallel authentication system.

---

# 22. 16F-4 — RBAC + Tenant Enforcement

Wire the approved authorization dependencies onto protected routes.

At minimum inspect:

```text
clinical cases
recommendations
administrative routes
professional routes
hospital onboarding
invitation routes
membership routes
plugin execution routes
```

Do not assume a route is safe merely because it exists behind the frontend.

The backend must enforce authorization.

---

# 23. 16F-5 — Frontend Supabase Session Integration

Integrate the approved Supabase client into the existing Vite + React frontend.

Use:

```text
@supabase/supabase-js
```

Integrate with the existing:

```text
authStore
LoginForm
HospitalRegistrationForm
API client
route guards
```

Do not create duplicate state-management systems unless existing architecture requires it.

Replace placeholder authentication failures such as:

```text
Authentication backend integration pending
```

with the approved implementation.

---

# 24. 16F-6 — Hospital Onboarding + Invitations

Implement the approved onboarding architecture.

This includes the documented hospital registration and invitation workflows.

The registration operation must maintain transactional integrity.

Conceptually:

```text
Create hospital
      ↓
Create professional profile
      ↓
Create admin membership
      ↓
Assign approved role
      ↓
Create audit event
```

Invitation flow:

```text
Admin
  ↓
Invite professional
  ↓
Invitation
  ↓
Authentication
  ↓
Profile
  ↓
Membership activation
```

Do not bypass the one-active-membership invariant.

---

# 25. 16F-7 — RLS Defence-in-Depth

Implement RLS only according to the approved RLS architecture.

RLS must reinforce, not replace:

```text
FastAPI authentication
FastAPI authorization
RBAC
tenant resolution
application ownership checks
```

Every tenant-owned table must be evaluated for the appropriate hospital boundary.

Shared/global knowledge tables such as WHO knowledge must not accidentally become hospital-scoped.

---

# 26. 16F-8 — Audit Integration

Integrate authenticated identity and tenant context into the audit architecture.

Audit events must be attributable to the authenticated professional and hospital where applicable.

Preserve:

```text
request_id
user identity
hospital/tenant
executed services
versions
recommendation
explanation
```

Do not let authentication implementation break the existing audit architecture.

---

# 27. 16F-9 — Security Validation

Before declaring Phase 6F complete, test at minimum:

### Authentication

* valid login;
* invalid credentials;
* expired token;
* invalid token;
* missing token;
* logout;
* session restoration.

### Authorization

* permitted action;
* denied action;
* missing permission;
* inactive account;
* inactive membership;
* invalid role.

### Tenant isolation

```text
Hospital A user
    X
Hospital B data
```

Cross-hospital access must fail.

### Database

* active-membership uniqueness;
* foreign keys;
* tenant ownership;
* RLS policies.

### API

* protected route without token → 401;
* authenticated but unauthorized → 403;
* cross-tenant resource → denied.

### Plugin security

Verify that a plugin cannot bypass:

* authentication;
* authorization;
* tenant isolation;
* audit.

---

# 28. No Silent Architectural Changes

If you encounter existing code that contradicts the approved architecture:

DO NOT silently rewrite the architecture.

Instead classify the finding:

```text
DOCUMENTATION-CODE CONFLICT
```

Then implement the approved architecture unless doing so would require an unresolved security decision.

If an unresolved decision blocks safe implementation:

```text
IMPLEMENTATION BLOCKED
```

and explain exactly what decision is missing.

---

# 29. No Overengineering

Do not introduce:

* unnecessary microservices;
* a second authentication provider;
* unnecessary abstractions;
* unnecessary dependencies;
* speculative multi-tenant architecture;
* speculative multi-organisation membership;
* unnecessary OAuth providers;
* custom identity infrastructure;
* custom JWT issuance;
* duplicate permission systems.

Follow the existing PharmaTrybe architecture.

Build incrementally.

Validate each slice before moving to the next.

---

# 30. Required Development Discipline

For every implementation slice:

```text
READ
 ↓
PLAN
 ↓
IMPLEMENT
 ↓
TEST
 ↓
VALIDATE
 ↓
DOCUMENT
 ↓
NEXT SLICE
```

Do not implement the entire phase blindly in one operation.

After each slice, report:

```text
Implemented
Files changed
Tests added/updated
Tests passed
Architectural requirements satisfied
Known limitations
Next slice
```

---

# 31. Definition of Done

Phase 6F is complete only when:

* Supabase Auth is integrated;
* frontend session management is functional;
* FastAPI verifies Supabase JWTs;
* professional identity is resolved;
* active hospital membership is resolved;
* RBAC is enforced server-side;
* tenant isolation is enforced;
* clinical routes are protected;
* onboarding is implemented;
* invitation flow is implemented;
* database constraints are implemented;
* RLS defence-in-depth is implemented;
* authenticated audit context is implemented;
* plugin execution remains inside the platform security boundary;
* cross-tenant access tests pass;
* authentication tests pass;
* authorization tests pass;
* the frontend/backend authentication contract is validated;
* documentation reflects the final implementation.

---

# 32. FINAL NON-NEGOTIABLE RULE

Repeat this internally before every architectural decision:

> **THE APPROVED ARCHITECTURAL DECISIONS ABOVE ARE AUTHORITATIVE. THEY MUST NOT BE REINTERPRETED.**

You are implementing the architecture.

You are NOT redesigning it.

If you believe an approved decision should change, do not change it yourself.

Report:

```text
PROPOSED ARCHITECTURAL CHANGE
```

with:

1. Current approved decision
2. Reason for proposed change
3. Impact
4. Security implications
5. Migration implications
6. Recommendation

Then wait for explicit approval.

---

# START CONDITION

Before writing any implementation code, confirm:

```text
✓ All docs/integration Markdown files reviewed
✓ Relevant architecture documents reviewed
✓ Existing authentication implementation inspected
✓ Existing frontend authentication inspected
✓ Existing database schema inspected
✓ Existing API routes inspected
✓ Existing audit architecture inspected
✓ Approved architectural decisions understood
✓ No approved decision will be reinterpreted
```

Then begin:

```text
16F-0 — Architectural Baseline Verification
```

Do not skip the verification step.

# END OF IMPLEMENTATION AUTHORIZATION

```

### One important point

I deliberately made the prompt distinguish between **architectural decisions** and **implementation details**. That prevents Copilot from taking something like the approved hybrid tenant model and "optimizing" it into JWT-only tenant claims, while still allowing it to choose ordinary implementation details where the architecture has already established the boundary.

This also preserves the official orchestration rule that clinical requests pass through FastAPI and that plugins cannot bypass the platform core. :contentReference[oaicite:0]{index=0} The Plugin Framework likewise explicitly keeps authentication, authorization, audit, and API responsibilities in the platform core. :contentReference[oaicite:1]{index=1}

**I would use this as the master Phase 6F implementation prompt.**
```
