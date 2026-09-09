# 10C.6 — Backend Security Tests

**Status:** approved
**Phase:** 10C — Backend Security Boundary
**Purpose:** Validate the backend authentication, execution identity, tenant context, RBAC, and protected API enforcement already defined in 10C.1–10C.5.

> **Important:** 10C.6 does **not** introduce a new security model.
> It is a test and validation specification for proving that the existing backend security architecture is correctly enforced.

---

## 1. Purpose

10C.6 defines the security tests required to verify that protected backend operations enforce the established security chain:

```text
Authenticated Request
        ↓
Authentication Boundary
        ↓
Execution Identity
        ↓
Tenant Context
        ↓
Backend RBAC
        ↓
Protected API Enforcement
        ↓
Application Operation
```

The tests must demonstrate that **no protected operation can bypass an earlier security boundary**.

The objective is not merely to confirm that valid requests succeed.

The primary objective is to prove that invalid, incomplete, forged, cross-tenant, or unauthorized requests are rejected.

---

# 2. Validation Principle

The backend must follow a **fail-closed** security model.

Therefore:

```text
Missing authentication
        → DENY

Invalid authentication
        → DENY

Inactive identity
        → DENY

Missing professional profile
        → DENY

Missing active membership
        → DENY

Invalid role
        → DENY

Missing permission
        → DENY

Missing tenant context
        → DENY

Tenant mismatch
        → DENY
```

A request must never proceed simply because a later layer happens to accept it.

---

# 3. Existing Security Model Under Test

10C.6 validates the existing implementation rather than creating alternative authorization mechanisms.

The current backend resolves authorization from:

```text
Supabase/Auth identity
        ↓
ProfessionalProfile
        ↓
HospitalMembership
        ↓
MembershipRole
        ↓
Role
        ↓
RolePermission
        ↓
Permission
```

The actual database relationships are:

```text
membership_roles
    membership_id → hospital_memberships.id

membership_roles
    role_id → roles.id

role_permissions
    role_id → roles.id

role_permissions
    permission_id → permissions.id
```

The tests must therefore validate the actual role/permission model rather than introducing a separate hard-coded RBAC matrix.

---

# 4. Test Scope

10C.6 covers six security categories:

```text
1. Authentication tests
2. Execution identity tests
3. Tenant-context tests
4. RBAC tests
5. Protected API tests
6. Security regression / fail-closed tests
```

---

# 5. Authentication Tests

## Test 1 — Missing Authorization Header

Request:

```http
GET /protected-endpoint
```

without:

```http
Authorization: Bearer <token>
```

Expected:

```text
HTTP 401
```

The endpoint must not reach:

```text
database authorization resolution
RBAC
business logic
```

---

## Test 2 — Malformed Authorization Header

Examples:

```text
Authorization: Basic ...
Authorization: Bearer
Authorization: invalid
```

Expected:

```text
HTTP 401
```

---

## Test 3 — Invalid Token

Use:

```text
expired token
malformed JWT
invalid signature
incorrect issuer
incorrect audience
```

Expected:

```text
HTTP 401
```

No application identity must be created.

---

## Test 4 — Valid Authentication

A valid authenticated identity should pass the authentication boundary.

Expected:

```text
Authentication = PASS
```

and execution proceeds to identity resolution.

---

# 6. Execution Identity Tests

## Test 5 — Unknown Authenticated User

A validly authenticated token whose subject does not correspond to a valid application professional profile.

Expected:

```text
HTTP 403
ACCOUNT_INACTIVE / equivalent application denial
```

The backend must not manufacture an application identity from the JWT alone.

---

## Test 6 — Inactive Professional Profile

Authenticated user exists, but:

```text
professional_profile.profile_status != ACTIVE
```

Expected:

```text
HTTP 403
```

No protected operation is executed.

---

## Test 7 — Missing Active Hospital Membership

Authenticated professional has no active hospital membership.

Expected:

```text
HTTP 403
```

---

## Test 8 — Multiple Active Hospital Memberships

The current architecture requires exactly one active hospital membership.

Therefore:

```text
active_memberships != 1
```

must result in:

```text
HTTP 403
```

This test is important because tenant identity must not become ambiguous.

---

# 7. Tenant Context Tests

## Test 9 — Tenant Context Successfully Resolved

Valid identity:

```text
User
 ↓
Professional
 ↓
Active Membership
 ↓
Hospital A
```

Expected:

```text
TenantContext.hospital_id = Hospital A
```

The tenant must originate from the authoritative backend membership relationship.

---

## Test 10 — Client-Supplied Hospital ID Cannot Override Tenant

Request body:

```json
{
  "hospital_id": "hospital-B"
}
```

while the authenticated user belongs to:

```text
Hospital A
```

Expected:

```text
DENY
```

The supplied value must never become the authoritative tenant.

If the field is accepted for validation or resource selection, the backend must verify:

```text
supplied_hospital_id
==
authenticated_tenant.hospital_id
```

otherwise reject the request.

---

## Test 11 — Cross-Tenant Resource Access

Authenticated user:

```text
Hospital A
```

attempts to access a resource belonging to:

```text
Hospital B
```

Expected:

```text
HTTP 403
```

or the established resource-not-found response where deliberately used to avoid information disclosure.

No Hospital B data may be returned.

---

## Test 12 — Missing Tenant Context

Simulate a protected backend operation where:

```text
TenantContext = None
```

Expected:

```text
DENY
```

The system must not fall back to:

```text
JWT hospital_id
request hospital_id
query parameter
global/default hospital
```

---

# 8. Role Resolution Tests

The test suite must use the **actual canonical roles currently present in the database**.

Current roles:

```text
HOSPITAL_ADMIN
PHARMACIST
CLINICIAN
INFECTIOUS_DISEASE_SPECIALIST
RESEARCHER
LABORATORY_SCIENTIST
```

These are not to be replaced with newly invented roles.

---

## Test 13 — Canonical Role Resolution

For each active membership role:

```text
membership_roles
        ↓
roles
```

the backend must resolve the canonical role code correctly.

Expected:

```text
role.code ∈ canonical role set
```

---

## Test 14 — Invalid Role

A membership containing an unknown/non-canonical role must not obtain protected access.

Expected:

```text
HTTP 403
```

---

# 9. Permission Resolution Tests

Permissions must be resolved through the existing database mapping:

```text
Role
 ↓
role_permissions
 ↓
Permission
```

The backend must not infer permissions merely from a role name.

---

## Test 15 — Permission Exists

For a role containing:

```text
role_permissions
```

the corresponding permission must appear in the resolved authorization context.

Example:

```text
HOSPITAL_ADMIN
    ↓
plugins:configure
```

if that mapping exists in the database.

---

## Test 16 — Permission Missing

A user whose role does not contain:

```text
required_permission
```

must receive:

```text
HTTP 403
```

even if the user is authenticated and has a valid hospital membership.

---

## Test 17 — Permission Cannot Be Forged by Request

A request must not be able to provide:

```json
{
  "permission": "plugins:configure"
}
```

and thereby obtain the permission.

Permissions must come from the backend authorization context.

---

# 10. Backend RBAC Tests

## Test 18 — Hospital Administrator

Verify the actual `HOSPITAL_ADMIN` role against its actual database permissions.

The test must confirm both:

```text
role resolution
permission resolution
```

rather than assuming that every administrator action is automatically authorized.

---

## Test 19 — Clinician

Verify the actual permissions assigned to:

```text
CLINICIAN
```

and confirm that:

```text
allowed permission → succeeds
missing permission → denied
```

---

## Test 20 — Pharmacist

Verify the actual permissions assigned to:

```text
PHARMACIST
```

including its recommendation, laboratory, case, and other currently mapped permissions.

---

## Test 21 — Infectious Disease Specialist

Verify the actual permissions assigned to:

```text
INFECTIOUS_DISEASE_SPECIALIST
```

without adding permissions that are not present in `role_permissions`.

---

## Test 22 — Laboratory Scientist

Verify the actual permissions assigned to:

```text
LABORATORY_SCIENTIST
```

especially laboratory-related operations.

---

## Test 23 — Researcher

Verify that:

```text
RESEARCHER
```

remains restricted to the permissions actually assigned to it.

The test must specifically ensure that read-only research access cannot accidentally acquire clinical-management permissions.

---

# 11. Protected API Enforcement

Every protected endpoint must be tested against the authorization chain.

The minimum matrix is:

| Authentication | Identity | Tenant       | Permission | Expected |
| -------------- | -------- | ------------ | ---------- | -------- |
| Missing        | —        | —            | —          | DENY     |
| Invalid        | —        | —            | —          | DENY     |
| Valid          | Invalid  | —            | —          | DENY     |
| Valid          | Valid    | Missing      | —          | DENY     |
| Valid          | Valid    | Valid        | Missing    | DENY     |
| Valid          | Valid    | Valid        | Present    | ALLOW    |
| Valid          | Valid    | Wrong tenant | Present    | DENY     |

---

# 12. Test 24 — Protected Endpoint Without Authentication

Every protected endpoint must reject unauthenticated access.

Expected:

```text
401
```

---

# 13. Test 25 — Protected Endpoint Without Required Permission

Authenticated user with valid tenant context but without the endpoint's required permission.

Expected:

```text
403
```

Business logic must not execute.

---

# 14. Test 26 — Correct Permission

Authenticated user:

```text
valid identity
+
valid tenant
+
required permission
```

Expected:

```text
ALLOW
```

The protected operation executes normally.

---

# 15. Test 27 — Correct Permission, Wrong Tenant Resource

Authenticated user has the required permission but attempts to operate on another hospital's resource.

Expected:

```text
DENY
```

This proves:

> Permission alone is insufficient; tenant scope remains mandatory.

---

# 16. Test 28 — Request Body Tenant Spoofing

Attempt:

```text
Authenticated tenant = Hospital A

Request:
hospital_id = Hospital B
```

Expected:

```text
DENY
```

No operation against Hospital B may occur.

---

# 17. Test 29 — Query Parameter Tenant Spoofing

Attempt:

```http
GET /resource?hospital_id=hospital-B
```

while authenticated under Hospital A.

Expected:

```text
DENY
```

The backend must not treat URL parameters as authoritative tenant identity.

---

# 18. Test 30 — Path Tenant Spoofing

Attempt:

```http
GET /hospitals/hospital-B/resource
```

while authenticated under Hospital A.

Expected:

```text
DENY
```

unless the endpoint is explicitly designed for cross-tenant/system access and has a separately authorized security context.

---

# 19. Test 31 — Role Spoofing

Attempt to provide:

```http
X-Role: HOSPITAL_ADMIN
```

or equivalent client-controlled role information.

Expected:

```text
DENY / ignored
```

The backend must use the database-resolved role.

---

# 20. Test 32 — Permission Spoofing

Attempt to provide:

```http
X-Permission: plugins:configure
```

or equivalent.

Expected:

```text
DENY / ignored
```

---

# 21. Test 33 — Hospital Spoofing in JWT

If a token contains an arbitrary hospital-related claim, the backend must not blindly treat it as the authoritative application tenant.

The authoritative tenant must remain the resolved active hospital membership.

---

# 22. Fail-Closed Tests

The following conditions must be explicitly tested:

```text
missing token
invalid token
expired token
unknown user
inactive professional
missing professional profile
missing active membership
multiple active memberships
invalid role
missing permission
missing TenantContext
tenant mismatch
resource tenant mismatch
invalid resource ownership
```

Every case must result in:

```text
DENY
```

and must not execute protected business logic.

---

# 23. Security Boundary Ordering Test

The test suite should prove that the order is preserved:

```text
Authentication
      ↓
Identity
      ↓
Tenant
      ↓
RBAC
      ↓
Resource authorization
      ↓
Business operation
```

For example:

A request with an invalid token must **not** reach RBAC.

A request with valid authentication but no active membership must **not** reach business logic.

A request with valid RBAC but a foreign tenant resource must **not** reach the resource operation.

---

# 24. No Authorization Bypass Tests

Search the backend for protected routes and verify that no route bypasses the established authorization dependencies.

The review should specifically inspect:

```text
router dependencies
get_current_user
get_authorization_context
require_permission
require_same_hospital
database queries
service-layer authorization
```

The test should identify any protected route that can execute without the required security boundary.

---

# 25. Database Relationship Integrity Tests

Validate the actual relationships:

```text
membership_roles.membership_id
        ↓
hospital_memberships.id
```

```text
membership_roles.role_id
        ↓
roles.id
```

```text
role_permissions.role_id
        ↓
roles.id
```

```text
role_permissions.permission_id
        ↓
permissions.id
```

Tests should detect:

```text
orphan membership_roles
orphan role_permissions
invalid role references
invalid permission references
```

where database constraints permit such states to be tested.

---

# 26. Permission Resolution Consistency

For a membership with multiple roles:

```text
Membership
    ↓
Role A
Role B
Role C
    ↓
permissions
```

the resulting permission set should be the union of permissions assigned through the actual `role_permissions` mappings.

No additional implicit permissions should appear.

---

# 27. Permission Removal Regression Test

Remove a permission mapping from:

```text
role_permissions
```

and verify that the corresponding operation becomes unauthorized.

This proves that backend authorization is actually driven by the database RBAC model.

---

# 28. Role Removal Regression Test

Remove a role from:

```text
membership_roles
```

and verify that permissions obtained exclusively through that role disappear from the authorization context.

---

# 29. Tenant Isolation Regression Matrix

At minimum:

```text
Hospital A user → Hospital A resource → ALLOW when authorized

Hospital A user → Hospital B resource → DENY

Hospital B user → Hospital A resource → DENY

Hospital B user → Hospital B resource → ALLOW when authorized
```

This must be tested with actual protected resources where possible.

---

# 30. Business Logic Non-Execution Test

Security rejection must occur before protected business logic executes.

For each important protected endpoint:

```text
Unauthorized request
        ↓
DENY
        ↓
business service NOT called
```

Tests may use mocks/spies to prove that the protected service was never invoked.

---

# 31. Error Response Tests

Security errors must not expose sensitive information.

Responses must not reveal:

```text
another hospital's data
database credentials
JWT secrets
internal authorization structures
permission tables
private patient information
```

The response should provide only the appropriate bounded error.

---

# 32. Audit Validation

Where the existing backend architecture requires security-sensitive audit events, verify that denied security operations are auditable.

The audit record should contain bounded security provenance such as:

```text
authenticated user
tenant
operation
allow/deny decision
reason
timestamp
```

It must not contain:

```text
access tokens
refresh tokens
passwords
credentials
patient payload
secrets
```

10C.6 does not introduce a new audit architecture; it only validates existing audit requirements.

---

# 33. Regression Test Requirements

The following existing backend security areas must remain green:

```text
Authentication
Identity resolution
Hospital membership
Role resolution
Permission resolution
Tenant isolation
Protected API authorization
```

Plugin-specific security tests remain governed by their dedicated plugin security phases and must not be duplicated here.

The backend security suite should therefore test the **common authorization boundary**, not recreate R9/R9H plugin isolation.

---

# 34. Suggested Test Structure

Recommended organisation:

```text
apps/api/tests/

├── test_authentication_boundary.py
├── test_execution_identity.py
├── test_tenant_context.py
├── test_backend_rbac.py
├── test_protected_api_enforcement.py
└── test_backend_security_regression.py
```

If equivalent existing test files already exist, extend them instead of creating duplicates.

---

# 35. Validation Commands

Use the repository's existing virtual environment and test architecture.

Focused validation:

```powershell
.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_authentication_boundary.py -q
```

Then:

```powershell
.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_execution_identity.py -q
```

Then:

```powershell
.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_tenant_context.py -q
```

Then:

```powershell
.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_backend_rbac.py -q
```

Then:

```powershell
.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_protected_api_enforcement.py -q
```

Finally run the relevant backend regression suite.

---

# 36. Compilation and Static Validation

After tests:

```powershell
.\.venv\Scripts\python.exe -m compileall -q apps/api/app apps/api/tests
```

Then:

```powershell
git diff --check
```

No unrelated files should be modified merely to satisfy this validation.

---

# 37. Security Acceptance Criteria

10C.6 is considered **COMPLETE** only when the tests demonstrate all of the following:

### Authentication

```text
Unauthenticated → DENY
Invalid token → DENY
Valid token → proceed
```

### Identity

```text
Unknown identity → DENY
Inactive identity → DENY
Invalid membership state → DENY
```

### Tenant

```text
Valid tenant → proceed
Missing tenant → DENY
Wrong tenant → DENY
Client-supplied tenant cannot override authoritative tenant
```

### RBAC

```text
Valid role + permission → ALLOW
Missing permission → DENY
Forged role → ignored/denied
Forged permission → ignored/denied
```

### Protected APIs

```text
Protected endpoint without authentication → DENY
Protected endpoint without permission → DENY
Protected endpoint with permission → ALLOW
Protected endpoint against another tenant → DENY
```

### Fail Closed

```text
Security context unavailable
        ↓
DENY
```

---

# 38. What 10C.6 Does Not Do

10C.6 does **not**:

* create new roles;
* create new permissions;
* modify the RBAC model;
* introduce a second authorization system;
* introduce a new tenant model;
* replace Supabase authentication;
* replace the existing `AuthorizationContext`;
* redesign plugin security;
* redesign RLS;
* introduce frontend authorization;
* claim production security merely because unit tests pass.

It validates the architecture already established in:

```text
10C.1 Authentication Boundary
10C.2 Execution Identity
10C.3 Tenant Context
10C.4 Backend RBAC
10C.5 Protected API Enforcement
```

---

# 39. Final Security Invariant

The complete 10C backend security boundary must make this property demonstrable:

```text
                    Request
                       │
                       ▼
              Authentication
                       │
                 ┌─────┴─────┐
                 │           │
              INVALID       VALID
                 │           │
                DENY         ▼
                       Execution Identity
                              │
                         ┌────┴────┐
                         │         │
                      INVALID     VALID
                         │         │
                        DENY       ▼
                            Tenant Context
                                  │
                             ┌────┴────┐
                             │         │
                          INVALID     VALID
                             │         │
                            DENY       ▼
                               Backend RBAC
                                    │
                               ┌────┴────┐
                               │         │
                            DENIED     ALLOWED
                               │         │
                              DENY       ▼
                         Protected API
                               │
                          Resource/Tenant
                           Authorization
                               │
                          ┌────┴────┐
                          │         │
                       DENIED     ALLOWED
                          │         │
                         DENY       ▼
                    Business Operation
```

The central acceptance property is:

> **No request may reach a protected backend operation unless authentication, execution identity, authoritative tenant context, required database-derived permission, and resource-level tenant authorization have all succeeded.**

---

# 40. 10C.6 Gate Decision

At the end of validation, report one of:

```text
COMPLETE
```

when the complete security matrix passes;

```text
PARTIALLY COMPLETE
```

when the architecture is implemented but one or more required validation areas remain untested or failing;

```text
BLOCKED
```

when the tests cannot establish the required security guarantees because a prerequisite backend security component is unavailable.

The test report must distinguish clearly between:

```text
Implementation failure
Test failure
Environment limitation
Deployment limitation
Pre-existing unrelated failure
```

**10C.6 therefore remains a validation gate, not an architectural change.**
