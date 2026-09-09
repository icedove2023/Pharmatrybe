# R9B — Plugin_Governance_Data_Model_ / _Registry

**Status:** DOCUMENTATION — PENDING CONFIRMATION
**Phase:** R9 — Plugin Governance & External Extension Security
**Depends On:** R9A — Plugin Governance & External Extension Security Architecture Decision — **APPROVED**
**Next:** R9C — Plugin Registration & Approval Lifecycle

---

## 1. Purpose

R9B defines the **data model and governance registry** required to safely register, approve, manage, activate, disable, revoke, and audit hospital-specific plugins.

The registry is the authoritative governance record for plugins.

It is distinct from the existing runtime `PluginRegistry`.

The governance registry answers:

> **What plugin is this, who owns it, which hospital does it belong to, how was it submitted, what state is it in, and is it authorized to execute?**

The runtime registry answers:

> **Which approved plugins are currently loaded and available to the Plugin Manager?**

These responsibilities must remain separate.

---

# 2. Core Architectural Principle

External plugins must ultimately use the **same plugin execution engine and workflow architecture as internal plugins**.

There must not be:

```text
Internal Plugin Engine
External Plugin Engine
```

Instead:

```text
                    ┌──────────────────────┐
                    │ Internal Plugins     │
                    │ WHO / SOAR / ARMD    │
                    └──────────┬───────────┘
                               │
                               │
                    ┌──────────▼───────────┐
                    │ Standard Plugin      │
                    │ Interface / SDK      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Plugin Manager       │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ Workflow Manager     │
                    └──────────┬───────────┘
                               │
                               ▼
                    Clinical Decision Flow
```

External hospital plugins enter the same path:

```text
Hospital Admin
      │
      ▼
Plugin Registration
      │
      ▼
Governance Registry
      │
      ▼
Validation / Approval
      │
      ▼
Approved Plugin
      │
      ▼
Plugin Manager
      │
      ▼
Workflow Manager
      │
      ▼
Clinical Decision Flow
```

This preserves one execution architecture.

The existing architecture already defines the Plugin Manager as the central gateway for plugin discovery, validation, registration, configuration, health, loading, unloading, and capability discovery. 

---

# 3. Plugin Classification

The registry MUST distinguish between **internal platform plugins** and **external hospital plugins**.

## 3.1 Internal Platform Plugins

Examples:

| Plugin | Type       | Classification |
| ------ | ---------- | -------------- |
| WHO    | Knowledge  | Internal       |
| SOAR   | Prediction | Internal       |
| ARMD   | Prediction | Internal       |

These plugins are maintained and controlled by the platform.

They do not require the hospital-plugin registration workflow.

The existing architecture confirms WHO as a knowledge plugin and SOAR/ARMD as prediction plugins. 

---

# 4. External Hospital Plugins

External plugins are plugins supplied for use by a specific hospital/organisation.

Examples may include:

### Knowledge plugins

* hospital antimicrobial guidelines;
* hospital formulary;
* local antimicrobial database;
* local stewardship policies;
* local resistance knowledge;
* hospital-specific clinical rules;
* local structured evidence repositories.

### Prediction plugins

Prediction plugins are **ML-model-based plugins**.

Examples:

* hospital-specific resistance prediction;
* local susceptibility prediction;
* antimicrobial risk prediction;
* locally trained MIC prediction;
* other approved ML models.

The registry MUST identify the plugin type explicitly.

```text
KNOWLEDGE
PREDICTION
```

Additional plugin categories may be added later through an approved architecture decision.

---

# 5. Registration Authority

Only an authenticated **Hospital Admin** may register a hospital plugin.

This is a mandatory governance rule.

```text
Professional
     │
     ├── Clinician        → NO
     ├── Pharmacist       → NO
     ├── Stewardship      → NO
     ├── Researcher       → NO
     └── Hospital Admin   → YES
```

The Hospital Admin's authority comes from the existing backend RBAC model.

The frontend MUST NOT be treated as the authorization authority.

The backend must verify:

1. authenticated identity;
2. active professional profile;
3. active hospital membership;
4. canonical Hospital Admin role;
5. plugin registration permission.

---

# 6. Hospital Ownership

Every external plugin MUST belong to exactly one hospital/organisation at registration time.

```text
Plugin
   │
   └── exactly one owning hospital
```

A plugin cannot be registered without an owning hospital.

A hospital admin cannot register a plugin on behalf of another hospital unless a future approved cross-organisation governance model explicitly permits it.

This follows the established identity architecture in which a professional belongs to one active hospital/organisation.

---

# 7. Governance Registry vs Runtime Registry

## 7.1 Governance Registry

Persistent and authoritative.

Stores:

* plugin identity;
* ownership;
* type;
* version;
* registration;
* approval;
* lifecycle;
* provenance;
* artifact information;
* capabilities;
* compatibility;
* audit references.

The governance registry should be database-backed.

Supabase/PostgreSQL is compatible with the existing architecture and is the preferred persistence direction because identity, membership, RBAC, RLS, and other governance-related platform data already use this foundation. 

---

## 7.2 Runtime Registry

The existing runtime registry remains responsible for:

* loaded plugins;
* instantiated plugin objects;
* runtime state;
* health;
* execution availability;
* lifecycle operations.

It MUST NOT become the authoritative source for governance.

Therefore:

```text
Governance Registry
        │
        │ approved configuration
        ▼
Plugin Manager
        │
        ▼
Runtime Registry
```

---

# 8. Plugin Registration Record

Each external plugin MUST have a persistent registration record.

Conceptually:

```text
plugin
```

### Required fields

| Field           | Purpose                              |
| --------------- | ------------------------------------ |
| `plugin_id`     | Globally unique plugin identity      |
| `plugin_name`   | Human-readable name                  |
| `plugin_type`   | KNOWLEDGE / PREDICTION               |
| `plugin_source` | INTERNAL / HOSPITAL                  |
| `hospital_id`   | Owning hospital                      |
| `description`   | Human-readable description           |
| `version`       | Plugin version                       |
| `status`        | Governance lifecycle state           |
| `capabilities`  | Declared capabilities                |
| `compatibility` | Platform/SDK compatibility           |
| `created_at`    | Registration creation time           |
| `updated_at`    | Last modification time               |
| `created_by`    | Registering Hospital Admin           |
| `approved_by`   | Approving authority where applicable |
| `approved_at`   | Approval timestamp                   |

---

# 9. Plugin Identity

`plugin_id` MUST be immutable once registration is created.

Changing the implementation version MUST NOT create an identity collision.

Conceptually:

```text
plugin_id
    │
    ├── version 1.0.0
    ├── version 1.1.0
    └── version 2.0.0
```

The system must preserve version history.

A new artifact must never silently replace an approved artifact under the same version.

---

# 10. Plugin Version Record

A separate version-level record is recommended.

```text
plugin
   │
   └── plugin_version
          ├── version
          ├── artifact
          ├── checksum
          ├── provenance
          ├── compatibility
          ├── approval
          └── lifecycle
```

This allows the platform to distinguish:

```text
Plugin identity
```

from:

```text
Specific executable/model/data version
```

---

# 11. Plugin Submission Method

The registration model must support two complementary submission mechanisms.

## 11.1 Structured Registration Form

A Hospital Admin may provide:

* plugin name;
* description;
* type;
* version;
* capabilities;
* compatibility information;
* plugin metadata;
* source/provenance information;
* configuration information.

The form does not replace validation.

It only captures governance metadata.

---

## 11.2 ZIP Package Upload

A Hospital Admin may upload a plugin package as a ZIP artifact.

Conceptually:

```text
Hospital Admin
      │
      ▼
Plugin ZIP
      │
      ▼
Upload
      │
      ▼
Artifact Storage
      │
      ▼
Validation
      │
      ▼
Governance Registry
```

The ZIP itself is **not trusted merely because a Hospital Admin uploaded it**.

It must pass the approved validation/security lifecycle defined by R9C/R9D.

---

# 12. Plugin Manifest

A ZIP plugin package MUST contain a machine-readable manifest.

The manifest provides the metadata required for validation and registration.

Conceptually:

```yaml
plugin_id:
name:
version:
type:
entrypoint:
sdk_version:
platform_version:
capabilities:
dependencies:
configuration_schema:
```

The exact manifest schema belongs to the implementation contract and MUST remain compatible with the existing Plugin SDK.

The manifest is metadata.

It is not an approval record.

---

# 13. Knowledge Plugin Data Model

A knowledge plugin MUST identify its knowledge source.

Conceptually:

```text
Knowledge Plugin
       │
       ├── Plugin metadata
       │
       ├── Knowledge source
       │       ├── database
       │       ├── API
       │       └── structured repository
       │
       └── Standard Knowledge Plugin Interface
```

The knowledge source may be backed by systems such as:

* PostgreSQL;
* Supabase;
* SQLite;
* REST;
* GraphQL;
* another approved structured source.

The existing architecture deliberately abstracts knowledge storage from the plugin interface. 

The registry therefore records the **source configuration and governance metadata**, rather than embedding the knowledge database itself inside the plugin record.

---

# 14. Prediction Plugin Data Model

Prediction plugins are ML-model plugins.

Conceptually:

```text
Prediction Plugin
       │
       ├── Model identity
       ├── Model version
       ├── Model artifact
       ├── Input contract
       ├── Output contract
       ├── Feature requirements
       ├── Compatibility
       └── Standard Prediction Plugin Interface
```

The registry MUST distinguish the model version from the plugin identity.

For example:

```text
Plugin:
    resistance-predictor

Version:
    1.3.0

Model:
    resistance-model-2026-08
```

The exact model storage mechanism belongs to R9D/G.

---

# 15. Artifact Record

For uploaded ZIP plugins and model artifacts, the registry should maintain artifact metadata.

Conceptually:

```text
plugin_artifact
```

Fields include:

| Field               | Purpose                      |
| ------------------- | ---------------------------- |
| `artifact_id`       | Artifact identity            |
| `plugin_id`         | Associated plugin            |
| `plugin_version_id` | Associated version           |
| `storage_reference` | Controlled artifact location |
| `filename`          | Uploaded artifact name       |
| `size`              | Artifact size                |
| `checksum`          | Integrity verification       |
| `content_type`      | Artifact type                |
| `uploaded_by`       | Uploading admin              |
| `uploaded_at`       | Upload time                  |
| `scan_status`       | Security validation state    |

Raw ZIP files MUST NOT be stored inside ordinary relational metadata tables.

A controlled artifact-storage mechanism should be used.

---

# 16. Provenance

Every external plugin must have provenance metadata.

At minimum:

```text
Who supplied it?
Which hospital owns it?
When was it submitted?
What version was submitted?
What artifact was submitted?
What checksum identifies it?
```

Optional publisher information may include:

* developer organisation;
* development team;
* source repository;
* vendor;
* model developer.

---

# 17. Integrity

Every uploaded executable/model artifact MUST have an integrity identifier.

At minimum:

```text
checksum / cryptographic hash
```

The registry must preserve the checksum associated with the approved version.

An approved plugin artifact must not silently change after approval.

If the artifact changes:

```text
old checksum ≠ new checksum
```

the system must treat it as a different artifact/version requiring the appropriate governance process.

---

# 18. Plugin Capability Record

Plugins must explicitly declare capabilities.

Examples:

```text
knowledge.guidelines
knowledge.formulary
knowledge.resistance
prediction.resistance
prediction.mic
prediction.risk
```

Capabilities are metadata and must not automatically grant permission.

A plugin declaring:

```text
prediction.resistance
```

does not automatically gain access to every clinical dataset.

Capability authorization is defined by the security model in R9D/R9E.

---

# 19. Plugin Configuration

Plugin configuration must be represented separately from plugin identity.

Conceptually:

```text
plugin
   │
   └── plugin_configuration
```

Configuration may include:

* approved data source;
* model configuration;
* endpoint configuration;
* feature configuration;
* hospital-specific parameters.

Sensitive credentials MUST NOT be stored as ordinary plugin metadata.

Credential handling belongs to the security architecture.

---

# 20. Plugin Governance Status

The registry MUST maintain a durable lifecycle state.

Initial state:

```text
PENDING
```

Possible states:

```text
PENDING
APPROVED
REJECTED
DISABLED
REVOKED
QUARANTINED
```

The exact transitions are defined in R9C.

A plugin's runtime `enabled` flag must never replace governance status.

---

# 21. Activation State

Governance status and runtime activation are distinct.

Example:

```text
Governance:
APPROVED

Runtime:
INACTIVE
```

or:

```text
Governance:
APPROVED

Runtime:
ACTIVE
```

An approved plugin is not necessarily immediately active.

The Plugin Manager may only load a plugin when governance permits activation.

---

# 22. Revocation

The registry must preserve revocation information.

Conceptually:

```text
revoked_at
revoked_by
revocation_reason
```

Revocation MUST be durable.

A revoked plugin must not become executable simply because its ZIP remains available.

---

# 23. Quarantine

A plugin may be placed into:

```text
QUARANTINED
```

when:

* validation fails;
* security review is required;
* suspicious behaviour is detected;
* artifact integrity changes;
* compatibility becomes invalid;
* an incident occurs.

A quarantined plugin must not execute.

---

# 24. Hospital Ownership Model

The registry must enforce:

```text
hospital
   │
   └── many plugins
```

while each plugin has:

```text
exactly one owning hospital
```

Example:

```text
Hospital A
 ├── Local Resistance Predictor
 ├── Hospital Guideline Knowledge
 └── Local Formulary

Hospital B
 ├── Resistance Predictor
 └── Stewardship Rules
```

Hospital A must never be able to administer Hospital B's plugins.

This must be enforced by backend authorization and database RLS where applicable.

---

# 25. Hospital Admin Authority

The governance registry must associate registration actions with the authenticated Hospital Admin.

```text
plugin_registration
    │
    ├── plugin_id
    ├── hospital_id
    ├── submitted_by
    └── submitted_at
```

This provides accountability.

The frontend must not be allowed to submit an arbitrary `hospital_id` as an authority override.

The backend derives the hospital from the authenticated identity/membership context.

This is consistent with the established tenant architecture.

---

# 26. Approval Record

Approval should be represented as an auditable record rather than merely changing a boolean.

Conceptually:

```text
plugin_approval
    │
    ├── plugin_version_id
    ├── decision
    ├── decided_by
    ├── decided_at
    ├── reason
    └── validation_reference
```

This preserves the history of governance decisions.

---

# 27. Registration Audit Record

Every important governance action should be auditable.

Examples:

```text
REGISTERED
SUBMITTED
VALIDATED
APPROVED
REJECTED
ACTIVATED
DISABLED
REVOKED
QUARANTINED
RESTORED
VERSION_UPLOADED
CONFIGURATION_CHANGED
```

Each event should identify:

* actor;
* hospital;
* plugin;
* version;
* timestamp;
* action;
* outcome;
* relevant reason/reference.

---

# 28. Plugin Audit Model

Conceptually:

```text
plugin_audit_event
```

with:

| Field               | Purpose                       |
| ------------------- | ----------------------------- |
| `event_id`          | Unique event                  |
| `plugin_id`         | Plugin                        |
| `plugin_version_id` | Version                       |
| `hospital_id`       | Tenant                        |
| `actor_id`          | Authenticated actor           |
| `event_type`        | Governance event              |
| `event_time`        | Timestamp                     |
| `reason`            | Explanation                   |
| `metadata`          | Additional structured context |

The audit trail must be append-oriented.

Historical governance events must not be silently overwritten.

---

# 29. Registry Relationships

The conceptual model is:

```text
Hospital
   │
   └──────────────┐
                  │
                  ▼
               Plugin
                  │
          ┌───────┴────────┐
          ▼                ▼
   Plugin Versions     Audit Events
          │
          ├── Artifact
          │
          ├── Approval
          │
          └── Configuration
```

And:

```text
Plugin
   │
   ▼
Governance Registry
   │
   │ APPROVED + ACTIVE
   ▼
Plugin Manager
   │
   ▼
Runtime Registry
   │
   ▼
Workflow Manager
```

---

# 30. Runtime Engine Principle

External plugins MUST NOT receive a separate execution engine.

The runtime path must remain:

```text
Internal Plugin
       │
       ├──────────────┐
       │              │
       ▼              ▼
Plugin Manager ← External Plugin
       │
       ▼
Workflow Manager
       │
       ▼
Clinical Decision Support Pipeline
```

Therefore, the distinction between internal and external plugins is primarily **governance and provenance**, not execution architecture.

This is a key R9B decision.

---

# 31. What the Registry Does NOT Do

The governance registry does not:

* execute plugins;
* perform clinical reasoning;
* replace the Plugin Manager;
* replace the Workflow Manager;
* determine final clinical recommendations;
* directly authorize clinical treatment;
* store raw clinical datasets inside plugin metadata;
* replace RBAC;
* replace RLS;
* replace plugin security isolation.

---

# 32. Separation of Concerns

The architecture must maintain:

```text
Identity / RBAC
        ↓
Who may administer plugins?

Governance Registry
        ↓
What plugin is approved?

Plugin Security
        ↓
Can the plugin safely execute?

Plugin Manager
        ↓
How is the plugin loaded?

Workflow Manager
        ↓
How does the plugin participate?

Clinical Decision Support
        ↓
How are outputs combined and explained?
```

No single component should assume all of these responsibilities.

---

# 33. Frontend Registration Model

The future frontend should provide a Hospital Admin plugin-management experience.

Conceptually:

```text
Plugin Management
│
├── Registered Plugins
├── Register Plugin
├── Upload Plugin
├── Plugin Details
├── Versions
├── Approval Status
├── Activation Status
└── Audit History
```

The UI is a client of the governance API.

It is not the governance authority.

---

# 34. Registration Form

The registration workflow should support structured metadata such as:

```text
Plugin Name
Plugin Type
Description
Version
Capabilities
Compatibility
Developer / Publisher
Data Source / Model Information
Plugin Package
```

For a ZIP submission:

```text
Plugin Metadata
        +
ZIP Artifact
```

must be treated as one registration/version submission.

---

# 35. Knowledge Plugin Registration

For a knowledge plugin:

```text
Plugin Type:
KNOWLEDGE
```

The registration should identify:

```text
Knowledge Source
```

rather than assuming the knowledge itself is embedded in the plugin.

For example:

```text
Hospital Knowledge Plugin
        │
        ▼
Approved Knowledge Source
        │
        ▼
Standard Knowledge Plugin Interface
```

This is compatible with the existing architecture's database/API-backed knowledge-source model. 

---

# 36. Prediction Plugin Registration

For a prediction plugin:

```text
Plugin Type:
PREDICTION
```

The registration must identify the ML model artifact and its contract.

At minimum:

```text
Model version
Model artifact
Input schema
Output schema
Feature requirements
Compatibility
Performance/validation metadata
```

The plugin still executes through the standard prediction-plugin interface.

---

# 37. Internal vs External Governance

Internal plugins:

```text
Platform-controlled
       ↓
Platform registry
       ↓
Plugin Manager
```

External hospital plugins:

```text
Hospital Admin
       ↓
Governance Registry
       ↓
Approval
       ↓
Plugin Manager
```

Both eventually converge:

```text
                 Plugin Manager
                       │
              ┌────────┴────────┐
              ▼                 ▼
       Internal Plugin    Approved External Plugin
              │                 │
              └────────┬────────┘
                       ▼
                Workflow Manager
```

---

# 38. Security Invariants

R9B establishes these mandatory invariants:

### Invariant 1 — Hospital Ownership

Every external plugin belongs to exactly one hospital.

### Invariant 2 — Admin Registration

Only a Hospital Admin can register a hospital plugin.

### Invariant 3 — Backend Authority

Hospital ownership and registration authority are resolved by the backend.

### Invariant 4 — No Unapproved Execution

A plugin cannot execute merely because it was uploaded.

### Invariant 5 — Artifact Integrity

An approved plugin version is bound to its approved artifact identity/checksum.

### Invariant 6 — Durable Governance

Governance state must survive application restart.

### Invariant 7 — Auditability

Governance actions must be attributable to an authenticated actor.

### Invariant 8 — Same Runtime Engine

External plugins use the same Plugin Manager and Workflow Manager architecture as internal plugins.

### Invariant 9 — Tenant Isolation

One hospital cannot administer or activate another hospital's plugins.

### Invariant 10 — Governance ≠ Runtime

The governance registry and runtime registry remain separate responsibilities.

---

# 39. R9B Data Model Summary

The conceptual entities are:

```text
Hospital
   │
   └── Plugin
          │
          ├── Plugin Version
          │      ├── Artifact
          │      ├── Approval
          │      └── Configuration
          │
          └── Audit Events
```

Supporting concepts:

```text
Plugin Capability
Plugin Compatibility
Plugin Provenance
Plugin Lifecycle Status
Plugin Runtime State
```

---

# 40. Relationship to Existing Architecture

R9B does **not** replace the existing Plugin Framework or Plugin SDK.

Instead:

```text
Existing Plugin SDK
        ↓
Standard Plugin Contract

R9B Governance Registry
        ↓
Controls which external plugins are permitted

Plugin Manager
        ↓
Loads approved plugins

Workflow Manager
        ↓
Executes them through existing workflows
```

The existing framework already provides the runtime foundations including plugin contracts, validation, lifecycle management, routing, and workflow integration. 

R9B adds the missing **governance layer**.

---

# 41. R9B Non-Goals

R9B does not yet implement:

* registration APIs;
* approval APIs;
* ZIP upload endpoints;
* artifact scanning;
* signature verification;
* sandboxing;
* process isolation;
* plugin runtime wiring;
* tenant plugin API;
* frontend upload UI;
* database migrations.

Those belong to subsequent R9 phases.

---

# 42. Dependency on Subsequent R9 Phases

```text
R9A
Plugin Governance & Security Architecture
        │
        ▼
R9B
Governance Data Model / Registry
        │
        ▼
R9C
Registration & Approval Lifecycle
        │
        ▼
R9D
Security, Trust & Execution Isolation
        │
        ▼
R9E
Tenant / Organisation Governance
        │
        ▼
R9F
Governance API & Backend Integration
        │
        ▼
R9G
Runtime Manager Integration
        │
        ▼
R9H
Governance Tests & Security Validation
        │
        ▼
R9 CLOSED
```

---

# 43. R9B Acceptance Criteria

R9B is considered complete as a documentation decision when the project explicitly confirms:

* [ ] Governance registry is separate from runtime registry.
* [ ] Governance registry is persistent.
* [ ] Hospital ownership is represented.
* [ ] Only Hospital Admins may register hospital plugins.
* [ ] Plugin type distinguishes Knowledge and Prediction.
* [ ] Prediction plugins represent ML-model plugins.
* [ ] Knowledge plugins may use approved external/structured data sources.
* [ ] ZIP artifact submission is supported conceptually.
* [ ] Structured registration form is supported conceptually.
* [ ] Plugin identity is separated from plugin version.
* [ ] Artifact identity/checksum is represented.
* [ ] Provenance is represented.
* [ ] Approval state is represented.
* [ ] Activation state is represented.
* [ ] Revocation/quarantine are represented.
* [ ] Audit events are represented.
* [ ] Hospital tenant isolation is represented.
* [ ] External plugins use the same runtime engine as internal plugins.
* [ ] No second external-plugin execution architecture is introduced.
* [ ] R9C–R9H responsibilities remain clearly separated.

---

# 44. R9B Gate

```text
R9B STATUS: DOCUMENTATION COMPLETE
```


> **External plugin ≠ different engine.**

It is:

> **External plugin = hospital-owned plugin that passes the governance/security gates and then uses the same standard plugin contract, Plugin Manager, Workflow Manager, and clinical pipeline as internal plugins.**

This is the direction I recommend we now treat as the **R9B candidate decision**.
