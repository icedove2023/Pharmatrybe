# 10C.5 — Protected API Enforcement

**Project:** PharmaTrybe
**Phase:** 10C — Backend Security Boundary
**Status:** Architecture / Implementation Contract Approved
**Scope:** FastAPI backend API protection
**Depends On:** 10C.1 Authentication Boundary, 10C.2 Execution Identity, 10C.3 Tenant Context, 10C.4 Backend RBAC

---

## 1. Purpose

This document defines how protected PharmaTrybe API endpoints enforce authentication, execution identity, tenant context, roles, and permissions.

The purpose is to establish a single authoritative authorization path for backend requests.

The backend must not rely on frontend visibility, caller-supplied hospital identifiers, or role names alone to determine whether an operation is permitted.

The API is the authoritative security boundary.

The existing implementation already provides reusable authorization dependencies, including `get_current_user()`, `get_authorization_context()`, and `require_permission()`. The backend inspection also confirms that permission enforcement is designed around canonical `resource:action` permissions. 

---

# 2. Security Principle

Every protected API request must pass through the following chain:

```text
HTTP Request
     │
     ▼
Bearer JWT
     │
     ▼
Authentication Boundary
     │
     ▼
Authenticated User
     │
     ▼
Execution Identity
     │
     ▼
Active Professional Profile
     │
     ▼
Exactly One Active Hospital Membership
     │
     ▼
Authoritative Tenant Context
     │
     ▼
Canonical Roles
     │
     ▼
Canonical Permissions
     │
     ▼
Endpoint Permission Check
     │
     ▼
Tenant-Scoped Resource Access
     │
     ▼
Business Operation
```

No protected endpoint may bypass this chain.

---

# 3. FastAPI Is the Enforcement Boundary

All externally accessible application APIs are exposed through the FastAPI backend.

The established architecture requires external communication to pass through FastAPI rather than allowing frontend clients or internal services to bypass the backend orchestration boundary. 

Therefore:

```text
Frontend
   │
   │ Bearer JWT
   ▼
FastAPI
   │
   ├── Authentication
   ├── Identity
   ├── Tenant Context
   ├── RBAC
   ├── Resource Scope
   └── Business Logic
```

The frontend is **not** an authorization boundary.

---

# 4. Protected vs Public Endpoints

Not every endpoint requires an authenticated professional identity.

Endpoints must explicitly belong to one of the following classes.

## 4.1 Public Endpoint

May be accessed without authentication.

Examples:

```text
GET /health
GET /version
GET /auth
```

Public endpoints must not expose:

* patient information
* hospital information
* professional information
* permissions
* clinical cases
* recommendations
* protected plugin information
* audit information

---

## 4.2 Authenticated Endpoint

Requires a valid authenticated user.

Authentication alone is insufficient for tenant-protected operations.

```text
Valid JWT
      ↓
Authenticated User
      ↓
Endpoint
```

---

## 4.3 Tenant-Protected Endpoint

Requires:

```text
Authenticated User
        +
Professional Profile
        +
Active Membership
        +
Authoritative Tenant Context
```

Examples include:

```text
patients
cases
laboratory
recommendations
stewardship
hospital
professionals
plugins
audit
```

---

## 4.4 Permission-Protected Endpoint

Requires a specific canonical permission.

For example:

```text
patients:view
cases:create
cases:update
laboratory:view
recommendations:request
recommendations:review
plugins:configure
roles:assign
audit:view
```

The endpoint should check the permission required for the operation rather than merely checking that the caller has a broad role.

---

# 5. Canonical Authorization Context

Protected endpoints consume the existing `AuthorizationContext`.

Conceptually:

```python
AuthorizationContext(
    user_id,
    user,
    professional,
    hospital,
    membership,
    roles,
    permissions,
    tenant_context,
)
```

This context is derived by the backend.

It is **not constructed from request-body tenant information**.

The backend inspection confirms that the current authorization path derives hospital identity from `AuthorizationContext` and requires an active professional profile with exactly one active membership. 

---

# 6. Request Body Must Not Establish Authority

A request may contain a hospital identifier as ordinary business data where appropriate.

However:

```json
{
  "hospital_id": "..."
}
```

must never establish the caller's tenant authority.

The authoritative tenant is:

```text
JWT
 ↓
Application Identity
 ↓
Professional Profile
 ↓
Active Hospital Membership
 ↓
TenantContext
```

Therefore:

```text
Caller hospital_id
        ≠
Authoritative tenant
```

If the request attempts to operate against a different tenant, the backend must deny the operation.

---

# 7. Permission Enforcement

The backend must use the existing canonical permission catalogue.

The project already defines permissions such as:

```text
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

professionals:view
professionals:invite
professionals:manage

roles:assign

plugins:view
plugins:configure

workflows:execute
workflows:manage

audit:view

data:export
```

These permissions are already represented in the backend RBAC model and mapped through `role_permissions`.

The protected API layer must therefore **consume the existing RBAC model rather than introduce a second permission system**.

---

# 8. Endpoint Enforcement Pattern

Protected routes should use FastAPI dependencies.

Conceptually:

```python
@router.get("/cases")
async def list_cases(
    context: Annotated[
        AuthorizationContext,
        Depends(require_permission("cases:view"))
    ],
):
    ...
```

For creation:

```python
@router.post("/cases")
async def create_case(
    context: Annotated[
        AuthorizationContext,
        Depends(require_permission("cases:create"))
    ],
):
    ...
```

For plugin configuration:

```python
@router.put("/plugins/{plugin_id}/configuration")
async def configure_plugin(
    context: Annotated[
        AuthorizationContext,
        Depends(require_permission("plugins:configure"))
    ],
):
    ...
```

The permission dependency performs authorization before the business operation executes.

---

# 9. Role Is Not Permission

A role and a permission have different responsibilities.

```text
Role
 ↓
Role-Permission Mapping
 ↓
Permission
 ↓
API Operation
```

For example:

```text
HOSPITAL_ADMIN
       ↓
plugins:configure
       ↓
PUT /plugins/{plugin_id}/configuration
```

The endpoint should ultimately enforce:

```text
plugins:configure
```

rather than relying exclusively on:

```text
HOSPITAL_ADMIN
```

This is important because the existing backend inspection identified role-only checks on plugin governance routes as an authorization gap. 

---

# 10. Existing RBAC Must Remain Canonical

The protected API layer must not introduce:

```text
if user.is_admin
```

or:

```text
if role == "admin"
```

as a replacement authorization model.

Instead:

```text
Canonical Role
      ↓
membership_roles
      ↓
roles
      ↓
role_permissions
      ↓
permissions
      ↓
AuthorizationContext.permissions
      ↓
require_permission(...)
```

This preserves the database-defined RBAC architecture already established in 10C.4.

---

# 11. Tenant-Scoped Resource Enforcement

Permission alone is insufficient.

A user may possess:

```text
cases:view
```

but that does not mean:

```text
cases:view for every hospital
```

The effective authorization decision is:

```text
Permission
        +
Tenant Context
        +
Resource Scope
```

Therefore:

```text
cases:view
+
Hospital A
=
may view Hospital A cases
```

but:

```text
cases:view
+
Hospital B resource
=
DENY
```

unless a future explicitly defined cross-tenant authority exists.

No such unrestricted cross-tenant authority should be assumed.

---

# 12. Tenant Filtering

Hospital-scoped queries must derive the hospital from the authorization context.

Preferred pattern:

```python
hospital_id = context.tenant_context.hospital_id

query = (
    select(Case)
    .where(Case.hospital_id == hospital_id)
)
```

Not:

```python
hospital_id = request.hospital_id
```

The first uses authoritative execution context.

The second trusts caller-controlled input.

---

# 13. Resource-Level Authorization

For resources belonging to a tenant:

```text
Request
 ↓
Permission
 ↓
Tenant Context
 ↓
Resource Lookup
 ↓
Verify Resource Tenant
 ↓
Operation
```

Example:

```text
GET /cases/{case_id}

        ↓

cases:view

        ↓

case.hospital_id == context.hospital_id

        ↓

ALLOW
```

If:

```text
case.hospital_id != context.hospital_id
```

the backend must deny access.

The resource must not be returned merely because the user possesses the correct permission.

---

# 14. Cross-Tenant Requests

Cross-tenant access must fail closed.

Example:

```text
Authenticated User
Hospital A

Request:
GET /patients/{hospital-B-patient}
```

Result:

```text
DENIED
```

The API must not:

* silently switch tenant;
* trust a submitted hospital ID;
* search globally;
* return the resource and hide the tenant mismatch;
* infer a new tenant from URL parameters.

---

# 15. Protected Plugin APIs

Plugin governance endpoints are particularly sensitive.

The established backend inspection identified the intended authorization path as:

```text
Bearer JWT
    ↓
get_current_user()
    ↓
get_authorization_context()
    ↓
active professional profile
    ↓
exactly one active membership
    ↓
canonical roles and permissions
    ↓
endpoint authorization
    ↓
hospital-scoped service query
```



Plugin operations must therefore enforce both:

```text
Tenant Context
+
plugins:view / plugins:configure
```

according to the operation.

Examples:

| Operation         | Required permission |
| ----------------- | ------------------- |
| View plugins      | `plugins:view`      |
| Configure plugin  | `plugins:configure` |
| Register plugin   | `plugins:configure` |
| Validate plugin   | `plugins:configure` |
| Approve plugin    | `plugins:configure` |
| Activate plugin   | `plugins:configure` |
| Deactivate plugin | `plugins:configure` |
| Reject plugin     | `plugins:configure` |
| Quarantine plugin | `plugins:configure` |
| Revoke plugin     | `plugins:configure` |

The exact governance operation may additionally require lifecycle/state validation.

RBAC does not replace governance state enforcement.

---

# 16. RBAC and Governance Are Separate Gates

For sensitive plugin operations:

```text
Authentication
      ↓
Tenant Context
      ↓
Permission
      ↓
Governance State
      ↓
Artifact / Version / Ownership
      ↓
Operation
```

Possessing:

```text
plugins:configure
```

does not automatically mean:

```text
plugin may be activated
```

Activation remains subject to plugin governance.

This maintains the separation between authorization and plugin lifecycle governance.

---

# 17. Authentication Failure

If no valid authentication exists:

```text
401 Unauthorized
```

Examples:

```text
missing token
invalid token
expired token
unverifiable token
```

The endpoint must not execute business logic.

---

# 18. Authorization Failure

If the user is authenticated but lacks the required permission:

```text
403 Forbidden
```

Example:

```text
Authenticated
+
CLINICIAN
+
no plugins:configure
```

Request:

```text
POST /plugins/{plugin_id}/activate
```

Result:

```text
403 Forbidden
```

---

# 19. Tenant Failure

If tenant context cannot be established:

```text
DENY
```

This includes:

```text
no active membership
multiple active memberships
missing hospital
inactive membership
tenant mismatch
invalid tenant context
```

The request must not proceed using a fallback tenant.

---

# 20. Fail-Closed Requirement

Protected API authorization must fail closed.

The following must never result in authorization success:

```text
missing user
missing professional profile
missing membership
ambiguous membership
missing tenant context
missing permission
invalid role
unknown permission
tenant mismatch
authorization service failure
```

The system must prefer denial over uncertain authorization.

---

# 21. Service-Layer Enforcement

Route dependencies are the first authorization boundary.

Tenant-sensitive service operations should also receive authoritative context where required.

Conceptually:

```python
service.create_case(
    tenant_context=context.tenant_context,
    actor=context.user_id,
    payload=payload,
)
```

This prevents lower-level business operations from accidentally losing the security context.

However, this must not create a second independent RBAC model.

The service layer consumes the already-established authorization context.

---

# 22. No Frontend Authorization Trust

Frontend checks such as:

```text
hide button
disable menu
route guard
role display
```

are usability mechanisms only.

They do not authorize API access.

For example:

```text
Frontend hides "Configure Plugin"
```

does not protect:

```text
PUT /plugins/{id}/configuration
```

The backend must independently enforce:

```text
plugins:configure
```

---

# 23. Request Context and Audit

The backend already has request-context middleware infrastructure for request-scoped metadata. The backend inspection identified `RequestContextMiddleware` as part of the application stack. 

Protected operations should associate security-sensitive events with:

```text
request_id
user_id
hospital_id
membership_id
permission
resource
action
result
timestamp
```

For denied requests, the audit record should capture the security decision without recording sensitive clinical payloads or credentials.

---

# 24. Authorization Decision Model

The protected API decision can be represented as:

```text
ALLOW =
    authenticated
    AND valid_execution_identity
    AND valid_tenant_context
    AND required_permission
    AND resource_belongs_to_tenant
    AND operation_allowed
```

Otherwise:

```text
DENY
```

For governance-sensitive operations:

```text
ALLOW =
    authenticated
    AND valid_execution_identity
    AND valid_tenant_context
    AND required_permission
    AND resource_belongs_to_tenant
    AND governance_state_allows_operation
```

---

# 25. Protected API Flow

The complete request path is:

```text
                    HTTP Request
                         │
                         ▼
                  Security Middleware
                         │
                         ▼
                    Bearer JWT
                         │
                         ▼
                 get_current_user()
                         │
                         ▼
              get_authorization_context()
                         │
              ┌──────────┴──────────┐
              │                     │
       Professional             Membership
          Profile                   │
              │                     │
              └──────────┬──────────┘
                         ▼
                  Tenant Context
                         │
                         ▼
                 Required Permission
                         │
                  ┌──────┴──────┐
                  │             │
                DENY          ALLOW
                  │             │
                  │             ▼
                  │      Tenant-Scoped
                  │       Resource Query
                  │             │
                  │             ▼
                  │      Business Service
                  │             │
                  │             ▼
                  │        Audit Event
                  │             │
                  └─────────────┴──► Response
```

---

# 26. Clinical API Protection

Clinical endpoints must receive the same protection.

For example:

```text
POST /recommendations
```

requires:

```text
Authenticated
+
Valid Professional Identity
+
Valid Tenant Context
+
recommendations:request
```

Then the clinical workflow executes.

The CDSS remains a supporting system and does not replace clinician authority. This is consistent with the platform architecture's explicit rule that clinicians retain final clinical authority. 

---

# 27. Explainability Protection

Explainability data is also protected.

A user must not be able to retrieve another hospital's explanation merely by knowing:

```text
recommendation_id
```

The API must enforce:

```text
recommendations:view
+
tenant ownership
```

before returning the explanation.

This maintains the project's requirement that recommendations and their supporting evidence remain auditable and appropriately scoped.

---

# 28. Audit Protection

Audit records are sensitive.

Access requires:

```text
audit:view
+
appropriate tenant scope
```

The API must not expose unrestricted audit history.

The permission definition itself states that audit viewing is subject to scope policy.

---

# 29. API Security Invariants

The following invariants are mandatory.

### Invariant 1

```text
No authenticated identity → no protected API access.
```

### Invariant 2

```text
No valid tenant context → no tenant-protected access.
```

### Invariant 3

```text
Role does not directly replace permission.
```

### Invariant 4

```text
Permission does not override tenant isolation.
```

### Invariant 5

```text
Tenant ID supplied by caller does not establish authority.
```

### Invariant 6

```text
Frontend authorization does not replace backend authorization.
```

### Invariant 7

```text
Plugin permission does not override plugin governance.
```

### Invariant 8

```text
Authorization uncertainty results in denial.
```

---

# 30. Current Implementation Alignment

The existing backend already contains important pieces of this architecture:

* `get_current_user()`
* `get_authorization_context()`
* `AuthorizationContext`
* canonical permission definitions
* `require_permission()`
* tenant-aware governance queries
* active professional membership resolution
* request-context middleware

The inspection specifically identified the reusable `require_permission()` dependency as an existing mechanism for enforcing resource-action permissions. 

Therefore, **10C.5 does not introduce a new authorization framework**.

It formalizes the existing backend security path and establishes where every protected API must connect to it.

---

# 31. Known Implementation Gap

The backend inspection identified an important inconsistency:

Some existing plugin governance routes were checking:

```text
HOSPITAL_ADMIN
```

without enforcing the corresponding canonical:

```text
plugins:configure
```

permission. 

This must be treated as an implementation gap rather than a reason to create another RBAC mechanism.

The correct direction is:

```text
Existing RBAC
      ↓
Canonical Permission
      ↓
require_permission(...)
      ↓
Protected API
```

---

# 32. Required API Authorization Tests

The protected API layer must eventually demonstrate:

| Scenario                                      | Expected                     |
| --------------------------------------------- | ---------------------------- |
| No JWT                                        | `401`                        |
| Invalid JWT                                   | `401`                        |
| Expired JWT                                   | `401`                        |
| Authenticated but no professional profile     | Deny                         |
| No active membership                          | Deny                         |
| Ambiguous active membership                   | Deny                         |
| Valid user + valid tenant + permission        | Allow                        |
| Valid user + missing permission               | `403`                        |
| Valid permission + wrong tenant               | Deny                         |
| Caller-supplied hospital differs from context | Deny                         |
| Hospital A accessing Hospital B resource      | Deny                         |
| Hospital admin without `plugins:configure`    | Deny                         |
| Hospital admin with `plugins:configure`       | Allow, subject to governance |
| Revoked plugin                                | Deny                         |
| Quarantined plugin                            | Deny                         |
| Disabled plugin                               | Deny                         |

These tests align with the project's broader security verification requirement that missing tenant context, tenant mismatch, invalid governance state, and unauthorized capability must fail closed. 

---

# 33. Architectural Boundary

10C.5 establishes the following boundary:

```text
                 ┌─────────────────────────┐
                 │       FastAPI API       │
                 │                         │
External ───────►│ Authentication           │
Request          │ Execution Identity       │
                 │ Tenant Context           │
                 │ RBAC / Permission        │
                 │ Resource Scope           │
                 │                         │
                 │        Business          │
                 │        Services          │
                 └────────────┬────────────┘
                              │
                              ▼
                       Internal Platform
```

No external request may bypass this boundary to directly invoke:

```text
database
plugin manager
workflow manager
decision engine
AI service
knowledge service
audit service
```

The established architecture similarly requires services to communicate through the FastAPI orchestration boundary rather than directly communicating with one another. 

---

# 34. Final Security Rule

The authoritative rule for protected APIs is:

> **A request may execute only when the backend has independently established the authenticated identity, authoritative tenant context, required canonical permission, and applicable resource or governance scope.**

Therefore:

```text
JWT
 ↓
Authenticated User
 ↓
Professional Identity
 ↓
Active Membership
 ↓
TenantContext
 ↓
Canonical Permission
 ↓
Tenant-Scoped Resource
 ↓
Business Operation
```

**Any missing or conflicting security context results in denial.**

---

# 35. Status

**10C.5 — Protected API Enforcement: ARCHITECTURAL CONTRACT ESTABLISHED**

### Confirmed

* FastAPI is the external API/security boundary.
* Existing `AuthorizationContext` is the authoritative backend security context.
* Existing canonical roles and permissions remain the RBAC source.
* `require_permission()` is the intended permission enforcement mechanism.
* Tenant context is derived from authenticated application identity rather than caller-supplied hospital data.
* Resource access must remain tenant-scoped.
* Plugin governance requires RBAC **and** governance-state enforcement.
* Authorization must fail closed.

### Known implementation gap

Existing API routes are not yet uniformly proven to enforce the complete chain, particularly the specific permission checks on some plugin governance endpoints. 

### Architectural decision

**Do not create another API authorization model.**

The implementation should complete and consistently apply:

```text
Authentication
→ Execution Identity
→ Tenant Context
→ Existing RBAC
→ Permission Enforcement
→ Tenant-Scoped Resource Enforcement
→ Business Operation
```

This preserves the architecture already established in 10C.1–10C.4 and the existing PharmaTrybe platform contracts.
