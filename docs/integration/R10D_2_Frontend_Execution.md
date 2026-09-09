# 10D.2 — Frontend Execution Identity Session State
status: approved 
## 1. Purpose

This document defines how the frontend maintains and derives **execution identity session state** after authentication.

The purpose of this layer is to allow the frontend to understand **who is currently operating the application and what capabilities the backend has granted to that identity**, without becoming an authorization authority.

The frontend execution identity is therefore a **consumed representation of backend identity**, not an independently created identity model.

The authoritative chain is:

```text
Supabase Authentication Session
        ↓
Authenticated User
        ↓
GET /auth/me
        ↓
Backend Authorization Context
        ↓
Frontend Execution Identity State
        ↓
UI Capability Decisions
```

The frontend must never construct authoritative identity, hospital, role, or permission information from browser-controlled values.

---

# 2. Architectural Principle

The frontend must not independently determine the authenticated professional's execution identity.

The backend remains authoritative for:

* authenticated user identity;
* professional identity;
* hospital membership;
* active membership;
* tenant/hospital context;
* assigned roles;
* effective permissions.

The frontend consumes this information through the authenticated backend identity endpoint.

Therefore:

> **Frontend execution identity is a cached client representation of backend-derived identity and authorization context.**

It is not a second authorization system.

---

# 3. Relationship to 10D.1

10D.1 establishes the frontend authentication boundary.

10D.2 builds the execution identity state that exists **after authentication has been established**.

The distinction is:

```text
10D.1
Authentication Boundary
        ↓
"Is this user authenticated?"

10D.2
Execution Identity Session State
        ↓
"Who does the backend say this authenticated user is?"
```

The frontend must not treat successful Supabase authentication alone as sufficient to determine application identity.

A valid authentication session must be resolved against the backend application identity.

---

# 4. Authoritative Identity Source

The authoritative application identity is obtained from:

```http
GET /auth/me
```

with the authenticated Supabase access token:

```http
Authorization: Bearer <access_token>
```

The frontend must treat the `/auth/me` response as the authoritative source for application execution identity.

Conceptually:

```text
Supabase Session
        │
        │ access token
        ▼
GET /auth/me
        │
        ▼
Backend Authorization Context
        │
        ├── authenticated user
        ├── professional
        ├── active membership
        ├── hospital
        ├── roles
        └── permissions
```

The frontend must not replace this resolution with locally stored role or hospital information.

---

# 5. Frontend Execution Identity Model

The frontend should maintain a session-level execution identity state representing the backend response.

Conceptually:

```text
ExecutionIdentity
│
├── authentication
│   ├── authenticated
│   └── authUserId
│
├── professional
│   ├── professionalId
│   └── profile information
│
├── membership
│   ├── membershipId
│   └── membership status
│
├── tenant
│   ├── hospitalId
│   └── hospital information
│
├── roles
│   └── canonical role codes
│
└── permissions
    └── canonical permission codes
```

The exact field names must follow the existing backend `/auth/me` contract.

This document does **not** introduce a new backend identity schema.

---

# 6. Identity State Lifecycle

The frontend execution identity follows a controlled lifecycle:

```text
UNKNOWN
   │
   ▼
AUTHENTICATING
   │
   ▼
AUTHENTICATED
   │
   ▼
IDENTITY_LOADING
   │
   ▼
IDENTITY_RESOLVED
```

Failure states must also be represented:

```text
IDENTITY_RESOLUTION_FAILED
        │
        ├── unauthenticated
        ├── inactive account
        ├── missing professional identity
        ├── missing active membership
        └── backend error
```

The frontend must not assume that an authenticated Supabase session automatically means that a usable application identity exists.

---

# 7. Session Restoration

When the application starts, the frontend must restore the Supabase authentication session.

The flow is:

```text
Application Start
      ↓
Restore Supabase Session
      ↓
No Session?
      ├── YES → Unauthenticated State
      │
      └── NO
           ↓
      Obtain Access Token
           ↓
      GET /auth/me
           ↓
      Resolve Execution Identity
```

Until `/auth/me` has resolved successfully, protected application areas should not assume that the user's roles or permissions are known.

---

# 8. Session Refresh

Supabase session refresh must update the authentication session without creating a separate frontend identity.

The flow is:

```text
Supabase Token Refresh
        ↓
Updated Access Token
        ↓
GET /auth/me
        ↓
Updated Execution Identity
```

The frontend must therefore regard authentication-token changes as potential identity-state refresh boundaries.

The frontend must not retain stale authorization information indefinitely after a session change.

---

# 9. Identity Reconciliation

Whenever the frontend obtains a new authenticated session, it should reconcile the session with `/auth/me`.

Conceptually:

```text
New Supabase Session
        ↓
Extract access token
        ↓
GET /auth/me
        ↓
Compare with current execution identity
        ↓
Replace execution identity
```

The frontend should replace the previous execution identity rather than attempting to merge potentially stale roles, permissions, or tenant information.

---

# 10. Hospital / Tenant Identity

The frontend may display the hospital associated with the current execution identity.

For example:

```text
Current Hospital
     ↓
Hospital A
```

However, the frontend must treat this as **display/context information**, not as an authorization mechanism.

The frontend must not establish tenant authority through:

```text
localStorage.hospital_id
```

or:

```text
URL hospital_id
```

or:

```text
request body hospital_id
```

or any other browser-controlled value.

The backend remains responsible for deriving and enforcing tenant context.

---

# 11. Roles

The frontend may consume the canonical roles returned by `/auth/me`.

For example:

```text
HOSPITAL_ADMIN
CLINICIAN
PHARMACIST
INFECTIOUS_DISEASE_SPECIALIST
LABORATORY_SCIENTIST
RESEARCHER
```

These values may be used for UI decisions such as:

```text
HOSPITAL_ADMIN
    ↓
Display administration navigation
```

However:

> A frontend role check must never be treated as proof that an operation is authorized.

The backend must independently resolve the user's roles and permissions.

---

# 12. Permissions

The frontend may consume backend-derived permission codes.

Examples include:

```text
professionals:view
professionals:invite
professionals:manage

cases:create
cases:view
cases:update

patients:view
patients:create

recommendations:view
recommendations:request
recommendations:review

plugins:view
plugins:configure

roles:assign
audit:view
```

These permissions may drive UI capabilities:

```text
permission
    ↓
UI capability
    ↓
show / hide / disable
```

They must never be used as a substitute for backend permission enforcement.

---

# 13. UI Capability Derivation

The frontend should derive capabilities from the backend-provided identity state.

Conceptually:

```text
Execution Identity
        ↓
Roles + Permissions
        ↓
Capability Resolver
        ↓
UI Capability
```

Examples:

```text
professionals:invite
        ↓
Show "Invite Professional"

plugins:configure
        ↓
Show plugin configuration controls

recommendations:review
        ↓
Show recommendation review controls
```

The capability resolver should operate only on the currently resolved execution identity.

---

# 14. No Client-Side Role Mutation

The frontend must not allow arbitrary application code to mutate:

```text
roles
permissions
hospitalId
membershipId
professionalId
```

through normal UI state operations.

Role changes must occur through the backend governance/identity mechanisms.

After such changes, the frontend should obtain refreshed identity information from the backend.

---

# 15. Identity Change

An identity change occurs when the authenticated execution context changes.

Examples include:

* logout;
* login as another user;
* session expiration;
* session refresh resulting in a different authenticated identity;
* account becoming inactive;
* backend membership becoming unavailable;
* role/permission changes;
* hospital membership changes.

When identity changes, the frontend must invalidate identity-dependent state.

The flow is:

```text
Identity Change
      ↓
Invalidate Execution Identity
      ↓
Invalidate Identity-Dependent Cache
      ↓
Clear Protected UI State
      ↓
Resolve New /auth/me
      ↓
Rebuild UI Capabilities
```

---

# 16. Cache Invalidation

Identity-dependent cached data must not survive an identity transition.

At minimum, identity changes should invalidate cached:

* user profile information;
* hospital information;
* role information;
* permission information;
* navigation capability state;
* protected API results;
* tenant-scoped resources.

Conceptually:

```text
Old Identity
    ↓
Cache A
Cache B
Cache C

Identity changes
    ↓
Invalidate A
Invalidate B
Invalidate C
```

This prevents one user's frontend state from being accidentally reused for another authenticated identity.

---

# 17. Logout

Logout must clear the frontend execution identity.

The sequence is:

```text
User Logout
     ↓
Clear/terminate Supabase session
     ↓
Clear Execution Identity
     ↓
Clear identity-dependent cache
     ↓
Clear protected application state
     ↓
Unauthenticated UI
```

After logout:

```text
roles = []
permissions = []
hospital = null
professional = null
membership = null
```

The exact implementation should follow the application's state-management conventions.

---

# 18. Inactive Account

An authenticated Supabase session does not guarantee that the user remains an active application user.

If `/auth/me` indicates that the backend identity is inactive or otherwise unavailable for application use:

```text
Supabase Session
        ↓
GET /auth/me
        ↓
Inactive Account
        ↓
Reject Application Identity
```

The frontend should transition to an appropriate inactive-account state.

It must not manufacture a usable execution identity from the Supabase session alone.

---

# 19. Forbidden State

A user may be authenticated but lack permission for a specific operation.

Therefore:

```text
Authenticated
     ≠
Authorized for every operation
```

The frontend may use permissions to prevent unnecessary interaction, but backend `403 Forbidden` responses remain authoritative.

Example:

```text
User
 ↓
Authenticated
 ↓
No plugins:configure
 ↓
Frontend hides configuration control
```

If the user nevertheless calls the API:

```text
API
 ↓
Backend authorization
 ↓
403 Forbidden
```

The frontend must handle the forbidden response explicitly.

---

# 20. Protected API Requests

Protected frontend API requests must use the current authenticated access token.

Conceptually:

```text
Execution Identity
       │
       └── Supabase access token
                    ↓
             Protected API
                    ↓
             Backend Auth
                    ↓
             Tenant Context
                    ↓
                  RBAC
```

The frontend must not send identity assertions such as:

```json
{
  "user_id": "...",
  "hospital_id": "...",
  "role": "HOSPITAL_ADMIN"
}
```

as a substitute for backend authentication and authorization.

Where such fields exist for legitimate domain purposes, they must not be treated by the backend as authoritative identity information.

---

# 21. Tenant Isolation in Frontend State

The frontend may know the current hospital for display and navigation purposes.

It must not use client state to enforce tenant isolation.

Incorrect:

```text
currentHospitalId
       ↓
filter API results
       ↓
assume tenant security
```

Correct:

```text
current authenticated identity
       ↓
backend /auth/me
       ↓
backend TenantContext
       ↓
RLS / authorization
       ↓
tenant-scoped result
       ↓
frontend display
```

Frontend filtering is therefore a presentation optimization, not a security boundary.

---

# 22. Loading-State Requirements

Protected UI must distinguish between:

```text
Authentication Loading
```

and:

```text
Execution Identity Loading
```

For example:

```text
Auth session restored
        ↓
Identity still loading
        ↓
Do not render authorization-sensitive controls yet
```

This prevents temporary incorrect UI states where controls appear before permissions have been resolved.

---

# 23. Identity Context API

The frontend should expose a single application-level identity context/service to consumers.

Conceptually:

```text
useExecutionIdentity()
```

or the equivalent mechanism used by the existing frontend architecture.

Consumers should obtain:

```text
authenticated
identity
hospital
roles
permissions
status
loading
error
```

from this centralized state.

Components should not independently call `/auth/me` and maintain competing identity states.

---

# 24. Capability Helpers

The frontend may provide helpers such as:

```text
hasRole(role)
hasPermission(permission)
can(capability)
```

Their purpose is strictly UI decision-making.

For example:

```text
hasPermission("plugins:configure")
        ↓
true
        ↓
display Configure button
```

The helper must not imply:

```text
hasPermission(...)
        ↓
API operation is guaranteed to succeed
```

The backend remains authoritative.

---

# 25. Security Boundary

The complete boundary is:

```text
                 FRONTEND
┌───────────────────────────────────┐
│ Supabase Session                  │
│        ↓                          │
│ /auth/me                          │
│        ↓                          │
│ Execution Identity State          │
│        ↓                          │
│ Roles + Permissions               │
│        ↓                          │
│ UI Capabilities                   │
└───────────────────────────────────┘
                 │
                 │ API + JWT
                 ▼
                 BACKEND
┌───────────────────────────────────┐
│ Authentication                    │
│        ↓                          │
│ Execution Identity                │
│        ↓                          │
│ TenantContext                     │
│        ↓                          │
│ RBAC                              │
│        ↓                          │
│ Resource / policy enforcement     │
└───────────────────────────────────┘
```

The frontend therefore **consumes authorization state but does not enforce security**.

---

# 26. Prohibited Patterns

The implementation must not introduce:

### Browser-authoritative roles

```text
localStorage.role
       ↓
authorization
```

### Browser-authoritative permissions

```text
localStorage.permissions
       ↓
API authorization
```

### Browser-authoritative tenant

```text
selectedHospitalId
       ↓
assume tenant authority
```

### Client-side identity fabrication

```text
Supabase user
       ↓
construct hospital membership locally
```

### Frontend-only protection

```text
hide button
       ↓
assume endpoint is secure
```

All of these violate the 10D architecture.

---

# 27. Validation Requirements

Implementation of 10D.2 must demonstrate:

### Identity resolution

* Supabase session can be restored.
* `/auth/me` is called for an authenticated session.
* Execution identity is populated from the backend response.
* Missing/invalid identity is represented as an error state.

### Session lifecycle

* Login resolves execution identity.
* Logout clears execution identity.
* Session refresh updates authentication state.
* Identity changes invalidate previous identity state.

### Tenant context

* Hospital identity comes from backend identity data.
* Frontend does not establish tenant authority from browser-controlled values.

### RBAC

* Roles come from backend identity data.
* Permissions come from backend identity data.
* Capability helpers operate on current identity state.

### Security

* UI checks are not relied upon for API security.
* `401` responses transition appropriately toward authentication recovery.
* `403` responses produce an appropriate forbidden state.
* Identity-dependent caches are invalidated when identity changes.

---

# 28. Architectural Decision

**Confirmed Design Decision — Frontend Execution Identity**

The frontend will maintain a centralized execution identity state derived from:

```text
Supabase Session
       ↓
/auth/me
       ↓
Backend-derived identity
```

The state may contain:

```text
authenticated user
professional
membership
hospital
roles
permissions
```

but these values are **consumed authorization context**, not client-authoritative security state.

---

# 29. Final 10D.2 Contract

The implementation must preserve the following invariant:

> **The frontend never decides who the user is, which hospital they belong to, or what they are authorized to do. The frontend consumes the backend's authoritative execution identity and uses it only to determine the appropriate user experience.**

Therefore:

```text
Supabase Session
       ↓
/auth/me
       ↓
Authoritative Backend Identity
       ↓
Frontend Execution Identity
       ↓
Roles + Permissions
       ↓
UI Capabilities
```

while security remains:

```text
JWT
 ↓
Backend Authentication
 ↓
Execution Identity
 ↓
TenantContext
 ↓
RBAC
 ↓
Resource / Policy Enforcement
```

This completes the architectural specification for **10D.2 — Frontend Execution Identity Session State** without introducing a new authorization model.
