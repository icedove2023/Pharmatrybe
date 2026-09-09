# Phase 16B — Identity + Tenant Database Schema

**Document:** `PHASE_16B_IDENTITY_TENANT_DATABASE_SCHEMA.md`  
**Phase:** 16B  
**Status:** APPROVED SCHEMA BASELINE — IMPLEMENTATION NOT PERFORMED
**Date:** 2026-08-19  
**Parent decision:** `PHASE_16A_IDENTITY_TENANT_ARCHITECTURE_DECISION.md`  
**Source of truth reference:** `FRONTEND_BACKEND_INTEGRATION_REPORT.md`, `PHASE_16_AUTH_SUPABASE_AUDIT.md`, `PHASE_16A_IDENTITY_TENANT_ARCHITECTURE_DECISION.md`  

**Approval Authority:** `docs/integration/approved_integration_docs.md` approves the identity, hospital, professional-profile, membership, role, invitation, and one-active-membership schema baseline. This document remains a schema specification; implementation still requires the approved downstream slice.

---

## 1. Purpose

This document defines the proposed database model for the identity, hospital/organisation, membership, role, invitation, account lifecycle, and tenant-isolation foundations of PharmaTrybe.

This document is a **schema-design specification**.

It is **not** a database migration and does not perform implementation.

Therefore, this document does not:

* create database tables;
* create Supabase migrations;
* create RLS policies;
* modify the existing database;
* implement authentication routes;
* implement FastAPI authentication middleware;
* implement frontend authentication behaviour;
* implement the role/permission matrix.

Those activities belong to later phases.

The purpose of Phase 16B is to establish the structural model that those implementation phases will follow.

---

# 2. Architectural Context

PharmaTrybe is a modular Clinical Intelligence Platform in which authentication and authorization belong to the platform core rather than the plugin layer. The existing Plugin Framework explicitly identifies authentication and authorization as platform-core responsibilities.

The platform architecture also establishes Supabase/PostgreSQL as the data layer and identifies audit logs and clinical metadata as persistent platform data.

All clinical requests pass through the FastAPI backend (`/api/v1/...`), where authentication, request identification and audit processing occur before clinical services execute.

Therefore, the identity and tenant model defined here must support:

* authenticated users;
* hospital-scoped authorization;
* hospital administration;
* clinical-data isolation;
* auditability;
* role assignment;
* professional lifecycle management;
* future transfer between hospitals;
* backend enforcement;
* database-level defence in depth.

---

# 3. Phase 16A Decisions Carried Forward

Phase 16B inherits the following decisions from Phase 16A.

### 3.1 Hospital is the tenant

Each hospital/organisation represents an independent PharmaTrybe tenant.

```text
Hospital / Organisation
    ↓
Tenant boundary
    ↓
Hospital-scoped users
    ↓
Hospital-scoped clinical data
```

---

### 3.2 One professional → one active hospital

A health professional may have **only one active hospital membership at any given time** (0 or 1 active memberships).

This is a deliberate PharmaTrybe architectural decision.

It does **not** claim that real-world healthcare identity systems universally restrict professionals to one organisation.

Healthcare identity systems can support multiple organisational associations. PharmaTrybe deliberately adopts a simpler cardinality for the first implementation.

---

### 3.3 Professionals cannot self-join hospitals

A professional cannot independently select or modify their hospital affiliation.

Hospital membership must be established through an authorised hospital onboarding process.

---

### 3.4 Hospital administrators control onboarding

Hospital administrators are responsible for inviting and onboarding professionals into their hospital.

---

### 3.5 Authentication and membership are separate concepts

The authenticated identity establishes **who the person is**.

Hospital membership establishes **which tenant the person currently belongs to**.

Role assignment establishes **what that person can do within that tenant**.

Therefore:

```text
Authentication Identity
        ↓
Professional Profile
        ↓
Hospital Membership
        ↓
Hospital Role
        ↓
Permissions
```

---

### 3.6 Hospital membership is a security boundary

`hospital_id` is not merely profile information.

It represents the tenant boundary used when determining access to hospital-owned resources.

Clinical data must never be returned solely because a user is authenticated.

The request must also satisfy the user's active hospital scope.

---

### 3.7 Transfer preserves person identity

When a professional moves from Hospital A to Hospital B, the underlying person/authentication identity is preserved.

The previous membership is terminated and a new membership is established.

```text
Same authenticated identity
          │
          ├── Hospital A membership → DEACTIVATED / TRANSFERRED
          │
          └── Hospital B membership → ACTIVE
```

---

# 4. Core Identity Model

The proposed identity hierarchy is:

```text
┌──────────────────────────┐
│ Supabase Auth Identity   │
│ auth.users.id (UUID)     │
└────────────┬─────────────┘
             │
             │ 1 : 1
             ▼
┌──────────────────────────┐
│ Professional Profile     │
│ public.professional_     │
│ profiles                 │
└────────────┬─────────────┘
             │
             │ 1 : many historical
             │ memberships
             │
             ▼
┌──────────────────────────┐
│ Hospital Membership      │
│ hospital_memberships    │
└────────────┬─────────────┘
             │
             │ many : 1
             ▼
┌──────────────────────────┐
│ Hospital / Organisation  │
│ hospitals                │
└──────────────────────────┘
```

The important distinction is:

> A professional may have multiple **historical membership records**, but only one membership may be **active** at a time.

This allows transfer history to be retained without allowing simultaneous cross-hospital access.

---

# 5. Authentication Identity

## 5.1 Source of authentication identity

Supabase Auth is the candidate authentication provider for PharmaTrybe.

Supabase Auth maintains authenticated users in its `auth` schema and exposes the user's UUID through the authentication system. Application-owned tables can reference the stable `auth.users.id` primary key.

The PharmaTrybe application should therefore **not duplicate authentication credentials** in its own user table.

PharmaTrybe should not store:

* password hashes;
* authentication tokens;
* refresh tokens;
* authentication-provider credentials.

Those remain responsibilities of the authentication layer.

---

## 5.2 Application identity

PharmaTrybe requires application-owned identity information in addition to the authentication identity.

Therefore:

```text
auth.users
    │
    │ user UUID
    ▼
professional_profiles
```

The application profile should reference the authentication user rather than recreate authentication.

---

# 6. Proposed Core Entities

Phase 16B defines the following core entities.

| Entity | Purpose |
|---|---|
| `auth.users` | Authentication identity managed by Supabase |
| `professional_profiles` | PharmaTrybe professional identity/profile |
| `hospitals` | Tenant/organisation entity |
| `hospital_memberships` | Professional ↔ hospital relationship |
| `roles` | Available application roles |
| `membership_roles` | Role assignment within a hospital membership |
| `hospital_invitations` | Controlled onboarding mechanism |
| `membership_events` | Membership lifecycle and transfer history |
| `audit_events` | Security and application audit trail |

These entities are deliberately separated rather than placing all information into a single `users` table.

---

# 7. Entity: `auth.users`

This entity is managed by Supabase Auth.

It represents the authenticated account.

Conceptually:

```text
auth.users
──────────
id (UUID)
email
phone
authentication metadata
account timestamps
```

The exact Supabase-managed schema must not be treated as PharmaTrybe-owned application schema.

### Architectural rule

PharmaTrybe application logic should treat:

```text
auth.users.id
```

as the stable authentication identity key.

---

# 8. Entity: `professional_profiles`

The professional profile represents the person within PharmaTrybe.

### Purpose

It contains professional information that is not authentication data.

Conceptual structure:

```text
professional_profiles

id (UUID)
auth_user_id (UUID -> auth.users.id)
first_name
last_name
professional_type
professional_registration_number
phone
profile_status
created_at
updated_at
```

### Important boundary

The professional profile must **not** be used as the primary tenant-security mechanism.

In particular:

```text
professional_profiles.hospital_id
```

should **not** be the authoritative representation of hospital membership.

The hospital relationship belongs in the membership model.

---

# 9. Why Membership Must Be a Separate Entity

A simple model such as storing `hospital_id` directly on the profile would create problems with:

* historical transfers;
* invitation lifecycle;
* suspension;
* deactivation;
* auditability;
* role changes;
* future membership history;
* enforcing the active-membership rule.

The membership entity provides a durable relationship:

```text
Professional
     │
     ├── Membership A → Hospital A → DEACTIVATED
     │
     └── Membership B → Hospital B → ACTIVE
```

Therefore:

> **Hospital affiliation is represented by membership, not by a mutable profile attribute.**

---

# 10. Entity: `hospitals`

A hospital represents a PharmaTrybe tenant/organisation.

Conceptual structure:

```text
hospitals

id (UUID)
name
legal_name
hospital_code
status
contact_information
created_at
updated_at
```

### Tenant identifier

The hospital primary key becomes the tenant identifier used throughout hospital-owned application data.

Conceptually:

```text
hospital_id
```

should be present on tenant-owned resources.

Examples include future:

* patients;
* clinical cases;
* recommendations;
* audit records;
* hospital guidelines;
* stewardship policies;
* workflows;
* hospital-specific plugins/configuration.

---

# 11. Entity: `hospital_memberships`

This is the central entity of the Phase 16B identity model.

Conceptual structure:

```text
hospital_memberships

id (UUID)
professional_id (UUID -> professional_profiles.id)
hospital_id (UUID -> hospitals.id)
status
joined_at
activated_at
suspended_at
deactivated_at
ended_at
created_at
updated_at
```

### Membership statuses

The initial lifecycle vocabulary is:

```text
INVITED
ACTIVATED
ACTIVE
SUSPENDED
DEACTIVATED
TRANSFERRED
```

---

# 12. Active Membership Constraint

The most important database invariant is:

> A professional must not have more than one active hospital membership at the same time.

Historical memberships are allowed. Simultaneous active memberships are not.

---

# 13. Database Enforcement of Active-Membership Uniqueness

The one-active-membership rule must not depend exclusively on application code.

PostgreSQL supports partial unique indexes, which can enforce uniqueness only among rows satisfying a predicate.

Therefore, the eventual implementation should enforce an invariant conceptually equivalent to:

```sql
CREATE UNIQUE INDEX idx_unique_active_membership 
ON hospital_memberships (professional_id) 
WHERE status = 'ACTIVE';
```

### Architectural invariant

```text
MAX(active_memberships per professional) = 1
```

---

# 14. Hospital Membership and Tenant Scope

The authenticated request should resolve the user's active membership:

```text
JWT / authenticated identity
          ↓
auth_user_id
          ↓
professional_profile
          ↓
ACTIVE hospital_membership
          ↓
hospital_id
          ↓
tenant context
```

The resolved tenant context then becomes part of the backend request context:

```text
RequestContext

user_id
professional_id
hospital_id
membership_id
role(s)
request_id
```

The clinical request must be evaluated using this context.

---

# 15. Hospital ID Must Never Come From the Client as Authority

A client may submit a `hospital_id` in future workflows, but that value must never become the authoritative security context.

For protected clinical operations:

```text
Authenticated identity
        ↓
Server resolves active membership
        ↓
Server determines hospital_id
        ↓
Server authorizes request
```

---

# 16. Roles Belong to Membership Context

A role should not be treated as a universal property of the authenticated identity.

The authorization model is:

```text
Professional
     ↓
Hospital Membership
     ↓
Role
     ↓
Permissions
```

---

# 17. Entity: `membership_roles`

```text
membership_roles

id (UUID)
membership_id (UUID -> hospital_memberships.id)
role_id (UUID -> roles.id)
assigned_by
assigned_at
revoked_at
status
```

---

# 18. Entity: `hospital_invitations`

Professional onboarding requires an explicit invitation mechanism:

```text
hospital_invitations

id (UUID)
hospital_id (UUID -> hospitals.id)
invited_email
invited_professional_id
invited_by
role
status
expires_at
accepted_at
created_at
```

---

# 19. Entity: `membership_events`

```text
membership_events

id (UUID)
membership_id (UUID -> hospital_memberships.id)
event_type
performed_by
previous_status
new_status
reason
metadata
created_at
```

---

# 20. Global Knowledge vs Tenant Clinical Data

WHO guideline entities, evidence catalogs, and drug data remain **global knowledge** entities without tenant scoping.

Tenant-owned clinical data (cases, recommendations, patient records, local audit logs) must have explicit `hospital_id` tenant keys.

```text
GLOBAL KNOWLEDGE (WHO Diseases, AWaRe Drugs, Guidelines)
    ├── Unscoped / Shared across all tenants

TENANT DATA (Cases, Recommendations, Audits, Local Policies)
    ├── Bound to hospital_id (UUID)
```

---

# 21. Summary of Invariants

1. Every professional profile references exactly one authenticated identity (`auth.users.id`).
2. A professional may have zero or one active hospital membership.
3. Historical memberships may exist.
4. A professional cannot self-change their hospital affiliation.
5. Hospital membership determines tenant scope.
6. Hospital roles are scoped to memberships.
7. Authentication alone does not grant hospital access.
8. Historical membership does not grant current access.
9. Hospital administrators operate within their own hospital scope.
10. Tenant-owned clinical data must have an enforceable hospital boundary.
11. Backend authorization is authoritative (`FastAPI /api/v1/...`).
12. Database-level authorization (PostgreSQL / RLS) provides defence in depth.
13. Membership transitions must be auditable.

---

# 22. Status

**PHASE 16B — DATABASE SCHEMA DESIGN DEFINED**

**Implementation status:** Not started (schema specification only)

**Parent decision:** `PHASE_16A_IDENTITY_TENANT_ARCHITECTURE_DECISION.md`

**Next Phase:** `PHASE_16C_ROLE_PERMISSION_MATRIX.md`
