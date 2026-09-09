````markdown
# R9A — Plugin Governance & External Extension Security Architecture Decision

**Project:** AMR Explainable AI Clinical Decision Support System (CDSS)  
**Phase:** R9A  
**Title:** Plugin Governance & External Extension Security Architecture Decision  
**Status:** **APPROVED**  
**Decision:** **APPROVED FOR IMPLEMENTATION**  
**Approved Scope:** Plugin governance, external extensions, trust, approval, security, tenant boundaries, runtime admission  
**Out of Scope:** Supabase deployment operations, clinical recommendation redesign, R8 redesign, R7 redesign

---

## 1. Approval Declaration

R9A — **Plugin Governance & External Extension Security Architecture Decision** has been formally **APPROVED**.

The architecture defined in this document is now an authoritative project decision and may be used as the basis for subsequent R9 implementation phases.

The approval authorizes implementation to proceed **incrementally and only within the approved architectural boundaries**.

---

## 2. Architectural Decision

The Pharmatrybe shall formally separate:

> **Plugin Governance** from **Plugin Runtime Execution**.

The existing runtime plugin infrastructure remains valid as the runtime foundation.

However, the existing runtime registry shall **not** be treated as the authoritative governance registry.

The approved architecture is:

```text
External Plugin
      ↓
Registration
      ↓
Identity / Provenance Verification
      ↓
Manifest & Compatibility Validation
      ↓
Security / Integrity Verification
      ↓
Capability / Permission Review
      ↓
Governance Approval
      ↓
Activation
      ↓
Runtime Plugin Registry
      ↓
Plugin Execution
      ↓
Monitoring / Audit
      ↓
Disable / Revoke / Quarantine
````

---

## 3. Approved Architectural Principles

The following principles are now authoritative for R9:

1. **Discovery does not constitute registration.**
2. **Registration does not constitute approval.**
3. **Approval does not constitute activation.**
4. **Activation does not remove authorization requirements.**
5. **Runtime registration is distinct from governance registration.**
6. **External plugins require explicit governance.**
7. **Unapproved plugins must not execute.**
8. **Plugin approval must be associated with a specific artifact identity.**
9. **Plugin provenance must be recorded.**
10. **External plugin integrity/signature verification is required.**
11. **Plugin capabilities and permissions must be explicitly governed.**
12. **External plugins must not receive unrestricted platform credentials.**
13. **External plugin execution requires an explicit isolation strategy.**
14. **Plugin governance must not create an alternative tenant authority.**
15. **Hospital-specific plugin governance requires an explicit tenant model.**
16. **Plugin lifecycle actions must be auditable.**
17. **Revoked and quarantined plugins must not execute.**
18. **Plugin versions and artifacts require independent governance.**
19. **Frontend plugin metadata is not governance authority.**
20. **Plugin failures must fail safely.**
21. **Plugins must not bypass clinical safety, evidence, authorization, or clinician oversight.**

---

## 4. Approved Governance States

The following governance states are approved:

```text
DISCOVERED
    ↓
REGISTERED
    ↓
VERIFIED
    ↓
PENDING_APPROVAL
    ↓
APPROVED
    ↓
ACTIVATED
    ↓
RUNNING
```

Exceptional states:

```text
REJECTED
DISABLED
REVOKED
QUARANTINED
```

The following transitions are explicitly prohibited:

```text
DISCOVERED → RUNNING
REGISTERED → RUNNING
UNAPPROVED → ACTIVE
REVOKED → ACTIVE
QUARANTINED → ACTIVE
```

without the appropriate governance process.

---

## 5. Approved Plugin Trust Model

The platform shall distinguish between:

### Platform-Trusted Plugins

Internally controlled plugins that remain subject to:

* validation;
* compatibility checks;
* testing;
* version control;
* security review;
* lifecycle governance.

### Approved External Plugins

Externally developed plugins that have successfully completed the required governance process.

### Unapproved / Pending / Rejected / Revoked / Quarantined Plugins

These plugins shall not execute in the production runtime.

---

## 6. Approved Governance Registry Boundary

A persistent governance registry shall become the authoritative source for:

* plugin identity;
* ownership;
* publisher;
* provenance;
* versions;
* artifacts;
* approval state;
* activation state;
* capabilities;
* permissions;
* tenant scope;
* security verification;
* audit history.

The existing runtime `PluginRegistry` shall remain responsible for runtime availability and loaded plugin instances.

Therefore:

```text
Governance Registry
        ↓
Runtime Admission
        ↓
Plugin Manager
        ↓
Runtime Plugin Registry
```

The runtime registry must not independently promote an unapproved plugin into execution.

---

## 7. Approved Security Requirements

External plugins shall be governed by:

* provenance verification;
* artifact integrity verification;
* cryptographic identity/signature support;
* capability declaration;
* permission/scoping;
* credential isolation;
* compatibility validation;
* execution isolation;
* revocation;
* quarantine.

The exact technologies for signatures, key management, sandboxing, and process isolation remain implementation decisions for later R9 phases.

---

## 8. Approved Tenant Boundary

The existing AMR identity architecture remains authoritative.

Plugin governance shall not introduce an alternative source of tenant identity.

In particular, plugins must not independently determine:

```text
hospital_id
organisation_id
tenant_id
```

Tenant context must continue to derive from the approved backend identity and membership architecture.

Hospital-specific plugins require a separate approved tenant-governance implementation.

---

## 9. Approved Clinical Safety Boundary

Plugins remain extensions of the CDSS.

They do not become autonomous clinical authorities.

Plugins must not:

* override approved clinical guidelines;
* bypass the knowledge base;
* suppress safety warnings;
* fabricate evidence;
* bypass explainability requirements;
* override backend authorization;
* bypass tenant isolation;
* replace clinician judgement.

Where plugin output contributes to clinical reasoning, plugin identity and provenance must remain attributable.

---

## 10. Approved Auditability Requirement

The governance system shall maintain durable records for material lifecycle events, including:

* registration;
* verification;
* approval;
* rejection;
* activation;
* deactivation;
* configuration change;
* revocation;
* quarantine;
* restoration;
* artifact/version replacement.

Audit records should identify the relevant:

* plugin;
* version;
* artifact;
* actor;
* timestamp;
* action;
* previous state;
* new state;
* reason.

---

# 11. Approved R9 Implementation Sequence

Implementation is authorized to proceed through the following controlled sequence:

```text
R9A — Plugin Governance & External Extension Security
        APPROVED
             ↓
R9B — Plugin Governance Data Model / Registry
             ↓
R9C — Plugin Registration & Approval Lifecycle
             ↓
R9D — Plugin Security, Trust & Execution Isolation
             ↓
R9E — Plugin Tenant / Organisation Governance
             ↓
R9F — Plugin Governance API & Backend Integration
             ↓
R9G — Plugin Runtime Manager Integration
             ↓
R9H — Plugin Governance Tests & Security Validation
             ↓
R9 CLOSED
```

Each subsequent phase must be implemented and validated before proceeding to the next architectural slice.

---

# 12. Implementation Gate

Although R9A is approved, this approval does **not** authorize unrestricted modification of the repository.

Implementation must remain:

* incremental;
* auditable;
* test-driven;
* scoped to the approved R9 architecture;
* compatible with R7/R7A/R7A-11;
* compatible with R8;
* consistent with Phase 16A–16E identity/RBAC decisions.

No unrelated refactoring should be introduced under the R9 workstream.

---

# 13. R9B Authorization

R9B is now authorized to begin.

### R9B — Plugin Governance Data Model / Registry

R9B shall define the persistent governance model for:

* plugin identity;
* plugin versions;
* artifact identity;
* publishers;
* owners;
* provenance;
* governance status;
* capabilities;
* permissions;
* tenant scope;
* approval records;
* lifecycle records;
* governance audit events.

R9B must **not yet implement the complete registration API, runtime admission system, sandboxing, or external-plugin execution model** unless explicitly required by the approved R9B contract.

---

# 14. Supabase Boundary

The approval of R9A does not reopen R8.

The following remain established:

```text
Supabase Auth
      ↓
Frontend Session
      ↓
Bearer Access Token
      ↓
FastAPI JWT Verification
      ↓
Professional Profile
      ↓
Hospital Membership
      ↓
RBAC
      ↓
Backend Authorization
```

Live Supabase deployment remains a separate operational/integration-validation track.

---

# 15. Existing Runtime Plugin Infrastructure

The existing:

* `PluginManager`;
* `PluginRegistry`;
* `PluginLoader`;
* `PluginValidator`;
* plugin manifests;
* workflow manager;
* routing policy;
* plugin contracts;

shall be preserved unless a later approved R9 decision establishes a necessary change.

R9 implementation should integrate governance with this foundation rather than unnecessarily replacing it.

---

# 16. No Architecture Reopening

Approval of R9A does not reopen:

* Phase 16A Identity/Tenant Architecture;
* Phase 16B Identity/Tenant Database Schema;
* Phase 16C Role & Permission Matrix;
* Phase 16D Supabase Auth Architecture;
* Phase 16E Backend Authentication/RBAC;
* R7;
* R7A;
* R7A-11;
* R8 Frontend Session Lifecycle.

Any change to those established decisions requires a separate architectural decision.

---

# 17. R9A Final Decision Record

| Decision ID | Decision                                                     | Status       |
| ----------- | ------------------------------------------------------------ | ------------ |
| R9A-01      | Governance and runtime registries are separate               | **APPROVED** |
| R9A-02      | Persistent governance registry is required                   | **APPROVED** |
| R9A-03      | External plugins require explicit registration               | **APPROVED** |
| R9A-04      | Registration does not imply approval                         | **APPROVED** |
| R9A-05      | Approval does not imply activation                           | **APPROVED** |
| R9A-06      | Unapproved plugins cannot execute                            | **APPROVED** |
| R9A-07      | Artifact identity must be governed                           | **APPROVED** |
| R9A-08      | Provenance must be recorded                                  | **APPROVED** |
| R9A-09      | External plugin integrity/signature verification is required | **APPROVED** |
| R9A-10      | Capabilities and permissions must be explicitly governed     | **APPROVED** |
| R9A-11      | Platform credentials must not be unrestrictedly exposed      | **APPROVED** |
| R9A-12      | External plugin execution requires isolation                 | **APPROVED** |
| R9A-13      | Plugin governance must respect existing tenant authority     | **APPROVED** |
| R9A-14      | Hospital-specific plugin governance requires explicit design | **APPROVED** |
| R9A-15      | Plugin lifecycle must be auditable                           | **APPROVED** |
| R9A-16      | Revoked/quarantined plugins cannot execute                   | **APPROVED** |
| R9A-17      | Plugin versions/artifacts require governance                 | **APPROVED** |
| R9A-18      | Frontend registry is not governance authority                | **APPROVED** |
| R9A-19      | Plugin failure must fail safely                              | **APPROVED** |
| R9A-20      | Plugins cannot bypass clinical safety or clinician authority | **APPROVED** |
| R9A-21      | R9 implementation proceeds incrementally                     | **APPROVED** |
| R9A-22      | R9B is authorized to begin                                   | **APPROVED** |

---

# 18. Final Status

```text
PHASE: R9A
TITLE: Plugin Governance & External Extension Security Architecture
STATUS: APPROVED
ARCHITECTURE: APPROVED
IMPLEMENTATION: AUTHORIZED
NEXT SLICE: R9B — Plugin Governance Data Model / Registry
```

> **R9A is formally approved. R9B may now begin.**

