# 10D.5 — Protected API Integration

## Status

**Confirmed Design Specification Approved**

This document defines how the frontend consumes protected backend APIs after authentication and identity resolution.

It does **not** introduce a new authorization model.

The backend remains the authoritative security boundary.

---

## 1. Purpose

10D.5 defines the frontend contract for calling protected backend APIs using the authenticated Supabase session.

The frontend must:

* obtain the current authenticated session;
* obtain the authoritative backend identity through `/auth/me`;
* attach the current access token to protected API requests;
* allow the backend to resolve identity, tenant, roles, and permissions;
* handle authentication and authorization failures consistently;
* prevent stale identity state from being used after session changes.

The frontend must **not** independently reproduce backend authorization logic.

---

# 2. Security Boundary

The protected request flow is:

```text
Frontend
   │
   │ Supabase access token
   ▼
Backend API
   │
   ├── JWT validation
   │
   ├── authenticated identity
   │
   ├── execution identity
   │
   ├── tenant context
   │
   ├── roles
   │
   └── permissions
   │
   ▼
Authorization decision
   │
   ├── ALLOW
   │
   └── DENY
```

The frontend may use roles and permissions to control the user interface, but the backend must independently enforce every protected operation.

Therefore:

> **Frontend authorization is UX. Backend authorization is security.**

---

# 3. Authentication Token

Protected API requests must use the authenticated Supabase access token.

The frontend request should conceptually contain:

```http
Authorization: Bearer <supabase-access-token>
```

The frontend must not construct or modify JWT claims.

The frontend must not send:

```http
X-User-Id
X-Professional-Id
X-Hospital-Id
X-Role
X-Permissions
```

as authoritative security identity.

These values must be derived by the backend.

---

# 4. Authoritative Identity

The frontend should establish identity through:

```text
Supabase Session
      ↓
Access Token
      ↓
GET /auth/me
      ↓
Backend identity resolution
      ↓
Authoritative user context
```

The `/auth/me` response is the frontend's authoritative source for application identity.

It should provide the identity information required by the frontend, including the resolved:

* authenticated user;
* professional identity;
* active hospital membership;
* hospital context;
* roles;
* permissions/capabilities;
* account/membership status.

The exact response shape must follow the existing backend contract.

The frontend must not infer these values from browser state.

---

# 5. Protected Request Contract

A protected API request follows:

```text
User interaction
      ↓
Frontend API client
      ↓
Retrieve current Supabase session
      ↓
Attach access token
      ↓
Backend API
      ↓
Authentication
      ↓
Execution identity
      ↓
Tenant context
      ↓
RBAC
      ↓
Endpoint operation
```

The frontend API client should centralize this behaviour rather than requiring individual components to manually construct authorization headers.

---

# 6. Central API Client

Protected API calls should use a shared frontend API client.

Conceptually:

```text
apiClient
   │
   ├── get()
   ├── post()
   ├── put()
   ├── patch()
   └── delete()
```

The client is responsible for:

1. obtaining the current session;
2. attaching the access token;
3. sending the request;
4. interpreting authentication failures;
5. interpreting authorization failures;
6. returning structured API errors to the UI.

Individual UI components should not implement their own JWT handling.

---

# 7. Token Handling

The frontend must use the Supabase authentication session as the source of the access token.

The frontend must not:

* decode a JWT and treat its claims as authoritative authorization;
* manually construct tokens;
* persist tokens in arbitrary application state;
* copy tokens into component state;
* pass tokens through URL parameters;
* use a user-supplied token as identity.

The backend remains responsible for validating the token.

---

# 8. Session Changes

Protected API access must respond to authentication state changes.

The relevant lifecycle is:

```text
SIGNED IN
   ↓
Identity loaded
   ↓
Protected API available
```

and:

```text
SIGNED OUT
   ↓
Identity cleared
   ↓
Capability state cleared
   ↓
Protected API requests unavailable
```

Likewise:

```text
SESSION REFRESH
      ↓
new access token
      ↓
API client uses current token
```

The API client must not continue using an expired or stale token after a session refresh.

---

# 9. Authentication Failure

When the backend reports that authentication is missing or invalid, the frontend must treat the request as unauthenticated.

Typical backend response:

```http
401 Unauthorized
```

The frontend should:

```text
401
 ↓
invalidate authentication-dependent state
 ↓
refresh/reload session where appropriate
 ↓
redirect/show authentication UI
```

The frontend must not attempt to bypass the authentication boundary.

---

# 10. Forbidden Request

A successfully authenticated user may still lack permission for an operation.

The backend should reject such requests.

Typical response:

```http
403 Forbidden
```

The frontend must distinguish:

```text
401 Unauthorized
```

from:

```text
403 Forbidden
```

### 401

Means:

> The frontend does not currently have a valid authenticated identity.

### 403

Means:

> The authenticated identity exists, but the backend does not permit the requested operation.

The frontend should display an appropriate forbidden/insufficient-permission state.

It must not retry the operation using a different client-supplied identity.

---

# 11. Tenant Enforcement

The frontend must not use a browser-supplied `hospital_id` to establish tenant authority.

Incorrect:

```text
Frontend
   ↓
POST /api/resource
hospital_id = selectedHospital
```

where the backend trusts the supplied value.

Correct:

```text
Frontend
   ↓
JWT
   ↓
Backend
   ↓
Authenticated user
   ↓
Professional profile
   ↓
Hospital membership
   ↓
TenantContext
   ↓
Authorization
```

If a request contains a hospital identifier for a legitimate resource or business operation, the backend must still validate it against the authoritative tenant context.

---

# 12. Cross-Tenant Requests

The frontend must not attempt to access another hospital's resources by changing identifiers in the request.

For example:

```text
Hospital A user
       ↓
Frontend
       ↓
hospital_id = Hospital B
```

must not result in access to Hospital B.

Expected behaviour:

```text
Backend TenantContext
        ↓
Hospital A
        ↓
Requested resource
        ↓
Hospital B
        ↓
DENY
```

The frontend should surface the resulting authorization/tenant error appropriately.

---

# 13. Permission-Aware Requests

Frontend capability state may prevent an obviously unauthorized action from being presented.

For example:

```text
permissions:
[
  "cases:view",
  "cases:create"
]
```

may cause the frontend to show:

```text
Create Case
```

while hiding or disabling administrative operations.

However:

> Hiding a control is not authorization.

A user may still invoke an endpoint manually.

Therefore every protected backend operation must independently perform its permission check.

---

# 14. API Request Example

Conceptually:

```text
Frontend
   │
   │ POST /api/clinical-cases
   │ Authorization: Bearer <access_token>
   ▼
Backend
   │
   ├── authenticate
   ├── resolve identity
   ├── resolve tenant
   ├── resolve permissions
   ├── check cases:create
   │
   ├── ALLOW → create case
   │
   └── DENY → 403
```

The frontend does not send:

```json
{
  "user_id": "...",
  "hospital_id": "...",
  "role": "CLINICIAN"
}
```

as the security authority.

---

# 15. Identity Change and Cache Invalidation

Identity-dependent frontend state must be invalidated when the authenticated identity changes.

This includes:

* `/auth/me` response;
* roles;
* permissions;
* hospital identity;
* professional profile;
* navigation state;
* capability state;
* protected resource caches.

For example:

```text
User A
  ↓
Hospital A
  ↓
cached permissions/resources
```

followed by:

```text
logout
  ↓
login as User B
  ↓
Hospital B
```

must not leave User B with User A's cached authorization or tenant data.

Required principle:

> **Identity changes invalidate identity-scoped application state.**

---

# 16. Request Race Conditions

The frontend should avoid issuing protected requests using stale identity state during authentication transitions.

For example:

```text
User A session
      ↓
logout
      ↓
login User B
```

Requests associated with User A must not continue to populate caches used by User B.

Identity-scoped requests should therefore be associated with the current authentication/session lifecycle.

---

# 17. Loading State

Protected UI should distinguish between:

```text
AUTH_LOADING
```

```text
AUTHENTICATED
```

```text
UNAUTHENTICATED
```

```text
FORBIDDEN
```

rather than assuming that absence of identity during startup means the user is unauthenticated.

Recommended flow:

```text
Application startup
       ↓
Restore Supabase session
       ↓
Session?
 ┌─────┴─────┐
No          Yes
│            │
Login       /auth/me
             │
             ▼
       Identity resolved
             │
             ▼
       Application ready
```

---

# 18. Protected Route Integration

Frontend routes requiring authentication should depend on the resolved authentication state.

Conceptually:

```text
Protected Route
      ↓
Session available?
      │
   ┌──┴──┐
  No    Yes
  │      │
Login   /auth/me
         │
         ▼
    identity valid?
      │
   ┌──┴──┐
  No    Yes
  │      │
Error   Render
```

Role or permission checks may further control UI access, but backend APIs remain the final authority.

---

# 19. Error Handling

The frontend API layer should normalize backend errors into predictable application states.

At minimum:

| Backend condition | Frontend meaning                |
| ----------------- | ------------------------------- |
| `401`             | Authentication required/invalid |
| `403`             | Authenticated but forbidden     |
| `404`             | Resource not found              |
| `409`             | Contract/state conflict         |
| `422`             | Validation failure              |
| `429`             | Rate/resource limitation        |
| `5xx`             | Backend/server failure          |

The frontend must not reinterpret a `403` as successful authorization.

---

# 20. No Client-Side Authorization Bypass

The following patterns are prohibited:

```text
if (user.role === "ADMIN") {
    assume backend will allow request
}
```

as a security mechanism.

Also prohibited:

```text
localStorage.role = "HOSPITAL_ADMIN"
```

or:

```text
localStorage.permissions = [...]
```

being treated as authoritative security state.

Client-side capability information is only for UX.

---

# 21. Required Integration Layers

The frontend implementation should maintain a clear separation between:

```text
Authentication
      ↓
Session
      ↓
Identity
      ↓
Capabilities
      ↓
API Client
      ↓
UI
```

Recommended conceptual modules:

```text
auth/
session/
identity/
capabilities/
api/
```

The exact directory structure should follow the existing frontend architecture rather than introducing unnecessary duplication.

---

# 22. Relationship to 10D.1–10D.4

10D.5 consumes the outputs established by the previous specifications.

```text
10D.1
Frontend Authentication Boundary
        ↓
10D.2
Frontend Execution Identity / Session State
        ↓
10D.3
Frontend Tenant / Hospital Context
        ↓
10D.4
Frontend RBAC / Capability Resolution
        ↓
10D.5
Protected API Integration
```

The complete frontend security flow is therefore:

```text
Supabase Auth
      ↓
Session
      ↓
/auth/me
      ↓
Execution Identity
      ↓
Hospital/Tenant Context
      ↓
Roles + Permissions
      ↓
Frontend Capabilities
      ↓
Protected API Request
      ↓
Backend Authorization
      ↓
Resource
```

---

# 23. Backend Authority Rule

The central rule of 10D.5 is:

> **The frontend consumes authorization information; it does not grant authorization.**

The frontend may determine:

```text
Should I show this button?
Should I show this navigation item?
Should I render this page?
```

The backend determines:

```text
May this authenticated identity perform this operation?
```

---

# 24. Acceptance Criteria

10D.5 is satisfied when:

* [ ] Protected API requests use the current Supabase access token.
* [ ] Authorization headers are centrally managed.
* [ ] `/auth/me` is used as the authoritative application identity source.
* [ ] Frontend components do not independently implement JWT handling.
* [ ] `401` responses are handled as authentication failures.
* [ ] `403` responses are handled as authorization failures.
* [ ] Frontend does not establish tenant authority from `hospital_id`.
* [ ] Cross-tenant requests cannot be authorized by frontend state.
* [ ] Identity changes invalidate identity-scoped caches.
* [ ] Session refreshes update the token used by protected requests.
* [ ] Stale authentication state cannot authorize protected UI operations.
* [ ] Backend authorization remains authoritative.
* [ ] No client-side role/permission state is treated as a security boundary.
* [ ] Protected API integration is covered by validation tests.

---

# 25. Validation Principle

10D.5 is a **frontend/backend integration specification**, not a replacement for backend security testing.

The implementation must demonstrate that:

```text
Valid session
      +
Valid tenant context
      +
Required permission
      ↓
API succeeds
```

while:

```text
No session
      ↓
401
```

```text
Authenticated
+
Missing permission
      ↓
403
```

and:

```text
Authenticated Hospital A
+
Hospital B resource
      ↓
DENIED
```

The backend must remain responsible for all three security decisions.

---

## Final Architectural Statement

10D.5 completes the protected API boundary for the frontend:

```text
                  FRONTEND
                     │
              Supabase Session
                     │
                     ▼
                 /auth/me
                     │
                     ▼
        Identity + Tenant + Capabilities
                     │
                     ▼
              Shared API Client
                     │
               Bearer Token
                     │
═════════════════════╪════════════════════
                  BACKEND
                     │
                JWT Validation
                     │
              Execution Identity
                     │
                TenantContext
                     │
                    RBAC
                     │
              Endpoint Policy
                     │
                     ▼
                  Resource
```

**No frontend state crosses the boundary as an authority. The backend remains the final security decision-maker.**
