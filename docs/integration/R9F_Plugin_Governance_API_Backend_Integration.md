# R9F — Plugin Governance API & Backend Integration

**Status:** APPROVED
**Phase:** R9 — Plugin Governance & External Extension Security
**Predecessors:** R9A, R9B, R9C, R9D, R9E
**Next Phase:** R9G — Plugin Runtime Manager Integration

---

## 1. Purpose

R9F defines the backend API and service-layer architecture through which authorised hospital administrators govern external plugins.

It translates the approved governance decisions from R9A–R9E into a controlled backend interface without yet implementing the runtime Plugin Manager integration covered by R9G.

The API must provide controlled mechanisms for:

* plugin registration;
* plugin package submission;
* validation;
* approval;
* rejection;
* activation;
* deactivation;
* revocation;
* quarantine;
* plugin configuration;
* governance status;
* audit history.

The backend remains the authoritative enforcement boundary.

---

# 2. Core Architectural Principle

> **The Plugin Governance API is a governance boundary, not the plugin execution engine.**

The API controls the lifecycle and authorisation of plugins.

It must not duplicate plugin execution logic.

The intended architecture is:

```text
Hospital Administrator
        ↓
Frontend
        ↓
FastAPI Governance API
        ↓
Authentication / RBAC / Tenant Context
        ↓
Plugin Governance Service
        ↓
Governance Registry
        ↓
Plugin Manager
        ↓
Common Plugin Engine
```

R9F therefore establishes the bridge between governance and runtime without implementing the runtime integration itself.

---

# 3. Backend Authority

All plugin governance decisions must be enforced server-side.

The backend determines:

* authenticated professional;
* active hospital;
* canonical role;
* governance permission;
* plugin ownership;
* plugin registration;
* lifecycle state;
* allowed action;
* approved capability;
* tenant scope.

The frontend must never be trusted to supply these as authoritative values.

---

# 4. Authentication

Plugin governance endpoints use the existing authentication architecture.

```text
Supabase Auth
      ↓
Bearer JWT
      ↓
FastAPI JWT verification
      ↓
Authenticated professional
```

No plugin-specific authentication mechanism is introduced.

R8 remains authoritative for frontend session handling.

---

# 5. RBAC Enforcement

Plugin governance must use the existing Phase 16C role and permission model.

Only an authorised hospital administrator may perform tenant governance operations.

Conceptually:

```text
Authenticated User
        ↓
Active Hospital Membership
        ↓
Canonical Role
        ↓
Plugin Governance Permission
        ↓
Requested Plugin Action
```

The API must reject governance operations when the authenticated user lacks the required permission.

---

# 6. Tenant Resolution

The backend must derive the hospital/organisation context from the authenticated identity and active membership.

The request must not be allowed to override tenant context through:

* request body;
* query parameter;
* URL path;
* frontend state;
* custom header.

For example, this must **not** become an authority:

```json
{
  "hospital_id": "some-other-hospital"
}
```

The backend resolves the authoritative hospital from the authenticated professional.

---

# 7. API Resource Model

R9F treats a plugin governance registration as a tenant-scoped resource.

Conceptually:

```text
Hospital
   │
   └── Plugin Registration
           │
           ├── Plugin Identity
           ├── Version
           ├── Type
           ├── Ownership
           ├── Governance State
           ├── Capabilities
           ├── Configuration
           └── Audit History
```

The detailed persistence structure is defined by R9B.

---

# 8. Plugin Types

The API must recognise at least the approved plugin categories relevant to external plugins:

### Knowledge Plugin

Provides structured knowledge through the common plugin framework.

### Prediction Plugin

Represents an ML model/plugin.

Prediction plugins must remain model-based and must not be registered as arbitrary non-ML plugins.

The API must validate plugin type against the submitted metadata/package.

---

# 9. Registration API

The registration endpoint creates a tenant-scoped plugin registration.

Conceptually:

```http
POST /api/v1/plugins
```

The exact route naming may be adjusted during implementation, but the architectural contract remains.

Registration must:

1. authenticate the requester;
2. resolve the active hospital;
3. verify administrator permission;
4. validate submission metadata;
5. validate plugin package/form data;
6. establish plugin identity;
7. establish tenant ownership;
8. create a registration;
9. record the governance event;
10. place the plugin into the appropriate lifecycle state.

Registration does **not** activate the plugin.

---

# 10. Package Upload

The API must support controlled submission of external plugin packages.

The approved submission model allows:

* ZIP package upload;
* form-based metadata submission with the required plugin artefact.

The API must not treat an uploaded ZIP as automatically trusted executable code.

The package must pass the R9D security and validation requirements before activation.

---

# 11. Upload Processing Boundary

The upload process should conceptually be:

```text
Upload
  ↓
Receive safely
  ↓
Identify package
  ↓
Validate structure
  ↓
Validate manifest
  ↓
Validate compatibility
  ↓
Validate integrity/trust requirements
  ↓
Create registration
  ↓
Pending approval
```

The API must not execute arbitrary uploaded code merely because it has been uploaded.

Runtime loading belongs to the governed Plugin Manager.

---

# 12. Registration State

The governance API must expose the lifecycle state defined in R9C.

At minimum:

```text
REGISTERED
PENDING_APPROVAL
APPROVED
REJECTED
ENABLED
DISABLED
REVOKED
QUARANTINED
```

The implementation may use a smaller internal state machine where appropriate, but transitions must preserve the governance semantics defined in R9C.

---

# 13. Approval API

Approval is a tenant governance operation.

Conceptually:

```http
POST /api/v1/plugins/{plugin_id}/approve
```

The backend must verify:

* authenticated user;
* hospital membership;
* administrator permission;
* plugin ownership;
* valid lifecycle state;
* successful security/validation requirements.

Approval must be recorded as an auditable governance event.

Approval must not automatically mean runtime execution unless the lifecycle contract explicitly permits activation as a separate step.

---

# 14. Rejection API

A plugin may be rejected.

Conceptually:

```http
POST /api/v1/plugins/{plugin_id}/reject
```

The rejection should record:

* actor;
* timestamp;
* plugin version;
* reason where required;
* resulting lifecycle state.

A rejected plugin must not execute.

---

# 15. Enable API

Activation must be explicitly controlled.

Conceptually:

```http
POST /api/v1/plugins/{plugin_id}/enable
```

The backend must confirm:

```text
Registered
    ↓
Validated
    ↓
Approved
    ↓
Security requirements satisfied
    ↓
Enable
```

An unapproved or revoked plugin cannot be enabled.

---

# 16. Disable API

A hospital administrator may disable a tenant-owned plugin.

Conceptually:

```http
POST /api/v1/plugins/{plugin_id}/disable
```

Disabling must:

* prevent future use;
* preserve governance history;
* preserve plugin identity/version information;
* record the actor and timestamp.

The operation must not silently delete audit history.

---

# 17. Revocation

Revocation is stronger than ordinary disabling.

Conceptually:

```http
POST /api/v1/plugins/{plugin_id}/revoke
```

Revocation may be initiated by:

* platform security authority;
* authorised governance authority;
* defined administrative policy.

A revoked plugin must not return to active use without a new approved governance process.

---

# 18. Quarantine

The API must support quarantine for plugins suspected of security or integrity problems.

Conceptually:

```http
POST /api/v1/plugins/{plugin_id}/quarantine
```

Quarantine must immediately prevent normal runtime use.

It is intended for situations such as:

* compromised package;
* failed integrity check;
* suspicious behaviour;
* security investigation;
* incompatible replacement;
* model integrity concern.

---

# 19. Plugin Status API

Hospital administrators should be able to inspect the status of plugins they are authorised to govern.

Conceptually:

```http
GET /api/v1/plugins
GET /api/v1/plugins/{plugin_id}
```

The response may expose:

* plugin identity;
* type;
* version;
* registration state;
* approval state;
* enabled state;
* compatibility;
* capabilities;
* tenant ownership;
* security status;
* registration timestamps.

Sensitive security information must not be unnecessarily exposed.

---

# 20. Audit History API

Governance actions must be auditable.

Conceptually:

```http
GET /api/v1/plugins/{plugin_id}/audit
```

The API may expose appropriate governance history such as:

```text
PLUGIN_REGISTERED
PLUGIN_APPROVED
PLUGIN_REJECTED
PLUGIN_ENABLED
PLUGIN_DISABLED
PLUGIN_REVOKED
PLUGIN_QUARANTINED
PLUGIN_UPDATED
```

Audit history must respect tenant isolation.

A hospital administrator must never retrieve another hospital's plugin audit records.

---

# 21. Configuration API

Where tenant-specific configuration is permitted:

```http
GET /api/v1/plugins/{plugin_id}/configuration
PUT /api/v1/plugins/{plugin_id}/configuration
```

Configuration changes must:

* require appropriate permission;
* be validated against the plugin's approved configuration schema;
* remain tenant-scoped;
* be auditable;
* not expand the plugin's approved capabilities.

A configuration update must never become a privilege-escalation mechanism.

---

# 22. Capability Enforcement

The API must not allow a hospital administrator to arbitrarily grant capabilities.

For example, if a plugin was approved for:

```text
KNOWLEDGE_READ
```

the administrator must not be able to modify its configuration to obtain:

```text
PATIENT_DATA_WRITE
```

unless that capability is explicitly supported and approved by the platform governance/security model.

---

# 23. Plugin Ownership Enforcement

Every governance API request involving a tenant plugin must verify:

```text
requester.hospital_id
        ==
plugin_registration.hospital_id
```

where the hospital ID is derived from backend identity context.

If not:

```text
403 FORBIDDEN
```

No information about the other tenant's plugin should be leaked.

---

# 24. Duplicate Registration

The API must prevent ambiguous duplicate registrations.

At minimum, uniqueness rules must consider the identity defined by R9B, such as:

* tenant;
* plugin identity;
* version;
* registration identity.

The exact database uniqueness constraints belong to R9B implementation.

The API must return a deterministic conflict response when a duplicate registration is attempted.

---

# 25. Version Updates

A new plugin version must not silently replace an existing approved version.

Conceptually:

```text
Plugin X v1
   ↓
Approved
   ↓
Enabled

Plugin X v2
   ↓
New registration/version
   ↓
Validation
   ↓
Approval
   ↓
Activation
```

The existing approved version remains governed until the new version passes its own lifecycle.

This supports rollback and auditability.

---

# 26. Package Integrity

R9F consumes the security guarantees established in R9D.

The API must integrate with the approved mechanisms for:

* checksum/hash;
* signature;
* provenance;
* publisher identity;
* package identity.

The API must not bypass security verification merely because a hospital administrator is submitting the plugin.

---

# 27. No Direct Runtime Execution

A critical boundary:

> **The governance API must not execute plugin code directly.**

It performs governance operations.

Runtime execution remains the responsibility of:

```text
Plugin Manager
      ↓
Common Plugin Engine
```

This separation is essential for:

* security;
* testability;
* auditability;
* lifecycle control.

---

# 28. Relationship With Plugin Manager

R9F establishes governance state that R9G will later consume.

Conceptually:

```text
Governance Registry
        ↓
Approved / Enabled Plugin
        ↓
Plugin Manager
        ↓
Plugin Loader
        ↓
Common Plugin Engine
```

R9F does not yet decide the exact startup/runtime wiring.

That is R9G.

---

# 29. Relationship With Internal Plugins

The governance API must not create a second plugin execution architecture.

Internal plugins such as the WHO knowledge plugin remain platform-managed.

External plugins become governed registrations that eventually enter the same runtime engine.

Therefore:

```text
             Plugin Governance
                    ↓
              Plugin Manager
                    ↓
            Common Plugin Engine
              ↙             ↘
       Internal Plugin   External Plugin
```

---

# 30. Error Semantics

The API should use consistent backend error semantics.

Examples include:

```text
401 UNAUTHORIZED
403 FORBIDDEN
404 NOT_FOUND
409 CONFLICT
422 VALIDATION_ERROR
```

Where applicable, structured error codes should distinguish:

```text
PLUGIN_NOT_FOUND
PLUGIN_ALREADY_REGISTERED
PLUGIN_INVALID
PLUGIN_INCOMPATIBLE
PLUGIN_NOT_APPROVED
PLUGIN_DISABLED
PLUGIN_REVOKED
PLUGIN_QUARANTINED
PLUGIN_TENANT_MISMATCH
PLUGIN_CAPABILITY_NOT_ALLOWED
PLUGIN_INTEGRITY_FAILURE
PLUGIN_SIGNATURE_INVALID
```

Exact error schema should follow the existing backend exception architecture.

---

# 31. Audit Event Authority

Governance audit events must be generated by the backend.

The frontend must never be able to claim:

```text
PLUGIN_APPROVED
```

merely by displaying a success message.

The backend records the actual state transition and audit event.

---

# 32. Transactional State Changes

Governance operations that modify both:

* plugin state; and
* audit history

should be performed transactionally where supported by the persistence layer.

For example:

```text
Approve Plugin
      ↓
Update registration state
      +
Create approval audit event
      ↓
Commit
```

A partially applied governance action must be avoided.

---

# 33. API and Database Separation

R9F must maintain separation between:

```text
API
 ↓
Governance Service
 ↓
Repository / Registry
```

The HTTP layer must not contain the complete plugin governance business logic.

This supports:

* testing;
* reuse;
* future UI/API changes;
* runtime manager integration.

---

# 34. API and Runtime Separation

Likewise:

```text
Governance Service
        ≠
Plugin Runtime
```

The governance service determines whether a plugin **may** run.

The Plugin Manager determines how an approved plugin **runs**.

This distinction is fundamental.

---

# 35. Tenant-Scoped Queries

All plugin queries made through the governance service must be tenant-scoped.

A generic query such as:

```text
get_all_plugins()
```

must not accidentally expose all tenant registrations to a hospital administrator.

The preferred conceptual form is:

```text
get_plugins(tenant_context)
```

or equivalent server-derived scoping.

---

# 36. Administrative Actions

The initial API governance operations are:

| Action                  |   Hospital Admin | Platform Security |
| ----------------------- | ---------------: | ----------------: |
| Register                |                ✓ |                 ✓ |
| View own plugins        |                ✓ |                 ✓ |
| Approve                 |                ✓ |                 ✓ |
| Reject                  |                ✓ |                 ✓ |
| Enable                  |                ✓ |                 ✓ |
| Disable                 |                ✓ |                 ✓ |
| Configure               |                ✓ |                 ✓ |
| Revoke                  | Policy-dependent |                 ✓ |
| Quarantine              |               No |                 ✓ |
| View audit              |     ✓ own tenant |                 ✓ |
| Govern another hospital |               No |  Policy-dependent |

The exact platform-level administrative authority may be refined in a future platform governance decision.

---

# 37. Hospital Administrator Cannot Bypass R9D

Even when a hospital administrator is authorised to approve a plugin, the administrator cannot bypass:

* package integrity;
* signature requirements;
* compatibility validation;
* execution isolation;
* capability restrictions;
* platform security policies.

Therefore:

> **Administrative approval is not a security bypass.**

---

# 38. API Security Requirements

All governance endpoints must enforce:

1. authenticated identity;
2. canonical RBAC permission;
3. active hospital membership;
4. tenant ownership;
5. lifecycle transition validity;
6. security validation;
7. audit generation.

---

# 39. Testing Requirements

R9F implementation must eventually provide tests for:

### Authentication

* unauthenticated request;
* expired session;
* invalid JWT.

### Authorization

* non-admin user;
* authorised hospital administrator;
* platform-authorised security actor.

### Tenant isolation

* same-tenant access;
* cross-tenant access;
* forged hospital ID;
* forged tenant header.

### Registration

* valid plugin;
* invalid plugin;
* duplicate plugin;
* invalid package;
* incompatible plugin.

### Lifecycle

* approve;
* reject;
* enable;
* disable;
* revoke;
* quarantine;
* invalid state transition.

### Security

* invalid signature;
* checksum mismatch;
* prohibited capability;
* untrusted package.

### Audit

* registration event;
* approval event;
* activation event;
* deactivation event;
* revocation event;
* configuration change.

---

# 40. OpenAPI

R9F implementation must expose the approved governance API through FastAPI/OpenAPI.

The API contract should clearly document:

* authentication requirements;
* required permissions;
* request schemas;
* response schemas;
* error responses;
* lifecycle states;
* tenant semantics.

OpenAPI documentation must not imply that frontend clients are authoritative for tenant identity.

---

# 41. No Separate Plugin Backend

R9F does **not** introduce a separate backend application for external plugins.

The intended architecture remains:

```text
Existing FastAPI Backend
        ↓
Plugin Governance
        ↓
Plugin Manager
        ↓
Common Plugin Engine
```

This preserves the project's architectural principle of extending the existing platform rather than creating parallel infrastructure.

---

# 42. No Plugin-Specific Authentication

External plugins do not receive their own user authentication system.

Human governance actions use the existing professional identity/RBAC system.

Plugin execution credentials, where required, are governed by the security model defined in R9D.

---

# 43. No Direct Frontend-to-Plugin Communication

The frontend must not directly invoke arbitrary external plugin code.

The intended path is:

```text
Frontend
   ↓
FastAPI
   ↓
Governance / Authorization
   ↓
Plugin Runtime
```

This maintains backend control over clinical and tenant boundaries.

---

# 44. Architectural Invariants

The following are mandatory:

1. **Backend is authoritative.**
2. **Hospital administrator is the tenant governance authority.**
3. **Tenant context is derived server-side.**
4. **Tenant ownership is enforced on every governance operation.**
5. **Registration does not imply activation.**
6. **Approval does not bypass security controls.**
7. **External plugin code is never executed directly by the governance API.**
8. **Governance state is auditable.**
9. **Plugin versions are independently governed.**
10. **Internal and external plugins ultimately use the common plugin engine.**
11. **No second authentication/RBAC architecture is introduced.**
12. **No frontend state can override backend plugin governance.**

---

# 45. R9F Decision Summary

| Decision                                         | Status                    |
| ------------------------------------------------ | ------------------------- |
| Governance API lives in existing FastAPI backend | **CONFIRMED**             |
| Backend remains authoritative                    | **INHERITED**             |
| Existing Supabase authentication is reused       | **INHERITED**             |
| Existing Phase 16C RBAC is reused                | **INHERITED**             |
| Tenant context is server-derived                 | **INHERITED**             |
| Hospital administrator governs tenant plugins    | **CONFIRMED**             |
| Plugin registration API                          | **CONFIRMED**             |
| Plugin approval/rejection API                    | **CONFIRMED**             |
| Enable/disable lifecycle API                     | **CONFIRMED**             |
| Revocation/quarantine controls                   | **CONFIRMED**             |
| Plugin audit API                                 | **CONFIRMED**             |
| Tenant-scoped configuration                      | **CONFIRMED**             |
| Governance API executes plugin code              | **PROHIBITED**            |
| Governance API directly loads plugins            | **PROHIBITED**            |
| Runtime integration                              | **R9G**                   |
| Common plugin engine                             | **INHERITED / CONFIRMED** |
| Dedicated external-plugin backend                | **PROHIBITED**            |
| Dedicated external-plugin authentication         | **PROHIBITED**            |

---

# 46. R9F Gate

### Current Status
APPROVED




```text
R9A — APPROVED
        ↓
R9B — APPROVED
        ↓
R9C — APPROVED
        ↓
R9D — APPROVED
        ↓
R9E — APPROVED
        ↓
R9F — APPROVED
        ↓
R9G — Plugin Runtime Manager Integration
```
