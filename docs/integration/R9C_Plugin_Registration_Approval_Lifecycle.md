# R9C — Plugin Registration & Approval Lifecycle

**Status:** APPROVED
**Phase:** R9 — Plugin Governance & External Extension Security
**Depends on:** R9A — Plugin Governance & External Extension Security Architecture Decision; R9B — Plugin Governance Data Model / Registry
**Next:** R9D — Plugin Security, Trust & Execution Isolation

---

## 1. Purpose

R9C defines the **registration, validation, approval, activation, suspension, rejection, and revocation lifecycle** for plugins within the Pharmatrybe.

The objective is to ensure that no external plugin becomes available to a hospital's clinical environment merely because a file has been uploaded.

A plugin must pass a controlled governance lifecycle before it can participate in the same plugin execution engine used by internal plugins.

The lifecycle is therefore:

```text
Upload / Submission
        ↓
Registration
        ↓
Validation
        ↓
Pending Approval
        ↓
Hospital Administrator Approval
        ↓
Activation
        ↓
Available to Plugin Engine
        ↓
Suspension / Deactivation
        ↓
Reactivation OR Revocation
```

---

# 2. Core Governance Principle

> **Only an authorised Hospital Administrator can register, approve, activate, deactivate, or revoke a plugin for that hospital.**

A normal healthcare professional must not be able to install or activate plugins.

The frontend must not be the authority for plugin approval.

The backend governance layer is authoritative.

---

# 3. Plugin Types

R9C recognises two principal external plugin categories.

## 3.1 Knowledge Plugins

Knowledge plugins provide structured clinical or antimicrobial knowledge to the CDSS.

Examples include:

* antimicrobial knowledge;
* resistance knowledge;
* guideline-derived knowledge;
* breakpoint knowledge;
* drug information;
* epidemiological knowledge;
* hospital-specific knowledge.

Knowledge may be sourced from:

* an uploaded plugin package;
* a structured database;
* Supabase;
* another approved data source.

### Important distinction

The existing **WHO knowledge plugin is an internal platform plugin**.

It therefore does not require hospital-admin registration.

External knowledge plugins must follow the R9C governance lifecycle.

---

## 3.2 Prediction Plugins

Prediction plugins provide machine-learning predictions.

Prediction plugins are expected to contain or connect to:

* trained ML models;
* model metadata;
* feature definitions;
* model version;
* expected input schema;
* output schema;
* compatibility information.

Examples may include models for:

* antimicrobial susceptibility prediction;
* resistance prediction;
* clinical risk prediction;
* treatment-response prediction.

All prediction plugins must pass the same governance lifecycle before activation.

---

# 4. Internal vs External Plugins

R9C does **not** create a separate execution engine for external plugins.

The architectural principle is:

```text
                    Plugin Engine
                         │
          ┌──────────────┴──────────────┐
          │                             │
   Internal Plugins              External Plugins
          │                             │
          └──────────────┬──────────────┘
                         ↓
                 Common Plugin Contract
                         ↓
                  Common Execution
                         ↓
                  Common Validation
                         ↓
                 Common Output Model
```

External plugins must ultimately operate through the same plugin framework and execution engine as internal plugins.

This prevents the platform from developing two incompatible plugin systems.

---

# 5. Registration Authority

Plugin governance is hospital-scoped.

The authoritative actor is:

```text
Hospital Administrator
```

The following actors do **not** have plugin registration authority by default:

* ordinary healthcare professionals;
* pharmacists;
* clinicians;
* researchers;
* hospital viewers;
* plugin developers;
* external plugin publishers;
* patients;
* frontend users without administrator authority.

The backend must enforce this authority.

---

# 6. Registration Methods

R9C supports two conceptual plugin submission mechanisms.

## 6.1 ZIP Package Upload

A Hospital Administrator may upload a plugin package as a ZIP file.

Conceptually:

```text
Hospital Administrator
        ↓
Upload ZIP
        ↓
Platform extracts/inspects package
        ↓
Manifest validation
        ↓
Security validation
        ↓
Registration
        ↓
Pending approval / review
```

The ZIP package must contain the information required by the plugin framework and R9B registry model.

The platform must not automatically activate a newly uploaded package.

---

## 6.2 Form-Based Registration

A Hospital Administrator may also register a plugin through a structured form.

The form may collect:

* plugin name;
* description;
* plugin type;
* version;
* publisher;
* ownership;
* source;
* provenance;
* capabilities;
* dependencies;
* compatibility information;
* configuration requirements;
* data requirements;
* model information where applicable;
* plugin package/artifact.

The form itself does not replace validation.

The submitted information must still pass the same governance and security checks as a ZIP submission.

---

# 7. Registration Lifecycle

## 7.1 Stage 1 — Submission

A Hospital Administrator submits a plugin.

Submission may occur through:

```text
ZIP upload
```

or

```text
Structured registration form
```

The platform records the submission.

The plugin is **not yet active**.

---

## 7.2 Stage 2 — Registration

The platform creates a governance registry record.

At this point the plugin receives a platform-level identity.

Conceptually:

```text
Plugin Submission
       ↓
Plugin Registry Record
       ↓
plugin_id
```

The registry must retain the relationship between:

* plugin;
* hospital;
* submitting administrator;
* plugin version;
* artifact;
* plugin type;
* lifecycle state.

---

# 8. Initial Plugin State

A newly submitted plugin enters:

```text
PENDING_VALIDATION
```

It must not enter the active runtime registry simply because registration succeeded.

---

# 9. Validation

The platform validates the plugin before approval.

Validation includes, where applicable:

### Identity

* plugin ID;
* plugin name;
* version;
* plugin type;
* publisher;
* owner.

### Compatibility

* platform version;
* plugin SDK version;
* plugin contract version;
* dependency compatibility.

### Structure

* required manifest;
* required metadata;
* required interfaces;
* configuration schema;
* input schema;
* output schema.

### Security

* artifact integrity;
* package contents;
* prohibited files;
* dependency concerns;
* signature/checksum where required;
* execution-risk characteristics.

### Clinical integration

For plugins contributing clinical information:

* expected input;
* expected output;
* clinical domain;
* evidence/provenance;
* version information;
* explainability metadata where applicable.

Validation failure must prevent activation.

---

# 10. Validation Result

A plugin may transition to:

```text
PENDING_APPROVAL
```

when validation succeeds.

If validation fails:

```text
VALIDATION_FAILED
```

The failure must be recorded.

A failed plugin must not be available to the clinical plugin engine.

---

# 11. Hospital Administrator Review

The Hospital Administrator reviews the plugin registration.

The administrator should be able to inspect information such as:

* plugin identity;
* plugin type;
* version;
* publisher;
* provenance;
* capabilities;
* dependencies;
* validation results;
* security status;
* artifact information;
* intended clinical function;
* configuration requirements.

The administrator then chooses an appropriate governance action.

---

# 12. Approval

A Hospital Administrator may approve a validated plugin.

Approval produces a durable governance event.

Conceptually:

```text
PENDING_APPROVAL
       ↓
APPROVED
```

Approval must record:

* approving administrator;
* timestamp;
* plugin version;
* plugin identity;
* hospital;
* approval decision;
* relevant validation result.

Approval is therefore auditable.

---

# 13. Rejection

An administrator may reject a plugin.

```text
PENDING_APPROVAL
       ↓
REJECTED
```

The rejection should record:

* rejecting administrator;
* timestamp;
* plugin version;
* reason;
* relevant validation information.

A rejected plugin must not execute.

---

# 14. Activation

Approval and activation are conceptually separate.

This distinction is important.

```text
APPROVED
   ↓
ACTIVATED
```

A plugin may be approved but not currently active.

Activation makes the plugin available to the common plugin runtime.

Only an authorised Hospital Administrator may activate the plugin.

---

# 15. Active State

An active plugin becomes eligible for execution by the plugin engine.

Conceptually:

```text
Governance Registry
        ↓
Approved + Active
        ↓
Runtime Plugin Registry
        ↓
Common Plugin Engine
```

The governance registry remains authoritative over whether the plugin is permitted to execute.

The runtime registry should not independently grant governance authority.

---

# 16. Deactivation

A Hospital Administrator may deactivate an active plugin.

```text
ACTIVE
   ↓
DISABLED
```

Deactivation should immediately prevent new plugin executions.

Existing executions should be handled according to the runtime execution policy defined in R9D.

Deactivation does not necessarily mean the plugin has been rejected or revoked.

It may simply mean:

> The hospital does not currently want this plugin active.

---

# 17. Reactivation

A previously disabled plugin may be reactivated if:

* its approval remains valid;
* its version remains valid;
* its security status remains valid;
* its dependencies remain compatible;
* no revocation applies.

Conceptually:

```text
DISABLED
   ↓
ACTIVE
```

The reactivation must be recorded as a governance event.

---

# 18. Revocation

Revocation is stronger than deactivation.

A plugin may be revoked because of:

* security compromise;
* malicious behaviour;
* invalid provenance;
* compromised publisher;
* unsafe model;
* serious clinical concern;
* integrity failure;
* expired trust;
* unacceptable vulnerability;
* policy violation.

Conceptually:

```text
ACTIVE / DISABLED / APPROVED
             ↓
          REVOKED
```

A revoked plugin cannot be reactivated through the ordinary activation process.

A new review or replacement version may be required.

---

# 19. Version Governance

Plugin approval is **version-aware**.

For example:

```text
Plugin A
   v1.0 → APPROVED
   v1.1 → PENDING_APPROVAL
```

Approval of version 1.0 must not automatically approve version 1.1.

A new version must pass the appropriate validation and governance process.

This is particularly important for prediction plugins because changing a model may change clinical behaviour.

---

# 20. Prediction Plugin Additional Governance

Prediction plugins must include model-specific information.

At minimum, governance should be able to identify:

* model name;
* model version;
* training/version metadata;
* model type;
* expected features;
* output schema;
* performance metadata where applicable;
* intended clinical use;
* limitations;
* provenance.

A prediction plugin must not silently replace an approved model.

A new model version is a new governed artifact/version.

---

# 21. Knowledge Plugin Additional Governance

Knowledge plugins must identify:

* knowledge source;
* source version;
* publication/update date where applicable;
* provenance;
* data format;
* knowledge domain;
* update mechanism;
* evidence/reference information where applicable.

For database-backed knowledge plugins, the governance record must identify the approved source.

The platform must distinguish:

```text
Plugin code
```

from:

```text
Knowledge source/data
```

where appropriate.

---

# 22. Hospital Scope

Plugin approval is scoped to the hospital that registered it.

Conceptually:

```text
Hospital A
   └── Plugin X → APPROVED

Hospital B
   └── Plugin X → NOT AUTOMATICALLY APPROVED
```

Approval by one hospital does not automatically grant another hospital access.

A global platform plugin may be separately classified as an internal/trusted plugin under R9A.

---

# 23. No Hospital-to-Hospital Authority Transfer

A Hospital Administrator cannot automatically approve a plugin for another hospital.

Each hospital maintains its own governance authority unless a future platform-level governance model explicitly introduces a higher authority.

Such a model is outside the current R9C scope.

---

# 24. Runtime Enforcement

The runtime must not execute a plugin solely because it exists on disk.

Execution eligibility should conceptually require:

```text
Plugin exists
    AND
Registered
    AND
Validated
    AND
Approved
    AND
Active
    AND
Not revoked
    AND
Compatible
    AND
Security requirements satisfied
```

Only then may the plugin enter normal execution.

---

# 25. Governance Registry vs Runtime Registry

R9C formally establishes the distinction:

### Governance Registry

Answers:

> Is this plugin authorised to exist and operate for this hospital?

### Runtime Registry

Answers:

> Which plugin implementations are currently loaded and available to the execution engine?

Therefore:

```text
Governance Registry
        ↓
Eligibility Decision
        ↓
Runtime Registry
        ↓
Plugin Engine
```

The runtime registry must not bypass the governance registry.

---

# 26. Audit Trail

Every significant lifecycle operation must produce an auditable event.

At minimum:

* submitted;
* registered;
* validation started;
* validation passed;
* validation failed;
* approved;
* rejected;
* activated;
* disabled;
* reactivated;
* revoked;
* version replaced;
* configuration changed.

Each event should identify:

* plugin;
* version;
* hospital;
* actor;
* timestamp;
* action;
* result;
* reason where applicable.

---

# 27. Failure-Safe Principle

If plugin governance state cannot be reliably determined, the plugin must **not execute**.

For example:

```text
Governance unavailable
        ↓
Do not activate unknown plugin
```

The platform should favour:

> **No execution rather than unverified execution.**

This is particularly important because the CDSS operates in a clinical environment.

---

# 28. No Direct Clinical Authority

Plugin approval does not mean that a plugin becomes the final clinical decision authority.

Plugins provide governed inputs to the CDSS.

The established architecture remains:

```text
Evidence / Knowledge
        +
Patient Information
        +
Governed Plugin Outputs
        +
Clinical Rules / Reasoning
        +
ML Predictions where applicable
        ↓
Explainable CDSS Recommendation
        ↓
Clinician
```

The clinician remains the final decision-maker.

---

# 29. Security Boundary

R9C defines governance but does not completely define plugin execution isolation.

The following are explicitly delegated to **R9D**:

* sandboxing;
* process isolation;
* resource limits;
* filesystem restrictions;
* network restrictions;
* dependency isolation;
* plugin credentials;
* secret access;
* malicious code handling;
* artifact signature verification;
* checksum enforcement;
* runtime security policy.

R9C only establishes that these controls must be satisfied before a plugin becomes executable.

---

# 30. Frontend Authority Boundary

The frontend may provide:

* plugin upload UI;
* plugin registration form;
* validation status;
* approval UI;
* activation/deactivation UI;
* audit history.

However:

> **The frontend must never be the authority that grants plugin permissions.**

Every governance operation must be validated by the backend against:

* authenticated identity;
* hospital membership;
* canonical role;
* administrator permission;
* plugin governance state.

---

# 31. API Authority

Future governance APIs should follow the established architecture:

```text
Frontend
   ↓
Authenticated Supabase session
   ↓
FastAPI
   ↓
Identity
   ↓
Hospital membership
   ↓
Canonical role
   ↓
Plugin governance permission
   ↓
Governance operation
```

The exact API contract is reserved for **R9F — Plugin Governance API & Backend Integration**.

---

# 32. Implementation Constraint

R9C does **not** introduce a separate external-plugin engine.

Implementation must reuse the existing:

* plugin contracts;
* plugin validation mechanisms;
* plugin loading mechanisms;
* plugin routing mechanisms;
* workflow engine;
* plugin execution engine.

The governance layer controls **whether a plugin may enter that engine**.

It does not create a second execution architecture.

---

# 33. R9C State Machine

The canonical lifecycle is:

```text
                    ┌──────────────────┐
                    │    SUBMITTED     │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │    REGISTERED    │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ PENDING_VALIDATION│
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 ↓                       ↓
        ┌─────────────────┐      ┌─────────────────┐
        │ VALIDATION_FAILED│      │PENDING_APPROVAL │
        └─────────────────┘      └────────┬────────┘
                                          │
                              ┌───────────┴───────────┐
                              ↓                       ↓
                         ┌─────────┐             ┌─────────┐
                         │ APPROVED│             │ REJECTED│
                         └────┬────┘             └─────────┘
                              ↓
                         ┌─────────┐
                         │ ACTIVE  │
                         └────┬────┘
                              │
                    ┌─────────┴─────────┐
                    ↓                   ↓
               ┌─────────┐        ┌─────────┐
               │ DISABLED│        │ REVOKED │
               └────┬────┘        └─────────┘
                    │
                    ↓
               ┌─────────┐
               │ ACTIVE  │
               └─────────┘
```

Version changes create a new governed version rather than silently mutating an approved version.

---

# 34. R9C Acceptance Criteria

R9C will be considered implemented only when:

* [ ] Only authorised Hospital Administrators can register plugins.
* [ ] ZIP submission is supported by the approved architecture.
* [ ] Form-based registration is supported by the approved architecture.
* [ ] Registration creates a durable governance record.
* [ ] Newly submitted plugins are inactive by default.
* [ ] Validation precedes approval.
* [ ] Approval is explicitly recorded.
* [ ] Rejection is explicitly recorded.
* [ ] Activation requires approval.
* [ ] Deactivation is supported.
* [ ] Revocation is supported.
* [ ] Version-specific approval is enforced.
* [ ] Hospital scope is enforced.
* [ ] One hospital's approval does not automatically approve the plugin for another hospital.
* [ ] Governance state controls runtime eligibility.
* [ ] Governance actions are auditable.
* [ ] Governance failure fails closed.
* [ ] Prediction plugins receive model-specific governance.
* [ ] Knowledge plugins receive provenance/source governance.
* [ ] External plugins ultimately use the same plugin engine as internal plugins.
* [ ] Frontend cannot independently grant plugin authority.
* [ ] Security/isolation requirements are delegated to and satisfied by R9D.
* [ ] API implementation is delegated to R9F.
* [ ] Runtime manager integration is delegated to R9G.
* [ ] Governance testing is delegated to R9H.

---

# 35. R9C Decision Summary

| Decision                                              | Status              |
| ----------------------------------------------------- | ------------------- |
| Hospital Administrator is plugin governance authority | **CONFIRMED**       |
| External plugins require registration                 | **CONFIRMED**       |
| Registration may use ZIP upload                       | **CONFIRMED**       |
| Registration may use structured form                  | **CONFIRMED**       |
| Registration does not equal activation                | **CONFIRMED**       |
| Validation precedes approval                          | **CONFIRMED**       |
| Approval is hospital-scoped                           | **CONFIRMED**       |
| Approval is version-specific                          | **CONFIRMED**       |
| Plugin lifecycle is auditable                         | **CONFIRMED**       |
| Revocation is distinct from deactivation              | **CONFIRMED**       |
| Governance registry controls runtime eligibility      | **CONFIRMED**       |
| External plugins use the common plugin engine         | **CONFIRMED**       |
| Internal WHO plugin remains platform/internal         | **CONFIRMED**       |
| Prediction plugins are ML-model plugins               | **CONFIRMED**       |
| Knowledge plugins may use database-backed knowledge   | **CONFIRMED**       |
| Plugin security isolation                             | **DEFERRED TO R9D** |
| Governance API                                        | **DEFERRED TO R9F** |
| Runtime integration                                   | **DEFERRED TO R9G** |
| Security/governance testing                           | **DEFERRED TO R9H** |

---

# 36. R9C Status

```text
R9A — Plugin Governance & External Extension Security
        APPROVED

R9B — Plugin Governance Data Model / Registry
        APPROVED

R9C — Plugin Registration & Approval Lifecycle
        APPROVED

NEXT:
R9D — Plugin Security, Trust & Execution Isolation
```

