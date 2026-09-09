# Phase 25-26 Live System Verification

## Commands and results
- `npm test`: PASS, 207 assertions.
- `npm run build`: PASS, Vite production bundle built; existing chunk/import warnings remain.
- `npm run lint`: FAIL, six existing React Start/router TypeScript errors in `src/router.tsx`, `src/routes/__root.tsx`, `src/server.ts`, and `src/start.ts`.
- `git diff --check`: PASS; Git reported line-ending warnings only.
- `.\\.venv\\Scripts\\python.exe -m pytest -q apps/api/tests/test_soar_deployment_contract.py apps/api/tests/test_soar_artifact_registry.py`: PASS, 12 tests.
- `.\\.venv\\Scripts\\python.exe -m pytest -q apps/api/tests/test_who_knowledge_plugin.py apps/api/tests/test_plugin_input_schema_contract.py apps/api/tests/test_plugin_integration.py`: PASS, 55 tests.
- `.\\.venv\\Scripts\\python.exe -m pytest -q apps/api/app/plugins/prediction/armd/tests/test_armd_plugin.py packages/prediction-framework/tests/test_armd_adapter.py`: PARTIAL, 29 passed and 1 failed.
- `.\\.venv\\Scripts\\python.exe -m pytest -q`: FAIL, three unrelated identity-registration tests fail because Supabase Auth rejects fixture ID `auth-user-id` as not a UUID.

## Runtime services
The frontend production build was verified. A credentialed browser login and production-like backend/database session were not performed. The supplied password was not used by automation.

## Status
`PARTIAL`; authenticated end-to-end assessment -> plugin -> fusion -> explainability -> audit rendering remains NOT CONFIRMED.
