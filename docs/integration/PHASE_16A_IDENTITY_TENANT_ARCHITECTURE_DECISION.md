# Phase 16A — Identity & Tenant Architecture Decision

**Project:** PharmaTrybe / AMR Explainable Clinical Decision Support System  
**Phase:** 16A  
**Document type:** Architecture Decision  
**Status:** APPROVED FOR IMPLEMENTATION BASELINE — R8-RELEVANT DECISIONS
**Date:** 2026-08-19  
**Predecessor:** `docs/integration/PHASE_16_AUTH_SUPABASE_AUDIT.md`  

**Approval Authority:** `docs/integration/approved_integration_docs.md` explicitly approves the Phase 16 identity, authentication, hybrid organisation-context, backend-authority, and one-active-membership baseline. Any decision in this document not covered by that approval remains unresolved and is not authorized by this clarification.

---

## 1. Purpose

This document defines the proposed identity, authentication, organisation, tenancy, RBAC, JWT, and database-security architecture for PharmaTrybe.

It is a **decision document, not an implementation document**.

No authentication routes, Supabase resources, migrations, database schemas, frontend authentication changes, or backend authorization changes should be implemented from this document until the decisions marked **Requires Approval** have been reviewed and accepted.

The purpose is to establish a stable architectural boundary so that subsequent implementation is deterministic and does not allow individual application components or coding agents to invent security-critical behaviour.

---

# 2. Architectural Principles

The following principles govern the Phase 16A decisions.

## 2.1 Clinical authority remains with the backend

Authentication infrastructure must not become the clinical decision engine.

Supabase may provide identity and session infrastructure, but clinical application rules remain under FastAPI.

The backend remains responsible for:

* clinical authorization;
* clinical-case access;
* recommendation generation;
* stewardship rules;
* evidence integration;
* explainability;
* safety controls;
* audit-worthy clinical operations.

---

## 2.2 The frontend is never an authorization authority

Frontend roles, permissions, route guards, Zustand state, and UI visibility are presentation mechanisms.

They must never be treated as proof that a user is authorised to perform an operation.

The backend must independently establish:

1. who the caller is;
2. whether the account is active;
3. which organisation or organisations the caller belongs to;
4. which role applies within the target organisation;
5. whether that role permits the requested operation;
6. whether the target resource belongs to an organisation the caller may access.

---

## 2.3 Authentication and application authorization are separate concerns

The proposed separation is:

```text
Supabase Auth
    |
    | identity + authentication + session
    v
JWT access token
    |
    v
FastAPI authentication boundary
    |
    | identity + membership + role
    v
FastAPI authorization boundary
    |
    | clinical/application permissions
    v
Clinical APIs / administrative APIs
    |
    v
PostgreSQL
```

Supabase Auth is therefore proposed as the identity authority, while FastAPI remains the application authority.

Supabase Auth uses JWT-based authentication and integrates with PostgreSQL/RLS, making this architecture technically compatible with the proposed boundary.

---

# 3. Decision 1 — Identity Provider

## Proposed decision

**Use Supabase Auth as the authentication and session authority.**

Supabase Auth should own:

* account creation;
* email/password authentication;
* email verification;
* password recovery;
* session issuance;
* access-token issuance;
* refresh-token lifecycle;
* session termination;
* MFA capability;
* authentication assurance.

FastAPI should not independently issue a second application JWT.

### Rationale

The current repository contains custom JWT verification scaffolding but no authentication lifecycle. Maintaining a second token-issuing system would introduce unnecessary duplication.

Supabase Auth already provides JWT-based authentication, session management, and authentication APIs.

### Explicit boundary

```text
Supabase:
    "Who is this user?"

FastAPI:
    "What is this authenticated user allowed to do here?"

Clinical domain:
    "What should be recommended for this clinical case?"
```

These responsibilities must remain separate.

---

# 4. Decision 2 — FastAPI Authentication Boundary

## Proposed decision

FastAPI will accept the Supabase access token as a Bearer token.

The backend authentication dependency will:

1. extract the Bearer token;
2. validate the JWT signature;
3. validate issuer;
4. validate audience;
5. validate expiry;
6. identify the subject/user ID;
7. establish authentication assurance where required;
8. resolve the application identity;
9. resolve organisation membership;
10. expose the authenticated context to downstream authorization.

Supabase JWTs include claims such as `iss`, `aud`, `exp`, `iat`, `sub`, `role`, `aal`, and `session_id`.

The existing custom JWT scaffold should therefore be treated as **replaceable implementation scaffolding**, not as the final token contract.

## Important constraint

The application must not rely on a locally generated JWT secret such as the current placeholder `change-me`.

The final implementation must use the approved Supabase signing-key/JWKS verification mechanism or an equivalent supported verification mechanism.

Supabase documents JWT signing keys and recommends established verification libraries rather than implementing JWT cryptography manually.

---

# 5. Decision 3 — Canonical User Identity

The canonical identity identifier will be the Supabase Auth user UUID.

Conceptually:

```text
auth.users.id
        |
        v
application profile
        |
        v
organisation memberships
```

The application should not create a second unrelated authentication identifier.

Application profile information may be stored separately from the Auth record.

## Proposed separation

```text
Supabase Auth
    auth.users
        |
        +---- application profile
        |
        +---- organisation memberships
```

The application's profile table should contain application-specific information rather than duplicating authentication credentials.

---

# 6. Decision 4 — Organisation Model

## Proposed decision

PharmaTrybe will use an explicit **organisation** model.

An organisation represents the hospital, healthcare institution, or authorised institutional tenant using the CDSS.

The architecture should not encode organisation identity as a free-text field such as:

```text
organization = "Hospital A"
```

Instead, organisation identity must be represented by a stable UUID foreign key (`organisation_id` / `hospital_id`).

## Conceptual model

```text
Organisation (Hospital)
    |
    +---- Membership
    |       |
    |       +---- User
    |
    +---- Clinical Cases
    |
    +---- Recommendations
    |
    +---- Audit Events
    |
    +---- Future prediction/surveillance records
```

---

# 7. Decision 5 — Membership Model

## Proposed decision

Users will belong to organisations through an explicit membership entity.

Conceptually:

```text
User
  |
  +---- Membership ---- Organisation (Hospital)
```

This is preferred over storing a single `organisation_id` directly on the user because the project may eventually require:

* multiple organisational memberships;
* temporary memberships;
* different roles in different organisations;
* invitation workflows;
* membership suspension;
* membership history;
* organisation-specific permissions.

## Proposed membership attributes

The eventual model should support, at minimum:

```text
membership_id
user_id
organisation_id (hospital_id)
role
status
created_at
updated_at
invited_by
```

Additional fields may be introduced only after the implementation design is approved.

---

# 8. Decision 6 — Organisation Ownership of Clinical Data

## Proposed decision

Clinical data that is institution-owned must have an explicit organisation ownership boundary.

At minimum, this applies to:

* clinical cases;
* patient-associated clinical records;
* recommendations;
* clinical review records;
* audit events;
* future SOAR surveillance records;
* future ARMD prediction records;
* other institution-generated clinical artefacts.

The ownership path should be deterministic.

For example:

```text
organisation (hospital)
    |
    +---- clinical_case
              |
              +---- recommendation
```

A user should not gain access to a clinical case merely because they know its UUID.

---

# 9. Global Knowledge vs Tenant Data

Not all data should be organisation-scoped.

The project's evidence and knowledge-base architecture distinguishes between shared clinical knowledge and institution-generated clinical data.

## Global/shared knowledge

Examples:

* WHO disease knowledge;
* antimicrobial knowledge;
* guideline evidence;
* pathogens;
* diagnostic guidance;
* stewardship knowledge.

These are **knowledge-base resources**, not hospital-owned records.

## Organisation-owned data

Examples:

* clinical cases;
* patient-linked records;
* recommendations generated for cases;
* clinical reviews;
* institution-specific audit events;
* institution-specific surveillance data.

The architecture must therefore distinguish:

```text
GLOBAL KNOWLEDGE
        |
        +---- shared clinical evidence

TENANT DATA
        |
        +---- organisation (hospital)
                 |
                 +---- clinical records
                 +---- operational records
```

This distinction is important because applying tenant isolation indiscriminately to global knowledge would be incorrect, while failing to tenant-isolate clinical records would be unsafe.

---

# 10. Decision 7 — Role Taxonomy

The Phase 16 audit identified a mismatch between frontend and backend role vocabularies.

### Frontend vocabulary

* Infectious Disease Specialist
* General Practitioner
* Pharmacist
* Admin
* Researcher

### Backend scaffold vocabulary

* Clinician
* Laboratory Scientist
* Stewardship Team
* Administrator

These vocabularies must **not** be silently merged.

## Proposed decision

Create a canonical application role taxonomy before implementation.

The role taxonomy should distinguish:

1. clinical function;
2. stewardship function;
3. laboratory function;
4. administration;
5. research/read-only access.

The final canonical role names must be approved before database migrations and authorization code are written.

### Requires Approval

**The exact canonical role list is still an approval decision.**

No implementation should invent a mapping such as:

```text
Infectious Disease Specialist -> Clinician
```

without explicitly recording that mapping as an approved project decision.

---

# 11. Decision 8 — RBAC Authority

## Proposed decision

RBAC enforcement belongs to the backend application boundary.

The frontend may maintain a corresponding permission map for UI purposes, but that map is not authoritative.

The enforcement sequence should conceptually be:

```text
Authenticated user
       |
       v
Organisation membership
       |
       v
Canonical role
       |
       v
Permission
       |
       v
Resource ownership
       |
       v
Allowed / denied
```

A role alone must not be sufficient to access an arbitrary resource.

For example:

```text
ROLE = clinician
```

does not imply:

```text
CAN_ACCESS_ANY_CLINICAL_CASE = true
```

The organisation/resource boundary must also be checked.

---

# 12. Decision 9 — Permission Model

The permission system should use explicit application permissions rather than embedding authorization logic directly into individual route handlers.

Conceptually:

```text
Role
   |
   +---- Permission
             |
             +---- Operation
             +---- Resource
```

Examples of eventual permissions may include:

```text
clinical_case.read
clinical_case.create
clinical_case.update

recommendation.generate
recommendation.read
recommendation.review

knowledge.read

stewardship.read

admin.user.read
admin.user.create
admin.user.update

audit.read
```

This document does **not** approve the final permission catalogue.

The catalogue must be defined in the implementation phase after the role taxonomy is approved.

---

# 13. Decision 10 — JWT Claims

## Proposed decision

The application should distinguish between:

### Trusted identity claims

Examples:

```text
sub
iss
aud
exp
iat
session_id
aal
```

These originate from the authentication authority.

### Application authorization claims

Potentially:

```text
organisation context
application role
```

These must be populated only through an authoritative server-side mechanism.

Supabase supports custom access-token claims through an access-token hook and documents using custom claims for RBAC.

## Important restriction

Authorization data must not be taken from user-editable metadata.

Supabase specifically warns that user metadata can be modified by authenticated users and should not be used as authorization data; application metadata is intended for authorization-related information.

Therefore:

```text
user_metadata
    X
    not an authorization authority

authoritative membership/role data
    |
    +---- approved token claims
    |
    +---- backend authorization lookup
```

---

# 14. Organisation Claims vs Database Lookup

### Requires Approval

The architecture must decide whether organisation membership is:

### Option A — Token-derived

The access token contains the relevant organisation/role context.

### Option B — Backend-resolved

The JWT identifies the user and FastAPI resolves the active organisation membership from the database.

### Option C — Hybrid

The JWT contains a limited trusted role/context claim while FastAPI verifies the current membership and resource ownership against the database.

## Recommended direction

**Hybrid is the preferred architecture for consideration.**

The token establishes identity and trusted authentication context.

FastAPI remains responsible for verifying the current application membership and resource authorization.

This avoids making long-lived application authorization assumptions entirely dependent on token contents.

---

# 15. Decision 11 — Row Level Security

## Proposed decision

PostgreSQL Row Level Security should be treated as **defence-in-depth for tenant-owned data**, not as a replacement for FastAPI authorization.

The intended boundary is:

```text
Frontend
   |
   v
FastAPI authorization
   |
   v
Database ownership constraints
   |
   v
RLS defence-in-depth where applicable
```

---

# 16. RLS Authority Decision

### Proposed position

RLS should protect against accidental or unexpected cross-tenant database access.

However, FastAPI remains the primary application authorization layer for clinical APIs.

Therefore:

```text
FastAPI authorization
    = application authority

RLS
    = database safety boundary / defence-in-depth
```

This avoids coupling the entire clinical authorization model directly to Supabase's generated database API.

### Requires Approval

The final implementation must determine exactly which tables are directly exposed through Supabase APIs and therefore require RLS policies for direct client access.

No RLS policy should be created during Phase 16A.

---

# 17. Decision 12 — Direct Supabase Data Access

## Proposed decision

The frontend should **not directly access sensitive clinical tables through Supabase's generated database API** unless a separate architecture decision explicitly approves that boundary.

The existing project architecture places clinical application logic behind FastAPI.

Therefore:

```text
Vite + React
  |
  v
FastAPI (/api/v1/...)
  |
  v
PostgreSQL
```

is the default clinical data path.

Supabase Auth may be accessed by the frontend for authentication/session operations, but that does not imply that the frontend should directly query clinical tables.

---

# 18. Decision 13 — FastAPI Remains Clinical Authority

FastAPI remains responsible for:

* clinical-case validation;
* clinical authorization;
* evidence retrieval;
* clinical rules;
* stewardship constraints;
* recommendation orchestration;
* explainability;
* audit-worthy clinical actions.

Supabase must not become a substitute for the CDSS clinical architecture.

This preserves the project's established principle:

> Evidence and structured clinical knowledge precede AI prediction, and the system supports rather than replaces clinician judgement.

---

# 19. Decision 14 — Authentication Lifecycle

The approved target lifecycle should conceptually be:

```text
Registration
    |
    v
Organisation creation / invitation
    |
    v
User account
    |
    v
Email verification
    |
    v
Authentication
    |
    v
Supabase session
    |
    v
JWT access token
    |
    v
FastAPI authentication
    |
    v
Membership + RBAC
    |
    v
Clinical application
```

Required lifecycle capabilities include:

* registration;
* hospital/organisation onboarding;
* email verification;
* login;
* session restoration;
* access-token refresh;
* logout;
* password recovery;
* account activation/deactivation;
* invitation;
* membership management.

The exact API contract is a subsequent implementation decision.

---

# 20. Decision 15 — Hospital Registration

Hospital registration must not simply create a user.

The organisation and its initial administrative membership must be treated as one controlled onboarding operation.

Conceptually:

```text
Register organisation (hospital)
        |
        +---- create organisation
        |
        +---- create/associate initial user
        |
        +---- create administrator membership
        |
        +---- establish account status
        |
        +---- establish audit event
```

The exact transaction boundary must be defined during implementation.

No registration endpoint should be implemented until this transaction model is approved.

---

# 21. Decision 16 — User Invitations and Provisioning

Administrative user provisioning should use an organisation membership workflow rather than arbitrary direct assignment.

Conceptually:

```text
Administrator
      |
      v
Invitation
      |
      v
User accepts
      |
      v
Membership activated
      |
      v
Role enforced
```

This supports:

* invited-by lineage;
* organisation membership;
* role assignment;
* account status;
* auditability.

Temporary passwords should not be generated by the frontend.

---

# 22. Decision 17 — Account Status

The application should distinguish authentication identity from application account status.

Potential status values include:

```text
active
invited
suspended
deactivated
```

The final enumeration requires approval.

An authenticated Supabase user must not automatically imply an active PharmaTrybe clinical account.

The backend must therefore verify application-level account/membership status before allowing protected clinical operations.

---

# 23. Decision 18 — Audit Logging

Authentication and administrative operations must generate durable audit records.

At minimum, the architecture should support auditing:

* registration;
* invitation;
* membership changes;
* role changes;
* account activation/deactivation;
* login/security events where required;
* administrative changes;
* clinical review operations;
* sensitive clinical access where required.

Audit records should be:

* attributable;
* timestamped;
* organisation-aware where appropriate;
* immutable after creation;
* queryable by authorised administrators;
* retained according to approved policy.

The current Pydantic audit model is **not sufficient evidence of persistent audit storage**.

---

# 24. Decision 19 — Last Administrator Protection

The organisation must not be allowed to reach a state with no active administrator unless an explicit recovery process exists.

The future administrative implementation must protect against:

```text
last active administrator
        |
        X
cannot be deactivated/demoted
without replacement
```

This must be enforced server-side and tested at the database/application boundary.

---

# 25. Decision 20 — MFA

### Proposed direction

MFA should be supported by the identity architecture and should be enforceable based on application policy.

Supabase Auth supports MFA and exposes an `aal` claim representing authentication assurance level, including `aal1` and `aal2`.

### Requires Approval

The project must decide whether MFA is:

* required for administrators;
* required for all clinical users;
* required only for sensitive operations;
* optional initially.

No MFA implementation decision is made by this document.

---

# 26. Decision 21 — Clinical Safety and Authorization

Authentication architecture must not weaken the CDSS safety model.

Authorization should determine whether a user may perform an operation.

It must not determine clinical truth.

For example:

```text
Authorization:
    "May this clinician generate a recommendation?"

Clinical decision:
    "What recommendation is supported by the evidence?"
```

These must remain separate.

---

# 27. Decision 22 — Patient Data Boundary

Patient identity and clinical information require additional protection.

The current audit found no verified patient identity model or tenant ownership model.

Therefore the future patient model must not be implemented merely as an extension of the current frontend patient types.

The patient architecture must explicitly establish:

* organisation ownership;
* patient identity;
* case linkage;
* access permissions;
* auditability;
* data minimisation;
* appropriate retention.

This requires a separate approved data-model design.

---

# 28. Decision 23 — Global Knowledge Boundary

WHO and other evidence-based knowledge should remain separate from organisation-owned clinical records.

```text
Knowledge Base
    |
    +---- global/shared

Clinical Data
    |
    +---- organisation-owned
```

The authentication/tenant architecture must not accidentally make global guideline knowledge hospital-specific.

Likewise, organisation-specific clinical records must not become globally readable simply because the knowledge layer is shared.

---

# 29. Decision 24 — Supabase Secrets

The frontend must never receive a Supabase service-role or equivalent privileged secret.

The frontend may use the public/publishable Supabase client configuration required by the chosen Auth architecture.

Privileged server credentials belong only in the backend/server environment.

Supabase's security guidance distinguishes client-accessible credentials from privileged server-side secrets and recommends appropriate production hardening.

---

# 30. Decision 25 — Environment Configuration

The implementation phase must define separate environment contracts for:

### Frontend

```text
VITE_SUPABASE_URL
VITE_SUPABASE_PUBLISHABLE_KEY
```

or the final approved equivalent.

### Backend

```text
SUPABASE_URL
SUPABASE_JWT_ISSUER
SUPABASE_JWT_AUDIENCE
SUPABASE_JWKS_URL
```

or the final approved verification configuration.

Actual secrets must never be committed to the repository.

These names are architectural examples, not yet an approved configuration contract.

---

# 31. Proposed Target Architecture

The resulting target architecture is:

```text
                    ┌─────────────────────┐
                    │     Supabase Auth   │
                    │                     │
                    │ Signup              │
                    │ Login               │
                    │ Verification        │
                    │ Recovery             │
                    │ Sessions             │
                    │ MFA                  │
                    │ JWT issuance         │
                    └──────────┬──────────┘
                               │
                               │ Access Token
                               v
┌──────────────────────────────────────────────────────┐
│                    React Frontend                    │
│                                                      │
│ Auth UI / Session UI / Role presentation             │
│                                                      │
│ NOT an authorization authority                       │
└──────────────────────┬───────────────────────────────┘
                       │ Bearer JWT
                       v
┌──────────────────────────────────────────────────────┐
│                     FastAPI                          │
│                                                      │
│ Authentication                                      │
│        ↓                                             │
│ Identity resolution                                  │
│        ↓                                             │
│ Organisation membership                              │
│        ↓                                             │
│ RBAC / permissions                                   │
│        ↓                                             │
│ Resource ownership                                   │
│        ↓                                             │
│ Clinical services / rules / explainability           │
└──────────────────────┬───────────────────────────────┘
                       │
                       v
┌──────────────────────────────────────────────────────┐
│                    PostgreSQL                        │
│                                                      │
│ Organisations (Hospitals)                            │
│ Users / profiles                                     │
│ Memberships                                          │
│ Clinical cases                                      │
│ Recommendations                                     │
│ Audit events                                         │
│ Knowledge (Global)                                   │
│                                                      │
│ RLS = defence-in-depth where approved                │
└──────────────────────────────────────────────────────┘
```

---

# 32. Dependency Order

Implementation must follow dependency order.

```text
Phase 16A
Identity/Tenant Architecture Decision
        |
        v
Role + Permission Decision
        |
        v
Identity/Data Model Decision
        |
        v
Supabase Project Configuration
        |
        v
Database Migrations
        |
        v
Auth + Membership Services
        |
        v
FastAPI Authentication
        |
        v
FastAPI RBAC
        |
        v
Tenant Ownership Enforcement
        |
        v
RLS / Database Security
        |
        v
Auth API
        |
        v
Admin/Provisioning API
        |
        v
Frontend Session Integration
        |
        v
Protected Clinical APIs
        |
        v
End-to-End Security Tests
```

No downstream implementation should bypass an unresolved upstream decision.

---

# 33. What Copilot Must Not Decide

Once implementation begins, Copilot or another coding agent must not independently decide:

* the canonical role vocabulary;
* organisation semantics;
* tenant ownership;
* JWT trust rules;
* whether a claim is authoritative;
* RLS policy semantics;
* permission definitions;
* admin privileges;
* authentication lifecycle semantics;
* clinical data access rules;
* audit retention;
* MFA policy.

Those decisions must originate from approved project architecture.

Copilot may implement an approved decision.

It must not create the decision.

---

# 34. Implementation Boundary

The following are explicitly **out of scope for Phase 16A**:

```text
NO AUTH ROUTES

NO SUPABASE PROJECT CREATION

NO SUPABASE MIGRATIONS

NO DATABASE MIGRATIONS

NO RLS POLICIES

NO FRONTEND AUTH CHANGES

NO JWT IMPLEMENTATION CHANGES

NO RBAC IMPLEMENTATION

NO ORGANISATION TABLES

NO MEMBERSHIP TABLES

NO USER PROVISIONING

NO PASSWORD FLOW

NO MFA FLOW

NO CLINICAL API CHANGES
```

Phase 16A establishes architecture only.

---

# 35. Required Approval Decisions

Before implementation proceeds, the following decisions require explicit project approval.

| Decision                                                | Status                                |
| ------------------------------------------------------- | ------------------------------------- |
| Supabase Auth as identity authority                     | **Proposed**                          |
| FastAPI as application/clinical authorization authority | **Proposed**                          |
| Supabase JWT as authentication token                    | **Proposed**                          |
| Organisation as explicit tenant                         | **Proposed**                          |
| Membership entity between user and organisation         | **Proposed**                          |
| Explicit organisation ownership of tenant clinical data | **Proposed**                          |
| Frontend is never an authorization authority            | **Confirmed architectural principle** |
| FastAPI server-side RBAC                                | **Proposed**                          |
| RLS as defence-in-depth                                 | **Proposed**                          |
| Direct frontend access to sensitive clinical tables     | **Not approved**                      |
| Exact canonical roles                                   | **Requires Approval**                 |
| Exact permission catalogue                              | **Requires Approval**                 |
| Single vs multi-organisation membership                 | **Requires Approval**                 |
| Exact JWT custom claims                                 | **Requires Approval**                 |
| Token-derived vs database-resolved organisation context | **Requires Approval**                 |
| MFA policy                                              | **Requires Approval**                 |
| Audit retention policy                                  | **Requires Approval**                 |
| Patient identity/data model                             | **Requires Separate Decision**        |
| Exact Supabase environment contract                     | **Requires Approval**                 |

---

# 36. Decision Gate

Phase 16A is considered complete when the project owner has explicitly approved or rejected the unresolved decisions above.

The implementation phase should then produce, in order:

1. approved identity data model;
2. approved organisation/membership model;
3. approved role and permission matrix;
4. approved JWT claim contract;
5. approved tenant ownership model;
6. approved RLS strategy;
7. approved authentication lifecycle;
8. approved security test matrix.

Only after those artifacts are approved should implementation begin.

---

# 37. Relationship to Existing Project Principles

This architecture preserves the project's established principles.

### Clinician support

Authentication and RBAC determine who may use the system; they do not replace clinical judgement.

### Explainability

Identity architecture does not obscure recommendation provenance or explanation.

### Patient safety

Access control, tenant isolation, and auditability are treated as safety requirements rather than optional infrastructure.

### Evidence before AI

Supabase authentication has no authority over evidence or clinical recommendations.

### Separation of concerns

```text
Identity
    ≠
Application authorization
    ≠
Clinical rules
    ≠
Machine learning
    ≠
Knowledge base
```

### Reproducibility

Security decisions are documented before implementation.

### Incremental development

Architecture precedes migrations; migrations precede protected routes; protected routes precede frontend activation.

---

# 38. Final Architecture Position

The proposed Phase 16A architecture is:

```text
SUPABASE AUTH
    |
    | authentication / sessions / JWT
    v
FASTAPI (/api/v1/...)
    |
    | identity resolution
    | organisation membership
    | RBAC
    | resource authorization
    | clinical authority
    v
POSTGRESQL
    |
    | tenant-owned data
    | global knowledge
    | audit records
    |
    +---- RLS where explicitly approved
```

The frontend remains a client of this architecture rather than an authority within it.

The central security rule is:

> **A user's presence in the frontend is never evidence that the user is authorised to access or modify clinical data.**

The central architectural rule is:

> **Supabase may establish identity; PharmaTrybe/FastAPI establishes application and clinical authority.**

The central project-governance rule is:

> **No coding agent may invent unresolved authentication, tenancy, RBAC, JWT, or RLS decisions during implementation.**

---

# 39. Status

**PHASE 16A — ARCHITECTURE DECISION DOCUMENT CREATED**

**Implementation status:** Not started

**Approval status:** Pending project-owner approval

**Next implementation gate:** Identity + Organisation + Membership + RBAC decision approval

**No code changes are authorised by this document.**
