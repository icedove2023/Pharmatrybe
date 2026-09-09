# R9 Acceptance, Closure and Architectural Freeze

**Date:** 2026-08-22  
**Decision:** **R9 COMPLETE WITH DEPLOYMENT-DEPENDENT ITEMS**

## 1. Purpose

This document records the repository-level acceptance review and architectural freeze for R9A through R9H. It is the authoritative closure record for the plugin governance, tenant-integrity, provenance, isolation-policy, and security-assurance work completed in the current worktree.

R9 is frozen after this document. New findings are classified as closure defects, deployment issues, new-phase work, or unrelated defects. No further R9 implementation is included in this closure exercise.

## 2. Scope

The review covers:

- plugin governance and lifecycle;
- artifact inspection, hashing, extraction, and manifest validation;
- authenticated tenant context and cross-hospital isolation;
- canonical plugin identity and reserved internal IDs;
- immutable execution provenance;
- JSON subprocess execution and isolation-provider contracts;
- bounded execution auditing;
- repository migrations and RLS declarations;
- the R9 regression matrix and relevant R8/RBAC regressions.

## 3. Phase Status

| Phase | Status | Closure finding |
|---|---|---|
| R9A Plugin Governance Architecture | COMPLETE | Governance, admission, lifecycle, and runtime boundaries are present and tested. |
| R9B Governance/Data Model | COMPLETE | Repository models and migrations contain governance, artifact, lifecycle, and audit fields. |
| R9C Plugin Lifecycle | COMPLETE | Lifecycle transitions and invalid transitions are covered by governance tests. |
| R9D Plugin Security / Artifact Integrity | COMPLETE | ZIP inspection, hash checks, manifest checks, and pre-import admission are present. |
| R9E Tenant Integrity | COMPLETE | Registry resolution and workflow execution are tenant-scoped. |
| R9F Identity / Provenance Integrity | COMPLETE | Immutable execution identity binds tenant, ID, version, governance, artifact, manifest, capabilities, and isolation mode. |
| R9G Execution Isolation Architecture | PARTIALLY COMPLETE | The provider contract and container adapter exist; production enforcement depends on deployment infrastructure. |
| R9H Security Assurance / Test Matrix | PARTIALLY COMPLETE | The required repository matrix passes, but the full theoretical cross-product is not exhaustive. |

## 4. Final Architecture

Authenticated identity is converted into an immutable `TenantContext`. Hospital-owned plugin entries are stored separately from platform-owned entries and resolved by `(canonical_plugin_id, hospital_id)`. Internal plugins require explicit system context.

External admission performs governance eligibility, artifact hash, artifact ownership, version, manifest, plugin type, plugin origin, and capability checks before extraction-backed proxy registration. The proxy retains an immutable `ExecutionIdentity` and revalidates governance, tenant, artifact, manifest, version, type, origin, capabilities, and lifecycle state immediately before external execution.

External execution remains JSON-only and subprocess-based. `IsolatedPluginExecutor` implements the isolation runtime contract for the development boundary. `ContainerIsolationRuntime` provides the deployment adapter for environments where container enforcement is available.

## 5. Security Invariants

The following repository-level invariants were directly reviewed and are covered by implementation and tests:

1. Hospital-owned plugins cannot be resolved without authoritative `TenantContext`.
2. Hospital A cannot resolve or execute Hospital B's plugin.
3. Identical plugin IDs may exist independently for different hospitals.
4. Internal plugins require explicit system context.
5. External plugins cannot register using reserved internal IDs.
6. Canonical IDs are used across governance, registry, routing, loading, and execution boundaries.
7. Executed identity is bound to the governed identity snapshot.
8. Executed tenant equals governed tenant.
9. Executed version equals governed version.
10. Executed artifact hash equals the governed artifact hash.
11. Executed manifest identity is revalidated against the admission snapshot.
12. Executed capabilities equal governed capabilities.
13. Disabled, quarantined, and revoked plugins are not runtime-eligible.
14. Artifact substitution fails closed.
15. Manifest substitution fails closed.
16. Capability substitution fails closed.
17. Missing tenant context fails closed for hospital-owned runtime paths.
18. Missing governance eligibility fails closed.
19. Unsupported required isolation fails closed.
20. Successful and denied external execution attempts that reach the workflow audit boundary produce bounded audit records.

## 6. Tenant Isolation Guarantee

The registry uses tenant ownership as part of hospital-owned entry identity. A global `get_plugin(plugin_id)` lookup returns no hospital-owned entry. Workflow routing filters tenant-owned entries before execution and resolves selected IDs through tenant-aware registry resolution.

Aliases are canonicalized before governance and registry checks. A hospital tenant cannot use an alias, known artifact hash, filesystem discovery path, or matching plugin ID to select another hospital's entry.

## 7. Provenance Guarantee

`ExecutionIdentity` is immutable and contains, for external execution:

- tenant ID;
- canonical plugin ID;
- plugin version;
- governance record ID;
- artifact SHA-256;
- canonical manifest hash;
- entrypoint module and class;
- plugin type and origin;
- approved capability set;
- isolation runtime name.

The external proxies use this snapshot for authority and compare it with current governance and artifact state before execution.

## 8. Isolation Guarantees

The development subprocess provides:

- JSON request/response transport;
- request, stdout, stderr, and result bounds;
- timeout and child termination;
- a temporary working directory;
- an explicitly allowlisted child environment;
- malformed response rejection;
- fail-closed network capability handling.

The development subprocess does **not** claim CPU quota, memory quota, host filesystem isolation, network namespace isolation, restricted OS identity, or complete sandboxing.

The container adapter declares CPU, memory, network, filesystem, and identity enforcement only after checking for an available container executable and daemon. This is deployment-dependent and is not verified as active in the current workspace.

## 9. Audit Guarantees

`PluginExecutionAudit` stores tenant, authenticated user, professional, canonical plugin ID, version, artifact hash, governance record, decision, status, isolation metadata, capability metadata, timing, and bounded denial/failure reasons.

Execution audit paths do not intentionally persist patient payloads, plugin inputs, plugin outputs, credentials, environment secrets, JWTs, API keys, or unrestricted subprocess output.

## 10. Database and Migration Status

**Repository verified. Live Supabase not verified.** No live Supabase connection or migration deployment evidence was available in this closure environment.

The repository migration set is ordered `0001` through `0008`:

| Migration | Purpose |
|---|---|
| `0001_identity_tenant_rls.sql` | Identity, hospitals, memberships, invitations, membership events, and foundational RLS. |
| `0002_rbac_seed.sql` | RBAC seed data. |
| `0003_invitation_delivery_outbox.sql` | Invitation delivery outbox support. |
| `0004_plugin_governance.sql` | Hospital-scoped plugin governance records, lifecycle fields, governance audit events, indexes, and restrictive RLS. |
| `0005_plugin_governance_hardening.sql` | Additive governance metadata, security validation, activation fields, and artifact-aware uniqueness. |
| `0006_plugin_execution_audit.sql` | Durable bounded execution audit records and restrictive RLS. |
| `0007_plugin_execution_isolation_provenance.sql` | Isolation enforcement and resource-policy provenance fields. |
| `0008_plugin_execution_tenant_provenance.sql` | Authenticated user and professional provenance fields. |

The reviewed migrations use foreign keys for hospital and governance relationships, tenant-scoped indexes, additive `if not exists` changes in hardening migrations, and restrictive client RLS policies for governance and execution audit tables. No R9 migration was added during closure. Existing identity, membership, invitation, R7, and audit structures were not intentionally modified.

## 11. Supabase Status

Live Supabase schema, applied migration history, RLS behavior in the deployed project, and production database constraints are **NOT VERIFIED**. The repository SQL is evidence of the intended database contract only.

## 12. Test Matrix

The final acceptance run covered:

- governance lifecycle and tenant scope;
- artifact hashing and ZIP traversal protection;
- pre-import admission rejection;
- external subprocess execution;
- manifest, capability, and artifact mutation;
- revocation and denial auditing;
- tenant-scoped same-ID resolution;
- system-context internal plugin resolution;
- isolation policy and unavailable container runtime;
- governance API authorization and route registration;
- plugin orchestration and infrastructure validation;
- R5 authorization, R6 identity events, R7 invitation, RBAC catalog, and router regressions.

Collected matrix size: **91 tests**.

## 13. Test Results

Command executed from `apps/api` using the repository `.venv`:

```text
.venv/Scripts/python.exe -m pytest \
  tests/test_plugin_governance.py \
  tests/test_plugin_security.py \
  tests/test_plugin_admission.py \
  tests/test_external_execution.py \
  tests/test_plugin_governance_api.py \
  tests/test_plugin_orchestration.py \
  tests/test_plugin_orchestration_extended.py \
  tests/test_infrastructure_validation.py \
  tests/test_isolation_policy.py \
  tests/test_r5_authorization.py \
  tests/test_r6_identity_events.py \
  tests/test_r7_invitation.py \
  tests/test_rbac_catalog.py \
  tests/test_router.py -q
```

Result: **91 passed, 0 failed, 0 skipped**.

Warnings were limited to existing Pydantic configuration deprecation warnings.

## 14. Static Validation

- `python -m compileall app tests`: **PASS**.
- VS Code diagnostics for touched R9 files: **PASS; no errors**.
- Route/OpenAPI registration: **PASS** through router and governance API tests.
- `git diff --check`: **NOT CLEAN because of unrelated pre-existing worktree noise** in `.gitignore` and `apps/api/app/api/v1/recommendations.py`. Those files were not modified.

## 15. Known Limitations

- The full combinatorial R9H cross-product is not exhaustively parameterized.
- Live Supabase deployment and applied migration history are unverified.
- Production container execution is not configured or verified in this workspace.
- The development subprocess is not an OS-level sandbox.
- Some admission/discovery failures are returned as bounded loader errors rather than persisted as durable audit records before a runtime audit boundary is reached.
- The structured governance registration API accepts a client-provided artifact hash; the upload path derives the hash server-side. Production policy should prefer server-derived artifact registration.

## 16. Deployment Dependencies

Before production external plugin execution:

1. Apply and verify migrations `0001` through `0008` in the target Supabase project.
2. Verify RLS policies and service-role boundaries in the deployed database.
3. Configure a verified container runtime and image with restricted identity, read-only filesystem, temporary writable storage, CPU/memory limits, process limits, and network policy.
4. Inject the production isolation provider into plugin runtime configuration.
5. Verify deployed audit persistence and alerting for denial categories.

## 17. Unresolved Risks

These are deployment or next-phase risks, not silently accepted production guarantees:

- A plain Windows development subprocess cannot enforce all requested OS controls.
- A live database can diverge from repository migrations until deployment verification is performed.
- Artifact registration should be changed in a future phase to derive hashes exclusively from uploaded server-side artifacts.
- The assurance matrix should be expanded with parameterized lifecycle, authorization, capability, and artifact combinations.

## 18. Explicit Non-Guarantees

R9 does not claim:

- production certification;
- full OS-level sandboxing on Windows;
- CPU or memory enforcement in the development subprocess;
- host filesystem or network namespace isolation in the development subprocess;
- live Supabase schema deployment;
- exhaustive proof of every possible plugin implementation behavior;
- autonomous clinical prescribing or clinical decision replacement.

## 19. Frozen Artifacts

The following R9 contracts are frozen:

- `TenantContext` and explicit system context semantics;
- canonical plugin ID normalization and reserved internal IDs;
- tenant-scoped registry ownership and resolution;
- governance admission before external import;
- artifact hash, version, manifest, capability, and tenant binding;
- immutable `ExecutionIdentity` provenance;
- external proxy execution through the isolation runtime contract;
- JSON subprocess transport and bounded I/O;
- durable execution audit contract;
- migrations `0001` through `0008` as the repository R9 migration set.

No R9 database migration was added during closure.

## 20. R9 Gate Decision

**B. R9 COMPLETE WITH DEPLOYMENT-DEPENDENT ITEMS**

Repository-level tenant isolation, identity binding, artifact checks, governance checks, bounded auditing, JSON subprocess behavior, and fail-closed policy checks passed the acceptance test run. Production-grade isolation and live Supabase deployment remain deployment-dependent and are explicitly not claimed.

## 21. Next Phase

### A. Supabase/database deployment

- **Status:** Repository SQL verified; live application not verified.
- **Dependency:** Target Supabase project access and migration runner.
- **Priority:** High.
- **Blocks clinical use:** Yes for production authorization and audit assurance.
- **New architectural decision:** No, unless deployed RLS differs from the frozen contract.

### B. Authentication/session completion

- **Status:** Repository authentication and RBAC regressions pass.
- **Dependency:** Deployed identity provider, session configuration, and token rotation policy.
- **Priority:** High.
- **Blocks clinical use:** Yes if production identity cannot be verified.
- **New architectural decision:** Possibly, for multi-hospital membership semantics.

### C. Identity and tenant production integration

- **Status:** Runtime tenant model verified in repository tests.
- **Dependency:** Authenticated production claims and membership source.
- **Priority:** High.
- **Blocks clinical use:** Yes for multi-hospital deployment.
- **New architectural decision:** No for the current single-active-membership contract; yes for future multi-membership support.

### D. Plugin governance frontend integration

- **Status:** Backend governance API and authorization paths are tested; frontend integration is outside this closure.
- **Dependency:** Frontend workflow and backend API contract.
- **Priority:** Medium.
- **Blocks clinical use:** No for backend-only operation; yes for a clinician-facing governance workflow.
- **New architectural decision:** No.

### E. Production isolation/container deployment

- **Status:** Container provider contract exists; deployment is unverified.
- **Dependency:** Container runtime, hardened image, service account, resource and network policy.
- **Priority:** Critical for external plugins in production.
- **Blocks clinical use:** Yes for production external plugin execution.
- **New architectural decision:** No if the existing provider contract is adopted; yes if a different sandbox technology is selected.

### F. Clinical/runtime integration

- **Status:** Plugin orchestration regressions pass; broader clinical workflow certification remains separate.
- **Dependency:** Verified identity, database, governance, and production isolation deployment.
- **Priority:** High.
- **Blocks clinical use:** Yes for clinical production release.
- **New architectural decision:** No for the existing explainable CDSS boundaries.

### G. Other outstanding architecture work

- **Status:** Expand the R9H parameterized matrix and server-derive structured registration artifact hashes.
- **Dependency:** New phase scope and product/security review.
- **Priority:** Medium.
- **Blocks clinical use:** The expanded matrix is assurance work; client hash acceptance should be resolved before untrusted production registration.
- **New architectural decision:** No for tests; possibly yes for artifact upload/API contract changes.
