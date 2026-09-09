# Frontend / Backend Integration Report

**Checkpoint**: Phase 15D integration verification  
**Date**: 2026-08-18  
**Mode**: Interactive, controlled frontend integration and test-contract cleanup  
**Backend source of truth**: Runtime FastAPI `app.openapi()`, backend implementation, schemas, and `Fdocs/Backend_Requirements.md`

## A. Repository Architecture

### Frontend

- Vite + React + TypeScript application at repository root.
- API clients under `src/api/`.
- React/Zustand/TanStack Query consumers under `src/components/`, `src/hooks/`, and `src/stores/`.
- Frontend scripts: `npm run lint`, `npm run build`, `npm test`.

### Backend

- FastAPI application under `apps/api/app/`.
- Runtime application: `from app.main import app`.
- V1 routes aggregate through `apps/api/app/api/router.py` and are mounted by `apps/api/app/main.py` with prefix `/api/v1`.
- WHO and clinical-case routes use database repositories/services.
- Recommendation generation is implemented at `/api/v1/recommendations/generate`.

## B. Integration Map

| Frontend capability | Frontend module | Backend endpoint | Backend verified? | Data-source classification | Action/status |
|---|---|---|---|---|---|
| WHO disease search/list | `src/api/whoApi.ts` | `GET /api/v1/who/diseases`, `GET /api/v1/who/search` | YES | `backend_authoritative` | Connected |
| WHO disease detail | `src/api/whoApi.ts` | `GET /api/v1/who/diseases/{disease_id}` | YES | `backend_authoritative` | Connected |
| WHO guideline bundle | `src/api/whoApi.ts` | `GET /api/v1/who/guideline/{disease_id}` | YES | `backend_authoritative` | Connected |
| WHO recommendations/evidence/pathogens | `src/api/whoApi.ts` | Corresponding `/who/*/{disease_id}` GET routes | YES | `backend_authoritative` | Connected |
| WHO diagnostics/monitoring/follow-up/referral/stewardship | `src/api/whoApi.ts` | Corresponding `/who/*/{disease_id}` GET routes | YES | `backend_authoritative` | Connected |
| Clinical case list/detail/create | `src/api/clinicalCasesApi.ts` | `GET/POST /api/v1/clinical-cases`, `GET /api/v1/clinical-cases/{case_id}` | YES | `backend_authoritative` | Connected; request UUIDs are client request identifiers, not clinical values |
| Recommendation generation | `src/api/recommendationApi.ts` | `POST /api/v1/recommendations/generate` | YES | `backend_authoritative` when caller supplies verified predictions | Connected at canonical boundary |
| Recommendation retrieval by case | `src/api/recommendationApi.ts` | No verified retrieval endpoint | NO | `unavailable` | Synthetic fallback removed |
| Clinical review/history | `src/api/recommendationApi.ts` | No active runtime route | NO | `unavailable` | Local session recorder removed |
| Authentication/session | `src/api/authApi.ts` | No active auth lifecycle endpoints; runtime `/api/v1/auth` is status-only | NO | `unavailable` | Explicit pending state |
| Hospital registration | `src/api/authApi.ts` | Not exposed by backend | NO | `unavailable` | No fake registration |
| User provisioning/admin | `src/api/adminApi.ts` | No active admin mutation/list contracts | NO | `unavailable` | Synthetic directory/admin data removed |
| SOAR surveillance records | `src/api/soarApi.ts` | `/api/v1/soar` GET status only | NO | `unavailable` | Synthetic surveillance removed |
| ARMD model registry/details | `src/api/armdApi.ts` | `/api/v1/armd` GET status only | NO | `unavailable` | Synthetic model metrics/MIC/SHAP removed |
| Dashboard aggregates | `src/api/index.ts` | No dashboard aggregate endpoint | NO | `unavailable` | Synthetic dashboard values removed |
| Patient directory/history | `src/api/index.ts` | No verified patient-directory contract for these methods | NO | `unavailable` | Synthetic patient records removed |
| Settings | `src/api/index.ts` | No backend settings endpoint | NO | `client_observed` | Local UI preference persistence retained; not clinical/auth state |

## C. Authentication Verification

`Fdocs/Backend_Requirements.md` describes future requirements for registration, login, sessions, refresh, logout, admin authorization, and audit logging. The active backend does not implement that lifecycle.

- Login: not exposed by the active backend.
- Session restore: no backend session endpoint; frontend returns unauthenticated.
- Logout: no backend session revocation endpoint; frontend no longer creates or treats local tokens as authoritative.
- 401/403: API client can parse backend HTTP errors, but no active auth workflow was verified.
- Role resolution: not authoritative; frontend route permissions are UI-only.
- Demo persona login: removed from the active login UI and auth adapter.
- Browser localStorage is retained only for UI settings; it is not used as an authentication authority.

**Authentication, hospital registration, and user provisioning remain pending backend implementation.**

## D. Hospital Registration Verification

The requirements document specifies `POST /api/v1/auth/register-hospital`, but runtime OpenAPI does not register it. The frontend no longer simulates organization creation, users, sessions, or generated JWT-like values.

Status: **Not exposed by backend**.

## E. User Provisioning Verification

The requirements document specifies admin user list/create/role/status routes, but the runtime registry does not expose those contracts. The frontend admin client now returns explicit unavailable errors instead of mutating a local directory or returning temporary passwords.

Status: **Not exposed by backend**.

## F. Mock/Stub Cleanup

### Removed from active production paths

- Disease-based fabricated prediction probabilities in `src/api/recommendationApi.ts`.
- Local fallback recommendation generation in `getRecommendation`.
- Local clinical-review response/history store in `src/api/recommendationApi.ts`.
- Demo credential/session generation and persona switching in `src/api/authApi.ts` and `src/stores/authStore.ts`.
- Demo persona buttons in `src/components/auth/LoginForm.tsx`.
- Hard-coded SOAR surveillance records in `src/api/soarApi.ts`.
- Hard-coded ARMD model metrics, feature importance, MIC distributions, and model metadata in `src/api/armdApi.ts`.
- Hard-coded admin users, audit events, telemetry, governance metrics, stewardship policies, and plugin registry responses in `src/api/adminApi.ts`.
- Synthetic dashboard aggregates, clinical pipeline, explainability fallback, and patient records in `src/api/index.ts`.
- Fabricated recommendation-view patient identity, allergies, eGFR, and susceptibility display in `src/components/recommendation/RecommendationView.tsx`.
- Browser-storage token injection from `src/api/client.ts`.

### Remaining fixtures and static data

- `src/__tests__/` contains deterministic contract/regression fixtures, including `buildCanonicalResponse`; these are test-only imports and are not used by the production API clients.
- `src/api/index.ts` retains local UI settings storage under `pharmatrybe_settings`; this is client-observed UI preference state, not backend-authoritative data.
- Clinical assessment option labels/presets remain UI configuration; they do not claim to be backend records.
- `src/api/directory.ts` was removed after confirming it had no production imports.
- Static plugin registry entries remain architecture metadata only; unverified version/model-version strings now read `Not exposed by backend`.

### Tests updated

- `src/__tests__/phase8_contracts.test.ts` now verifies unavailable clinical review and client-side validation without fabricated auth state.
- `src/__tests__/phase9_integration.test.ts` now verifies canonical response shape, immutability, and forbidden method absence.
- `src/__tests__/phase10_knowledge_surveillance.test.ts` now verifies WHO/client method presence and explicit SOAR/ARMD unavailability.
- `src/__tests__/phase13_administration_governance.test.ts` and `src/__tests__/phase13_admin_governance_hardening.test.ts` now verify unavailable admin/audit/prediction capabilities.
- `src/__tests__/phase14_testing_contract_validation.test.ts` now verifies canonical fields, forbidden methods, and deferred authentication.
- `run-tests.ts` now awaits the asynchronous Phase 8 suite.

## G. Forbidden/Speculative Endpoint Audit

No active frontend network call was found for:

- `/api/v1/soar/predict`
- `/api/v1/armd/predict`
- `/api/v1/plugins`
- `/api/v1/telemetry`
- `/api/v1/model-registry`
- `/accept`
- `/override`
- `/modify`
- `/sign`
- `/prescription`

`clinical-review` remains as a method name/comment in `recommendationApi.ts` and as UI review functionality, but it is not called over HTTP; its implementation now explicitly reports that the active backend does not expose it.

## H. Test Results

### Passed

- `npm run lint` — **PASS** (`tsc --noEmit` completed with no errors).
- `npm run build` — **PASS**. Vite produced a production bundle. It emitted only the existing large-chunk warning.
- `npm test` — **PASS**, all 116 frontend assertions passed across Phase 8, 9, 10, 11, 13, and 14 suites.
- `python -m pytest tests/test_phase6_api_integration.py -q` — **PASS**, 16 passed.
- Runtime OpenAPI inspection — **PASS**, application imported and schema inspected.

### Failed / blocked

- `python -m pytest -q` from `apps/api` — **COLLECTION FAILURE** in four existing backend test modules due import-path/environment issues, including `ModuleNotFoundError: contracts`, `packages`, and `apps`.
- `rg` was unavailable in the Windows PowerShell environment; equivalent PowerShell static searches were run successfully.

## I. Known Limitations

- The backend recommendation endpoint requires `prediction_results` in the request. The frontend has no verified standalone SOAR/ARMD prediction endpoint from which to obtain those values. It therefore does not fabricate them.
- The backend has no active recommendation retrieval endpoint by case ID; the frontend cannot reconstruct or synthesize a prior recommendation.
- The backend has no active clinical-review route in runtime OpenAPI; review submission/history is unavailable.
- Auth, hospital registration, provisioning, audit, telemetry, plugin registry, and governance APIs described in the requirements are not active runtime contracts.
- Existing frontend regression tests that encoded the old mock/demo behavior were updated to assert the truthful unavailable capability contract.
- The complete backend suite remains blocked by existing Python import-path collection failures.

## J. Final Integration Status

**INTEGRATION INCOMPLETE — ACTION REQUIRED**

The real WHO, clinical-case, and canonical recommendation-generation boundaries are connected and the frontend production paths no longer silently substitute fabricated clinical data. The frontend lint, build, and current integration suites pass. The status remains incomplete because backend authentication/admin/review/prediction-surveillance capabilities remain unavailable by runtime contract, and the complete backend suite has unresolved collection/import-path failures.

## Appendix — Runtime OpenAPI Paths

Runtime inspection used `from app.main import app; app.openapi()` from `apps/api`.

Phase-relevant registered paths:

```text
/api/v1/auth                         GET (status only)
/api/v1/clinical-cases               GET, POST
/api/v1/clinical-cases/{case_id}     GET, PUT, DELETE
/api/v1/recommendations              GET (status only)
/api/v1/recommendations/generate     POST
/api/v1/who/diseases                 GET
/api/v1/who/diseases/{disease_id}    GET
/api/v1/who/search                   GET
/api/v1/who/guideline/{disease_id}   GET
/api/v1/who/recommendations/{disease_id} GET
/api/v1/who/evidence/{disease_id}    GET
/api/v1/who/pathogens/{disease_id}   GET
/api/v1/who/diagnostics/{disease_id} GET
/api/v1/who/monitoring/{disease_id}  GET
/api/v1/who/follow-up/{disease_id}   GET
/api/v1/who/referral/{disease_id}    GET
/api/v1/who/stewardship/{disease_id} GET
/api/v1/soar                         GET (status placeholder)
/api/v1/armd                         GET (status placeholder)
/api/v1/admin                        GET (status placeholder)
```

The canonical recommendation route remains:

```text
POST /api/v1/recommendations/generate
```

## Git Change Summary

The repository already contained extensive unrelated/previous changes and untracked files before this pass. The integration files changed in this pass are:

- `src/api/authApi.ts`
- `src/api/client.ts`
- `src/api/index.ts`
- `src/api/recommendationApi.ts`
- `src/api/soarApi.ts`
- `src/api/armdApi.ts`
- `src/api/adminApi.ts`
- `src/stores/authStore.ts`
- `src/components/auth/LoginForm.tsx`
- `src/components/recommendation/ClinicalReviewSection.tsx`
- `src/components/recommendation/RecommendationView.tsx`
- `docs/integration/FRONTEND_BACKEND_INTEGRATION_REPORT.md`

`git status --short` also shows the pre-existing backend/frontend repository changes and generated/untracked files; those were not reverted. The frontend integration pass additionally changed the API clients, unavailable-state adapters, truthful surveillance/plugin labels, recommendation view, auth UI/store, and the test files listed above.

## Phase 15D.1 — Backend Test Infrastructure Repair

### Scope

This repair changed only Python test/import infrastructure and stale test import paths. No clinical logic, API route, schema, response contract, frontend client, or UI component was changed.

### Root cause

The backend package is rooted at `apps/api/app`, while shared framework code is rooted at repository-level `packages/prediction_framework`. Existing configuration only exposed `apps/api`:

```ini
[pytest]
pythonpath = .
testpaths = tests
```

That configuration worked only for the backend-local working directory and did not expose repository-level packages during root execution. Two tests also retained imports from the former flat layout (`contracts`, `rules`, and `apps.api.app...`). The importable compatibility package lacked `packages.prediction_framework.adapters`, although application/plugin code imported it.

### Files changed

- `pytest.ini` — added repository-root test discovery and `pythonpath = . apps/api`.
- `apps/api/pytest.ini` — retained backend-local execution and added repository root to `pythonpath`.
- `apps/api/tests/test_clinical_decision.py` — corrected imports to `app.clinical_decision.contracts` and `app.clinical_decision.rules`.
- `apps/api/tests/test_phase6_explainability.py` — corrected `apps.api.app...` import to `app...`.
- `packages/prediction_framework/adapters/__init__.py` — added the importable compatibility package.
- `packages/prediction_framework/adapters/armd_adapter.py` — delegated the compatibility import to the existing hyphenated source tree.

### Collection results

Both commands now collect successfully:

```text
Repository root: 186 tests collected, 0 collection errors
apps/api:         186 tests collected, 0 collection errors
```

The prior `ModuleNotFoundError` failures for `contracts`, `apps`, and `packages` during collection are resolved.

### Full backend suite results

Canonical command:

```text
python -m pytest -q
```

Result:

```text
186 collected
166 passed
20 failed
0 collection errors
```

The 20 failures occur after collection and are behavioral failures in existing clinical-decision, plugin-integration, and WHO-plugin tests. Representative failure groups are:

- `tests/test_clinical_decision.py` — guideline, stewardship, fusion, explainability, and orchestrator behavior.
- `tests/test_plugin_integration.py` — SOAR plugin manager/runtime behavior.
- `tests/test_who_knowledge_plugin.py` — mocked repository search/query behavior.

These failures were not repaired because this task prohibits changing application behavior. They are not import-resolution failures.

### Backend-local suite

```text
cd apps/api
python -m pytest -q
```

The same 186 tests collect from the backend-local directory after the local `pythonpath` correction. Execution reaches the same 20 behavioral failures; no collection/import failure remains.

### Focused backend contract

```text
python -m pytest tests/test_phase6_api_integration.py -q
```

Result: **PASS — 16 passed**.

### Frontend regression after repair

- `npm run lint` — **PASS**.
- `npm test` — **PASS**, 116 assertions.
- `npm run build` — **PASS**, with the existing large-chunk warning only.

### Runtime OpenAPI regression

The application remains importable with the configured backend path and the canonical route remains:

```text
POST /api/v1/recommendations/generate
```

The test-infrastructure repair added no routes and did not add authentication, registration, admin mutation, clinical-review, telemetry, plugin-registry, model-registry, standalone SOAR, or standalone ARMD endpoints.

### Final validation matrix

| Validation | Result |
|---|---|
| Frontend lint | PASS |
| Frontend tests | PASS — 116 assertions |
| Frontend build | PASS |
| Backend focused contract tests | PASS — 16 passed |
| Backend full collection from repository root | PASS — 186 collected, 0 collection errors |
| Backend full suite from repository root | FAIL — 166 passed, 20 behavioral failures |
| Backend-local collection | PASS — 186 collected, 0 collection errors |
| Runtime OpenAPI | PASS — route surface unchanged |
| Forbidden endpoint audit | PASS — no speculative endpoints added |
| Mock/fabrication audit | PASS — no changes introduced |

### Status

**PHASE 15D — INTEGRATION VERIFIED WITH BACKEND TEST BLOCKER**

The Phase 15D.1 infrastructure objective is complete: the full backend suite now collects and executes deterministically from both repository root and `apps/api`. The remaining blocker is the 20 genuine behavioral test failures, which require a separate backend behavior/test-contract investigation and were intentionally not changed in this infrastructure-only task.

Authentication, registration, hospital onboarding, user provisioning, RBAC backend implementation, and Supabase remain deferred to **Phase 16**.
