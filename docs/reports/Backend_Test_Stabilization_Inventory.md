# Backend Test Stabilization Inventory

## Baseline

Command:

```text
.\.venv\Scripts\python.exe -m pytest apps/api/tests -q
```

Result: **31 failed**, remaining tests passed, exit code `1`.

No production behavior was changed during inventory collection.

## Failure inventory

| Test or group | Failure | Classification | Current runtime evidence | Required action |
| --- | --- | --- | --- | --- |
| `apps/api/tests/test_clinical_decision.py` guideline tests (3) | `ModuleNotFoundError: guideline_engine` | **B. STALE_TEST_EXPECTATION** | The implementation is `app.clinical_decision.guideline_engine`; the test imports a removed top-level module. | Update imports to the authoritative package path. |
| `apps/api/tests/test_clinical_decision.py` stewardship tests (2) | `ModuleNotFoundError: stewardship` | **B. STALE_TEST_EXPECTATION** | The implementation is `app.clinical_decision.stewardship`. | Update imports. |
| `apps/api/tests/test_clinical_decision.py` decision-fusion tests (2) | `ModuleNotFoundError: decision_fusion` | **B. STALE_TEST_EXPECTATION** | The implementation is `app.clinical_decision.decision_fusion`. | Update imports. |
| `apps/api/tests/test_clinical_decision.py` explainability tests (2) | `ModuleNotFoundError: explainability` | **B. STALE_TEST_EXPECTATION** | The implementation is `app.clinical_decision.explainability`. | Update imports. |
| `apps/api/tests/test_clinical_decision.py` orchestrator tests (3) | `ModuleNotFoundError: orchestrator` | **B. STALE_TEST_EXPECTATION** | The implementation is `app.clinical_decision.orchestrator`. | Update imports. |
| `apps/api/tests/test_phase6_api_integration.py` recommendation assertions (16) | Requests receive HTTP 401 `UNAUTHORIZED` before response assertions. | **F. AUTHENTICATION_EXPECTATION_MISMATCH** | Recommendation routes use `require_permission("recommendations:request")`; anonymous requests are intentionally rejected. | Add a test-only authenticated authorization dependency override. Do not disable route authentication. |
| `apps/api/tests/test_plugin_integration.py::test_soar_runtime_context_initializes_and_lazy_loads_models` | Test sends organism/antimicrobial payload with no `context.deployment_id`; runtime rejects it. | **C. OBSOLETE_LEGACY_BEHAVIOR** | Current SOAR contract requires explicit deployment ID and forbids implicit fallback. | Update the test to provide explicit metadata-backed ID and valid artifact-pair fixture. |
| `apps/api/tests/test_r7_invitation.py::test_backend_settings_resolve_env_file_from_workspace_root` | Expected project root is the parent of the repository root. | **B. STALE_TEST_EXPECTATION** | `app.core.config.PROJECT_ROOT` is the current repository root containing the backend `.env` resolution. | Correct expected path to the repository root. |
| `apps/api/tests/test_soar_artifact_registry.py::test_deployment_scanner_discovers_deployment` | Fixture has model artifacts only; scanner returns zero deployments. | **D. TEST_INFRASTRUCTURE_FAILURE** | `DeploymentScanner` intentionally requires both `deployment_info.json` and `feature_schema.json` before activation. | Add the required metadata/schema fixture; do not weaken scanner behavior. |

## Classification totals

- **A. GENUINE_RUNTIME_BUG:** 0 identified.
- **B. STALE_TEST_EXPECTATION:** 13 failures: 12 removed top-level imports and 1 repository-root assumption.
- **C. OBSOLETE_LEGACY_BEHAVIOR:** 1 SOAR fallback expectation.
- **D. TEST_INFRASTRUCTURE_FAILURE:** 1 missing artifact-pair fixture.
- **E. MISSING_COMPATIBILITY_LAYER:** 0 identified.
- **F. AUTHENTICATION_EXPECTATION_MISMATCH:** 16 recommendation API assertions.
- **G. OUT_OF_SCOPE_EXTERNAL_DEPENDENCY:** 0 identified.

The totals above refer to all 31 pytest failures: 13 stale expectations, 16 authentication expectation mismatches, 1 obsolete SOAR behavior expectation, and 1 invalid scanner fixture.

## Scope decision

No production fix is justified by this inventory. The required repairs are stale test imports, authenticated test setup, obsolete SOAR test behavior, and fixture/path corrections. Explicit SOAR deployment selection remains unchanged.
