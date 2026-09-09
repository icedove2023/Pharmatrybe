# Backend Contract Freeze Readiness Report

Status: SUPERSEDED by `BACKEND_CONTRACT_FREEZE_REPORT.md` after Phase 17 closure decisions.

## 1. Scope

This pass stabilized backend tests and audited contract readiness before any frontend/backend reconciliation. Scope was limited to backend tests, backend contract documentation, plugin runtime behavior, authentication expectations, and public error behavior.

No React/frontend code, SOAR deployment artifacts, model artifacts, preprocessing, encoders, ARMD artifacts, WHO database contents, or broad canonical schema were modified.

## 2. Failure inventory and repairs

The baseline command was:

```text
.\.venv\Scripts\python.exe -m pytest apps/api/tests -q
```

Baseline result: **31 failed**.

The detailed inventory is [Backend_Test_Stabilization_Inventory.md](Backend_Test_Stabilization_Inventory.md).

All 31 failures were classified without changing production behavior:

- stale imports in clinical-decision tests;
- authentication expectation mismatch in recommendation API tests;
- obsolete SOAR fallback expectation;
- stale repository-root expectation;
- scanner fixture missing the required artifact metadata pair.

After repairs, the same full suite passed:

```text
.\.venv\Scripts\python.exe -m pytest apps/api/tests -ra
276 passed, 7 warnings in 74.68s (0:01:14)
```

## 3. Production fixes

No production runtime fixes were required. Current runtime behavior was consistent with the contracts after test-layer repairs.

## 4. Tests corrected as stale or infrastructure-invalid

- Clinical-decision tests now import `app.clinical_decision.*`, the authoritative package paths.
- Recommendation API tests now provide a test-only permission dependency override. Authentication remains enforced in production.
- The SOAR integration test now supplies explicit `context.deployment_id` and artifact metadata. It no longer exercises forbidden implicit fallback.
- The scanner fixture now supplies both `deployment_info.json` and `feature_schema.json`, matching the active deployment contract.
- The repository-root test now matches `app.core.config.PROJECT_ROOT`.

No fallback, heuristic routing, or anonymous production access was restored.

## 5. Legacy behavior explicitly not restored

The following remain forbidden and were not reintroduced:

- organism-only deployment selection;
- antimicrobial-only deployment selection;
- filename-token inference;
- first-valid deployment fallback;
- silent deployment substitution;
- `infection_site` to `BodyLocation_Group` inference;
- `organism`, `pathogen`, and `species` equivalence;
- clinician ownership claims for SOAR artifact fields.

## 6. Authentication findings

Recommendation and pipeline routes are protected by `require_permission(...)`. The previous API integration failures were test authentication expectation mismatches, not evidence that authentication should be disabled. The corrected tests override the authorization dependency locally with the required permission and do not alter application authentication.

Authentication failures are represented by the application’s reusable error middleware/envelope in the observed route path. Protected route authorization remains a platform-owned boundary.

## 7. Error-contract findings

The reusable `ApiFailure`/`ApiError` models define a stable error shape with `code`, `message`, and optional `details`. Current public behavior is not uniformly normalized:

- authentication middleware emits the reusable structured envelope;
- pipeline routes still use HTTP exceptions for unsupported mode, unavailable runtime, unknown plugins, and pipeline failure;
- plugin internals expose typed exceptions such as `DeploymentSelectionError` and `PredictionError`, which are caught at orchestration boundaries;
- WHO provider/service paths return provider failure results or service exceptions depending on caller;
- recommendation paths include legacy response shapes as well as protected API envelopes.

Classification:

- Existing structured authentication errors: **SAFE_TO_NORMALIZE_NOW** only within already-established middleware behavior.
- Pipeline/plugin/recommendation error normalization: **REQUIRES_ARCHITECTURAL_DECISION** because status codes, response models, and consumers differ.
- No broad normalization was performed in this pass.

## 8. Final test results

Required focused suites:

```text
.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_plugin_orchestration.py -q
4 passed

.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_soar_deployment_contract.py -q
8 passed

.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_plugin_input_schema_contract.py -q
9 passed

.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_who_knowledge_plugin.py -q
37 passed

.\.venv\Scripts\python.exe -m pytest apps/api/app/plugins/prediction/armd/tests/test_armd_plugin.py -q
15 passed
```

Directly repaired clusters:

```text
.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_clinical_decision.py apps/api/tests/test_phase6_api_integration.py apps/api/tests/test_plugin_integration.py apps/api/tests/test_r7_invitation.py apps/api/tests/test_soar_artifact_registry.py -q
62 passed
```

Full backend suite:

```text
.\.venv\Scripts\python.exe -m pytest apps/api/tests -ra
276 passed, 7 warnings
```

Additional checks:

```text
.\.venv\Scripts\python.exe -m compileall -q apps/api/app apps/api/tests
exit code 0

git diff --check
exit code 0
```

Warnings are existing Pydantic configuration, SHAP deprecation, and `datetime.utcnow()`/serialized model warnings. No test failures remain.

## 9. Contract freeze readiness

| Contract | Readiness | Blocker | Evidence | Owner / next decision |
| --- | --- | --- | --- | --- |
| Plugin Runtime | `NOT_READY_TO_FREEZE` | Plugin-specific boundaries and mixed public response paths remain. | Plugin schemas/runtime and full suite pass. | Platform contract owner must approve one public normalization boundary. |
| SOAR Deployment | `NOT_READY_TO_FREEZE` | Upstream deployment owner and raw input provenance remain incomplete. | Explicit-ID tests and artifact inspection pass; upstream producer is not implemented. | SOAR/platform owner must define approved routing evidence owner. |
| SOAR Upstream Ownership | `NOT_READY_TO_FREEZE` | No connected producer for `deployment_id` or six raw fields. | Ownership report and propagation tests. | Platform/domain owner must introduce an approved producer or retain explicit caller ownership. |
| ARMD Runtime | `NOT_READY_TO_FREEZE` | Cross-plugin/raw field ownership and canonical mappings remain unresolved. | ARMD artifact-backed tests pass. | Clinical/platform owner must decide ownership and mappings. |
| WHO Query | `NOT_READY_TO_FREEZE` | Public query refinements and application-wide database/error envelope are not one frozen contract. | WHO focused suite passes with configured database routing. | WHO/platform owner must approve public query and routing boundary. |
| Backend Request | `NOT_READY_TO_FREEZE` | `AUTO` routing and plugin-specific payload ownership coexist with unresolved SOAR upstream routing. | Pipeline/orchestration tests pass. | Platform owner must approve request ownership and routing semantics. |
| Recommendation | `NOT_READY_TO_FREEZE` | Multiple response paths and plugin-specific sections are not one normalized public envelope. | Phase 6 API tests pass with authenticated setup. | API contract owner must select canonical response path. |
| Explainability | `NOT_READY_TO_FREEZE` | Explainability is assembled across API/plugin-specific paths. | Explainability API tests and runtime contracts pass. | API/clinical owner must approve normalization and missing-explanation semantics. |
| Backend Error | `NOT_READY_TO_FREEZE` | HTTP exceptions, typed plugin errors, provider results, and reusable `ApiFailure` coexist. | Failure behavior is documented; full suite passes. | Platform/API owner must make the normalization decision. |

## 10. Final transition decision

The backend test baseline is now green and the known failures are classified and repaired at the correct layer. The backend is not contract-frozen because several ownership and normalization decisions remain architectural rather than test failures.

```text
BACKEND STABILIZATION = COMPLETE

BACKEND CONTRACT BASELINE = NOT READY

FRONTEND ↔ BACKEND RECONCILIATION = NOT AUTHORIZED
```
