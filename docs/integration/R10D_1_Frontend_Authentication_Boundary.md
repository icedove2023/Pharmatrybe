# 10D.1 — Frontend Authentication Boundary

**Status:** Approved/ Documentation Baseline
**Phase:** 10D — Frontend Identity + RBAC Integration
**Document:** 10D.1
**Authority:** Supabase Authentication + Backend Authentication Boundary
**Security Principle:** Frontend authentication state is not authorization authority.

---

## 1. Purpose

This document defines the **frontend authentication boundary** for the AMR CDSS.

The purpose of this boundary is to establish how the frontend:

* establishes an authenticated session;
* restores an existing session;
* observes authentication changes;
* obtains the authenticated user's application identity;
* handles logout;
* handles expired or invalid sessions;
* handles inactive accounts;
* communicates authentication state to the rest of the frontend.

This document does **not** introduce a new authentication system.

The frontend consumes the existing authentication architecture established by the platform and the backend security architecture documented in 10C.

---

# 2. Architectural Principle

The frontend must distinguish between:

> **Authentication** — determining whether a user has a valid authenticated session.

and:

> **Authorization** — determining what that authenticated user is permitted to do.

Authentication is established through **Supabase Auth**.

Application identity and authorization information are obtained from the **backend**.

Therefore:

```text
Supabase Auth
      ↓
Authenticated Session
      ↓
Frontend
      ↓
/auth/me
      ↓
Backend-derived Application Identity
      ↓
Roles + Permissions
      ↓
Frontend UI Capabilities
```

The frontend must never become the authoritative source of authorization.

---

# 3. Security Boundary

The frontend authentication boundary is:

```text
┌─────────────────────────────┐
│        Supabase Auth        │
│                             │
│  Sign in                    │
│  Sign out                   │
│  Session                    │
│  Token refresh              │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          Frontend           │
│                             │
│  Session state              │
│  Authentication state       │
│  Loading state              │
│  Error state                │
└──────────────┬──────────────┘
               │
               │ authenticated JWT
               ▼
┌─────────────────────────────┐
│        FastAPI Backend      │
│                             │
│  JWT validation             │
│  Authenticated identity     │
│  Application identity       │
│  Tenant context             │
│  RBAC                       │
└──────────────┬──────────────┘
               │
               ▼
          /auth/me
               │
               ▼
┌─────────────────────────────┐
│    Frontend Identity State  │
│                             │
│  Professional               │
│  Hospital                   │
│  Membership                 │
│  Roles                      │
│  Permissions                │
└─────────────────────────────┘
```

The browser controls presentation and session interaction.

The backend controls security decisions.

---

# 4. Authentication Authority

## Confirmed Decision

Supabase Auth is the authentication authority for frontend users.

The frontend must use the existing Supabase authentication mechanism rather than implementing an independent:

* username/password system;
* JWT issuer;
* token-signing mechanism;
* session database;
* authentication authority.

The frontend should consume the Supabase session and access token.

---

# 5. Supabase Session

A successful login produces an authenticated Supabase session.

Conceptually:

```text
User
 ↓
Supabase Auth
 ↓
Authenticated Session
 ↓
Access Token
 ↓
Frontend
```

The frontend may use the session to determine:

```text
authenticated
unauthenticated
loading
```

However, the existence of a valid Supabase session alone does **not** establish that the user has an active AMR CDSS application identity.

Therefore:

```text
Supabase session exists
        ≠
Application access is authorized
```

The frontend must obtain application identity from the backend.

---

# 6. Application Identity Resolution

After authentication, the frontend must resolve the user's application identity through the backend.

The expected flow is:

```text
Supabase session
       ↓
Access token
       ↓
GET /auth/me
       ↓
Backend validates JWT
       ↓
Backend resolves application identity
       ↓
Frontend receives identity
```

The frontend must not reconstruct the application identity independently from arbitrary client-side information.

The backend remains responsible for resolving:

* authenticated user;
* professional profile;
* active hospital membership;
* hospital;
* roles;
* permissions.

---

# 7. Authentication State Model

The frontend should maintain an explicit authentication lifecycle.

The conceptual states are:

```text
INITIALIZING
      │
      ▼
SESSION_CHECK
      │
 ┌────┴─────┐
 ▼          ▼
NO_SESSION  SESSION_FOUND
 │               │
 ▼               ▼
SIGNED_OUT   RESOLVING_IDENTITY
                  │
             ┌────┴─────┐
             ▼           ▼
          IDENTITY     IDENTITY
          RESOLVED     FAILED
             │           │
             ▼           ▼
        AUTHENTICATED  ERROR/
                       INACTIVE/
                       FORBIDDEN
```

The exact frontend state-management mechanism is an implementation concern.

The state model itself should remain explicit.

---

# 8. Initial Application Load

When the frontend application starts:

```text
Application starts
       ↓
Restore Supabase session
       ↓
Does session exist?
       │
   ┌───┴────┐
   │        │
  NO       YES
   │        │
   ▼        ▼
Signed out  GET /auth/me
              │
              ▼
       Resolve application identity
```

The frontend must not immediately assume that a restored Supabase session grants application access.

It must resolve the backend identity first.

---

# 9. Session Restoration

An existing Supabase session may be restored when the application starts.

The frontend must:

1. restore the Supabase session;
2. obtain the current access token;
3. establish authenticated frontend state;
4. request `/auth/me`;
5. populate application identity;
6. expose the authenticated application state to the UI.

Conceptually:

```text
Persisted Supabase Session
          ↓
      Session Restore
          ↓
      Access Token
          ↓
       /auth/me
          ↓
 Application Identity
          ↓
       UI Ready
```

The frontend should not display protected application content as authorized before identity resolution is complete.

---

# 10. Login

The login flow is:

```text
User
 ↓
Login UI
 ↓
Supabase Auth
 ↓
Successful authentication
 ↓
Supabase session
 ↓
Access token
 ↓
/auth/me
 ↓
Application identity
 ↓
Authenticated application
```

Successful Supabase authentication is therefore only the first stage.

The frontend must subsequently resolve the application identity.

---

# 11. Login Failure

If authentication fails:

```text
Login
 ↓
Supabase Auth
 ↓
Authentication failure
```

The frontend must remain unauthenticated.

It must not:

* create a local authenticated state;
* invent an identity;
* retain stale identity from a previous user;
* grant application access.

The login error should be surfaced through the frontend's normal authentication error handling.

---

# 12. `/auth/me` Failure

Authentication and application identity resolution are separate boundaries.

Therefore:

```text
Supabase authentication succeeds
              ↓
          /auth/me
              ↓
            FAIL
```

must not result in an authenticated application state.

Depending on the backend response, the frontend should distinguish between:

* invalid/expired authentication;
* inactive account;
* missing application identity;
* forbidden application access;
* temporary backend failure.

The frontend must fail closed with respect to protected application access.

---

# 13. Inactive Account

A valid Supabase session does not necessarily mean that the user's application membership remains active.

For example:

```text
Supabase Session
      ↓
Valid
      ↓
Backend Identity Resolution
      ↓
Membership inactive
      ↓
Application access denied
```

The frontend must not treat a valid authentication token as sufficient to enter the protected application.

An inactive application identity must transition into an appropriate restricted state.

The frontend should:

* prevent protected application access;
* avoid presenting authorized controls;
* display an appropriate account-status message;
* preserve the distinction between authentication and application access.

The backend remains responsible for determining whether the account/membership is active.

---

# 14. Logout

Logout must terminate the frontend authentication state through the existing Supabase authentication mechanism.

Conceptually:

```text
Authenticated Application
        ↓
Logout
        ↓
Supabase Sign Out
        ↓
Session Removed
        ↓
Frontend Identity Cleared
        ↓
Protected Cache Cleared
        ↓
Signed Out
```

Logout must clear identity-dependent frontend state, including:

* application identity;
* hospital context;
* roles;
* permissions;
* capability state;
* protected query/cache state.

The frontend must not retain the previous user's application identity after logout.

---

# 15. Authentication Change Events

The frontend should observe authentication changes from the Supabase authentication layer.

Relevant events include, where supported by the existing Supabase integration:

* sign in;
* sign out;
* token refresh;
* session restoration;
* authentication state change.

The frontend must react to these events rather than assuming that the initial authentication state remains valid indefinitely.

---

# 16. Token Refresh

Supabase manages authentication token lifecycle.

The frontend must use the current valid access token when making protected backend requests.

Conceptually:

```text
Supabase Session
       ↓
Token Refresh
       ↓
Current Access Token
       ↓
Protected API Request
```

The frontend must not:

* manufacture JWTs;
* modify JWT claims;
* extend token expiration;
* treat an expired token as valid;
* use a stale token indefinitely.

If token refresh fails, the frontend should transition toward an unauthenticated state and clear protected identity state as appropriate.

---

# 17. Protected API Authentication

Every protected backend request must carry the authenticated user's access token through the established API mechanism.

Conceptually:

```text
Frontend
   │
   │ Authorization: Bearer <access_token>
   ▼
FastAPI
   │
   ▼
10C Authentication Boundary
```

The frontend does not decide whether the request is authorized.

It only supplies the authenticated credential.

The backend performs:

```text
JWT validation
      ↓
Execution identity
      ↓
Tenant context
      ↓
RBAC
      ↓
Allow / Deny
```

---

# 18. HTTP 401 Handling

A `401 Unauthorized` response indicates an authentication problem.

Examples include:

* missing credentials;
* invalid token;
* expired token;
* authentication failure.

The frontend should treat a terminal `401` as an authentication-state problem.

The expected behavior is:

```text
Protected API
      ↓
401
      ↓
Attempt normal session/token recovery where appropriate
      ↓
If authentication cannot be restored
      ↓
Clear application identity
      ↓
Return to unauthenticated state
```

The frontend must not attempt to bypass a `401`.

---

# 19. HTTP 403 Handling

A `403 Forbidden` response is different.

It means the request reached the backend with an authenticated identity but the operation was not permitted.

Conceptually:

```text
Authenticated
      ↓
Backend authorization
      ↓
403 Forbidden
```

The frontend should present an appropriate forbidden state.

It must **not** interpret `403` as permission to modify its own authorization state.

For example, it must not:

```text
403
 ↓
add permission locally
 ↓
retry
```

Backend authorization remains authoritative.

---

# 20. Frontend Role State

The frontend may expose role information for UI purposes after `/auth/me` resolves application identity.

For example:

```text
roles:
[
    "CLINICIAN"
]
```

However:

> Frontend role state is a representation of backend-derived identity, not an authorization authority.

The frontend must not allow users to modify:

* role;
* membership;
* hospital;
* permission;
* authorization context.

---

# 21. Frontend Permission State

Likewise, permissions obtained from `/auth/me` may be used for UI capability decisions.

Example:

```text
permissions:
[
    "cases:view",
    "cases:create",
    "recommendations:view"
]
```

The frontend may derive:

```text
canViewCases
canCreateCases
canViewRecommendations
```

These are **presentation capabilities**.

They do not replace backend authorization.

The backend must independently verify every protected operation.

---

# 22. No Client-Supplied Authorization Context

The frontend must never establish authorization by sending arbitrary identity information such as:

```text
hospital_id
user_id
membership_id
role
permissions
```

and expecting the backend to trust those values.

The security flow is:

```text
JWT
 ↓
Backend
 ↓
Authoritative identity resolution
 ↓
TenantContext
 ↓
RBAC
```

not:

```text
Browser
 ↓
hospital_id + role + permissions
 ↓
Backend
```

---

# 23. Hospital Identity Display

The frontend may display the authenticated user's hospital information.

However, that hospital identity must come from the authoritative backend application identity.

Conceptually:

```text
/auth/me
   ↓
hospital
   ↓
Hospital name displayed in UI
```

The frontend must not use a browser-supplied `hospital_id` to establish or change the user's security context.

---

# 24. Identity Change

Identity-dependent state must be invalidated whenever the authenticated identity changes.

Examples:

```text
User A
  ↓
Logout
  ↓
User B
```

or:

```text
Old session
  ↓
Session expires
  ↓
New authentication
```

The frontend must not allow cached state belonging to one authenticated identity to appear under another identity.

At minimum, identity changes should invalidate:

* application identity;
* roles;
* permissions;
* hospital context;
* protected API caches;
* protected clinical data;
* governance data;
* plugin administration data.

---

# 25. Authentication Boundary and Clinical Data

Because the AMR CDSS handles clinical workflows, authentication state must be established before protected clinical information is presented.

The frontend should not expose protected clinical resources while authentication or application identity resolution is incomplete.

The conceptual boundary is:

```text
Authentication
      ↓
Application Identity
      ↓
Authorization
      ↓
Protected Clinical Data
```

Authentication failure must therefore fail closed.

---

# 26. Security Responsibilities

### Frontend responsibilities

The frontend is responsible for:

* interacting with Supabase Auth;
* maintaining session state;
* restoring sessions;
* observing authentication changes;
* obtaining `/auth/me`;
* presenting authentication state;
* handling logout;
* handling authentication failures;
* presenting role/permission-aware UI;
* clearing identity-dependent state.

### Backend responsibilities

The backend remains responsible for:

* JWT validation;
* authenticated identity;
* professional resolution;
* membership resolution;
* hospital/tenant resolution;
* role resolution;
* permission resolution;
* authorization;
* resource-level security;
* cross-tenant protection.

---

# 27. Explicit Non-Responsibilities

10D.1 does **not** authorize the frontend to:

* validate application permissions independently;
* assign roles;
* assign memberships;
* select the authoritative hospital;
* override backend authorization;
* modify JWT claims;
* create authorization tokens;
* bypass the backend;
* trust client-supplied tenant identifiers.

---

# 28. Required Authentication Contract

The frontend authentication integration should ultimately provide an application-level interface conceptually equivalent to:

```text
auth state
    ↓
session
    ↓
application identity
    ↓
authenticated / unauthenticated / resolving / unavailable
```

The exact implementation names are deliberately left to the existing frontend architecture.

No new state-management framework or authentication abstraction should be introduced solely because of this document.

---

# 29. Validation Requirements

The implementation of 10D.1 must demonstrate that:

### Authentication

* unauthenticated users cannot enter protected application areas;
* successful Supabase authentication produces an application identity;
* invalid authentication is rejected;
* expired authentication is handled;
* logout clears authentication state.

### Identity

* `/auth/me` is used to establish application identity;
* application identity is not reconstructed from browser-controlled data;
* inactive identities do not receive protected application access.

### Session

* existing sessions are restored;
* authentication changes are observed;
* token refresh is handled;
* stale identity state is cleared.

### API

* protected requests use the authenticated access token;
* `401` is handled as an authentication problem;
* `403` is handled as an authorization/forbidden state.

### Security

* frontend state does not replace backend authorization;
* browser-supplied `hospital_id` is not treated as authoritative;
* roles and permissions are consumed as backend-derived information;
* identity changes invalidate protected cached state.

---

# 30. Architectural Invariant

The following invariant is mandatory:

> **A frontend session may establish that a user is authenticated, but only the backend may establish the user's authoritative application identity, tenant context, roles, permissions, and authorization.**

Therefore:

```text
Supabase
   ↓
Authentication
   ↓
Frontend
   ↓
/auth/me
   ↓
Backend-derived Identity
   ↓
UI Capability
```

while security remains:

```text
Frontend Request
       ↓
      JWT
       ↓
    Backend
       ↓
Authentication
       ↓
Execution Identity
       ↓
Tenant Context
       ↓
RBAC
       ↓
ALLOW / DENY
```

---

# 31. Relationship to 10C

10D.1 consumes the security boundaries established by 10C.

| 10C Backend Security      | 10D Frontend Integration                        |
| ------------------------- | ----------------------------------------------- |
| Authentication Boundary   | Supabase session + authenticated frontend state |
| Execution Identity        | `/auth/me` application identity                 |
| Tenant Context            | Backend-derived hospital identity               |
| Backend RBAC              | Frontend role/permission presentation           |
| Protected API Enforcement | Authenticated API requests                      |
| Security Tests            | Frontend authentication validation              |

10D does not modify the 10C security model.

It integrates the frontend with it.

---

# 32. Final Rule

The frontend may **know** the user's identity, roles, permissions, and hospital for the purpose of producing an appropriate user experience.

The frontend may **not decide** whether the user is authorized to perform a protected operation.

The authoritative security path remains:

```text
User
 ↓
Supabase Authentication
 ↓
JWT
 ↓
FastAPI
 ↓
Authentication
 ↓
Execution Identity
 ↓
Tenant Context
 ↓
Backend RBAC
 ↓
Protected Operation
```

**Frontend authorization is UX. Backend authorization is security.**
