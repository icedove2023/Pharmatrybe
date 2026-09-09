# 10C.1 — Authentication Boundary

**Status:**Approved
**Phase:** 10C — Backend Authentication / RBAC
**Depends on:** 10C.0 — Backend Inspection, 16D — Supabase Auth Architecture, 16E — Backend Authentication / RBAC Design

---

## 1. Purpose

This section defines the **authentication boundary** between Supabase Auth and the PharmaTrybe backend.

The authentication boundary is the point at which an incoming HTTP request transitions from:

> **untrusted external request**

to:

> **authenticated PharmaTrybe execution context**

The backend must not trust client-supplied identity, professional, hospital, role, or permission information.

Authentication must originate from the validated Supabase Auth identity.

---

# 2. Architectural Principle

The backend follows this trust chain:

```text
Client
  │
  │ Authorization: Bearer <Supabase JWT>
  ▼
FastAPI
  │
  │ Validate JWT
  ▼
Authenticated Supabase User
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
Authenticated Tenant Context
  │
  ▼
RBAC / Permission Evaluation
  │
  ▼
Application Service
```

The backend must **not** derive tenant identity from:

```text
request body
query parameter
URL parameter
HTTP header supplied by the client
frontend state
role supplied by the client
hospital_id supplied by the client
```

These values may be supplied as application data, but they must never establish authorization.

---

# 3. Authentication Authority

Supabase Auth is the authentication authority.

The backend does not create an independent user identity system.

The authenticated identity is represented by:

```text
auth.uid()
```

and corresponds to:

```text
professional_profiles.auth_user_id
```

The existing database design confirms this relationship.

The backend therefore treats the Supabase authenticated user ID as the root identity identifier.

---

# 4. Authentication Boundary

The authentication boundary exists at the FastAPI request layer.

Conceptually:

```text
                    UNTRUSTED
                       │
                       ▼
              ┌─────────────────┐
              │   HTTP Request  │
              └────────┬────────┘
                       │
                       │ Bearer JWT
                       ▼
              ┌─────────────────┐
              │ Authentication  │
              │    Boundary     │
              └────────┬────────┘
                       │
                       │ validated identity
                       ▼
              ┌─────────────────┐
              │ Trusted Request │
              │    Context      │
              └────────┬────────┘
                       │
                       ▼
              Authorization / RBAC
```

No protected application service should execute before the authentication boundary has established an authenticated identity.

---

# 5. Responsibilities of the Authentication Boundary

The authentication boundary is responsible for:

1. Extracting the bearer token.
2. Validating the token.
3. Establishing the authenticated Supabase user identity.
4. Rejecting missing authentication.
5. Rejecting invalid authentication.
6. Rejecting expired authentication.
7. Resolving the corresponding professional profile.
8. Establishing the authenticated execution identity.
9. Resolving the active hospital/tenant.
10. Passing trusted identity information to authorization.

It is **not** responsible for making clinical decisions.

It is also not responsible for deciding whether a user has a particular application permission.

Those belong to later authorization layers.

---

# 6. Authentication vs Authorization

These concerns must remain separate.

### Authentication answers:

> **Who is this user?**

Example:

```text
auth_user_id
    ↓
professional_profile
```

### Authorization answers:

> **What is this authenticated user allowed to do?**

Example:

```text
professional
    ↓
hospital membership
    ↓
roles
    ↓
permissions
```

Therefore:

```text
Authentication
        ↓
Identity
        ↓
Tenant
        ↓
Authorization
        ↓
Permission
```

---

# 7. Trusted Identity

After successful authentication, the backend should establish an internal trusted identity representation.

Conceptually:

```python
ExecutionIdentity(
    auth_user_id=...,
    professional_id=...,
    hospital_id=...,
)
```

The exact implementation may differ from this example.

The important architectural rule is that these values are **server-derived**.

They must not originate from the request payload.

---

# 8. Professional Resolution

The backend resolves the authenticated professional using:

```text
auth_user_id
        ↓
professional_profiles.auth_user_id
```

Conceptually:

```sql
select *
from professional_profiles
where auth_user_id = <validated_supabase_user_id>;
```

If no corresponding professional profile exists, the request must not be treated as an authenticated PharmaTrybe professional request.

Authentication with Supabase therefore does not automatically imply application access.

There are two distinct states:

```text
Authenticated with Supabase
```

and

```text
Authenticated PharmaTrybe professional
```

The second requires the corresponding application identity.

---

# 9. Tenant Resolution

Once the professional has been identified, the backend must establish the user's hospital context.

The project's identity architecture establishes:

```text
One professional
        ↓
One active hospital membership
        ↓
One active hospital
```

The database already exposes:

```text
public.current_hospital_id()
```

which resolves the active hospital using the authenticated Supabase identity.

The backend should therefore **not independently invent a competing tenant-resolution mechanism**.

The database remains authoritative for tenant enforcement.

---

# 10. Database Authority

The existing function:

```sql
public.current_hospital_id()
```

uses:

```text
auth.uid()
    ↓
professional_profiles.auth_user_id
    ↓
hospital_memberships.professional_id
    ↓
hospital_memberships.hospital_id
```

and restricts membership to:

```text
status = 'ACTIVE'
```

This creates an important architectural boundary:

```text
Supabase Auth
      │
      ▼
auth.uid()
      │
      ▼
Database identity resolution
      │
      ▼
Active hospital
      │
      ▼
RLS
```

The backend should cooperate with this model rather than bypass it.

---

# 11. Service-Role Restriction

The authentication boundary must not use a Supabase service-role connection as a substitute for user authentication.

A service-role connection bypasses normal Row Level Security protections.

Therefore:

```text
User request
    │
    ▼
Authenticated user context
    │
    ▼
RLS-protected database access
```

is the normal path.

A privileged service-role connection, if required by a specific trusted backend operation, must be treated as a separate privileged execution path and must never cause the backend to assume that the caller is authorized.

---

# 12. Client-Supplied Hospital ID

A client may send:

```json
{
  "hospital_id": "..."
}
```

for legitimate application purposes.

However:

> **The presence of `hospital_id` in a request does not establish tenant authorization.**

For protected tenant resources, authorization must be based on the authenticated execution context and database RLS.

For example:

```text
Client says:
hospital_id = Hospital B

        ↓

Backend does NOT trust this as proof

        ↓

Authenticated user
        ↓
Database tenant resolution
        ↓
RLS
        ↓
Allowed / denied
```

---

# 13. Authentication Failure Conditions

The authentication boundary should reject requests when:

### 13.1 No Authorization header

```text
401 Unauthorized
```

### 13.2 Malformed bearer token

```text
401 Unauthorized
```

### 13.3 Invalid JWT

```text
401 Unauthorized
```

### 13.4 Expired JWT

```text
401 Unauthorized
```

### 13.5 Authenticated user has no professional profile

The application should reject access to protected professional endpoints.

This is an application identity failure rather than merely a missing JWT.

### 13.6 No active hospital membership

The professional is authenticated but does not currently have an active tenant context.

The protected tenant operation must therefore be rejected.

---

# 14. Authentication Must Precede RBAC

The order must remain:

```text
JWT Authentication
       ↓
Professional Identity
       ↓
Hospital/Tenant Context
       ↓
Role Resolution
       ↓
Permission Resolution
       ↓
Endpoint
```

Not:

```text
Request
   ↓
Role supplied by client
   ↓
Permission
```

and not:

```text
Request
   ↓
hospital_id supplied by client
   ↓
Authorization
```

---

# 15. FastAPI Dependency Boundary

The backend should expose a reusable authentication dependency conceptually equivalent to:

```python
get_current_identity()
```

Protected endpoints then depend upon the authenticated identity.

Conceptually:

```python
@router.get("/protected")
async def protected_endpoint(
    identity: ExecutionIdentity = Depends(get_current_identity),
):
    ...
```

The actual names should follow the existing backend conventions discovered during **10C.0**.

The important requirement is that authentication is centralized rather than independently implemented by every endpoint.

---

# 16. No Authentication Logic in Business Services

Business/application services should not independently parse:

```text
Authorization
Bearer tokens
JWT claims
```

Authentication belongs at the boundary.

Therefore:

```text
HTTP Layer
    │
    ├── Authentication
    │
    └── Authorization
          │
          ▼
Application Service
          │
          ▼
Domain Logic
```

This prevents authentication logic from becoming duplicated throughout the backend.

---

# 17. JWT Claims

JWT claims may provide useful identity information.

However, the backend must distinguish between:

### Authentication claims

Used to establish who authenticated.

and:

### Application authorization data

Such as:

```text
hospital_id
role
permission
professional_type
```

Application authorization should not depend solely on arbitrary client-controlled metadata.

The authoritative application relationships remain in the PharmaTrybe database.

---

# 18. RLS as the Final Tenant Enforcement Layer

The architecture intentionally uses multiple security boundaries.

```text
                 Client
                   │
                   ▼
             JWT Authentication
                   │
                   ▼
          Backend Authentication
                   │
                   ▼
          Backend Authorization
                   │
                   ▼
            Supabase/Postgres
                   │
                   ▼
                 RLS
```

Backend authorization improves application-level control.

RLS provides database-level isolation.

Neither should be treated as a replacement for the other.

---

# 19. Security Invariant

The following invariant must always hold:

> **A request can access tenant-scoped data only when the authenticated Supabase identity resolves to the appropriate active hospital membership and the database RLS policy permits the operation.**

This is the core authentication-to-tenant security boundary.

---

# 20. Authentication Boundary Contract

The authentication layer should ultimately provide the following trusted information to downstream authorization/application code:

```text
ExecutionIdentity

├── auth_user_id
├── professional_id
└── hospital_id
```

Potentially:

```text
├── authentication_status
└── membership_status
```

Role and permission information should remain part of the subsequent RBAC layer rather than being conflated with authentication.

---

# 21. Request Lifecycle

The resulting protected request lifecycle is:

```text
HTTP Request
     │
     ▼
Extract Bearer Token
     │
     ▼
Validate Supabase JWT
     │
     ├── invalid ───────► 401
     │
     ▼
auth_user_id
     │
     ▼
Resolve professional_profiles
     │
     ├── missing ───────► reject application access
     │
     ▼
Resolve active hospital membership
     │
     ├── none ──────────► reject tenant access
     │
     ▼
ExecutionIdentity
     │
     ▼
RBAC / Permission
     │
     ├── denied ────────► 403
     │
     ▼
Application Service
     │
     ▼
Database / RLS
     │
     ▼
Response
```

---

# 22. 10C.1 Decision

### Confirmed architectural direction

The PharmaTrybe backend will use a **centralized authentication boundary** based on Supabase Auth.

The boundary will:

* validate the Supabase JWT;
* establish `auth_user_id`;
* resolve the corresponding professional profile;
* establish the active hospital context;
* create a trusted execution identity;
* hand that identity to the authorization/RBAC layer.

Tenant authorization will remain anchored to the database identity model and RLS.

---

# 23. Explicit Non-Goals

10C.1 does **not** implement:

* Role resolution
* Permission resolution
* RBAC policy evaluation
* Clinical authorization
* Plugin authorization
* Clinical workflow authorization
* API endpoint-specific permissions

Those belong to the subsequent authorization/RBAC work.

---

# 24. Security Boundary Summary

The final architecture is:

```text
                    ┌─────────────────────┐
                    │       Client        │
                    └──────────┬──────────┘
                               │
                         Bearer JWT
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Authentication      │
                    │ Boundary            │
                    │                     │
                    │ JWT validation      │
                    │ auth_user_id        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Professional        │
                    │ Identity            │
                    │                     │
                    │ professional_id     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Tenant Resolution   │
                    │                     │
                    │ active hospital_id  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ RBAC / Authorization│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Application Services│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ PostgreSQL / RLS    │
                    └─────────────────────┘
```

This preserves the project's fundamental principle:

> **Authentication establishes identity; authorization establishes what that identity may do; RLS enforces tenant isolation at the database boundary.**

The existing plugin architecture is also consistent with this separation: the platform remains responsible for authentication and authorization, while plugins provide capabilities/evidence rather than bypassing platform security.  The SDK likewise places plugin execution behind the platform's Plugin Manager rather than allowing plugins to establish their own platform-level security boundary. 
