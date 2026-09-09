# R9D — Plugin Security, Trust & Execution Isolation

**Status:** Approved
**Phase:** R9 — Plugin Governance & External Extension Security
**Predecessor:** R9C — Plugin Registration & Approval Lifecycle
**Next:** R9E — Plugin Tenant / Organisation Governance

---

## 1. Purpose

R9D defines the security, trust, integrity, and execution-isolation architecture for plugins used by the Pharmatrybe.

The purpose is to ensure that both **internal plugins** and **externally supplied hospital plugins** can use the same platform plugin engine while maintaining appropriate security boundaries.

R9D specifically addresses:

* plugin trust;
* plugin integrity;
* uploaded plugin security;
* execution isolation;
* plugin permissions;
* credential access;
* dependency security;
* malicious or compromised plugins;
* activation safety;
* runtime failure containment;
* security monitoring;
* revocation and quarantine.

R9D does **not** redesign the plugin engine.

The architectural objective remains:

> **External plugins must use the same plugin engine, contracts, orchestration, and execution lifecycle as internal plugins.**

The difference is in **governance and trust controls**, not in the fundamental plugin execution model.

---

# 2. Architectural Principle

The platform shall maintain a single plugin execution architecture.

```text
Internal Plugin
      │
      ├── registration
      ├── validation
      ├── approval
      ├── activation
      ▼
┌──────────────────────────────┐
│      Common Plugin Engine    │
└──────────────────────────────┘
      ▲
      │
      ├── registration
      ├── validation
      ├── approval
      ├── activation
      │
External Hospital Plugin
```

The platform must **not** create a completely separate backend implementation for external plugins.

Instead:

```text
Different trust/governance path
             ↓
Same validated plugin contract
             ↓
Same plugin engine
             ↓
Same orchestration
             ↓
Same clinical safety boundary
```

---

# 3. Plugin Trust Model

R9D establishes three security-relevant plugin states:

```text
UNTRUSTED
    ↓
VALIDATED
    ↓
APPROVED
    ↓
ACTIVE
```

And two protective states:

```text
ACTIVE
  │
  ├── DISABLED
  │
  ├── REVOKED
  │
  └── QUARANTINED
```

These states must not be treated as interchangeable.

### 3.1 Untrusted

A plugin is untrusted when it has been:

* uploaded;
* submitted;
* discovered;
* imported;
* or otherwise introduced into the platform

but has not yet passed the required validation and approval process.

An untrusted plugin:

* must not execute clinical workloads;
* must not access patient data;
* must not access hospital data;
* must not access protected credentials;
* must not become part of clinical orchestration.

---

## 3.2 Validated

A validated plugin has passed the technical validation requirements defined by R9C/R9D.

Validation may include:

* manifest validation;
* plugin identity validation;
* version validation;
* plugin contract validation;
* package integrity checks;
* dependency checks;
* capability checks;
* security checks;
* compatibility checks.

Validation does **not** mean the plugin is approved for clinical use.

Therefore:

```text
VALIDATED ≠ APPROVED
```

---

## 3.3 Approved

A plugin becomes approved only through the governance process defined in R9C.

For hospital-controlled plugins:

> **Only an authorised hospital administrator may approve a plugin for that hospital.**

Approval establishes that the hospital has accepted the plugin for its intended use.

---

## 3.4 Active

Only an approved plugin may become active.

An active plugin may participate in its authorised workflows subject to:

* capability restrictions;
* permission restrictions;
* tenant restrictions;
* execution controls;
* plugin contract rules.

---

# 4. Internal and External Plugins

R9D recognises two major plugin origins.

### 4.1 Internal plugins

Examples include:

* WHO knowledge plugin;
* internally developed knowledge plugins;
* internal prediction plugins;
* internally maintained clinical plugins.

Internal plugins are developed and controlled by the Pharmatrybe project/platform.

The WHO plugin is considered an **internal knowledge plugin**, even though its knowledge may originate from an external organisation or external data source.

---

### 4.2 External hospital plugins

External plugins are plugins supplied or uploaded by a hospital.

Examples include:

* hospital-specific knowledge plugins;
* hospital-specific antimicrobial resistance knowledge;
* hospital-approved prediction models;
* hospital-developed ML prediction plugins.

External plugins are still required to conform to the same platform plugin contracts.

---

# 5. Knowledge Plugins

Knowledge plugins may obtain structured knowledge from approved sources such as:

* Supabase;
* approved external databases;
* hospital-managed knowledge repositories;
* approved knowledge services.

The plugin itself must not bypass the platform governance model.

For example:

```text
Knowledge Plugin
      ↓
Approved data source
      ↓
Structured knowledge
      ↓
Common Plugin Engine
      ↓
Workflow
```

The fact that knowledge originates from a database does not automatically make the plugin trusted.

Trust applies to:

1. the plugin implementation;
2. its declared capabilities;
3. its data sources;
4. its configuration;
5. its approved use.

---

# 6. Prediction Plugins

Prediction plugins are ML-model-based plugins.

They may contain:

* trained model artifacts;
* preprocessing logic;
* feature transformation;
* model inference logic;
* model metadata;
* model version information.

A prediction plugin must not be allowed to bypass the common plugin interface.

The platform should treat:

```text
Prediction Plugin
      ↓
Model inference
      ↓
Structured prediction
      ↓
Common orchestration
```

as the normal execution path.

The plugin does not directly determine the final clinical recommendation.

---

# 7. Plugin Package Security

External plugins may be supplied as a ZIP package.

However:

> **Uploading a ZIP file does not mean the ZIP file is trusted or executable.**

The upload process must initially treat the package as untrusted input.

Conceptually:

```text
Hospital Admin Upload
        ↓
Untrusted Package
        ↓
Package Inspection
        ↓
Manifest Extraction
        ↓
Integrity Validation
        ↓
Security Validation
        ↓
Compatibility Validation
        ↓
Governance Approval
        ↓
Activation
```

No clinical execution occurs before approval and activation.

---

# 8. Package Integrity

Every uploaded plugin package should receive a cryptographic integrity identity.

At minimum, the platform should calculate a cryptographic hash of the submitted artifact.

Conceptually:

```text
Plugin ZIP
    ↓
SHA-256
    ↓
Artifact Hash
```

The hash becomes part of the plugin's governance record.

This allows the platform to detect:

* replacement;
* modification;
* corruption;
* unexpected package changes.

A changed artifact must not silently remain associated with an existing approved plugin version.

---

# 9. Plugin Identity

Each plugin must have a stable identity.

The identity should distinguish at least:

```text
plugin_id
plugin_version
artifact_hash
```

The combination provides a traceable identity for an approved plugin artifact.

A new artifact should not overwrite an existing approved artifact without going through the appropriate lifecycle.

For example:

```text
Plugin A
v1.0
hash X
```

is distinct from:

```text
Plugin A
v1.1
hash Y
```

even though both share the same logical plugin identity.

---

# 10. Manifest Security

Every plugin package must contain a machine-readable manifest appropriate to its plugin type.

The manifest should identify information such as:

* plugin ID;
* plugin name;
* version;
* plugin type;
* publisher;
* capabilities;
* entry point;
* SDK/platform compatibility;
* declared dependencies;
* configuration requirements.

The manifest is **metadata**, not proof of trust.

Therefore:

> A plugin must never become trusted merely because its manifest claims that it is trusted.

The platform must independently validate the package.

---

# 11. Signature Verification

R9D establishes support for plugin artifact signing as a security control for external plugins.

Where the platform requires signed plugins, the uploaded artifact must contain or be accompanied by verifiable signing information.

Conceptually:

```text
Plugin Artifact
      +
Digital Signature
      +
Trusted Publisher Key
      ↓
Signature Verification
```

The platform must verify:

* signature validity;
* artifact integrity;
* trusted publisher identity;
* signature association with the submitted artifact.

An invalid signature must result in rejection or quarantine according to the governance lifecycle.

---

# 12. Publisher and Provenance

External plugins must maintain provenance information.

At minimum, governance should be able to identify:

* who submitted the plugin;
* which hospital owns the registration;
* plugin publisher;
* plugin version;
* artifact hash;
* registration timestamp;
* approval actor;
* approval timestamp.

This provides an auditable chain:

```text
Publisher
   ↓
Artifact
   ↓
Submission
   ↓
Validation
   ↓
Approval
   ↓
Activation
```

---

# 13. Dependency Security

External plugins must declare their dependencies.

The platform must validate dependencies before activation.

Dependency validation should consider:

* supported versions;
* incompatible versions;
* prohibited dependencies;
* known platform conflicts;
* dependency availability;
* dependency integrity.

The platform must avoid silently installing arbitrary dependencies from an uploaded plugin package.

A plugin should not be able to introduce uncontrolled packages into the production runtime.

---

# 14. Arbitrary Code Execution

A major security concern is that external Python plugins may contain arbitrary executable code.

Therefore:

> **An uploaded external plugin must never be treated as automatically safe merely because it conforms to the plugin interface.**

Interface compliance validates structure.

It does not prove code safety.

The architecture must therefore distinguish:

```text
Plugin Contract Validation
            ≠
Code Trust
```

and:

```text
Plugin Validation
            ≠
Security Clearance
```

---

# 15. Execution Isolation

R9D establishes execution isolation as a mandatory architectural concern for external plugins.

The exact implementation mechanism may be selected during implementation, but the architecture must support isolation sufficient to prevent an external plugin from freely accessing:

* unrelated application internals;
* other hospital data;
* unrelated filesystem data;
* unrestricted credentials;
* unrestricted database access;
* unrelated plugins;
* platform secrets.

The preferred execution boundary should be:

```text
Platform
   │
   ├── Plugin Governance
   │
   ├── Plugin Runtime
   │
   └── Controlled Plugin Execution Boundary
             │
             └── External Plugin
```

The implementation must not assume that Python module-level separation constitutes security isolation.

---

# 16. Credential Isolation

Plugins must not receive unrestricted platform credentials.

In particular, external plugins must not receive:

* Supabase service-role credentials;
* database administrator credentials;
* application signing keys;
* arbitrary backend secrets;
* unrelated hospital credentials.

A plugin should receive only explicitly authorised resources.

Conceptually:

```text
Platform Credentials
        │
        X
        │
External Plugin

Approved Capability
        │
        ↓
Controlled Plugin Interface
```

---

# 17. Supabase Access

External plugins must not directly receive unrestricted Supabase access.

If a plugin needs knowledge from Supabase, the preferred architecture is:

```text
Plugin
  ↓
Approved plugin capability/interface
  ↓
Platform service
  ↓
Supabase
```

rather than:

```text
Plugin
  ↓
Supabase service-role key
```

This preserves the platform's security boundary.

---

# 18. Database Access

External plugins must not have unrestricted direct database access.

Any database interaction must be mediated through an approved platform capability or appropriately scoped mechanism.

The plugin must not be able to:

* query unrelated hospitals;
* modify identity records;
* modify RBAC;
* alter governance records;
* bypass application authorization;
* directly manipulate clinical recommendation state.

---

# 19. Tenant Security

R9D establishes the security principle that:

> **A plugin must never gain access to a hospital's data merely because the plugin code is executing inside the hospital's context.**

Tenant access must be explicitly authorised.

This is particularly important because the Pharmatrybe is multi-tenant.

The plugin execution context should therefore include a controlled tenant context rather than unrestricted access to tenant data.

Detailed hospital/plugin ownership rules are deferred to:

**R9E — Plugin Tenant / Organisation Governance.**

---

# 20. Capability-Based Access

Plugins should operate through declared capabilities.

For example:

```text
Knowledge Plugin
    ├── read approved knowledge source
    └── return structured knowledge

Prediction Plugin
    ├── receive authorised model input
    └── return prediction output
```

A plugin should not automatically receive:

```text
filesystem
database
Supabase
email
network
patient records
RBAC
governance
```

simply because those services exist in the application.

---

# 21. Network Access

External plugins should not receive unrestricted outbound network access.

If network access is required, it should be:

* explicitly declared;
* governed;
* limited to approved destinations where practical;
* auditable.

This is particularly important for external knowledge plugins.

A plugin must not silently transmit patient or hospital information to arbitrary external services.

---

# 22. Clinical Data Protection

External plugins may process clinical information only when explicitly authorised for the relevant workflow.

The platform must minimise the data supplied to plugins.

Where possible:

```text
Full Patient Record
       ↓
Required Clinical Features
       ↓
Plugin
```

rather than:

```text
Full Patient Record
       ↓
External Plugin
```

The plugin receives only the information required for its declared function.

---

# 23. Plugin Output Boundary

A plugin must return structured output through the common plugin contract.

For example:

```text
Plugin
  ↓
Structured Result
  ↓
Validation
  ↓
Workflow Orchestration
  ↓
Clinical Evidence / Knowledge / Prediction Fusion
  ↓
CDSS Recommendation
```

A plugin must not directly:

* prescribe treatment;
* modify the final recommendation;
* bypass evidence rules;
* override clinical safety rules;
* alter RBAC;
* modify governance state.

This preserves the project's core principle:

> **AI and plugins support clinical decision-making; they do not replace clinician judgement.**

---

# 24. Plugin Failure Isolation

A plugin failure must not automatically bring down the entire CDSS.

Failures should be contained and represented as structured execution failures.

Examples include:

* timeout;
* invalid output;
* dependency failure;
* unavailable data source;
* runtime exception;
* resource exhaustion;
* security violation.

The platform should be able to distinguish:

```text
Plugin failed
```

from:

```text
Platform failed
```

---

# 25. Timeout and Resource Controls

External plugins must operate within defined resource boundaries.

The implementation should support controls for:

* execution timeout;
* memory consumption;
* CPU/resource consumption;
* request size;
* response size;
* concurrency.

A plugin must not be able to consume unlimited platform resources.

Exact thresholds are implementation/configuration decisions and are not fixed by this document.

---

# 26. Malicious Behaviour

The platform must have a mechanism to respond to suspicious plugin behaviour.

Potential triggers include:

* repeated execution failures;
* integrity mismatch;
* invalid signature;
* unexpected package modification;
* prohibited capability access;
* resource abuse;
* unexpected network access;
* security policy violation.

The resulting lifecycle may be:

```text
ACTIVE
  ↓
SUSPENDED
  ↓
QUARANTINED
  ↓
REVOKED
```

The exact governance transition is defined jointly with R9C/R9F.

---

# 27. Quarantine

A quarantined plugin must not execute normal clinical workloads.

Quarantine is intended to preserve the artifact and evidence while preventing further execution.

Possible reasons include:

* failed security validation;
* signature failure;
* integrity mismatch;
* suspected compromise;
* repeated runtime violations;
* administrative security action.

---

# 28. Revocation

Revocation is stronger than disabling.

### Disabled

The plugin is intentionally inactive but remains approved.

### Revoked

The plugin's approval is withdrawn.

A revoked plugin must not become active again without going through the appropriate approval process.

Conceptually:

```text
APPROVED
   ↓
ACTIVE
   ↓
REVOKED
   X
   │
   └── cannot reactivate directly
```

---

# 29. Plugin Replacement

An approved plugin artifact must never be silently replaced.

If a hospital uploads a new version:

```text
Existing Plugin
      ↓
Existing Approved Artifact
```

must remain identifiable.

The new artifact becomes:

```text
New Version
      ↓
New Hash
      ↓
New Validation
      ↓
New Approval
```

This ensures reproducibility and auditability.

---

# 30. Auditability

Security-sensitive plugin operations must be auditable.

At minimum, the system should be able to determine:

* plugin identity;
* plugin version;
* artifact hash;
* plugin origin;
* submitting administrator;
* approval administrator;
* activation actor;
* deactivation actor;
* revocation actor;
* timestamps;
* relevant security events.

Detailed governance audit data is addressed in R9B/R9F.

---

# 31. Internal Plugin Security

Internal plugins should use the same common plugin contracts and runtime engine.

However, internal plugins may have a different trust establishment process because they are controlled by the platform development process.

This does **not** mean internal plugins bypass:

* validation;
* compatibility checks;
* lifecycle controls;
* runtime monitoring;
* output validation.

The distinction is:

```text
Internal:
Platform-controlled trust establishment

External:
Hospital-controlled governance + platform security validation
```

---

# 32. No Separate External Plugin Engine

The platform must not create:

```text
Internal Plugin Engine
External Plugin Engine
```

Instead:

```text
                 Plugin Governance
                        │
            ┌───────────┴───────────┐
            ↓                       ↓
       Internal Plugin       External Plugin
            │                       │
            └───────────┬───────────┘
                        ↓
                 Common Plugin Engine
                        ↓
                   Orchestration
```

This preserves maintainability and prevents the platform from developing two incompatible plugin architectures.

---

# 33. Security Boundary Summary

| Boundary                                | Required Control              |
| --------------------------------------- | ----------------------------- |
| Plugin package → platform               | Validation + integrity        |
| Publisher → plugin identity             | Provenance                    |
| Artifact → approved version             | Hash/signature                |
| Plugin → platform secrets               | Denied by default             |
| Plugin → Supabase                       | Controlled capability         |
| Plugin → database                       | Controlled capability         |
| Plugin → tenant data                    | Explicit tenant authorization |
| Plugin → network                        | Controlled/limited            |
| Plugin → filesystem                     | Restricted                    |
| Plugin → other plugins                  | Controlled                    |
| Plugin → clinical workflow              | Common contract               |
| Plugin → final recommendation           | No direct authority           |
| Plugin → platform resources             | Resource limits               |
| Plugin failure → platform               | Isolation                     |
| Compromised plugin → clinical execution | Quarantine/revocation         |

---

# 34. Security Invariants

The following are mandatory R9D invariants.

### R9D-S1 — Untrusted plugins cannot execute clinical workloads

```text
UNTRUSTED ≠ EXECUTABLE
```

### R9D-S2 — Approval is required before activation

```text
APPROVED → ACTIVE
```

not:

```text
UPLOADED → ACTIVE
```

### R9D-S3 — Artifact integrity must be verifiable

An approved artifact must be identifiable through a stable integrity mechanism.

### R9D-S4 — External plugins cannot receive unrestricted credentials

Platform secrets remain outside plugin authority.

### R9D-S5 — Plugins cannot bypass tenant authorization

Plugin execution must remain within the approved tenant context.

### R9D-S6 — Plugins cannot directly control clinical recommendations

Plugin outputs remain inputs to the CDSS workflow.

### R9D-S7 — Plugin failures must be contained

A plugin failure must not automatically become a platform failure.

### R9D-S8 — Approved artifacts cannot be silently replaced

Any material artifact change creates a new version/approval boundary.

### R9D-S9 — Revoked plugins cannot directly reactivate

Reactivation requires governance.

### R9D-S10 — External plugins use the common plugin engine

No separate external-plugin execution architecture is permitted.

---

# 35. Relationship to R9C

R9C defines **who may register/approve and how the lifecycle progresses**.

R9D defines **whether the plugin is safe to execute and what the plugin is allowed to access**.

Therefore:

```text
R9C
Governance Lifecycle
        ↓
R9D
Security / Trust / Isolation
```

Both are required before a plugin can become clinically active.

---

# 36. Relationship to R9E

R9D establishes the security principle that plugin access must respect tenant boundaries.

R9E will define the detailed organisation/hospital model, including:

* hospital ownership;
* hospital plugin visibility;
* hospital plugin installation;
* hospital plugin configuration;
* hospital-specific plugin activation;
* cross-hospital restrictions;
* global versus hospital-scoped plugins.

R9D does not pre-empt those detailed decisions.

---

# 37. Relationship to R9F

R9F will define the backend/API implementation of:

* registration;
* approval;
* activation;
* deactivation;
* revocation;
* quarantine;
* plugin metadata;
* security status.

R9D defines the security requirements those APIs must enforce.

---

# 38. Relationship to R9G

R9G will integrate the approved governance model into the existing:

* `PluginManager`;
* `PluginRegistry`;
* `PluginLoader`;
* `PluginValidator`;
* workflow/orchestration infrastructure.

R9G must preserve the principle:

> **Governance controls determine what may enter the runtime; the existing plugin engine determines how an approved plugin executes.**

---

# 39. Relationship to R9H

R9H must verify the R9D security invariants through automated tests.

Tests should eventually cover:

* untrusted plugin cannot execute;
* invalid artifact rejected;
* hash mismatch detected;
* signature failure rejected;
* incompatible plugin rejected;
* prohibited dependency rejected;
* unauthorized capability denied;
* unauthorized tenant access denied;
* credential isolation;
* resource limits;
* plugin failure isolation;
* quarantine;
* revocation;
* artifact replacement detection;
* approved external plugin executes through the same engine as internal plugins.

---

# 40. Implementation Constraint

R9D is an architectural decision document.

It does **not** authorize implementation of:

* sandbox infrastructure;
* signature infrastructure;
* plugin APIs;
* database tables;
* plugin execution services;
* tenant plugin controls.

Those belong to subsequent R9 implementation slices after the relevant architecture decisions have been confirmed and approved.

---

# 41. Decision Summary

R9D establishes:

1. External plugins are untrusted until validated and approved.
2. Hospital administrators control hospital plugin approval under the R9C governance lifecycle.
3. Plugin packages must have verifiable identity and integrity.
4. Signature/provenance controls are required for external plugin trust.
5. External plugins must not receive unrestricted credentials.
6. External plugins must use controlled capabilities rather than unrestricted platform access.
7. External plugins must respect tenant boundaries.
8. External plugins require execution isolation appropriate to their trust level.
9. Plugin failures must be contained.
10. Plugins can be disabled, quarantined, or revoked.
11. Approved plugin artifacts cannot be silently replaced.
12. Plugin operations must be auditable.
13. Internal and external plugins must use the **same plugin engine and execution architecture**.
14. Plugin governance controls determine **whether** a plugin may execute; the common plugin engine determines **how** it executes.
15. Plugins remain subordinate to the CDSS clinical safety and evidence hierarchy.

---

# 42. Approval Gate

### R9D Status

**Approval decision: Approved**

Before implementation, the project owner should confirm that the following are accepted:

* [ ] External plugins are untrusted by default.
* [ ] Hospital administrators control approval for hospital plugins.
* [ ] Plugin artifact integrity must be verifiable.
* [ ] Signature/provenance controls are required for external plugins.
* [ ] External plugins cannot receive unrestricted platform credentials.
* [ ] External plugins cannot bypass tenant authorization.
* [ ] External plugins require execution isolation.
* [ ] Plugin failures must be contained.
* [ ] Revocation/quarantine are security controls.
* [ ] Approved artifacts cannot be silently replaced.
* [ ] Internal and external plugins use the same plugin engine.
* [ ] Plugin outputs cannot directly override the clinical recommendation.
* [ ] R9E will define the detailed hospital/tenant plugin governance model.

**Approval decision: Approved**
