# 10D.6 — Frontend Identity Security Tests

````markdown
# 10D.6 — Frontend Identity Security Tests

**Phase:** 10D — Frontend Identity + RBAC Integration  
**Status:** Specification   Approved 
**Type:** Validation / Test Specification  
**Authority:** 10D Frontend Identity + RBAC Integration  
**Depends On:**
- 10D.1 — Frontend Authentication Boundary
- 10D.2 — Frontend Execution Identity Session State
- 10D.3 — Frontend Tenant / Hospital Context
- 10D.4 — Frontend RBAC / Capability Resolution
- 10D.5 — Protected API Integration
- 10C.1 — Authentication Boundary
- 10C.2 — Execution Identity
- 10C.3 — Tenant Context
- 10C.4 — Backend RBAC
- 10C.5 — Protected API Enforcement

---

## 1. Purpose

This document defines the validation and test requirements for the frontend identity and authorization integration implemented in Phase 10D.

The purpose is to verify that the frontend correctly consumes the backend's authoritative identity and authorization context.

The tests must establish that:

- authentication is derived from the real Supabase session;
- session state is restored correctly;
- `/auth/me` is treated as the authoritative application identity source;
- execution identity is not invented or derived from browser-controlled values;
- hospital context is derived from the authenticated backend identity;
- roles and permissions are consumed from the backend;
- frontend capabilities are derived from permissions;
- protected API requests carry the authenticated session;
- authentication failures are handled safely;
- inactive accounts are handled safely;
- forbidden responses are handled safely;
- identity changes invalidate stale frontend state;
- stale tenant, role, or permission information cannot remain active after identity changes;
- frontend authorization remains a UX concern and never becomes the security boundary.

---

# 2. Security Principle

The frontend must never become the authoritative authorization layer.

The architectural boundary is:

```text
Supabase Authentication
        ↓
Authenticated Session
        ↓
Backend /auth/me
        ↓
Authoritative Identity
        ↓
Authoritative Membership
        ↓
Authoritative Hospital
        ↓
Authoritative Roles
        ↓
Authoritative Permissions
        ↓
Frontend Capability State
        ↓
UI behaviour
````

The frontend may hide, show, enable, disable, or navigate UI elements based on capabilities.

However:

```text
Frontend capability
        ≠
Security authorization
```

Backend authorization remains authoritative.

Therefore, a frontend test passing does not prove that an endpoint is secure.

Backend security remains governed by the 10C security architecture.

---

# 3. Test Scope

The 10D.6 test suite covers the following boundaries:

```text
10D.1 Authentication Boundary
10D.2 Execution Identity Session State
10D.3 Tenant / Hospital Context
10D.4 RBAC / Capability Resolution
10D.5 Protected API Integration
```

The test suite must validate both:

### Positive behaviour

Correctly authenticated and authorized users can use the appropriate frontend functionality.

### Negative behaviour

Invalid, stale, missing, or insufficient identity information cannot cause the frontend to treat a user as authenticated or authorized.

---

# 4. Test Categories

The implementation should contain tests covering:

1. Authentication state
2. Session restoration
3. Session refresh
4. Logout
5. `/auth/me` resolution
6. Inactive account handling
7. Execution identity state
8. Hospital context
9. Role resolution
10. Permission resolution
11. Capability resolution
12. Protected API requests
13. Unauthorized responses
14. Forbidden responses
15. Identity-change cache invalidation
16. Tenant-change protection
17. Role/permission state invalidation
18. UI authorization behaviour
19. Cross-tenant frontend protection
20. Backend-authority preservation

---

# 5. Authentication Boundary Tests

## 5.1 No Session

Given:

```text
Supabase session = null
```

Expected:

```text
authenticated = false
```

The frontend must not create an application identity from:

* local storage values;
* previously cached `/auth/me`;
* browser state;
* route parameters;
* query parameters;
* manually supplied user IDs.

Expected behaviour:

```text
No session
    ↓
Unauthenticated frontend state
```

---

## 5.2 Valid Session

Given a valid Supabase session:

```text
session.user.id = authenticated user
session.access_token = valid JWT
```

Expected:

```text
session restored
        ↓
/auth/me requested
        ↓
authoritative identity loaded
```

The frontend must not consider the user fully application-authenticated solely because a Supabase session exists.

The application identity must be resolved through the backend contract.

---

## 5.3 Invalid Session

If the Supabase session is invalid or cannot be restored:

Expected:

```text
authenticated = false
identity = null
hospital = null
roles = []
permissions = []
capabilities = []
```

No protected application state should remain active.

---

## 5.4 Expired Session

When the access token expires:

Expected behaviour:

```text
expired access token
        ↓
Supabase/session refresh
        ↓
new valid session
        ↓
/auth/me revalidation
```

If refresh fails:

```text
authenticated = false
```

Protected application state must be cleared.

---

# 6. `/auth/me` Tests

The backend `/auth/me` endpoint is the authoritative application identity source.

Tests must verify that the frontend:

1. requests `/auth/me` after authentication;
2. stores the returned identity;
3. derives hospital context from the returned identity;
4. derives roles from the returned identity;
5. derives permissions from the returned identity;
6. derives capabilities from permissions;
7. does not independently reconstruct authorization from browser state.

---

## 6.1 Successful `/auth/me`

Given a valid backend response:

```json
{
  "user": {},
  "professional": {},
  "membership": {},
  "hospital": {},
  "roles": [],
  "permissions": []
}
```

Expected:

```text
identity state populated
hospital context populated
roles populated
permissions populated
capabilities derived
```

---

## 6.2 `/auth/me` Unauthorized

If `/auth/me` returns:

```text
401 Unauthorized
```

Expected:

```text
session/application identity invalid
```

The frontend must not continue using the previous authenticated identity.

Expected state:

```text
identity = null
hospital = null
roles = []
permissions = []
capabilities = []
```

---

## 6.3 `/auth/me` Forbidden / Inactive

If the backend indicates that the authenticated account is inactive or no longer has an active membership:

Expected:

```text
application access denied
```

The frontend must not manufacture an active hospital context.

---

# 7. Execution Identity Tests

The frontend execution identity must be derived from the backend identity contract.

It must not accept:

```text
user_id
professional_id
membership_id
hospital_id
role
permissions
```

from arbitrary client-controlled sources as authoritative identity.

Tests must verify that route or request data cannot overwrite the authenticated identity.

---

## 7.1 User Identity Consistency

Given:

```text
Supabase user A
/auth/me → user A
```

Expected:

```text
currentUser.id = user A
```

A browser-supplied:

```text
user_id = user B
```

must not change the frontend execution identity.

---

## 7.2 Professional Identity Consistency

The frontend must consume the professional identity returned by the backend.

It must not infer the professional identity from:

* URL parameters;
* form fields;
* local storage;
* manually entered IDs.

---

# 8. Tenant / Hospital Context Tests

The hospital context must originate from the authoritative backend identity.

Expected architecture:

```text
/auth/me
   ↓
membership
   ↓
hospital
   ↓
frontend hospital context
```

---

## 8.1 Hospital Context Loaded

Given an authenticated user with:

```text
active membership
hospital A
```

Expected:

```text
currentHospital = Hospital A
```

---

## 8.2 Browser Hospital Spoofing

Given:

```text
authenticated user → Hospital A
```

and the browser attempts:

```text
hospital_id = Hospital B
```

Expected:

```text
frontend identity remains Hospital A
```

The frontend must not treat Hospital B as the authenticated tenant.

---

## 8.3 Hospital Context Must Not Be Independently Trusted

The following must not become authoritative tenant state:

```text
localStorage.hospital_id
URL hospital_id
query.hospital_id
form hospital_id
React state manually set by UI
```

Such values may exist for non-authoritative UI purposes where appropriate, but they must never override backend identity.

---

# 9. Role Resolution Tests

Roles must be consumed from the backend authorization context.

The frontend must not invent a role model that differs from the canonical backend RBAC model.

The canonical roles currently include:

```text
HOSPITAL_ADMIN
CLINICIAN
PHARMACIST
INFECTIOUS_DISEASE_SPECIALIST
LABORATORY_SCIENTIST
RESEARCHER
```

Tests must verify that the frontend correctly represents the roles returned by `/auth/me`.

---

## 9.1 Role Loaded

Given:

```text
roles = ["CLINICIAN"]
```

Expected:

```text
frontend roles contains CLINICIAN
```

---

## 9.2 Multiple Roles

If the backend returns multiple roles, the frontend must preserve the complete returned set.

The frontend must not arbitrarily collapse multiple backend roles into one role unless such behaviour is explicitly defined elsewhere.

---

## 9.3 Unknown Role

If the backend returns a role that the frontend does not recognize:

Expected:

```text
role preserved as backend data where safe
```

but no unsupported frontend privilege should automatically be granted.

Unknown roles must fail closed for capability mapping.

---

# 10. Permission Resolution Tests

Permissions must be consumed from the backend.

The frontend must not reconstruct the permission graph independently.

Examples of canonical permissions include:

```text
cases:create
cases:view
cases:update

patients:create
patients:view

laboratory:create
laboratory:view

recommendations:request
recommendations:view
recommendations:review

professionals:view
professionals:invite
professionals:manage

roles:assign

plugins:view
plugins:configure

hospital:view
hospital:update

guidelines:view
guidelines:manage

stewardship:view
stewardship:manage

workflows:execute
workflows:manage

audit:view
data:export
```

The test suite should use the actual permission codes exposed by the backend rather than introducing synthetic permissions.

---

## 10.1 Permission Loaded

Given:

```text
permissions = [
    "cases:view",
    "recommendations:request"
]
```

Expected:

```text
hasPermission("cases:view") = true
hasPermission("recommendations:request") = true
```

---

## 10.2 Permission Not Granted

Given:

```text
permissions = [
    "cases:view"
]
```

Expected:

```text
hasPermission("plugins:configure") = false
```

The frontend must not infer the missing permission merely because the user has a particular role.

---

# 11. Capability Resolution Tests

Frontend capabilities are derived from backend permissions.

Example:

```text
permission
    ↓
capability
    ↓
UI decision
```

A capability resolver may provide helpers such as:

```text
can("cases:view")
can("cases:create")
can("recommendations:request")
can("plugins:configure")
```

The exact implementation may vary.

The security requirement does not.

---

## 11.1 Granted Capability

Given:

```text
permissions contains cases:create
```

Expected:

```text
can("cases:create") = true
```

---

## 11.2 Denied Capability

Given:

```text
permissions does not contain cases:create
```

Expected:

```text
can("cases:create") = false
```

---

## 11.3 Capability Cannot Grant Backend Permission

The frontend must never use:

```text
can("plugins:configure")
```

as proof that the backend will authorize the request.

The backend must perform its own permission check.

---

# 12. Protected API Request Tests

Protected API requests must use the authenticated session.

Expected flow:

```text
Frontend
   ↓
Supabase access token
   ↓
Authorization: Bearer <token>
   ↓
Backend
   ↓
Authentication
   ↓
Execution identity
   ↓
Tenant context
   ↓
RBAC
   ↓
Endpoint
```

---

## 12.1 Authenticated Request

Given a valid session:

Expected request:

```http
Authorization: Bearer <valid-access-token>
```

The token must come from the active Supabase session.

---

## 12.2 Unauthenticated Request

Given no authenticated session:

Expected:

```text
protected request is rejected or redirected
```

The frontend must not send fabricated identity headers.

---

## 12.3 No Client-Supplied Authorization

The frontend must not attempt to authorize itself by sending:

```http
X-Role: HOSPITAL_ADMIN
X-Permission: plugins:configure
X-Hospital-ID: hospital-b
X-User-ID: user-b
```

as a substitute for backend authentication and authorization.

---

# 13. Forbidden Response Tests

If the backend returns:

```text
403 Forbidden
```

the frontend must interpret this as an authorization failure.

Expected behaviour may include:

```text
permission denied message
access denied state
disable/restrict the relevant UI
```

It must not:

```text
retry with a different role
change hospital_id
change user_id
invent permissions
bypass the endpoint
```

---

# 14. Unauthorized Response Tests

If the backend returns:

```text
401 Unauthorized
```

the frontend should treat the session as invalid or requiring reauthentication/refresh according to the authentication implementation.

Expected state after unrecoverable authentication failure:

```text
identity = null
hospital = null
roles = []
permissions = []
capabilities = []
```

---

# 15. Identity Change Tests

Identity changes are security-sensitive state transitions.

The frontend must invalidate identity-dependent state when the authenticated user changes.

Example:

```text
User A
Hospital A
Roles A
Permissions A
```

changes to:

```text
User B
Hospital B
Roles B
Permissions B
```

Expected:

```text
User A state cleared
        ↓
User B session
        ↓
/auth/me
        ↓
User B identity
        ↓
Hospital B
        ↓
Roles B
        ↓
Permissions B
        ↓
Capabilities B
```

---

# 16. Logout Tests

On logout:

```text
Supabase session
        ↓
signed out
```

Expected frontend state:

```text
currentUser = null
professional = null
membership = null
hospital = null
roles = []
permissions = []
capabilities = []
```

Cached protected API data must also be invalidated where applicable.

---

# 17. Session Refresh Tests

A successful token refresh must not blindly preserve stale authorization state.

Expected:

```text
session refresh
      ↓
identity revalidation where required
      ↓
current authorization state
```

If backend identity changes after refresh, the frontend must update accordingly.

---

# 18. Inactive Account Tests

Given an authenticated identity whose membership/account is inactive:

Expected:

```text
authenticated session may exist
BUT
application authorization unavailable
```

The frontend must not treat:

```text
Supabase session exists
```

as equivalent to:

```text
application access granted
```

The UI should enter an appropriate inactive/blocked state.

---

# 19. Role-Aware Navigation Tests

Navigation may be filtered according to capabilities.

Example:

```text
plugins:configure
```

may permit the frontend to display plugin administration navigation.

If the permission is absent:

```text
plugin administration navigation hidden or disabled
```

However, manually navigating to the route must still result in backend enforcement.

Therefore:

```text
Hidden navigation
        ≠
Security protection
```

---

# 20. Permission-Aware Controls

Controls such as:

```text
Create
Edit
Approve
Configure
Activate
Disable
Export
Manage
```

may be conditionally rendered based on permissions.

Tests should verify that:

```text
permission present → control available
permission absent → control unavailable/hidden
```

But the underlying API must remain protected.

---

# 21. Cache Invalidation Tests

Identity-dependent caches must be invalidated when:

* logout occurs;
* authenticated user changes;
* hospital context changes;
* membership becomes inactive;
* `/auth/me` changes;
* permissions change;
* session becomes invalid.

Protected cached data must never leak from one identity or tenant context into another.

Example:

```text
Hospital A data
        ↓
logout
        ↓
Hospital B login
        ↓
Hospital A cached data MUST NOT remain available
```

---

# 22. Cross-Tenant UI Tests

The frontend must correctly reflect the tenant returned by the backend.

Example:

```text
User A
Hospital A
```

must not display:

```text
Hospital B
```

because a browser-controlled value requested it.

If an API request attempts to access Hospital B resources and the backend rejects it:

```text
403 Forbidden
```

the frontend must preserve the backend denial.

---

# 23. Stale Authorization Tests

The frontend must not retain permissions after authorization state changes.

Example:

```text
User has:

plugins:configure
```

Then backend authorization changes and the user no longer has the permission.

After identity revalidation:

```text
can("plugins:configure") = false
```

The frontend must not continue displaying the old privileged state indefinitely.

---

# 24. Frontend Tampering Tests

Tests should simulate modification of frontend state.

Examples:

```text
role = HOSPITAL_ADMIN
permissions = ["plugins:configure"]
hospital = Hospital B
```

The frontend may be manipulated in development/browser tooling.

This must not grant backend access.

The test should verify that:

```text
tampered frontend state
        ↓
protected API
        ↓
backend authorization
        ↓
DENIED
```

This test explicitly demonstrates the architectural rule:

> Frontend authorization is UX, never security.

---

# 25. Test Fixtures

Tests should use realistic identity fixtures based on the canonical backend model.

A fixture should represent:

```text
Authenticated User
        ↓
Professional Profile
        ↓
Hospital Membership
        ↓
Hospital
        ↓
Roles
        ↓
Permissions
```

Where possible, fixtures should use the existing application/backend contracts rather than inventing parallel identity structures.

---

# 26. Mocking Rules

Frontend unit tests may mock:

* Supabase session responses;
* `/auth/me` responses;
* protected API responses.

However, mocks must follow the actual backend contract.

Do not create synthetic contracts solely to make tests pass.

For example, do not invent:

```text
GET /user/permissions
```

if the actual architecture uses:

```text
GET /auth/me
```

Similarly, do not invent frontend-only role authorities that contradict the backend RBAC model.

---

# 27. Integration Tests

Where practical, integration tests should verify:

```text
Supabase session
      ↓
frontend auth state
      ↓
/auth/me
      ↓
identity context
      ↓
capability resolver
      ↓
protected API
```

The test should verify that the components work together rather than only testing isolated helper functions.

---

# 28. Minimum Required Test Matrix

| Test                | Expected                             |
| ------------------- | ------------------------------------ |
| No session          | Unauthenticated                      |
| Valid session       | `/auth/me` resolved                  |
| Invalid session     | Access cleared                       |
| Expired session     | Refresh/re-authentication            |
| `/auth/me` success  | Identity populated                   |
| `/auth/me` 401      | Identity cleared                     |
| Inactive membership | Application access denied            |
| Hospital loaded     | Backend hospital displayed           |
| Hospital spoofing   | Ignored/rejected                     |
| Role loaded         | Backend role represented             |
| Permission loaded   | Backend permission represented       |
| Missing permission  | Capability denied                    |
| Protected request   | JWT attached                         |
| Missing JWT         | Request rejected                     |
| 401 response        | Authentication failure               |
| 403 response        | Authorization failure                |
| Logout              | Identity state cleared               |
| User switch         | Previous state invalidated           |
| Permission change   | Capabilities refreshed               |
| Tenant change       | Previous tenant cache cleared        |
| Frontend tampering  | Backend still denies                 |
| Unauthorized route  | UI restriction + backend enforcement |

---

# 29. Security Invariants

The following invariants must hold after implementation.

### Identity

```text
Frontend identity
    =
backend-resolved authenticated identity
```

### Tenant

```text
Frontend hospital context
    =
backend-resolved hospital context
```

### Authorization

```text
Frontend capabilities
    =
derived from backend permissions
```

### API Security

```text
Frontend capability
    ≠
backend authorization
```

### Cross-tenant protection

```text
Browser-supplied hospital_id
    ≠
authoritative tenant context
```

### Identity isolation

```text
User A state
    must never leak into
User B state
```

### Logout isolation

```text
After logout:
no authenticated application state remains active
```

### Backend authority

```text
All protected operations
    must remain enforceable by backend authorization
```

---

# 30. Acceptance Criteria

10D.6 is considered satisfied when:

* [ ] authentication boundary tests pass;
* [ ] session restoration tests pass;
* [ ] session refresh tests pass;
* [ ] logout tests pass;
* [ ] `/auth/me` integration tests pass;
* [ ] inactive-account tests pass;
* [ ] execution identity tests pass;
* [ ] hospital context tests pass;
* [ ] role resolution tests pass;
* [ ] permission resolution tests pass;
* [ ] capability resolution tests pass;
* [ ] protected API request tests pass;
* [ ] 401 handling tests pass;
* [ ] 403 handling tests pass;
* [ ] identity-change invalidation tests pass;
* [ ] tenant/cache isolation tests pass;
* [ ] frontend tampering tests demonstrate backend authority;
* [ ] role-aware navigation tests pass;
* [ ] permission-aware control tests pass;
* [ ] no frontend-only authorization mechanism is treated as security;
* [ ] tests use the actual backend identity/RBAC contracts;
* [ ] no new RBAC model is introduced;
* [ ] no new tenant model is introduced;
* [ ] no client-supplied identity becomes authoritative.

---

# 31. Validation Command

The exact command depends on the frontend test framework.

The implementation should run the project's existing frontend test command rather than introducing a new testing framework solely for 10D.

Examples, only where already supported by the repository:

```bash
npm test
```

or:

```bash
npm run test
```

or the repository's established test command.

The implementation must report:

```text
Test command
Tests executed
Tests passed
Tests failed
Coverage, if configured
```

---

# 32. Failure Interpretation

A failed 10D.6 test must not automatically result in changing the architecture.

First determine whether the failure represents:

1. implementation defect;
2. incorrect test assumption;
3. stale frontend contract;
4. incorrect mock;
5. backend contract mismatch;
6. documentation inconsistency.

Tests must be corrected when they incorrectly model the approved architecture.

The implementation must not be modified merely to satisfy an unrealistic synthetic test.

---

# 33. Architectural Boundary

10D.6 does not introduce a new security architecture.

It validates the implementation of:

```text
10D.1 Authentication Boundary
10D.2 Execution Identity Session State
10D.3 Tenant / Hospital Context
10D.4 RBAC / Capability Resolution
10D.5 Protected API Integration
```

The backend remains the security authority established in Phase 10C.

The frontend remains a consumer of that authority.

---

# 34. Final Security Model

The completed frontend identity architecture must therefore remain:

```text
                 SUPABASE
                    │
                    ▼
              Authenticated
                 Session
                    │
                    ▼
                /auth/me
                    │
                    ▼
        ┌───────────────────────┐
        │ Backend Identity      │
        │                       │
        │ User                  │
        │ Professional          │
        │ Membership            │
        │ Hospital              │
        │ Roles                 │
        │ Permissions           │
        └───────────────────────┘
                    │
                    ▼
             Frontend Identity
                 Context
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
    Hospital Context      Capability
                              Resolver
                                │
                                ▼
                         UI Decisions
                                │
                                ▼
                         Protected API
                                │
                                ▼
                         Backend 10C
                         Authorization
```

The critical rule remains:

> **The frontend may decide what the user sees. The backend decides what the user is allowed to do.**

---

# 35. Relationship to 10C

Phase 10D must consume, not duplicate, the security model established by 10C.

```text
10C — Backend Security
        │
        │ authoritative
        ▼
Authentication
Execution Identity
Tenant Context
RBAC
API Enforcement
        │
        ▼
10D — Frontend Integration
        │
        ▼
Session
Identity
Hospital Context
Capabilities
Protected Requests
UX Enforcement
```

Therefore, successful 10D.6 validation means that the frontend correctly participates in the existing security architecture without becoming a competing authorization authority.

```
```
