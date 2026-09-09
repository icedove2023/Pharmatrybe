# R9G — Plugin Runtime Manager Integration

**Status:** Aprroved
**Phase:** R9 — Plugin Governance & External Extensions
**Predecessors:** R9A, R9B, R9C, R9D, R9E, R9F
**Next:** R9H — Plugin Governance Tests & Security Validation

---

## 1. Purpose

R9G defines how the approved plugin governance system integrates with the existing plugin runtime engine.

The objective is **not to create a separate execution engine for external plugins**.

Instead:

> **Internal and approved external plugins must use the same Plugin Manager, Plugin Registry, Plugin Loader, validation mechanisms, orchestration pathways, execution contracts, and result-handling engine.**

Governance determines **whether and how a plugin may enter and operate within the runtime**.

The runtime engine determines **how an approved plugin executes**.

---

# 2. Core Architectural Principle

The platform shall maintain **one plugin execution engine**.

```text
                    ┌──────────────────────────┐
                    │      Plugin Governance   │
                    │                          │
                    │ Registration             │
                    │ Approval                 │
                    │ Security validation      │
                    │ Tenant authorization     │
                    │ Activation               │
                    │ Revocation               │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   Authorised Plugin      │
                    │        Registry          │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      Plugin Manager      │
                    │                          │
                    │ Discovery                │
                    │ Loading                  │
                    │ Validation               │
                    │ Lifecycle                │
                    │ Health                   │
                    │ Routing                  │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ Existing Plugin Engine   │
                    └────────────┬─────────────┘
                                 │
             ┌───────────────────┴──────────────────┐
             ▼                                      ▼
    Internal Plugins                         External Plugins
             │                                      │
             └───────────────────┬──────────────────┘
                                 ▼
                    Same execution contracts
                    Same orchestration
                    Same result handling
                    Same clinical boundaries
```

There shall be no:

```text
Internal Plugin Engine
        +
External Plugin Engine
```

Instead:

```text
ONE Plugin Engine
```

---

# 3. Internal and External Plugin Model

The system distinguishes between **plugin origin** and **plugin execution**.

### Internal plugin

A plugin maintained and controlled by the platform/project.

Examples include:

* WHO knowledge plugin;
* internally developed knowledge plugins;
* internally developed prediction plugins;
* other platform-controlled plugins.

### External plugin

A plugin supplied by a hospital through the approved governance process.

Examples:

* hospital-provided knowledge plugin;
* hospital-provided ML prediction plugin.

The distinction affects:

* registration;
* ownership;
* approval;
* provenance;
* security validation;
* tenant scope;
* lifecycle governance.

It does **not** create a different execution engine.

---

# 4. Plugin Categories

R9G inherits the plugin categories defined by the preceding R9 architecture decisions.

## 4.1 Knowledge Plugins

Knowledge plugins provide structured clinical or domain knowledge to the platform.

Examples:

```text
WHO knowledge
Hospital antimicrobial guideline
Hospital formulary knowledge
Local resistance knowledge
Institution-specific stewardship rules
```

Knowledge plugins may obtain their underlying knowledge from an approved database or knowledge source.

For example:

```text
Knowledge Plugin
      ↓
Supabase / approved knowledge database
      ↓
Structured knowledge
      ↓
Plugin engine
      ↓
Clinical workflow
```

The fact that knowledge originates from a database does not create a separate execution pathway.

---

# 5. WHO Plugin

The WHO plugin remains an **internal platform plugin**.

It is not treated as an external hospital plugin merely because it retrieves information from a database.

Therefore:

```text
WHO Plugin
   ↓
Internal Plugin
   ↓
Existing Plugin Engine
```

The WHO plugin remains governed by platform-level internal controls.

Its architecture must not be unnecessarily redesigned as part of external-plugin onboarding.

---

# 6. Prediction Plugins

Prediction plugins represent machine-learning prediction capabilities.

They are expected to provide model-based predictions through the approved plugin contract.

Examples may include:

```text
AMR prediction
Resistance probability prediction
Treatment-response prediction
Risk prediction
```

A prediction plugin must therefore conform to the prediction plugin interface and execute through the same engine as other plugins.

The platform does not create a separate ML execution architecture for external prediction plugins.

---

# 7. External Plugin Onboarding

An external plugin enters the runtime only after completing the approved governance lifecycle.

The high-level flow is:

```text
Hospital Admin
      │
      ▼
Submit Plugin
      │
      ▼
Registration
      │
      ▼
Metadata / Manifest Validation
      │
      ▼
Security / Trust Validation
      │
      ▼
Compatibility Validation
      │
      ▼
Hospital Approval
      │
      ▼
Authorised Plugin Registry
      │
      ▼
Activation
      │
      ▼
Plugin Manager
      │
      ▼
Common Plugin Engine
```

An uploaded plugin must never become executable merely because it exists in storage.

---

# 8. Plugin Upload Boundary

The hospital administrator is the authorised actor for external plugin registration.

The administrator may submit a plugin through the approved registration mechanism.

The submission may be represented by:

```text
ZIP package
```

or an approved structured registration form with the required plugin artifact and metadata.

The exact UI mechanism is governed by R9C/R9F.

R9G is concerned with what happens **after governance has authorised the plugin**.

---

# 9. ZIP Package Handling

Where a ZIP package is used, the runtime must not treat the ZIP file itself as an executable plugin.

The lifecycle is:

```text
ZIP Upload
    ↓
Quarantine / controlled storage
    ↓
Integrity verification
    ↓
Manifest extraction
    ↓
Security validation
    ↓
Compatibility validation
    ↓
Governance approval
    ↓
Authorised installation
    ↓
Plugin Manager loading
```

The runtime must never bypass the governance state simply because a package can technically be imported.

---

# 10. Governance Registry → Runtime Registry

R9G establishes a clear relationship between the two registries.

### Governance Registry

The governance registry answers:

> **May this plugin exist and operate?**

It contains authoritative lifecycle and governance state.

### Runtime Registry

The runtime registry answers:

> **Which authorised plugins are currently loaded and available to the engine?**

Therefore:

```text
Governance Registry
        │
        │ authorised plugin
        ▼
Runtime Registry
        │
        ▼
Plugin Manager
```

The runtime registry must not independently authorise plugins.

---

# 11. Runtime Eligibility

A plugin may enter the runtime only when the governance system determines that it is eligible.

Conceptually:

```text
eligible_for_runtime(plugin)
```

requires the relevant governance conditions to be satisfied.

These include, as applicable:

* registered;
* approved;
* security validated;
* compatible;
* active;
* not revoked;
* not quarantined;
* valid tenant scope;
* valid plugin version;
* valid artifact identity.

A plugin failing these conditions must not be loaded into the active runtime.

---

# 12. Plugin Manager as Runtime Gateway

The existing Plugin Manager remains the principal runtime gateway.

R9G does not replace it.

The Plugin Manager is responsible for runtime operations such as:

* discovery;
* loading;
* validation;
* initialization;
* registration;
* health;
* lifecycle;
* routing;
* shutdown.

However, R9G adds an important boundary:

> **The Plugin Manager may load only plugins that have passed governance eligibility checks.**

---

# 13. Runtime Loading

The runtime loading sequence becomes:

```text
Plugin Manager
      │
      ▼
Query authorised plugin registry
      │
      ▼
Identify active plugin versions
      │
      ▼
Verify artifact identity
      │
      ▼
Load plugin
      │
      ▼
Validate plugin contract
      │
      ▼
Initialize plugin
      │
      ▼
Register runtime instance
      │
      ▼
Health check
      │
      ▼
Available for execution
```

A failure at any mandatory validation stage prevents activation.

---

# 14. No Governance Bypass

The following must not be allowed:

```text
Filesystem plugin
      ↓
PluginLoader
      ↓
Immediate execution
```

Instead:

```text
Filesystem / Storage
      ↓
Governance Registry
      ↓
Approved + Active
      ↓
Plugin Manager
      ↓
PluginLoader
      ↓
Execution
```

This prevents the existing filesystem discovery mechanism from becoming an unintended external-plugin security bypass.

---

# 15. Plugin Versioning

The runtime must treat plugin versions as governed artifacts.

A plugin update must not silently replace the currently authorised version.

Example:

```text
Plugin v1.2
   ↓
Approved
   ↓
Active
```

An uploaded:

```text
Plugin v1.3
```

must undergo the appropriate governance and compatibility process before becoming active.

The runtime must retain sufficient identity information to distinguish versions.

---

# 16. Plugin Replacement Protection

An approved plugin artifact must not be silently replaced while retaining the same governance identity.

The runtime should verify the governed artifact identity before activation.

Conceptually:

```text
Governed Plugin Identity
        +
Governed Version
        +
Governed Artifact Integrity
        ↓
Runtime Load Eligibility
```

If the artifact no longer corresponds to the approved artifact, loading must fail or the plugin must enter the appropriate security state.

---

# 17. Plugin Activation

Activation is a governance-controlled operation.

The runtime must not activate a plugin solely because it has been successfully loaded.

Conceptually:

```text
Registered
   ↓
Validated
   ↓
Approved
   ↓
Active
   ↓
Runtime Loaded
```

Only the appropriate authorised lifecycle operation may move a plugin into the active state.

---

# 18. Plugin Deactivation

When a plugin is deactivated:

```text
Active
  ↓
Disabled
```

the runtime must stop treating it as an available execution target.

Deactivation must not require deletion of the plugin artifact.

The governance record remains available for:

* audit;
* reactivation;
* investigation;
* version history.

---

# 19. Plugin Revocation

Revocation is stronger than deactivation.

When a plugin is revoked:

```text
Approved / Active
        ↓
REVOKED
```

the runtime must prevent further activation.

If the plugin is currently loaded, the runtime must execute the approved revocation handling process.

A revoked plugin must not automatically return to service merely because its files remain available.

---

# 20. Plugin Quarantine

A plugin may be placed into quarantine when a security or integrity concern is identified.

Example:

```text
Active
  ↓
Security concern
  ↓
Quarantine
```

A quarantined plugin must not be available for normal clinical execution.

Quarantine is distinct from ordinary administrative deactivation.

---

# 21. Tenant-Aware Runtime Loading

R9E establishes tenant governance.

R9G therefore requires the runtime to respect the approved plugin tenant scope.

Conceptually:

```text
Current Hospital
      ↓
Authorised Plugin Scope
      ↓
Eligible Plugin
      ↓
Execution
```

A hospital must not receive another hospital's plugin merely because that plugin is globally present in the runtime registry.

---

# 22. Global vs Hospital Plugin

The architecture supports the distinction between:

### Platform/global plugin

Available according to platform governance.

Example:

```text
WHO Plugin
```

### Hospital-scoped plugin

Registered and approved by a particular hospital administrator.

Example:

```text
Hospital A
   ↓
Hospital A resistance prediction plugin
```

The runtime must enforce the appropriate scope.

---

# 23. Clinical Execution Boundary

Plugins provide capabilities and outputs.

They do not become autonomous clinical decision-makers.

The established CDSS hierarchy remains:

```text
Clinical Guidelines
        ↓
Knowledge Base
        ↓
Patient Information
        ↓
Machine Learning
        ↓
Recommendation
```

Plugin execution must remain inside this architecture.

A prediction plugin does not independently prescribe treatment.

A knowledge plugin does not independently issue final clinical recommendations.

---

# 24. Plugin Output Contract

Plugin results must pass through the established plugin contracts.

For example:

```text
Plugin
   ↓
Structured Result
   ↓
Workflow / Orchestration
   ↓
Clinical synthesis
   ↓
Explainable recommendation
```

External plugins must not bypass the existing orchestration layer to inject arbitrary final recommendations.

---

# 25. Common Execution Engine

The following must be identical between internal and external plugins wherever their plugin category and contract are the same:

* plugin interfaces;
* lifecycle handling;
* orchestration;
* result structures;
* validation;
* routing;
* health monitoring;
* error handling;
* logging/auditing boundaries;
* clinical synthesis boundaries.

The source of the plugin does not determine a separate engine.

---

# 26. Plugin Configuration

Plugin configuration must be resolved through the approved governance/configuration mechanism.

External plugins must not arbitrarily read:

* platform secrets;
* Supabase service-role credentials;
* unrelated environment variables;
* another hospital's configuration;
* unrelated plugin credentials.

Configuration access must follow the security and scope rules established by R9D and R9E.

---

# 27. Plugin Credentials

Where a plugin requires credentials to access an external service:

```text
Plugin
   ↓
Approved credential scope
   ↓
Approved external service
```

The plugin must not inherit unrestricted platform credentials.

Credentials must not become part of ordinary plugin metadata or frontend-visible state.

---

# 28. Runtime Health

The Plugin Manager remains responsible for runtime health information.

Health information may include:

* loaded;
* initialized;
* available;
* degraded;
* failed;
* disabled;
* quarantined.

Runtime health must not override governance state.

For example:

```text
Governance = REVOKED
Runtime Health = HEALTHY
```

must still result in:

```text
NOT EXECUTABLE
```

Governance takes precedence over runtime health.

---

# 29. Runtime Failure

A plugin runtime failure must be isolated from unrelated plugins where possible.

Example:

```text
Plugin A → failure
Plugin B → remains available
Plugin C → remains available
```

The failure must be recorded according to the established audit requirements.

A plugin failure must not silently alter clinical recommendation logic outside its defined output contract.

---

# 30. Startup Behaviour

At application startup:

```text
Application
   ↓
Governance Registry
   ↓
Determine runtime-eligible plugins
   ↓
Plugin Manager
   ↓
Load eligible plugins
   ↓
Validate
   ↓
Initialize
   ↓
Health check
   ↓
Runtime Registry
```

The application must not blindly load every plugin discovered on disk.

---

# 31. Runtime Shutdown

On shutdown:

```text
Application shutdown
       ↓
Plugin Manager
       ↓
Plugin lifecycle shutdown
       ↓
Runtime registry cleanup
```

External and internal plugins use the same lifecycle mechanism.

---

# 32. Dynamic Reloading

Dynamic plugin reload remains subject to governance.

A reload must not become a mechanism for bypassing approval.

Therefore:

```text
Reload
```

means:

> reload the currently authorised artifact/version.

It does not mean:

> execute whatever code currently exists at the plugin path.

---

# 33. Auditability

Runtime lifecycle events should be attributable to the governed plugin identity.

Relevant events include:

* registration;
* approval;
* installation;
* activation;
* loading;
* initialization;
* health changes;
* deactivation;
* revocation;
* quarantine;
* version replacement;
* runtime failure.

The authoritative governance audit model is defined by R9B/R9C/R9F.

R9G consumes that model rather than creating a competing audit system.

---

# 34. Runtime Registry Authority

The runtime registry is **not** the governance authority.

Therefore:

```text
Runtime Registry ≠ Governance Registry
```

The runtime registry is a derived operational representation.

If governance says:

```text
REVOKED
```

the runtime must eventually converge to:

```text
not loaded / not executable
```

---

# 35. State Synchronisation

The runtime must respond to governance state changes.

Conceptually:

```text
Governance State Change
        ↓
Runtime Reconciliation
        ↓
Load / unload / disable / quarantine
```

The implementation mechanism may be:

* startup reconciliation;
* explicit lifecycle operation;
* event-driven update;
* controlled reload.

The exact mechanism is an implementation detail and must not change the governance authority model.

---

# 36. No Duplicate Plugin Codebase

R9G explicitly rejects creating:

```text
external_plugins/
    separate engine
    separate manager
    separate executor
```

for external plugins.

External plugins must ultimately become compatible plugin instances within the existing framework.

The implementation should extend the current architecture rather than duplicate it.

---

# 37. Existing Internal Plugins Must Remain Functional

R9G implementation must not unnecessarily rewrite working internal plugins.

Existing plugins must continue using the established engine.

Regression testing must verify at minimum:

* WHO knowledge plugin;
* existing prediction plugin pathways;
* plugin orchestration;
* workflow execution;
* clinical synthesis boundaries.

---

# 38. Migration Principle

R9G implementation should be incremental.

The intended sequence is:

```text
Existing Plugin Runtime
        ↓
Introduce Governance Eligibility
        ↓
Connect Governance Registry
        ↓
Reconcile Runtime Registry
        ↓
Protect Loading
        ↓
Protect Activation
        ↓
Protect Deactivation / Revocation
        ↓
Validate Internal Plugins
        ↓
Enable Approved External Plugins
```

The existing runtime should not be discarded and rewritten.

---

# 39. Implementation Constraints

Implementation of R9G must obey the following:

1. Do not create a second plugin engine.
2. Do not bypass the existing Plugin Manager.
3. Do not bypass governance approval.
4. Do not allow filesystem discovery to imply approval.
5. Do not allow frontend state to determine plugin authority.
6. Do not allow hospital users other than authorised hospital administrators to govern hospital plugins.
7. Do not expose plugin credentials to the frontend.
8. Do not allow plugin governance to override backend authorization.
9. Do not allow plugins to bypass clinical synthesis.
10. Do not redesign R8.
11. Do not redesign R7/R7A.
12. Preserve internal plugin behaviour.
13. Preserve tenant isolation.
14. Validate each implementation incrementally.

---

# 40. R9G Acceptance Criteria

R9G will be considered implemented when:

### Runtime integration

* [ ] Governance registry can determine runtime eligibility.
* [ ] Plugin Manager consumes governance state.
* [ ] Runtime Registry contains only eligible plugins.
* [ ] Filesystem discovery cannot bypass governance.
* [ ] Startup reconciliation is implemented.
* [ ] Activation is governance-controlled.
* [ ] Deactivation is respected.
* [ ] Revocation is respected.
* [ ] Quarantine is respected.

### Common engine

* [ ] Internal plugins use the existing engine.
* [ ] External plugins use the same engine.
* [ ] No duplicate external-plugin execution engine exists.
* [ ] Plugin contracts remain unified.
* [ ] Orchestration remains unified.

### Security

* [ ] Artifact identity is checked.
* [ ] Governance state is checked before loading.
* [ ] Tenant scope is enforced.
* [ ] Plugin credentials remain scoped.
* [ ] Plugin execution remains subject to R9D isolation controls.

### Clinical safety

* [ ] Plugins cannot bypass clinical synthesis.
* [ ] Prediction plugins do not independently prescribe.
* [ ] Knowledge plugins do not independently prescribe.
* [ ] Plugin failures cannot silently alter unrelated clinical workflows.

### Regression

* [ ] Existing internal plugins continue to work.
* [ ] WHO plugin remains functional.
* [ ] Existing prediction pathways remain functional.
* [ ] R8 remains intact.
* [ ] R7/R7A remain intact.

---

# 41. Relationship to Previous R9 Decisions

R9G does not replace the preceding decisions.

```text
R9A
Plugin Governance & Security
        ↓
R9B
Governance Registry / Data Model
        ↓
R9C
Registration & Approval Lifecycle
        ↓
R9D
Trust / Security / Isolation
        ↓
R9E
Tenant / Organisation Governance
        ↓
R9F
Governance API / Backend Integration
        ↓
R9G
Runtime Manager Integration
```

R9G is the bridge between **governance** and the **existing plugin execution engine**.

---

# 42. Decision Summary

The architectural decision is:

> **The Pharmatrybe shall use one unified plugin execution engine for both internal and approved external plugins.**

External plugins will enter that engine only through the approved governance lifecycle.

The governance registry determines whether a plugin is authorised.

The runtime registry represents currently eligible operational plugins.

The Plugin Manager remains the runtime gateway.

The existing plugin engine remains the execution mechanism.

No separate external-plugin engine shall be created.

---

# 43. R9G Status

```text
R9G — Plugin Runtime Manager Integration

STATUS: Approved
