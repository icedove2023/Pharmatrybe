# 10D.3 — Frontend Tenant / Hospital Context

**Status:** Approved Specification
**Phase:** 10D — Frontend Identity + RBAC Integration
**Scope:** Frontend consumption and presentation of authoritative hospital/tenant identity
**Depends on:** 10D.1, 10D.2, 10C.3, 10C.4, 10C.5
**Security principle:** Frontend tenant context is a UX state, not a security boundary.

---

## 1. Purpose

This document defines how the frontend obtains, stores, restores, displays, and reacts to the authenticated user's hospital/tenant context.

The frontend must not independently determine the authenticated user's hospital.

The authoritative chain remains:

```text
Supabase Authentication
        ↓
/auth/me
        ↓
Backend identity resolution
        ↓
Professional profile
        ↓
Active hospital membership
        ↓
Hospital / tenant
        ↓
Frontend tenant context
```

The frontend consumes this context for presentation and UX decisions.

It must never become the authority for authorization.

---

# 2. Architectural Principle

The backend remains authoritative for tenant identity.

The frontend may maintain:

```text
currentHospital
currentMembership
```

for UI purposes, but these values are derived from the authenticated backend identity.

The frontend must **not** derive tenant identity from:

* URL parameters
* browser storage supplied by the user
* form fields
* query parameters
* arbitrary `hospital_id` values
* frontend role state
* locally configured organization identifiers

Therefore:

```text
Frontend
   ↓
/auth/me
   ↓
Authoritative tenant context
```

rather than:

```text
Frontend
   ↓
localStorage.hospital_id
   ↓
assume tenant
```

---

# 3. Authoritative Source

The primary source of frontend tenant identity is the authenticated backend identity endpoint:

```http
GET /auth/me
Authorization: Bearer <JWT>
```

The frontend should consume the hospital/tenant information returned by the backend identity contract.

Conceptually:

```json
{
  "user": {},
  "professional": {},
  "membership": {},
  "hospital": {},
  "roles": [],
  "permissions": []
}
```

The exact response shape must follow the existing backend `/auth/me` contract.

**This document does not introduce a new `/auth/me` schema.**

---

# 4. Tenant Context Model

The frontend identity state should conceptually contain:

```text
IdentityState
│
├── authenticated
│
├── user
│
├── professional
│
├── membership
│
├── hospital
│
├── roles
│
├── permissions
│
└── loading/error state
```

The tenant portion is therefore derived from the authenticated membership:

```text
Authenticated User
        ↓
Professional
        ↓
Active Membership
        ↓
Hospital
```

The frontend should not construct this relationship independently.

---

# 5. Single-Hospital Membership Rule

The existing identity architecture establishes that a professional belongs to one active hospital/organisation.

Therefore the frontend should model the authenticated tenant as a **single active hospital context**.

It should not introduce:

```text
hospitalSwitcher[]
```

or:

```text
selectedHospitalId
```

as an authorization mechanism.

The expected state is:

```text
authenticated professional
        ↓
one active membership
        ↓
one hospital
```

If the backend reports that the identity has no valid active membership, the frontend must not invent a tenant.

---

# 6. Tenant Context Initialization

After successful authentication:

```text
Login
 ↓
Supabase session established
 ↓
JWT available
 ↓
GET /auth/me
 ↓
Resolve identity
 ↓
Resolve active membership
 ↓
Resolve hospital
 ↓
Populate frontend identity state
 ↓
Render authenticated application
```

The frontend should not consider the user fully initialized merely because Supabase authentication succeeded.

Authentication establishes the session.

`/auth/me` establishes the application's authoritative identity and tenant context.

---

# 7. Session Restoration

When the application starts:

```text
Application startup
       ↓
Restore Supabase session
       ↓
Session exists?
    ┌──┴──┐
   NO     YES
   ↓       ↓
Login     GET /auth/me
screen      ↓
        identity resolved
             ↓
        tenant context
```

If a valid session exists but `/auth/me` cannot establish a valid application identity, the frontend must not continue using stale tenant information.

The identity state should transition to an appropriate unauthenticated, inactive, forbidden, or error state according to the backend response.

---

# 8. Tenant Context Must Not Be Client-Authoritative

The following pattern is prohibited:

```text
Browser
 ↓
hospital_id = request body
 ↓
API
 ↓
trust hospital_id
```

Likewise, the frontend must not attempt to enforce tenant isolation by simply attaching:

```json
{
  "hospital_id": "..."
}
```

to every request.

A client-supplied hospital identifier may be present where required by an API contract, but it must never be treated by the frontend or backend as proof of tenant membership.

The backend resolves and validates the tenant context.

---

# 9. Protected API Requests

Authenticated frontend requests should follow:

```text
Frontend API request
       ↓
Supabase access token
       ↓
Authorization: Bearer <JWT>
       ↓
Backend authentication
       ↓
Execution identity
       ↓
Tenant context
       ↓
RBAC
       ↓
Endpoint operation
```

The frontend's responsibility is to provide the authenticated session credential.

The backend's responsibility is to determine:

* who the user is;
* which professional identity applies;
* which hospital membership applies;
* which roles apply;
* which permissions apply;
* whether the requested operation is allowed.

---

# 10. Hospital Identity Display

The frontend may display hospital information obtained from `/auth/me`.

Examples include:

```text
Hospital name
Hospital logo
Hospital identifier
Organisation information
```

This is presentation data.

For example:

```text
┌──────────────────────────────────┐
│ Pharmatrybe                      │
│                                  │
│ Lagos University Hospital       │
│ Dr. Example User                 │
│ Clinician                        │
└──────────────────────────────────┘
```

The displayed hospital should come from authoritative identity state rather than a browser-selected tenant.

---

# 11. Hospital Identity in Navigation

The hospital context may be used to shape navigation.

For example:

```text
Hospital context
       ↓
role + permission state
       ↓
navigation capabilities
```

An administrator may see administrative navigation while a clinician may see clinical workflows.

However:

> Hiding a navigation item is not authorization.

A user must not gain access merely because the frontend displays a route.

---

# 12. Tenant Context and UI Capability

Tenant identity participates in frontend capability decisions.

Conceptually:

```text
/auth/me
    ↓
identity
    ↓
hospital
    ↓
roles
    ↓
permissions
    ↓
UI capabilities
```

For example:

```text
hospital context
+
professionals:manage
        ↓
display professional-management controls
```

But the corresponding backend endpoint must independently enforce:

```text
authenticated identity
+
tenant context
+
required permission
```

---

# 13. Route Protection

Frontend route protection may use tenant state to determine whether an authenticated application can be rendered.

Example:

```text
Protected route
      ↓
Authenticated?
   ┌──┴──┐
  NO     YES
  ↓       ↓
Login   Identity loaded?
             ↓
        Hospital context?
             ↓
          Render
```

If the application requires an active hospital membership, the absence of that membership must prevent normal tenant-scoped application access.

The frontend should present an appropriate state rather than fabricating a default hospital.

---

# 14. Invalid Tenant Context

The frontend must handle situations such as:

### No active membership

```text
Authenticated
    ↓
No active hospital membership
    ↓
Application access unavailable
```

### Invalid identity

```text
Session exists
    ↓
/auth/me fails identity resolution
    ↓
Do not use stale tenant state
```

### Forbidden resource

```text
Valid Hospital A context
        ↓
Request Hospital B resource
        ↓
Backend → 403
        ↓
Frontend → forbidden state
```

The frontend must not attempt to bypass the backend decision.

---

# 15. Tenant Context Refresh

Tenant context should be refreshed whenever the authenticated identity may have changed.

Relevant events include:

* login;
* session restoration;
* token refresh where application identity may change;
* logout;
* account deactivation;
* membership status changes;
* role changes;
* explicit identity refresh.

The frontend should be able to re-fetch:

```http
GET /auth/me
```

and replace its identity state with the latest authoritative result.

---

# 16. Identity Change

If the identity changes:

```text
User A
 ↓
logout
 ↓
User B login
```

the frontend must not retain:

```text
User A
Hospital A
roles A
permissions A
```

while rendering User B.

The required sequence is:

```text
Identity change
      ↓
Clear identity-derived state
      ↓
Clear tenant-scoped caches
      ↓
Establish new session
      ↓
GET /auth/me
      ↓
Populate new identity
      ↓
Populate new tenant context
      ↓
Render application
```

---

# 17. Cache Invalidation

Tenant-scoped frontend data must not survive an identity or tenant transition.

Examples include:

```text
clinical cases
patients
recommendations
laboratory results
plugin governance data
hospital professionals
hospital settings
```

When the identity changes:

```text
identity change
      ↓
invalidate tenant-scoped caches
      ↓
reload under new identity
```

This prevents stale Hospital A data from being presented after authentication as Hospital B.

---

# 18. Browser Storage

The frontend should avoid treating browser storage as an authoritative source for tenant identity.

Prohibited pattern:

```text
localStorage.hospital_id
        ↓
current tenant
```

If hospital information is cached for performance, it remains:

> derived cache data.

The authoritative source remains:

```text
/backend /auth/me
```

The cache must be invalidated when the identity changes.

---

# 19. API Error Handling

The frontend should distinguish tenant-related backend responses.

Conceptually:

| Backend condition         | Frontend behaviour                   |
| ------------------------- | ------------------------------------ |
| `401 Unauthorized`        | Session/authentication recovery      |
| `403 Forbidden`           | Forbidden UI                         |
| inactive account          | Inactive-account state               |
| missing active membership | Tenant/application unavailable state |
| tenant/resource mismatch  | Forbidden/resource unavailable state |
| network failure           | Retry/error state                    |

The frontend must not reinterpret a backend `403` as permission to retry using a different tenant identifier.

---

# 20. Tenant Context and RBAC

Tenant context and permissions are related but distinct.

```text
Identity
   ↓
Hospital membership
   ↓
Tenant context
   ↓
Roles
   ↓
Permissions
   ↓
UI capability
```

For example:

```text
Hospital A
   +
CLINICIAN
   +
cases:view
   ↓
Clinical case navigation/control visible
```

The frontend does not independently assign:

```text
CLINICIAN
```

or:

```text
cases:view
```

Those values originate from the backend authorization model.

---

# 21. No Frontend Tenant Switching

Because the current identity architecture establishes one active hospital membership per professional, the initial frontend implementation should not introduce multi-tenant switching.

Therefore no requirement is introduced for:

```text
Select hospital
Switch organisation
Change tenant
Impersonate hospital
```

Such functionality would require a separate architectural decision.

---

# 22. Security Boundary

The fundamental boundary is:

```text
                 TRUST BOUNDARY
                       │
                       ▼
Frontend ──────────── Backend
  │                      │
  │ UX decisions         │ Security decisions
  │                      │
  │ display hospital     │ resolve hospital
  │ hide controls        │ resolve membership
  │ route UX             │ enforce tenant
  │                      │ enforce RBAC
  │                      │ enforce resource policy
```

Therefore:

> Frontend tenant context is informative and operational for UX, but it is never authoritative for security.

---

# 23. Required Frontend State

The implementation should provide a single authoritative application identity state capable of representing:

```text
loading
authenticated
unauthenticated
inactive
forbidden
error
```

When authenticated:

```text
user
professional
membership
hospital
roles
permissions
```

should be available from the backend-derived identity contract.

The exact frontend state-management technology is intentionally not prescribed by this specification.

---

# 24. Acceptance Criteria

10D.3 is satisfied when:

### Identity

* [ ] Frontend obtains tenant context from the authenticated backend identity.
* [ ] Frontend does not independently determine the hospital.
* [ ] One active hospital context is represented for the current identity.
* [ ] Missing active membership is handled explicitly.

### API

* [ ] Protected requests carry the authenticated JWT.
* [ ] Frontend does not rely on `hospital_id` supplied by the browser for authorization.
* [ ] Backend `401` and `403` responses are handled appropriately.

### UI

* [ ] Hospital identity can be displayed from authoritative identity state.
* [ ] Tenant context can influence UX and navigation.
* [ ] Tenant context does not become a security mechanism.

### Session

* [ ] Tenant context is restored after session restoration.
* [ ] Tenant context refreshes after identity changes.
* [ ] Identity-derived state is cleared on logout.

### Cache

* [ ] Tenant-scoped caches are invalidated when identity changes.
* [ ] A previous user's hospital data cannot remain as the active frontend tenant context.

### Security

* [ ] No frontend-only tenant switching is introduced.
* [ ] No client-supplied hospital identifier is trusted as authorization.
* [ ] Backend authorization remains authoritative.

---

# 25. Validation Principle

Validation must prove that the frontend correctly **consumes** backend tenant identity rather than creating a parallel tenant-security model.

The central test is:

```text
Backend identity
      ↓
Hospital A
      ↓
Frontend tenant context
```

and not:

```text
Browser
      ↓
hospital_id = Hospital A
      ↓
Frontend assumes Hospital A
```

A successful implementation therefore demonstrates:

```text
Supabase Session
       ↓
/auth/me
       ↓
Professional
       ↓
Active Membership
       ↓
Hospital
       ↓
Frontend Tenant Context
       ↓
UI / navigation / presentation
```

while all actual tenant authorization remains:

```text
Backend
   ↓
TenantContext
   ↓
RBAC
   ↓
Resource authorization
```

---

## 26. Non-Goals

This document does **not** introduce:

* a new backend tenant model;
* a new RBAC model;
* frontend authorization as a security boundary;
* multi-hospital membership;
* tenant switching;
* client-controlled tenant authorization;
* a replacement for `/auth/me`;
* a second source of truth for hospital membership.

It defines only the frontend integration boundary for the tenant identity already established by the backend architecture.
