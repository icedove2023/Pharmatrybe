# 10C.4 — Backend RBAC

**Project:** PharmaTrybe Clinical Intelligence Platform
**Phase:** 10C — Backend Security Boundary
**Section:** 10C.4 — Backend Role-Based Access Control (RBAC)
**Status:** Architecture / Backend Inspection Baseline Approved
**Source of Truth:** Existing `roles`, `permissions`, `membership_roles`, and `role_permissions` definitions and data
**Decision:** Use the existing canonical RBAC model; do not introduce a parallel authorization model.

---

# 1. Purpose

This document defines how the PharmaTrybe backend resolves and enforces **role-based authorization** after authentication, execution identity, and tenant context have been established.

RBAC answers the question:

> **"Given this authenticated professional and their active hospital membership, what operations are they authorized to perform?"**

The backend must derive authorization from the existing database relationships:

```text
Authenticated User
       │
       ↓
Professional Profile
       │
       ↓
Hospital Membership
       │
       ↓
Membership Roles
       │
       ↓
Roles
       │
       ↓
Role Permissions
       │
       ↓
Permissions
```

The backend must **not invent permissions from role names**, hard-code a second role matrix, or use frontend role information as the authorization source.

The existing database is authoritative.

The backend's responsibility is to resolve that data and enforce it at the appropriate authorization boundary.

---

# 2. Architectural Position

RBAC occurs after the previous security boundaries:

```text
10C.1 Authentication Boundary
        │
        ↓
10C.2 Execution Identity
        │
        ↓
10C.3 Tenant Context
        │
        ↓
10C.4 Backend RBAC
        │
        ↓
Resource / Operation Authorization
        │
        ↓
Business Logic
```

Therefore:

* Authentication establishes **who** the caller is.
* Execution identity establishes the backend identity associated with the request.
* Tenant context establishes **which hospital/organisation** the request operates within.
* RBAC establishes **what that identity may do within that tenant**.

These are separate security decisions.

---

# 3. Existing RBAC Data Model

The inspected backend models define:

```text
roles
permissions
membership_roles
role_permissions
hospital_memberships
```

The relationships are:

```text
membership_roles.membership_id
        ↓
hospital_memberships.id

membership_roles.role_id
        ↓
roles.id

role_permissions.role_id
        ↓
roles.id

role_permissions.permission_id
        ↓
permissions.id
```

The backend therefore resolves permissions through two many-to-many mappings:

```text
Hospital Membership
        │
        │ membership_roles
        ↓
      Role
        │
        │ role_permissions
        ↓
   Permission
```

The existing `Role` model identifies roles as canonical application roles, while `Permission` represents canonical resource-action permissions. 

---

# 4. Canonical Authorization Model

The authorization model is:

```text
User
 │
 │ authenticated identity
 ↓
ProfessionalProfile
 │
 │ professional_id
 ↓
HospitalMembership
 │
 │ membership_id
 ↓
MembershipRole
 │
 │ role_id
 ↓
Role
 │
 │ role_id
 ↓
RolePermission
 │
 │ permission_id
 ↓
Permission
```

A permission is therefore **not assigned directly to a user**.

A permission is inherited through a role assigned to the user's hospital membership.

This preserves the existing architecture:

```text
User
  ↓
Membership
  ↓
Role
  ↓
Permission
```

---

# 5. Canonical Roles

The inspected database currently contains the following canonical roles.

| Role Code                       | Name                          | Description                                     |
| ------------------------------- | ----------------------------- | ----------------------------------------------- |
| `HOSPITAL_ADMIN`                | Hospital Administrator        | Hospital administration and governance          |
| `PHARMACIST`                    | Pharmacist                    | Medication review and stewardship               |
| `CLINICIAN`                     | Clinician                     | Clinical assessment and recommendation workflow |
| `INFECTIOUS_DISEASE_SPECIALIST` | Infectious Disease Specialist | Complex antimicrobial resistance case review    |
| `RESEARCHER`                    | Researcher                    | Approved read-only research access              |
| `LABORATORY_SCIENTIST`          | Laboratory Scientist          | Laboratory diagnostics and AST                  |

These are the actual canonical role records and are not newly defined by this document.

The backend model itself describes `Role` as the **canonical application role from the approved role matrix**. 

---

# 6. Canonical Permissions

The inspected database contains the following permissions.

| Permission                | Purpose                                                                             |
| ------------------------- | ----------------------------------------------------------------------------------- |
| `professionals:manage`    | Manage professional memberships, including activation, suspension, and deactivation |
| `guidelines:view`         | View global WHO and guideline knowledge                                             |
| `guidelines:manage`       | Manage hospital guidelines                                                          |
| `recommendations:request` | Request recommendations                                                             |
| `laboratory:view`         | View laboratory results                                                             |
| `audit:view`              | View audit events subject to scope policy                                           |
| `plugins:view`            | View configured plugins                                                             |
| `workflows:execute`       | Execute approved workflows subject to approval policy                               |
| `roles:assign`            | Assign canonical roles to memberships                                               |
| `laboratory:create`       | Enter laboratory results                                                            |
| `cases:create`            | Create clinical cases                                                               |
| `cases:view`              | View clinical cases                                                                 |
| `plugins:configure`       | Configure plugins                                                                   |
| `stewardship:manage`      | Manage stewardship policies subject to contextual policy                            |
| `patients:create`         | Create patient records subject to contextual policy                                 |
| `hospital:view`           | View the hospital profile                                                           |
| `stewardship:view`        | View stewardship policies                                                           |
| `data:export`             | Export data subject to controlled policy                                            |
| `recommendations:review`  | Review recommendations subject to contextual policy                                 |
| `recommendations:view`    | View recommendations subject to contextual policy                                   |
| `cases:update`            | Update clinical cases subject to resource policy                                    |
| `hospital:update`         | Update the hospital profile                                                         |
| `professionals:view`      | View hospital professionals                                                         |
| `workflows:manage`        | Manage workflows                                                                    |
| `patients:view`           | View patient records subject to contextual policy                                   |
| `professionals:invite`    | Invite professionals to the hospital                                                |

These permission codes are the authorization vocabulary currently present in the database.

---

# 7. Existing Role → Permission Mapping

The backend must use the existing `role_permissions` data.

## 7.1 HOSPITAL_ADMIN

Current permissions:

```text
professionals:manage
guidelines:view
guidelines:manage
audit:view
plugins:view
roles:assign
plugins:configure
hospital:view
stewardship:view
hospital:update
professionals:view
workflows:manage
professionals:invite
```

Therefore:

```text
HOSPITAL_ADMIN
    ├── professionals:manage
    ├── professionals:view
    ├── professionals:invite
    ├── roles:assign
    ├── hospital:view
    ├── hospital:update
    ├── guidelines:view
    ├── guidelines:manage
    ├── stewardship:view
    ├── plugins:view
    ├── plugins:configure
    ├── workflows:manage
    └── audit:view
```

---

## 7.2 PHARMACIST

Current permissions:

```text
guidelines:view
recommendations:request
laboratory:view
workflows:execute
cases:create
cases:view
hospital:view
stewardship:view
recommendations:review
recommendations:view
professionals:view
patients:view
```

Therefore:

```text
PHARMACIST
    ├── guidelines:view
    ├── recommendations:request
    ├── recommendations:view
    ├── recommendations:review
    ├── laboratory:view
    ├── workflows:execute
    ├── cases:create
    ├── cases:view
    ├── hospital:view
    ├── stewardship:view
    ├── professionals:view
    └── patients:view
```

---

## 7.3 CLINICIAN

Current permissions:

```text
guidelines:view
recommendations:request
laboratory:view
workflows:execute
cases:create
cases:view
patients:create
hospital:view
stewardship:view
recommendations:review
recommendations:view
cases:update
professionals:view
patients:view
```

Therefore:

```text
CLINICIAN
    ├── guidelines:view
    ├── recommendations:request
    ├── recommendations:view
    ├── recommendations:review
    ├── laboratory:view
    ├── workflows:execute
    ├── cases:create
    ├── cases:view
    ├── cases:update
    ├── patients:create
    ├── patients:view
    ├── hospital:view
    ├── stewardship:view
    └── professionals:view
```

---

## 7.4 INFECTIOUS_DISEASE_SPECIALIST

Current permissions:

```text
guidelines:view
recommendations:request
laboratory:view
workflows:execute
cases:create
cases:view
patients:create
hospital:view
stewardship:view
recommendations:review
recommendations:view
cases:update
professionals:view
patients:view
```

Therefore, the currently stored permission set is the same as the inspected `CLINICIAN` permission set:

```text
INFECTIOUS_DISEASE_SPECIALIST
    ├── guidelines:view
    ├── recommendations:request
    ├── recommendations:view
    ├── recommendations:review
    ├── laboratory:view
    ├── workflows:execute
    ├── cases:create
    ├── cases:view
    ├── cases:update
    ├── patients:create
    ├── patients:view
    ├── hospital:view
    ├── stewardship:view
    └── professionals:view
```

**Important:** this document does not invent additional ID-specialist permissions merely because the role description says "Complex antimicrobial resistance case review."

The database mapping remains authoritative.

---

# 7.5 RESEARCHER

Current permission:

```text
guidelines:view
```

Therefore:

```text
RESEARCHER
    └── guidelines:view
```

The existing data describes the role as:

```text
Approved read-only research access
```

but the actual permission assignment inspected is the single `guidelines:view` permission.

No additional permissions should be inferred from the description.

---

# 7.6 LABORATORY_SCIENTIST

Current permissions:

```text
guidelines:view
laboratory:view
workflows:execute
laboratory:create
cases:view
hospital:view
stewardship:view
professionals:view
```

Therefore:

```text
LABORATORY_SCIENTIST
    ├── guidelines:view
    ├── laboratory:view
    ├── laboratory:create
    ├── workflows:execute
    ├── cases:view
    ├── hospital:view
    ├── stewardship:view
    └── professionals:view
```

---

# 8. Permission Resolution

The backend permission resolver should conceptually perform:

```text
Authenticated User
       ↓
Find ProfessionalProfile
       ↓
Find active HospitalMembership
       ↓
Find MembershipRole records
       ↓
Resolve Role records
       ↓
Resolve RolePermission records
       ↓
Resolve Permission records
       ↓
Build effective permission set
```

Conceptually:

```python
effective_permissions = {
    permission.code
    for membership_role in membership.roles
    for role_permission in membership_role.role.role_permissions
    for permission in [role_permission.permission]
}
```

The exact implementation may differ, but the authorization semantics must remain equivalent.

---

# 9. Multiple Roles

The existing schema permits multiple roles to be assigned to a hospital membership because `membership_roles` is a mapping between memberships and roles.

Therefore, if a membership has:

```text
CLINICIAN
+
PHARMACIST
```

the effective permission set is the **union** of permissions granted by those roles.

Conceptually:

```text
CLINICIAN permissions
          +
PHARMACIST permissions
          ↓
Effective permissions
```

A permission is granted when **at least one assigned canonical role grants it**.

There is no separate "combined role" definition.

---

# 10. No Direct User Permissions

The current RBAC model does not contain a direct:

```text
user → permission
```

relationship.

Therefore, backend authorization must not introduce one.

The canonical path is:

```text
professional
      ↓
membership
      ↓
membership_roles
      ↓
roles
      ↓
role_permissions
      ↓
permissions
```

This preserves centralized authorization governance.

---

# 11. Tenant-Bound RBAC

RBAC must always operate against the user's **active hospital membership**.

The permission:

```text
patients:view
```

does not mean:

> "The user can view patients everywhere."

It means:

> "The user's active membership has a role that grants `patients:view`, subject to the resource's tenant and contextual authorization policy."

This distinction is essential because PharmaTrybe is tenant-aware.

The identity model already represents the hospital membership separately from the professional profile, with `hospital_memberships` connecting a professional to a hospital. 

---

# 12. RBAC Is Not the Entire Authorization Decision

A permission grant does **not automatically mean unrestricted access**.

Several existing permission descriptions explicitly contain contextual restrictions:

```text
patients:view
patients:create
cases:update
recommendations:view
recommendations:review
audit:view
data:export
stewardship:manage
workflows:execute
```

For example:

```text
recommendations:review
```

is described as:

```text
Review recommendations subject to contextual policy
```

Therefore the backend authorization model is:

```text
Authentication
      ↓
Execution Identity
      ↓
Tenant Context
      ↓
Role Resolution
      ↓
Permission Resolution
      ↓
Contextual / Resource Authorization
      ↓
Allow or Deny
```

RBAC provides the **coarse-grained capability**.

Resource and contextual policies provide the **fine-grained boundary**.

---

# 13. Authorization Decision

The backend should conceptually evaluate:

```python
authorize(
    execution_identity,
    tenant_context,
    required_permission,
    resource_context=None,
)
```

The decision should follow:

```text
Is request authenticated?
        │
       NO ──→ DENY
        │
       YES
        ↓
Does execution identity have active membership?
        │
       NO ──→ DENY
        │
       YES
        ↓
Does membership belong to current tenant?
        │
       NO ──→ DENY
        │
       YES
        ↓
Does an assigned role grant required permission?
        │
       NO ──→ DENY
        │
       YES
        ↓
Does resource/contextual policy allow operation?
        │
       NO ──→ DENY
        │
       YES
        ↓
      ALLOW
```

---

# 14. Backend Enforcement Boundary

Authorization must occur **before protected business operations execute**.

The desired structure is:

```text
HTTP Request
     ↓
Authentication
     ↓
Execution Identity
     ↓
Tenant Context
     ↓
RBAC / Authorization
     ↓
Endpoint Handler
     ↓
Service Layer
     ↓
Repository / Database
```

The endpoint should not perform business work first and check permissions afterwards.

---

# 15. Permission-Based Checks

Backend code should check permissions rather than role names wherever possible.

Prefer:

```python
require_permission("patients:view")
```

over:

```python
require_role("CLINICIAN")
```

This is important because permissions represent the actual capability granted by the database.

For example:

```text
CLINICIAN
```

is a role.

```text
patients:view
```

is an authorization capability.

The endpoint should normally care about the capability required to execute the operation.

---

# 16. Example Authorization

### Viewing a patient

```text
Request
  ↓
Authenticated user
  ↓
Active hospital membership
  ↓
Resolve assigned roles
  ↓
Resolve permissions
  ↓
Check patients:view
  ↓
Check patient belongs to permitted tenant/context
  ↓
Allow / Deny
```

### Creating a clinical case

```text
Request
  ↓
Check cases:create
  ↓
Check tenant context
  ↓
Create case
```

### Updating a clinical case

```text
Request
  ↓
Check cases:update
  ↓
Check tenant
  ↓
Check resource policy
  ↓
Update case
```

### Requesting a recommendation

```text
Request
  ↓
Check recommendations:request
  ↓
Check tenant/resource context
  ↓
Execute approved workflow
```

The existing platform architecture already treats workflow execution as an orchestration concern and keeps clinical reasoning outside the workflow manager. 

---

# 17. Role Assignment Authorization

The permission:

```text
roles:assign
```

is itself an authorization capability.

Therefore, role assignment must not simply be available to any authenticated user.

The backend should require:

```text
roles:assign
```

before allowing a membership role assignment operation.

Similarly:

```text
professionals:invite
```

controls invitation capability, while:

```text
professionals:manage
```

controls management of professional memberships.

The permission model therefore governs administrative operations through the same canonical RBAC mechanism.

---

# 18. Role and Permission IDs

The backend should use the database identifiers internally:

```text
roles.id
permissions.id
```

but application authorization checks should normally use stable canonical codes:

```text
CLINICIAN
PHARMACIST
patients:view
cases:create
recommendations:request
```

The `code` fields are unique in the inspected models for both roles and permissions. 

This means code-based authorization is preferable to scattering UUIDs throughout application code.

---

# 19. Do Not Hard-Code the Permission Matrix

The following pattern should **not** become the source of truth:

```python
ROLE_PERMISSIONS = {
    "CLINICIAN": [
        "patients:view",
        "cases:create",
        ...
    ]
}
```

Such a structure would duplicate the database's existing authorization model.

Instead:

```text
Database
   ↓
roles
   ↓
role_permissions
   ↓
permissions
   ↓
Backend resolver
```

The backend should resolve the current assignments.

This ensures that changes to canonical role assignments can be governed through the database rather than requiring application-code changes.

---

# 20. Frontend Roles Are Not Authoritative

The frontend may display:

```text
Clinician
Pharmacist
Hospital Administrator
```

but these values must never be trusted as authorization evidence.

The backend must derive authorization from:

```text
authenticated identity
+
active membership
+
database role assignment
+
database permission assignment
```

A client-supplied value such as:

```json
{
  "role": "HOSPITAL_ADMIN"
}
```

must not grant administrative authority.

---

# 21. JWT Claims and RBAC

Authentication claims may establish the authenticated identity, but the backend RBAC decision should remain grounded in the canonical application identity and membership model.

The conceptual distinction is:

```text
JWT
 ↓
Who authenticated?
```

versus:

```text
Application database
 ↓
What hospital membership does this identity have?
 ↓
What roles are assigned?
 ↓
What permissions do those roles grant?
```

This prevents application authorization from becoming dependent on arbitrary client-controlled role information.

---

# 22. Permission Failure

When the authenticated user lacks the required permission, the backend must deny the operation.

Conceptually:

```text
Authenticated
    +
Valid tenant
    +
No required permission
    ↓
DENY
```

Authentication success must never imply authorization success.

---

# 23. Unknown Role or Permission

The backend should fail closed when RBAC data cannot be resolved safely.

Examples:

```text
Unknown role
        ↓
Do not infer permissions
        ↓
DENY
```

or:

```text
Role exists
but role_permissions cannot be resolved
        ↓
Do not assume permissions
        ↓
DENY
```

No fallback role should be invented.

No default administrative permission set should be applied.

---

# 24. Revocation

Because permissions are derived through:

```text
membership_roles
        ↓
roles
        ↓
role_permissions
```

authorization must account for changes to those records.

Examples:

```text
Role removed from membership
        ↓
Effective permissions change
```

```text
Permission removed from role
        ↓
Effective permissions change
```

```text
Membership suspended
        ↓
Authorization must fail
```

```text
Membership deactivated
        ↓
Authorization must fail
```

This reinforces the importance of resolving the active membership and current role assignments rather than treating a previously observed role as permanent.

The existing `HospitalMembership` model explicitly supports membership states including `INVITED`, `ACTIVE`, `SUSPENDED`, and historical/deactivated states. 

---

# 25. RBAC and Auditability

Authorization decisions should be compatible with the platform's audit architecture.

The platform baseline requires auditability for clinical operations and maintains traceability through execution metadata and audit trails. 

For security-sensitive operations, the audit context should be capable of identifying:

```text
authenticated identity
professional identity
hospital / tenant
membership
role(s)
permission requested
authorization result
resource/context where applicable
trace/correlation ID
timestamp
```

The authorization layer should not modify clinical decisions.

It only establishes whether the caller may perform the requested operation.

---

# 26. RBAC and Clinical Safety

RBAC is an **access-control mechanism**, not a clinical reasoning mechanism.

Therefore:

```text
RBAC
  ↓
May this actor perform this operation?
```

while:

```text
Clinical Rules Engine
  ↓
Is this clinical action appropriate/safe?
```

and:

```text
Decision Fusion Engine
  ↓
How should available evidence be synthesized?
```

These boundaries must remain separate.

The platform baseline explicitly separates workflow orchestration, clinical rules, decision fusion, and explainability responsibilities. 

---

# 27. Complete Backend Authorization Flow

The resulting backend security flow is:

```text
┌─────────────────────────────┐
│       Incoming Request      │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 10C.1 Authentication        │
│ Verify authenticated user   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 10C.2 Execution Identity    │
│ Resolve application identity│
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 10C.3 Tenant Context        │
│ Resolve active membership   │
│ and hospital                │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 10C.4 Backend RBAC          │
│                             │
│ membership_roles            │
│        ↓                    │
│ roles                       │
│        ↓                    │
│ role_permissions            │
│        ↓                    │
│ permissions                 │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Context / Resource Policy   │
└──────────────┬──────────────┘
               ↓
        ┌──────┴──────┐
        ↓             ↓
      ALLOW          DENY
        ↓             ↓
 Business Logic    403 / reject
```

---

# 28. Authorization Resolution Algorithm

The canonical backend algorithm is therefore:

```text
1. Obtain authenticated user identity.

2. Resolve the corresponding professional profile.

3. Resolve the active hospital membership.

4. Verify that the membership is valid for the current tenant.

5. Load all roles assigned through membership_roles.

6. Resolve permissions through role_permissions.

7. Build the effective permission set.

8. Check the endpoint's required permission.

9. If permission is absent:
      deny.

10. If permission is present:
      evaluate any required resource/contextual policy.

11. If contextual policy fails:
      deny.

12. Otherwise:
      allow operation.

13. Record appropriate authorization/audit context
    for security-sensitive operations.
```

---

# 29. Architectural Invariants

The following are the RBAC invariants for 10C.4.

### Invariant 1 — Database is authoritative

The existing:

```text
roles
permissions
membership_roles
role_permissions
```

model is the source of truth.

### Invariant 2 — No direct user permissions

Permissions are inherited through roles.

### Invariant 3 — Roles are membership-scoped

A role is assigned to a `hospital_membership`, not globally to a person.

### Invariant 4 — Tenant context precedes authorization

Permissions cannot be evaluated independently of the active hospital context.

### Invariant 5 — Multiple roles are additive

The effective permission set is the union of permissions granted by assigned roles.

### Invariant 6 — Permission codes are the application authorization vocabulary

Endpoints should request capabilities such as:

```text
patients:view
cases:create
recommendations:request
```

rather than embedding role-specific assumptions.

### Invariant 7 — Unknown authorization state fails closed

The backend must not invent permissions when identity, membership, role, or permission resolution fails.

### Invariant 8 — RBAC does not replace contextual authorization

A granted permission may still be subject to resource, tenant, or contextual policy.

### Invariant 9 — Frontend claims are never authoritative

The backend independently resolves authorization.

### Invariant 10 — RBAC does not perform clinical reasoning

Authorization and clinical decision-making remain separate architectural boundaries.

---

# 30. Current RBAC Baseline

The inspected implementation therefore establishes this current baseline:

```text
6 canonical roles
        ↓
membership_roles
        ↓
role_permissions
        ↓
25 canonical permissions
```

with the six actual roles:

```text
HOSPITAL_ADMIN
PHARMACIST
CLINICIAN
INFECTIOUS_DISEASE_SPECIALIST
RESEARCHER
LABORATORY_SCIENTIST
```

and the existing permission assignments described above.

The backend should **resolve and enforce this existing model**, rather than introducing a new authorization abstraction that duplicates it.

---

# 31. Relationship to 10C.1–10C.3

The complete security boundary now becomes:

```text
10C.1 — Authentication Boundary
        "Who are you?"
              ↓
10C.2 — Execution Identity
        "Which application identity
         does this request represent?"
              ↓
10C.3 — Tenant Context
        "Which hospital/organisation
         does this identity operate within?"
              ↓
10C.4 — Backend RBAC
        "Which capabilities does this
         membership possess?"
              ↓
Resource / Context Policy
        "May this capability be used
         on this specific resource?"
              ↓
Business Operation
```

This separation is important because **authentication, identity, tenancy, and authorization are not interchangeable concepts**.

---

# 32. Decision

**Confirmed Decision — 10C.4**

PharmaTrybe will use the existing database-backed RBAC model:

```text
hospital_memberships
        ↓
membership_roles
        ↓
roles
        ↓
role_permissions
        ↓
permissions
```

The backend will resolve the effective permission set from the authenticated professional's active hospital membership and use permission codes for authorization checks.

No second hard-coded RBAC matrix will be introduced.

No frontend role claim will be trusted as authorization evidence.

No permission will be inferred from a role description.

No authorization decision will bypass tenant context.

Where a permission is marked as subject to contextual, resource, approval, or controlled policy, RBAC will provide the capability gate but the relevant contextual policy must provide the final authorization decision.

This preserves the existing identity architecture and maintains a clean boundary between **authentication → identity → tenancy → RBAC → contextual authorization → business logic**.
