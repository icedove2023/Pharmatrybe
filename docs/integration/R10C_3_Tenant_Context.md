# 10C.3 — Tenant Context
status : Approved 
This section defines how the backend determines **which hospital/tenant the authenticated professional is operating within**.

It follows the decisions already established in **16A–16E** and the completed **10C.0–10C.2** authentication boundary and execution identity work.

## 10C.3.1 — Purpose

The Tenant Context layer answers:

> **“Which hospital does this authenticated professional currently belong to?”**

The backend must **not accept `hospital_id` from the client as the authoritative tenant identity**.

Instead, tenant context is derived from the authenticated identity and the database membership relationship.

The authoritative relationship is:

```text
Supabase Auth User
        │
        │ auth_user_id
        ▼
professional_profiles
        │
        │ professional_id
        ▼
hospital_memberships
        │
        │ hospital_id
        ▼
hospitals
```

Therefore:

```text
Authenticated User
        ↓
Execution Identity
        ↓
Active Hospital Membership
        ↓
Tenant Context
```

---

# 10C.3.2 — Existing Database Foundation

The current database already contains the required relationship.

`professional_profiles` contains:

```text
id
auth_user_id
first_name
last_name
professional_type
professional_registration_number
phone
profile_status
```

`hospital_memberships` contains:

```text
id
professional_id
hospital_id
status
invited_by
joined_at
activated_at
suspended_at
deactivated_at
ended_at
created_at
updated_at
```

`hospitals` contains:

```text
id
name
legal_name
hospital_code
status
created_at
updated_at
```

The project's current architectural decision is:

> **One authenticated health-professional identity → one active hospital membership.**

Therefore, the backend does not need a user-selected tenant mechanism for the initial implementation.

---

# 10C.3.3 — Authoritative Tenant Resolution

The database already provides the following function:

```sql
public.current_hospital_id()
```

Its current definition resolves the hospital through the authenticated Supabase user:

```sql
select hm.hospital_id
from public.hospital_memberships hm
join public.professional_profiles pp
    on pp.id = hm.professional_id
where pp.auth_user_id = auth.uid()
  and hm.status = 'ACTIVE'
limit 1
```

This establishes the authoritative tenant-resolution path:

```text
auth.uid()
   ↓
professional_profiles.auth_user_id
   ↓
professional_profiles.id
   ↓
hospital_memberships.professional_id
   ↓
hospital_memberships.hospital_id
```

The backend must therefore treat the database membership relationship as the source of truth.

---

# 10C.3.4 — Tenant Context Object

After authentication and execution identity resolution, the backend should construct an internal tenant context.

Conceptually:

```text
TenantContext
├── hospital_id
├── hospital
│   ├── id
│   ├── name
│   ├── hospital_code
│   └── status
└── membership
    ├── id
    └── status
```

The minimum mandatory value is:

```text
hospital_id
```

Additional hospital and membership information may be loaded when required by authorization or application logic.

---

# 10C.3.5 — Tenant Context Is Server-Derived

The following must **not** be treated as authoritative:

```http
X-Hospital-ID: ...
```

or:

```json
{
  "hospital_id": "..."
}
```

or:

```text
/hospitals/{hospital_id}/...
```

when supplied by the client.

A client-supplied hospital identifier may be used as a **requested resource identifier**, but it must never establish the caller's tenant.

For example:

```http
GET /hospitals/HOSPITAL-B/patients
```

does not mean:

```text
caller belongs to HOSPITAL-B
```

The backend must first determine:

```text
caller → authenticated user → professional → active membership → hospital
```

and then authorize access to the requested resource.

---

# 10C.3.6 — Tenant Context Resolution Sequence

The backend request flow becomes:

```text
HTTP Request
     │
     ▼
Authentication Boundary
     │
     ▼
Authenticated Supabase Identity
     │
     ▼
Execution Identity
     │
     ├── auth_user_id
     ├── professional_id
     └── identity status
     │
     ▼
Tenant Context Resolution
     │
     ├── active membership?
     │
     └── hospital_id
     │
     ▼
Authorization / RBAC
     │
     ▼
Application Service
     │
     ▼
Repository / Database
```

The important ordering is:

```text
Authentication
      ↓
Identity
      ↓
Tenant
      ↓
Authorization
      ↓
Business operation
```

Tenant resolution must therefore occur **before tenant-scoped business operations**.

---

# 10C.3.7 — Missing Tenant Context

An authenticated user does not automatically have access to a hospital.

The following state is possible:

```text
Authenticated
     ↓
Professional profile exists
     ↓
No ACTIVE membership
```

In this situation:

```text
TenantContext = unavailable
```

The backend must not guess a hospital.

The request should therefore be rejected for tenant-scoped operations.

Conceptually:

```text
401 Unauthorized
```

should be reserved for failure of authentication.

A successfully authenticated identity without an active tenant should instead be treated as an authorization/context failure, typically:

```text
403 Forbidden
```

The exact HTTP mapping should remain consistent with the backend error model defined in 10C.1/10C.2.

---

# 10C.3.8 — Inactive Membership

Only an active membership establishes tenant context.

The current database function explicitly requires:

```sql
hm.status = 'ACTIVE'
```

Therefore:

```text
INVITED
SUSPENDED
DEACTIVATED
ENDED
```

must not establish an active tenant context.

The intended rule is:

```text
ACTIVE membership
    → tenant context available

non-ACTIVE membership
    → tenant context unavailable
```

This is important because authentication and organizational authorization are separate concerns.

A user may remain a valid Supabase Auth user while no longer being authorized to operate within a hospital.

---

# 10C.3.9 — Tenant Context and RBAC

Tenant context identifies **where** the user operates.

RBAC determines **what** the user can do there.

Therefore:

```text
Tenant Context
    =
    WHERE
```

while:

```text
Role / Permission
    =
    WHAT
```

For example:

```text
User A
 ├── hospital_id = Hospital A
 └── role = ADMIN
```

and:

```text
User B
 ├── hospital_id = Hospital B
 └── role = CLINICIAN
```

The role must never be evaluated without the tenant boundary.

The authorization model therefore becomes:

```text
Authenticated Identity
        +
Tenant Context
        +
Role / Permission
        ↓
Authorized Operation
```

---

# 10C.3.10 — RLS Relationship

Tenant context is also aligned with the PostgreSQL/Supabase Row Level Security design.

The database already exposes:

```sql
public.current_hospital_id()
```

as:

```text
STABLE
SECURITY DEFINER
```

with:

```sql
SET search_path TO 'public'
```

The function derives the hospital from:

```sql
auth.uid()
```

rather than trusting a client-provided hospital identifier.

This creates an important security boundary:

```text
Supabase JWT
      ↓
auth.uid()
      ↓
current_hospital_id()
      ↓
RLS policy
      ↓
tenant-isolated rows
```

Thus the backend and database should use the same tenant identity model rather than maintaining two independent interpretations of tenancy.

---

# 10C.3.11 — Backend and Database Must Agree

The backend must not calculate:

```text
hospital_id = value supplied by frontend
```

while PostgreSQL calculates:

```text
hospital_id = active membership
```

because this creates two competing tenant contexts.

Instead:

```text
Backend Tenant Context
          │
          │ same identity model
          ▼
Database RLS Tenant Context
```

Both must ultimately derive from:

```text
authenticated Supabase user
        ↓
professional profile
        ↓
active hospital membership
```

This maintains a single authoritative tenant boundary.

---

# 10C.3.12 — Current Verified Test State

The RLS test data confirms the intended model.

Hospital A:

```text
RLS Test Hospital A
RLS-A
```

Hospital B:

```text
RLS Test Hospital B
RLS-B
```

Professional A is associated with Hospital A:

```text
rls_test_a@gmail.com
        ↓
professional A
        ↓
ACTIVE membership
        ↓
RLS Test Hospital A
```

Professional B is associated with Hospital B:

```text
rls_test_b@gmail.com
        ↓
professional B
        ↓
ACTIVE membership
        ↓
RLS Test Hospital B
```

The database therefore currently demonstrates the intended one-professional/one-active-hospital relationship.

---

# 10C.3.13 — Security Rules

The following rules are established for Tenant Context:

### Rule 1 — Never trust client tenant identifiers

```text
hospital_id supplied by client
≠
authoritative tenant identity
```

### Rule 2 — Resolve tenant from authenticated identity

```text
auth.uid()
→ professional
→ active membership
→ hospital
```

### Rule 3 — Only ACTIVE memberships establish tenant context

```text
status = ACTIVE
```

is required.

### Rule 4 — Authentication does not imply tenancy

A valid authenticated user may have:

```text
no active hospital membership
```

and therefore no tenant context.

### Rule 5 — Tenant precedes authorization

The authorization layer must evaluate permissions within the resolved hospital context.

### Rule 6 — Backend and RLS must share the same tenant model

There must be one authoritative interpretation of tenant membership.

---

# 10C.3.14 — What 10C.3 Does Not Do

Tenant Context does **not** determine:

* whether the JWT is valid;
* whether the user is authenticated;
* what role the user has;
* what permissions the role grants;
* whether a particular resource may be accessed;
* whether a plugin may execute.

Those responsibilities belong to the appropriate layers.

The separation is:

```text
10C.1 Authentication Boundary
        ↓
Who authenticated?

10C.2 Execution Identity
        ↓
Which professional is executing?

10C.3 Tenant Context
        ↓
Which hospital does the professional operate within?

10C.4 Authorization / RBAC
        ↓
What may the professional do?

Application / Plugin Governance
        ↓
May this operation/plugin execute?
```

---

# 10C.3.15 — Architectural Decision

**Confirmed Decision**

The backend will derive tenant context from the authenticated user's active hospital membership rather than accepting tenant identity from the client.

The authoritative chain is:

```text
Supabase Auth User
        ↓
professional_profiles.auth_user_id
        ↓
hospital_memberships.professional_id
        ↓
hospital_memberships.hospital_id
        ↓
TenantContext
```

The existing:

```text
public.current_hospital_id()
```

function provides the database-side implementation of the same principle.

---

# 10C.3.16 — Completion Criteria

10C.3 is considered complete when the backend can reliably:

* identify the authenticated user;
* resolve the corresponding professional profile;
* resolve exactly one active hospital membership;
* construct an internal tenant context;
* reject authenticated users without an active tenant for tenant-scoped operations;
* prevent client-supplied `hospital_id` from overriding tenant identity;
* maintain consistency between backend tenant resolution and PostgreSQL RLS;
* pass the Hospital A / Hospital B isolation test.

The next architectural layer should therefore build on:

```text
Authentication Boundary
        ↓
Execution Identity
        ↓
Tenant Context
```

before introducing the detailed **authorization/RBAC enforcement boundary**.
