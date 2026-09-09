# Phase 27C Unified Plugin Readiness Matrix

Statuses use only the Phase 27 values. `READY_FOR_CONTROLLED_EXECUTION` means repository-supported technical execution is proven; it does not mean autonomous clinical deployment.

| Plugin/deployment | Contract | Input resolution | Form/validation | Backend execution | Output | Explainability | Audit | Status |
|---|---|---|---|---|---|---|---|---|
| SOAR: each of 10 listed deployments | PASS | PASS | PASS | PASS real artifacts | PASS normalized S/I/R | PASS at governed explanation boundary | PASS audit event path | READY_FOR_CONTROLLED_EXECUTION |
| ARMD: 20 WP4 registry models | PASS | PASS | PASS | PASS, 20/20 adapter results | PASS prediction execution objects | PASS focused adapter/plugin tests | PASS shared audit path | READY_FOR_CONTROLLED_EXECUTION |
| WHO knowledge/provider | PASS | PASS explicit query contract | PASS | PASS focused/provider tests | PASS structured knowledge result | PASS evidence/provider provenance path | PASS shared audit path | READY_FOR_CONTROLLED_EXECUTION |

## Evidence commands
- SOAR: `.\\.venv\\Scripts\\python.exe -m pytest -q apps/api/tests/test_phase27_soar_execution.py`, 12 passed.
- ARMD: `.\\.venv\\Scripts\\python.exe -m pytest -q apps/api/app/plugins/prediction/armd/tests/test_armd_plugin.py packages/prediction-framework/tests/test_armd_adapter.py`, 31 passed; direct registry run 20/20 success.
- WHO/fusion/explainability/plugin integration: `.\\.venv\\Scripts\\python.exe -m pytest -q apps/api/tests/test_clinical_decision.py apps/api/tests/test_phase6_explainability.py apps/api/tests/test_plugin_integration.py apps/api/tests/test_who_knowledge_plugin.py`, 80 passed.
- Audit: `.\\.venv\\Scripts\\python.exe -m pytest -q apps/api/tests/test_external_execution.py apps/api/tests/test_logging.py apps/api/tests/test_middleware.py`, 15 passed.

Authenticated browser execution was not claimed; it requires manual login.
