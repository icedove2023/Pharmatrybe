

# 10C.2 — Execution Identity

## 1. Objective
status : Approved
Define the canonical identity that represents **who is executing an operation, within which hospital tenant, and under which governed plugin execution context**.

The execution identity must be derived from the authenticated request and validated tenant context.

It must **never be supplied by the client as authoritative identity data**.

The intended chain is:

```text
Supabase JWT
     │
     ▼
Authenticated User
     │
     ▼
Professional Profile
     │
     ▼
Active Hospital Membership
     │
     ▼
TenantContext
     │
     ▼
ExecutionIdentity
     │
     ▼
Governed Plugin Execution
```

This preserves the architectural separation between:

* authentication identity,
* tenant identity,
* application execution identity,
* plugin execution identity.

---

# 2. Canonical Identity Sources

The backend identity model established in the previous phases gives us three important identifiers:

```text
authenticated_user_id
        │
        ▼
professional_id
        │
        ▼
hospital_id
```

The database model confirms that:

* `professional_profiles.auth_user_id` identifies the authenticated Supabase user.
* `hospital_memberships.professional_id` connects the professional to the membership.
* `hospital_memberships.hospital_id` establishes the tenant.
* Membership status determines whether the relationship is active.

Therefore:

> **The hospital/tenant must be resolved from the active membership, not from a request parameter.**

This is consistent with the existing database function `current_hospital_id()`.

---

# 3. ExecutionIdentity Is Not Authentication

This distinction is important.

`ExecutionIdentity` should **not** authenticate the user.

Authentication occurs earlier.

```text
Authentication Boundary
        │
        │ establishes authenticated_user_id
        ▼
Tenant Resolution
        │
        │ establishes professional_id + hospital_id
        ▼
TenantContext
        │
        ▼
ExecutionIdentity
```

Therefore:

```text
JWT ≠ TenantContext ≠ ExecutionIdentity
```

Each has a different responsibility.

### JWT

Answers:

> Who authenticated?

### TenantContext

Answers:

> Which professional and hospital does this authenticated identity currently belong to?

### ExecutionIdentity

Answers:

> Under what validated identity and governance decision is this execution being performed?

---

# 4. Existing Implementation

The backend already contains:

```text
apps/api/app/plugins/security/execution_identity.py
```

The existing class is explicitly documented as an immutable provenance snapshot for an admitted external plugin execution. 

The class is already constructed from:

```python
ExecutionIdentity.from_admission(
    tenant,
    record,
    manifest,
    isolation_mode,
)
```

The inspection confirms this call occurs in the plugin loader. 

This is the correct architectural direction.

---

# 5. ExecutionIdentity Must Be Derived

The canonical construction should remain:

```text
TenantContext
      +
Governance Admission
      +
Validated Plugin Manifest
      +
Isolation Mode
      ↓
ExecutionIdentity
```

Not:

```text
HTTP request
      ↓
ExecutionIdentity
```

And not:

```text
client-supplied hospital_id
      ↓
ExecutionIdentity
```

---

# 6. Tenant Binding

The execution identity must contain a tenant identifier derived from the validated tenant context.

The current implementation already does this:

```python
tenant_id=tenant.hospital_id
```

The backend inspection confirms this exact relationship. 

This means plugin execution is intrinsically tenant-bound.

---

# 7. Professional and Authenticated User Identity

The execution path already carries:

```text
authenticated_user_id
professional_id
hospital_id
```

through `TenantContext`. 

Therefore the execution identity should preserve the distinction:

```text
authenticated_user_id
        │
        │ Supabase identity
        ▼
professional_id
        │
        │ application identity
        ▼
hospital_id
        │
        │ tenant identity
        ▼
ExecutionIdentity
```

We should **not collapse these identifiers into a single `user_id` field**.

This is particularly important because the earlier 10B work established that `professional_profiles` is the application-level identity associated with the authenticated Supabase user.

---

# 8. Immutability

Once an execution identity has been created, it must be immutable.

The current architecture explicitly describes it as:

> immutable identity bound to one governance admission decision. 

Therefore:

```text
Admission
   │
   ▼
ExecutionIdentity
   │
   ├── tenant
   ├── professional
   ├── authenticated user
   ├── plugin
   ├── version
   ├── capabilities
   ├── governance record
   └── isolation context
```

must remain fixed for that execution.

A plugin cannot change:

```text
hospital_id
professional_id
authenticated_user_id
plugin_id
plugin_version
capabilities
governance identity
```

during execution.

---

# 9. Plugin Identity Binding

The existing architecture also binds the execution identity to the validated plugin identity.

The external proxy exposes values such as:

```text
plugin_id
plugin_version
capabilities
```

from `ExecutionIdentity` when available. 

This is correct because the execution identity should represent:

```text
WHO
 +
WHERE
 +
WHAT
 +
UNDER WHICH GOVERNANCE DECISION
```

---

# 10. Governance Binding

Execution identity must also remain tied to the governance admission.

The architecture already constructs it from an admission record:

```python
ExecutionIdentity.from_admission(
    tenant,
    record,
    manifest,
    isolation_mode,
)
```

The documentation describes this as snapshotting the governed and validated identity at admission time. 

Therefore:

```text
Plugin discovered
       ↓
Manifest validated
       ↓
Governance evaluated
       ↓
Admission approved
       ↓
ExecutionIdentity created
       ↓
Plugin executed
```

The plugin must not execute first and acquire its identity afterwards.

---

# 11. Isolation Binding

The existing container runtime already enforces identity at the container level using:

```text
policy.execution_identity
```

as the container user. 

This gives us an important security property:

```text
Governance Identity
       ↓
ExecutionIdentity
       ↓
Isolation Policy
       ↓
Container Runtime
```

The execution identity is therefore not merely metadata.

It participates in actual runtime isolation.

---

# 12. Tenant Boundary During Execution

The existing external proxy also contains a runtime tenant guard.

The inspection shows:

```python
runtime_guard(...)
```

and a comparison between the request tenant and the bound tenant context. 

The important invariant is:

```text
request tenant
      ==
execution tenant
```

If they differ:

```text
DENY
```

This is exactly the behaviour required for the multi-tenant architecture.

---

# 13. Required Invariants

10C.2 should establish the following invariants.

### Identity invariant

```text
authenticated_user_id
    must originate from authenticated JWT
```

### Professional invariant

```text
professional_id
    must originate from the authenticated user's
    professional profile
```

### Tenant invariant

```text
hospital_id
    must originate from the user's ACTIVE membership
```

### Execution invariant

```text
ExecutionIdentity
    must originate from validated TenantContext
```

### Governance invariant

```text
ExecutionIdentity
    must correspond to the governance admission
```

### Plugin invariant

```text
ExecutionIdentity.plugin_id
    must correspond to the validated plugin manifest
```

### Runtime invariant

```text
execution tenant
    ==
request tenant
```

### Isolation invariant

```text
execution identity
    ==
identity enforced by plugin runtime
```

---

# 14. What We Should NOT Change Yet

Because 10C.0 shows that much of this infrastructure already exists, **we should not rewrite**:

```text
ExecutionIdentity
TenantContext
PluginLoader
ExternalProxy
ContainerRuntime
```

simply to make them look different.

Instead, 10C.2 should verify that the existing implementation satisfies the new authentication architecture.

This follows the project principle:

> **Inspect → validate → modify only where necessary.**

---

# 15. 10C.2 Acceptance Criteria

Before moving to 10C.3, we should be able to demonstrate:

### A. Authenticated identity

```text
JWT
 ↓
authenticated_user_id
```

### B. Professional resolution

```text
authenticated_user_id
 ↓
professional_profiles
 ↓
professional_id
```

### C. Tenant resolution

```text
professional_id
 ↓
ACTIVE hospital_membership
 ↓
hospital_id
```

### D. TenantContext

```text
authenticated_user_id
professional_id
hospital_id
```

are represented consistently.

### E. ExecutionIdentity

```text
TenantContext
 +
Governance Admission
 +
Plugin Manifest
 ↓
ExecutionIdentity
```

### F. Tenant isolation

User A cannot execute against Hospital B.

### G. Plugin isolation

A plugin admitted for Hospital A cannot be reused under Hospital B's execution context.

### H. Runtime enforcement

The runtime uses the bound execution identity rather than a client-provided identity.

---

## 10C.2 Architectural Decision

I recommend recording the following as the formal decision:

> **10C.2 — Execution Identity Decision**
>
> PharmaTrybe will derive `ExecutionIdentity` exclusively from an authenticated and validated `TenantContext` together with the approved plugin governance admission. `ExecutionIdentity` is an immutable provenance snapshot representing the authenticated user, professional, hospital tenant, validated plugin identity, granted capabilities, governance admission, and isolation context for a specific execution. Client-supplied tenant or identity values are never authoritative. Execution identity must remain tenant-bound and must be enforced consistently through plugin admission, runtime isolation, and execution auditing.

This fits the architecture already present rather than introducing a competing identity mechanism. The existing backend already demonstrates the core of this design. 

**So 10C.2 should now be treated as an architectural verification/normalisation task, not a new implementation from scratch.**
