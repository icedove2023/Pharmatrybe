# 10D.4 — Frontend RBAC / Capability Resolution

**Status:** Approved Specification
**Phase:** 10D — Frontend Identity + RBAC Integration
**Scope:** Frontend consumption of authoritative backend roles and permissions
**Depends on:** 10D.1, 10D.2, 10D.3, 10C.4, 10C.5
**Security principle:** Frontend RBAC is UX capability resolution, not authorization.

---

## 1. Purpose

This document defines how the frontend consumes the authoritative roles and permissions resolved by the backend and converts them into UI capabilities.

The frontend must not implement an independent authorization model.

The intended flow is:

```text
Supabase Session
       ↓
/auth/me
       ↓
Authoritative identity
       ↓
Active membership
       ↓
Backend roles
       ↓
Backend permissions
       ↓
Frontend capability resolution
       ↓
UI decisions
```

The frontend therefore answers:

> **"What should this user see or be allowed to attempt through the UI?"**

The backend answers:

> **"Is this operation actually authorized?"**

---

# 2. Existing RBAC Model

The frontend must consume the existing backend RBAC model.

The canonical database relationships are:

```text
membership_roles
    │
    ├── membership_id → hospital_memberships.id
    │
    └── role_id → roles.id

role_permissions
    │
    ├── role_id → roles.id
    │
    └── permission_id → permissions.id
```

Therefore:

```text
Hospital Membership
        ↓
Membership Roles
        ↓
Roles
        ↓
Role Permissions
        ↓
Permissions
```

The frontend must **not create another role-permission mapping**.

---

# 3. Authoritative Permission Source

Permissions returned by the backend identity contract are authoritative for frontend capability resolution.

Conceptually:

```json
{
  "roles": [
    "CLINICIAN"
  ],
  "permissions": [
    "cases:create",
    "cases:view",
    "cases:update",
    "recommendations:request"
  ]
}
```

The exact `/auth/me` response shape must follow the existing backend contract.

This document does not redefine that API contract.

---

# 4. Roles Are Not Permissions

The frontend must distinguish between:

```text
Role
```

and:

```text
Permission
```

For example:

```text
CLINICIAN
```

is a role.

Whereas:

```text
cases:view
recommendations:request
```

are permissions.

The preferred frontend capability decision is based on **permissions**, not hard-coded role names.

Therefore prefer:

```text
can("cases:view")
```

over:

```text
role === "CLINICIAN"
```

wherever the UI decision represents an actual backend capability.

---

# 5. Why Permissions Should Drive UI Capabilities

A role is a grouping of permissions.

The backend may change the permissions associated with a role without changing the role's identity.

Therefore:

```text
Role
  ↓
Permissions
  ↓
Capability
  ↓
UI
```

is more maintainable than:

```text
Role
  ↓
hard-coded UI behaviour
```

This also keeps the frontend aligned with the canonical backend RBAC model.

---

# 6. Capability Resolution

The frontend should expose a central capability mechanism conceptually equivalent to:

```text
can(permission)
```

For example:

```text
can("cases:view")
can("cases:create")
can("cases:update")
can("recommendations:request")
can("plugins:view")
can("plugins:configure")
```

The function should resolve against the permissions obtained from the authoritative identity state.

Conceptually:

```text
permissions = [
    "cases:view",
    "cases:create",
    "recommendations:request"
]

can("cases:view")
        ↓
true

can("patients:create")
        ↓
false
```

---

# 7. No Client-Supplied Permissions

The frontend must never accept permissions from:

* query parameters;
* URL fragments;
* request bodies;
* local storage;
* cookies controlled as application state;
* form fields;
* arbitrary configuration;
* plugin metadata.

The source must be the authenticated backend identity.

```text
Backend
   ↓
roles + permissions
   ↓
Frontend identity state
   ↓
Capability resolver
```

---

# 8. No Frontend Role Assignment

The frontend must never assign or elevate a role.

Prohibited:

```text
user clicks "Admin"
       ↓
frontend sets role = HOSPITAL_ADMIN
```

Also prohibited:

```text
localStorage.role = "HOSPITAL_ADMIN"
```

and:

```text
if (user.email === ...)
    role = "HOSPITAL_ADMIN"
```

Role assignment remains a backend administrative operation governed by the existing RBAC system.

---

# 9. UI Capability Examples

The existing permissions should be consumed directly.

Examples include:

```text
professionals:view
professionals:invite
professionals:manage
roles:assign

hospital:view
hospital:update

patients:view
patients:create

cases:view
cases:create
cases:update

laboratory:view
laboratory:create

recommendations:view
recommendations:request
recommendations:review

stewardship:view
stewardship:manage

guidelines:view
guidelines:manage

plugins:view
plugins:configure

workflows:execute
workflows:manage

audit:view
data:export
```

The frontend should not invent additional permission codes merely to simplify UI logic.

---

# 10. Capability-to-UI Mapping

The frontend may maintain a presentation mapping between permissions and UI capabilities.

For example:

```text
Permission
    ↓
UI Capability
```

Conceptually:

```text
cases:view
    ↓
show clinical case navigation

cases:create
    ↓
show "Create Case"

cases:update
    ↓
show "Edit Case"

professionals:invite
    ↓
show "Invite Professional"

plugins:configure
    ↓
show plugin configuration controls
```

This mapping is a UI concern.

It does not replace backend enforcement.

---

# 11. Navigation Resolution

Navigation should be permission-aware.

Conceptually:

```text
Navigation definition
        ↓
required permission
        ↓
can(permission)
        ↓
visible / hidden
```

Example:

```text
Clinical Cases
    required: cases:view

Plugin Governance
    required: plugins:view

Professional Management
    required: professionals:view

Hospital Settings
    required: hospital:update
```

The frontend should not display administrative navigation to users who lack the corresponding capability unless there is an intentional read-only presentation requirement.

---

# 12. Route Capability

Protected frontend routes may define required capabilities.

Example:

```text
/cases
    → cases:view

/cases/new
    → cases:create

/professionals
    → professionals:view

/plugins
    → plugins:view

/plugins/configure
    → plugins:configure
```

The frontend route guard may use these permissions to provide a good UX.

However:

> A frontend route guard is not a security boundary.

A direct API request must still be rejected by the backend if the user lacks permission.

---

# 13. Component-Level Capability

Individual controls may also use permissions.

Example:

```text
Cases page
 ├── View case
 ├── Create case
 └── Edit case
```

The UI can resolve:

```text
cases:view
cases:create
cases:update
```

independently.

This avoids using broad role checks where a specific permission is available.

---

# 14. Disabled vs Hidden Controls

The frontend may either hide or disable controls depending on UX requirements.

For example:

```text
No cases:create
        ↓
"Create Case" hidden
```

or:

```text
No cases:create
        ↓
"Create Case" disabled
```

The choice is a UX decision.

It must not affect backend authorization.

---

# 15. Forbidden State

A user may legitimately reach a frontend route without possessing the required capability.

For example:

```text
User navigates directly to:
/plugins/configure
        ↓
Frontend capability check
        ↓
plugins:configure = false
        ↓
Forbidden UI
```

The frontend should provide an explicit forbidden state rather than pretending that the resource does not exist when that distinction is useful.

Conceptually:

```text
403 / insufficient capability

       ↓

┌─────────────────────────────┐
│ Access denied               │
│                             │
│ You do not have permission  │
│ to perform this operation.  │
└─────────────────────────────┘
```

---

# 16. Backend 403 Remains Authoritative

Even if the frontend believes:

```text
can("plugins:configure") === true
```

the backend may still reject an operation because authorization can depend on contextual policies beyond simple permission membership.

Therefore:

```text
Frontend capability
        ↓
UX expectation
```

while:

```text
Backend authorization
        ↓
actual permission decision
```

remains authoritative.

---

# 17. Contextual Authorization

Some existing permissions explicitly indicate contextual policies.

Examples include:

```text
recommendations:view
recommendations:review
patients:view
patients:create
cases:update
stewardship:manage
data:export
audit:view
```

The frontend should not attempt to reproduce all contextual authorization logic.

For example:

```text
can("patients:view")
```

means:

> The UI may expose patient-view functionality.

It does **not** mean:

> Every patient record is necessarily accessible.

The backend remains responsible for resource-level and contextual authorization.

---

# 18. Role-Aware UI

Roles may still be consumed for presentation purposes.

For example:

```text
CLINICIAN
PHARMACIST
LABORATORY_SCIENTIST
INFECTIOUS_DISEASE_SPECIALIST
HOSPITAL_ADMIN
RESEARCHER
```

The frontend may display:

```text
Clinician
Pharmacist
Hospital Administrator
```

as part of the user's identity.

Roles may also help describe broad application experiences.

However, role names should not become a substitute for backend permissions.

Preferred:

```text
role → display identity
permission → capability
```

---

# 19. Multiple Roles

If the backend returns multiple roles, the frontend should preserve them as returned.

Conceptually:

```text
roles:
[
    "CLINICIAN",
    "PHARMACIST"
]
```

The frontend should resolve capabilities from the effective permission set rather than assuming a single role.

For example:

```text
Role A
   ↓
permissions A

Role B
   ↓
permissions B

Effective permissions
   ↓
capability resolver
```

The frontend must not independently calculate role inheritance or modify role permissions.

---

# 20. Permission Set Representation

The frontend may normalize permissions into an efficient lookup structure.

For example:

```text
Set<string>
```

containing:

```text
cases:view
cases:create
recommendations:request
```

This is an implementation detail.

The source remains the backend identity response.

---

# 21. Identity State Integration

The capability resolver should consume the same authoritative identity state established by 10D.1–10D.3.

Conceptually:

```text
IdentityState
│
├── user
├── professional
├── membership
├── hospital
├── roles
└── permissions
        ↓
CapabilityResolver
        ↓
UI
```

There should not be separate frontend stores for:

```text
user
tenant
roles
permissions
```

that can independently become inconsistent.

---

# 22. Loading State

Capability decisions must not be evaluated as:

```text
permissions === undefined
        ↓
false
```

without distinguishing between:

```text
not yet loaded
```

and:

```text
permission absent
```

The frontend should conceptually distinguish:

```text
LOADING
AUTHORIZED
UNAUTHORIZED
ERROR
```

This prevents authenticated users from seeing incorrect UI while `/auth/me` is still resolving.

---

# 23. Authentication Dependency

Capability resolution requires an established application identity.

Therefore:

```text
No session
    ↓
No identity
    ↓
No permissions
    ↓
No authenticated capabilities
```

Similarly:

```text
Session exists
       ↓
/auth/me pending
       ↓
capabilities not yet authoritative
```

The frontend should wait for identity initialization before making final capability-dependent rendering decisions.

---

# 24. Logout

When the user logs out:

```text
Logout
   ↓
Clear session
   ↓
Clear identity state
   ↓
Clear roles
   ↓
Clear permissions
   ↓
Clear tenant-scoped caches
   ↓
Unauthenticated UI
```

Permissions must never remain active in frontend state after logout.

---

# 25. Identity Change

When another user logs in:

```text
User A
 ↓
logout
 ↓
clear capability state
 ↓
User B login
 ↓
/auth/me
 ↓
new roles + permissions
 ↓
new capabilities
```

The frontend must never combine:

```text
User B identity
+
User A permissions
```

---

# 26. Permission Refresh

When `/auth/me` is refreshed, the frontend should replace the existing roles and permissions with the newly returned authoritative values.

Conceptually:

```text
Old permissions
       ↓
GET /auth/me
       ↓
New permissions
       ↓
replace identity state
       ↓
recalculate UI capabilities
```

This supports backend changes such as:

```text
role assignment
role removal
permission changes
membership suspension
```

without requiring the frontend to maintain its own authorization database.

---

# 27. No Optimistic Permission Elevation

The frontend must not assume a capability before the backend confirms the new identity state.

For example:

```text
Admin assigns role
       ↓
frontend immediately adds permission
```

is not authoritative.

Instead:

```text
Role assignment
       ↓
backend succeeds
       ↓
refresh /auth/me
       ↓
new permissions
       ↓
frontend capability updates
```

---

# 28. Capability Resolution API

The implementation should provide a simple central interface.

Conceptually:

```text
can(permission: string): boolean
```

Optional higher-level helpers may be provided:

```text
canAny([...permissions])
canAll([...permissions])
```

These helpers are presentation utilities.

They must resolve only against backend-derived permissions.

---

# 29. Example

Given:

```text
roles:
    CLINICIAN

permissions:
    cases:view
    cases:create
    cases:update
    recommendations:view
    recommendations:request
```

The frontend may resolve:

```text
can("cases:view")
    → true

can("cases:create")
    → true

can("cases:update")
    → true

can("plugins:configure")
    → false
```

The resulting UI could be:

```text
Clinical Cases
    ✓ View
    ✓ Create
    ✓ Edit

Plugin Governance
    ✗ Configuration controls unavailable
```

The backend must still independently enforce every operation.

---

# 30. Hospital Administrator Example

For:

```text
HOSPITAL_ADMIN
```

with permissions such as:

```text
professionals:view
professionals:invite
professionals:manage
roles:assign
hospital:view
hospital:update
plugins:view
plugins:configure
```

the frontend may expose:

```text
Hospital
Professionals
Role Management
Plugin Governance
Hospital Settings
```

This does not grant the administrator additional authority.

It merely reflects permissions already resolved by the backend.

---

# 31. Researcher Example

For:

```text
RESEARCHER
```

with:

```text
guidelines:view
```

the frontend may expose read-only guideline functionality.

It must not infer:

```text
guidelines:manage
```

from the role name.

---

# 32. Plugin Governance Example

The frontend governance interface should use the actual permissions:

```text
plugins:view
plugins:configure
```

rather than a synthetic:

```text
isPluginAdmin
```

For example:

```text
plugins:view
       ↓
show plugin governance

plugins:configure
       ↓
show configuration / governance actions
```

The backend remains responsible for determining whether the specific operation is allowed.

---

# 33. Capability Resolution Does Not Replace RLS

Frontend capability resolution is independent of database row-level security.

The security chain remains:

```text
Frontend
   ↓
JWT
   ↓
Backend authentication
   ↓
Execution identity
   ↓
TenantContext
   ↓
RBAC
   ↓
API authorization
   ↓
Supabase / RLS
```

The frontend capability resolver sits only at the UX layer:

```text
Backend identity
       ↓
Frontend capability state
       ↓
UI
```

---

# 34. Security Boundary

The complete model is:

```text
                 SECURITY BOUNDARY
                        │
                        ▼
Frontend ───────────── Backend
   │                       │
   │ capability UX         │ authoritative RBAC
   │                       │
   │ navigation             │ permission checks
   │ visibility             │ tenant checks
   │ controls               │ resource checks
   │                       │ RLS
```

Therefore:

> **Frontend RBAC is an optimization for user experience, not a security mechanism.**

---

# 35. Acceptance Criteria

10D.4 is satisfied when:

### Identity

* [ ] Roles are obtained from authoritative backend identity state.
* [ ] Permissions are obtained from authoritative backend identity state.
* [ ] Frontend does not assign roles.
* [ ] Frontend does not invent permissions.

### Capability Resolution

* [ ] A central permission-based capability resolver exists.
* [ ] UI decisions can use `can(permission)`.
* [ ] Optional `canAny` / `canAll` helpers do not introduce a second authorization model.
* [ ] Capabilities are recalculated when identity state changes.

### Navigation

* [ ] Navigation can be permission-aware.
* [ ] Protected frontend routes can define required capabilities.
* [ ] Hidden/disabled UI is treated as UX only.

### API Security

* [ ] Protected API requests use the authenticated JWT.
* [ ] Backend `403` responses remain authoritative.
* [ ] Frontend does not bypass denied operations.

### Contextual Authorization

* [ ] Frontend does not reproduce resource-level authorization rules.
* [ ] Frontend does not infer contextual permissions from role names.
* [ ] Backend remains responsible for final authorization.

### Identity Changes

* [ ] Logout clears permissions.
* [ ] Identity changes invalidate old capability state.
* [ ] New `/auth/me` data replaces the previous authorization state.
* [ ] Tenant-scoped caches are invalidated on identity change.

---

# 36. Validation Principle

The implementation must prove that frontend RBAC is a **consumer of backend authorization state**, not a replacement for it.

The expected architecture is:

```text
Supabase Session
       ↓
/auth/me
       ↓
Backend-resolved roles
       ↓
Backend-resolved permissions
       ↓
Frontend Identity State
       ↓
Capability Resolver
       ↓
Navigation / Routes / Controls
```

while the actual security path remains:

```text
Frontend Request
       ↓
JWT
       ↓
Backend Authentication
       ↓
Execution Identity
       ↓
Tenant Context
       ↓
Backend RBAC
       ↓
Resource / Contextual Authorization
       ↓
Supabase / RLS
```

---

## 37. Non-Goals

This document does **not** introduce:

* a new RBAC model;
* new roles;
* new permissions;
* frontend-only authorization;
* role assignment in the browser;
* client-controlled permissions;
* a frontend permission database;
* replacement of backend RBAC;
* replacement of Supabase RLS;
* contextual authorization logic duplicated in the frontend.

The purpose of 10D.4 is strictly to turn **authoritative backend roles and permissions into frontend UX capabilities**.
