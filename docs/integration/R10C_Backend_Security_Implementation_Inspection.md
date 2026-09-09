# 10C — Backend Security Implementation Inspection

**Document Type:** Implementation Inspection Specification
**Status:** Ready for execution and approved
**Phase:** 10C — Backend Security
**Scope:** Inspection only — no implementation changes
**Purpose:** Establish the actual implementation state of backend authentication, execution identity, tenant context, RBAC, protected API enforcement, and security tests before implementing 10C.1–10C.6.

---

## 1. Purpose

This document defines the inspection procedure for the existing PharmaTrybe backend before implementing the 10C security architecture.

The inspection must determine what already exists, what is partially implemented, what is missing, and what requires modification.

The inspection **must not introduce a new security model**.

It must validate the existing backend against the already-defined 10C architecture:

```text
10C.1 Authentication Boundary
        ↓
10C.2 Execution Identity
        ↓
10C.3 Tenant Context
        ↓
10C.4 Backend RBAC
        ↓
10C.5 Protected API Enforcement
        ↓
10C.6 Backend Security Tests
```

The inspection is therefore an **implementation-state assessment**, not a redesign.

---

# 2. Architectural Basis

The inspection must preserve the established PharmaTrybe architecture.

The platform architecture identifies Authentication and Authorization as responsibilities of the platform core. 

The API layer is FastAPI, with request validation, request context, and backend routing responsibilities. 

The data-flow architecture also establishes that clinical requests pass through the FastAPI backend and that FastAPI authenticates the user before continuing the request lifecycle. 

Therefore the security boundary being inspected is:

```text
Client
  │
  │ HTTP + Bearer Token
  ▼
FastAPI
  │
  ├── Authentication
  ├── Execution Identity
  ├── Tenant Context
  ├── RBAC
  ├── API Authorization
  │
  ▼
Application Services
  │
  ▼
Database / Plugins / Clinical Engines
```

---

# 3. Inspection Principles

The inspection must follow these rules.

### 3.1 Read Before Modifying

No implementation file should be changed during this inspection.

The inspection must first establish the current state.

---

### 3.2 Existing Architecture Takes Precedence

The inspection must use the already-defined:

* authentication architecture;
* identity model;
* tenant model;
* role model;
* permission model;
* API architecture;
* database relationships.

It must not invent alternative mechanisms.

---

### 3.3 Database RBAC Is Authoritative

The existing RBAC relationship is:

```text
hospital_memberships
        │
        │ membership_id
        ▼
membership_roles
        │
        │ role_id
        ▼
roles
        │
        │ role_id
        ▼
role_permissions
        │
        │ permission_id
        ▼
permissions
```

The inspection must verify that backend authorization follows this structure.

---

### 3.4 Fail-Closed

The inspection must specifically identify any location where:

```text
authentication failure
        ↓
continues execution
```

or:

```text
missing membership
        ↓
continues execution
```

or:

```text
missing permission
        ↓
continues execution
```

is possible.

---

### 3.5 No Frontend Authority

Frontend role or permission information must not be treated as authoritative.

The backend must derive authorization from authenticated identity and backend/database state.

---

# 4. Inspection Objectives

The inspection must answer six primary questions.

| Area               | Question                                                                    |
| ------------------ | --------------------------------------------------------------------------- |
| Authentication     | How does the backend establish that a request is authenticated?             |
| Execution Identity | How does the backend determine which professional is executing the request? |
| Tenant Context     | How does the backend determine the authoritative hospital?                  |
| RBAC               | How are roles and permissions resolved?                                     |
| API Enforcement    | Which endpoints actually enforce authorization?                             |
| Security Tests     | Which security properties are already tested?                               |

---

# 5. Backend Repository Inspection

Inspect the complete backend structure beginning with:

```text
apps/api/
```

Particular attention must be given to:

```text
apps/api/app/
apps/api/tests/
```

The platform architecture identifies the FastAPI application and backend test suite as the implementation locations. 

---

## 5.1 Application Bootstrap

Inspect:

```text
apps/api/app/main.py
```

Determine:

* FastAPI application creation;
* middleware;
* dependency registration;
* exception handlers;
* authentication middleware;
* request context middleware;
* router registration;
* API versioning;
* global security dependencies.

Record whether authentication is:

```text
GLOBAL
ROUTER-LEVEL
ENDPOINT-LEVEL
MIXED
MISSING
```

---

# 6. Authentication Boundary Inspection

## 6.1 Locate Authentication Implementation

Search the backend for:

```text
supabase
auth
get_user
get_session
access_token
bearer
authorization
jwt
token
current_user
authenticated
```

Identify all authentication-related files.

---

## 6.2 Determine Authentication Flow

Document the actual flow.

Expected architectural target:

```text
HTTP Request
     │
     ▼
Authorization Header
     │
     ▼
Bearer Token
     │
     ▼
Supabase Auth Verification
     │
     ▼
Authenticated User
```

Determine whether the implementation actually performs this sequence.

---

## 6.3 Authentication Inspection Questions

Answer:

1. Is a Bearer token required?
2. Where is the token extracted?
3. How is the token verified?
4. Is Supabase Auth authoritative?
5. Is token expiration checked?
6. Is invalid authentication rejected with `401`?
7. Is missing authentication rejected with `401`?
8. Can an endpoint execute without authentication?
9. Are service-role credentials ever exposed to request clients?
10. Are authentication failures logged appropriately?

---

## 6.4 Authentication Result

Classify the implementation as:

```text
PASS
PARTIAL
MISSING
INCONSISTENT
UNSAFE
```

---

# 7. Execution Identity Inspection

The next inspection boundary is:

```text
Authenticated User
        ↓
Professional
        ↓
Hospital Membership
        ↓
Execution Identity
```

Inspect the existing identity implementation.

Search for:

```text
professional
hospital_membership
membership
user_id
auth_user_id
profile
identity
current_user
```

---

## 7.1 Verify Identity Resolution

Determine how:

```text
auth.users.id
```

maps to the application's professional identity.

Document the actual database path.

For example:

```text
Supabase Auth User
        ↓
professional
        ↓
hospital_membership
```

Do not assume this path unless it exists in the implementation.

---

## 7.2 Membership Resolution

Determine:

* how active membership is identified;
* whether membership status is checked;
* whether inactive/suspended memberships are rejected;
* whether exactly one active hospital membership is enforced;
* whether membership is loaded for every protected request or only selected endpoints.

---

## 7.3 Execution Identity Object

Determine whether the backend already has an equivalent of:

```python
ExecutionIdentity
```

If it exists, inspect:

* fields;
* construction;
* validation;
* lifetime;
* dependency injection;
* usage by downstream services.

If it does not exist, record:

```text
MISSING — implementation required under 10C.2
```

Do not create it during inspection.

---

# 8. Tenant Context Inspection

Tenant context must be derived from authenticated execution identity.

Target architecture:

```text
Authenticated User
        ↓
Execution Identity
        ↓
Active Hospital Membership
        ↓
hospital_id
        ↓
Tenant Context
```

---

## 8.1 Search

Inspect for:

```text
hospital_id
tenant_id
tenant
hospital
membership
organization
```

---

## 8.2 Determine Tenant Authority

For every protected endpoint inspected, determine whether `hospital_id` comes from:

### A

```text
Authenticated Membership
```

### B

```text
JWT Claim
```

### C

```text
Request Body
```

### D

```text
URL Parameter
```

### E

```text
Query Parameter
```

### F

```text
Frontend State
```

The desired authoritative source is the backend-resolved active membership.

---

## 8.3 Client-Supplied Tenant Test

Identify endpoints accepting:

```json
{
  "hospital_id": "..."
}
```

or:

```text
/hospitals/{hospital_id}/...
```

Determine whether the supplied value is:

```text
validated against execution identity
```

or:

```text
trusted directly
```

A client-supplied hospital identifier must not override the authoritative execution tenant.

---

## 8.4 Tenant Result

Classify:

```text
PASS
PARTIAL
MISSING
BYPASS POSSIBLE
```

---

# 9. Backend RBAC Inspection

The RBAC inspection must use the existing role/permission model.

It must not introduce:

```text
new role hierarchy
new permission hierarchy
new authorization framework
new role names
```

---

## 9.1 Existing Roles

Verify the implementation against the actual roles:

```text
HOSPITAL_ADMIN
PHARMACIST
CLINICIAN
INFECTIOUS_DISEASE_SPECIALIST
RESEARCHER
LABORATORY_SCIENTIST
```

These roles are already represented in the current database data.

---

## 9.2 Existing Permission Model

Inspect:

```text
permissions
roles
membership_roles
role_permissions
```

The authorization chain must remain:

```text
membership
   ↓
membership_roles
   ↓
role
   ↓
role_permissions
   ↓
permission
```

---

## 9.3 Permission Resolution

Search for:

```text
has_permission
require_permission
permission
role_permission
membership_roles
role_permissions
```

Determine whether permission checking is:

```text
DATABASE-DRIVEN
HARDCODED
FRONTEND-DRIVEN
MIXED
MISSING
```

---

## 9.4 Actual Permission Codes

The inspection must verify the existing permission codes rather than inventing replacements.

Examples include:

```text
professionals:manage
professionals:view
professionals:invite

roles:assign

patients:create
patients:view

cases:create
cases:view
cases:update

laboratory:create
laboratory:view

recommendations:request
recommendations:view
recommendations:review

stewardship:view
stewardship:manage

guidelines:view
guidelines:manage

hospital:view
hospital:update

workflows:execute
workflows:manage

plugins:view
plugins:configure

audit:view
data:export
```

---

# 10. RBAC Enforcement Inspection

For each protected endpoint determine:

```text
Authentication required?
        ↓
Execution identity required?
        ↓
Tenant context required?
        ↓
Permission required?
        ↓
Resource scope required?
```

Create an endpoint matrix:

| Endpoint   | Auth | Identity | Tenant | Permission | Resource Scope | Status  |
| ---------- | ---: | -------: | -----: | ---------: | -------------: | ------- |
| Endpoint A |    ✓ |        ✓ |      ✓ |          ✓ |              ✓ | PASS    |
| Endpoint B |    ✓ |        ✓ |      ✗ |          ✓ |              ✗ | PARTIAL |
| Endpoint C |    ✓ |        ✗ |      ✗ |          ✗ |              ✗ | FAIL    |

The actual endpoints must be populated from repository inspection.

No endpoint should be invented for this document.

---

# 11. Protected API Enforcement Inspection

Inspect every API router.

The platform baseline identifies FastAPI as the API layer responsible for routing and request handling. 

Search:

```text
APIRouter
@router.get
@router.post
@router.put
@router.patch
@router.delete
Depends
Security
```

Determine how dependencies are attached.

---

## 11.1 Enforcement Patterns

Identify whether the project currently uses:

```python
Depends(get_current_user)
```

or:

```python
Depends(require_authenticated)
```

or:

```python
Depends(require_permission(...))
```

or another existing mechanism.

---

## 11.2 Public vs Protected Routes

Create two inventories:

### Public

Routes intentionally accessible without authentication.

### Protected

Routes requiring authentication and authorization.

Every protected route must have an identifiable enforcement point.

---

# 12. Clinical API Inspection

Particular attention must be given to clinical decision endpoints.

The documented architecture includes clinical recommendation endpoints under the FastAPI backend. 

Inspect:

```text
clinical_decision.py
```

and related routes.

Determine:

* authentication;
* execution identity;
* tenant;
* permissions;
* audit identity;
* downstream service calls.

The clinical pipeline must not execute for an unauthenticated or unauthorized user.

---

# 13. Audit Context Inspection

The data-flow architecture specifies that FastAPI assigns a request ID and records audit information during request processing. 

Inspect:

```text
request_id
audit
clinician
user_id
membership_id
hospital_id
```

Determine whether security events can be associated with:

```text
authenticated user
execution identity
hospital
request
```

---

# 14. Database Security Inspection

Inspect database access patterns.

Search for:

```text
supabase
service_role
anon
RLS
row level security
hospital_id
membership_id
```

Determine:

1. Which database client is used by API requests?
2. Where is the service-role client used?
3. Can request code bypass RLS?
4. Is tenant filtering performed in application code?
5. Is tenant isolation additionally enforced by database policies?
6. Are role/permission tables readable only through intended paths?

The inspection must distinguish:

```text
Application authorization
```

from:

```text
Database authorization / RLS
```

They are complementary controls, not interchangeable ones.

---

# 15. Service-Role Boundary

Explicitly inspect whether the Supabase service-role credential is used in request execution.

If found, document:

```text
FILE
FUNCTION
PURPOSE
DATA ACCESS
AUTHORIZATION IMPACT
```

The inspection must determine whether a service-role client can bypass tenant/RLS protections.

---

# 16. Middleware and Dependency Boundary

Inspect:

```text
middleware/
dependencies/
security/
core/
auth/
```

Determine where security context enters the application.

The preferred implementation boundary should ultimately be centralized rather than duplicating authentication logic throughout individual route functions.

However, the inspection must report the **actual current implementation**, not assume this structure exists.

---

# 17. Error Handling Inspection

Verify HTTP responses for:

| Condition                | Expected                                    |
| ------------------------ | ------------------------------------------- |
| Missing token            | `401`                                       |
| Invalid token            | `401`                                       |
| Expired token            | `401`                                       |
| No professional identity | `403` or defined identity failure           |
| No active membership     | `403`                                       |
| Missing permission       | `403`                                       |
| Cross-tenant resource    | `403` or `404` according to resource policy |

The exact status policy must follow the previously documented 10C specifications.

---

# 18. Security Test Inspection

Inspect:

```text
apps/api/tests/
```

Search for:

```text
auth
authentication
authorization
rbac
permission
role
tenant
hospital
membership
security
protected
403
401
```

Determine whether tests already cover:

### Authentication

```text
missing token
invalid token
expired token
valid token
```

### Identity

```text
unknown professional
inactive membership
valid membership
```

### Tenant

```text
same hospital
different hospital
client-supplied hospital_id
```

### RBAC

```text
allowed role
denied role
missing permission
multiple roles
```

### API Enforcement

```text
unprotected endpoint
protected endpoint
clinical endpoint
administrative endpoint
```

---

# 19. Security Test Classification

Each test should be classified as:

```text
EXISTS AND PASSES
EXISTS AND FAILS
EXISTS BUT INCOMPLETE
MISSING
NOT APPLICABLE
```

No new tests should be written during this inspection.

---

# 20. Static Inspection

The implementation inspection should include static searches for dangerous patterns.

Search for:

```text
hospital_id =
user_id =
role =
permission =
is_admin
admin =
request.user
current_user
service_role
supabase.auth
Authorization
Bearer
```

Also inspect for direct authorization decisions such as:

```python
if user.role == "admin":
```

Determine whether they are legitimate existing boundaries or bypasses of the canonical RBAC model.

---

# 21. Security Bypass Inspection

Explicitly look for these bypasses.

### Bypass 1 — Frontend role trust

```text
Frontend role
      ↓
Backend authorization
```

**Result:** must be rejected.

---

### Bypass 2 — Client hospital ID

```text
Request hospital_id
      ↓
Database query
```

without membership verification.

**Result:** security finding.

---

### Bypass 3 — Service-role overreach

```text
HTTP request
      ↓
service-role Supabase client
      ↓
unrestricted database access
```

**Result:** security finding unless explicitly constrained by backend authorization.

---

### Bypass 4 — Role-only authorization

```text
role == ADMIN
```

without membership/tenant context.

**Result:** inspect for tenant isolation implications.

---

### Bypass 5 — Missing permission enforcement

```text
Authenticated
     ↓
Endpoint executes
```

without permission verification.

---

### Bypass 6 — Direct route access

A protected service may be callable through a route that lacks the expected security dependency.

---

# 22. Plugin Boundary Inspection

Plugins are not responsible for platform authentication or authorization.

The Plugin Framework explicitly assigns authentication, authorization, auditing, and security policies to the platform core. 

Therefore inspect whether:

```text
API
 ↓
Authentication
 ↓
Authorization
 ↓
Plugin execution
```

is maintained.

Do not move authentication into individual plugins.

The Plugin Developer Guide likewise states that authentication and authorization remain platform responsibilities. 

---

# 23. Inspection of Plugin-Triggered Clinical Execution

Because the backend orchestrates plugins through the FastAPI architecture, inspect whether a protected clinical request can reach:

```text
Workflow Manager
        ↓
Plugin Manager
        ↓
Prediction / Knowledge Plugin
```

without first passing the backend security boundary.

The documented plugin architecture places plugin loading and workflow execution behind platform services. 

---

# 24. Configuration and Environment Inspection

Inspect environment configuration for:

```text
SUPABASE_URL
SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
JWT_SECRET
AUTH configuration
```

Do not expose secret values in the inspection report.

Only record:

```text
PRESENT
MISSING
REFERENCED
UNUSED
MISCONFIGURED
```

---

# 25. Implementation Status Matrix

At the end of inspection, produce the following matrix.

| Security Component              | Expected                         | Actual | Status | Evidence      |
| ------------------------------- | -------------------------------- | ------ | ------ | ------------- |
| 10C.1 Authentication Boundary   | Central auth verification        | TBD    | TBD    | File/function |
| 10C.2 Execution Identity        | Auth → professional → membership | TBD    | TBD    | File/function |
| 10C.3 Tenant Context            | Membership-derived hospital      | TBD    | TBD    | File/function |
| 10C.4 Backend RBAC              | Existing roles/permissions       | TBD    | TBD    | File/function |
| 10C.5 Protected API Enforcement | Route-level enforcement          | TBD    | TBD    | File/function |
| 10C.6 Security Tests            | Validation suite                 | TBD    | TBD    | Test files    |

---

# 26. Finding Classification

Every finding must use one of these classifications.

### `IMPLEMENTED`

The documented requirement exists and is correctly enforced.

### `PARTIAL`

The requirement exists but has incomplete coverage or weaknesses.

### `MISSING`

No implementation was found.

### `BYPASS`

An implementation exists but another path can bypass it.

### `INCONSISTENT`

Different parts of the backend implement different security behaviour.

### `UNVERIFIED`

The repository does not provide enough evidence to establish the behaviour.

---

# 27. Required Inspection Output

The inspection must produce these artifacts.

```text
10C_BACKEND_SECURITY_INSPECTION.md
```

Containing:

```text
1. Executive Summary
2. Repository Security Surface
3. Authentication Boundary Findings
4. Execution Identity Findings
5. Tenant Context Findings
6. RBAC Findings
7. Protected API Findings
8. Database/RLS Findings
9. Audit Context Findings
10. Plugin Boundary Findings
11. Security Test Findings
12. Security Bypass Findings
13. Implementation Status Matrix
14. Findings and Severity
15. Implementation Plan
16. Files Requiring Modification
17. Files Requiring Creation
18. Files Requiring Tests
19. Final Readiness Decision
```

---

# 28. No-Code-Change Rule

This inspection phase must **not**:

* create authentication code;
* create RBAC utilities;
* modify routes;
* modify database schemas;
* modify RLS;
* modify Supabase configuration;
* change roles;
* change permissions;
* change membership relationships;
* create a new authorization framework.

The inspection establishes the baseline first.

---

# 29. Implementation Readiness Decision

The inspection must conclude with exactly one of:

```text
READY FOR 10C IMPLEMENTATION
```

or:

```text
BLOCKED — ARCHITECTURAL GAP REQUIRES DECISION
```

or:

```text
BLOCKED — EXISTING IMPLEMENTATION CONFLICTS WITH 10C
```

If the result is `READY`, implementation proceeds in this order:

```text
10C.1
  ↓
10C.2
  ↓
10C.3
  ↓
10C.4
  ↓
10C.5
  ↓
10C.6
```

---

# 30. Final Architectural Constraint

The inspection must preserve the established security ownership:

```text
                    PharmaTrybe Platform Core
                             │
             ┌───────────────┼────────────────┐
             │               │                │
     Authentication     Authorization       Audit
             │               │                │
             └───────────────┼────────────────┘
                             │
                     FastAPI Backend
                             │
                   Execution Identity
                             │
                       Tenant Context
                             │
                         Backend RBAC
                             │
                  Protected API Enforcement
                             │
             ┌───────────────┼────────────────┐
             │               │                │
        Clinical         Knowledge        Plugin
        Services         Services         Services
```

This is consistent with the established architecture in which Authentication and Authorization remain platform-core responsibilities rather than plugin responsibilities. 

The inspection therefore exists to answer a very specific question:

> **What security controls already exist in the actual backend, where are they enforced, where are they missing, and what must be implemented to bring the backend into conformance with the already-approved 10C.1–10C.6 specifications?**

No new RBAC model, tenant model, authentication model, or security architecture is introduced by this document.
