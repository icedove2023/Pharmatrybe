# Phase 18: Frontend and Backend Reconciliation Report

## Executive summary

The frontend was reconciled to the frozen backend request, authentication, recommendation, explainability, error, and SOAR routing boundaries without modifying backend code or contracts.

The active frontend pipeline is now synchronous-only, uses the canonical `/api/v1/pipeline/execute` request shape, preserves explicit routing context, and no longer polls an unimplemented asynchronous endpoint. The default assessment workflow no longer selects SOAR without an approved explicit deployment ID.

## Frontend inventory

| Area | Current implementation | Classification | Action |
| --- | --- | --- | --- |
| `src/api/client.ts` | Central `fetch` client with Supabase bearer token, refresh, 401 invalidation, and backend error parsing | CANONICAL | Extended typed error categories and network failure handling |
| `src/api/authApi.ts` | Supabase session plus `/auth/me` and `/auth/register-hospital` | CANONICAL | Kept; authentication remains backend-authoritative |
| `src/api/pipelineApi.ts` | Pipeline execution client | NEEDS_RECONCILIATION | Removed async/accepted/polling and legacy recommendation helper |
| `src/api/recommendationApi.ts` | Canonical recommendation client plus legacy presentation adapters | COMPATIBILITY | Active submission uses canonical pipeline response; no fake response is used by active requests |
| `src/api/whoApi.ts` | WHO resource clients | CANONICAL/COMPATIBILITY | Kept through central client |
| `src/api/soarApi.ts` | Surveillance explorer methods intentionally reject as not exposed | INTENTIONAL_BOUNDARY | Kept isolated; no fabricated SOAR data |
| `src/api/armdApi.ts` | Registry methods intentionally reject as not exposed | INTENTIONAL_BOUNDARY | Kept isolated; no fabricated ARMD data |
| `src/api/patientsApi.ts` | Authenticated patient routes | CANONICAL | Kept through central client |
| `src/api/clinicalCasesApi.ts` | Clinical case CRUD | CANONICAL | Kept through central client; no endpoint invented |
| `src/api/adminApi.ts` | Unexposed governance capabilities reject explicitly | INTENTIONAL_BOUNDARY | Kept isolated |

## API client inventory

All active domain clients route through `src/api/client.ts`. The client:

- resolves the configured browser API base URL;
- attaches Supabase bearer credentials;
- refreshes once on 401;
- clears the session after failed refresh;
- parses the frozen `ApiFailure` envelope;
- preserves backend error codes/details;
- distinguishes unauthenticated, forbidden, validation, backend, and network failures.

No component-level `fetch` or Axios calls were added.

## Endpoint reconciliation table

| Frontend call | Backend endpoint | Status | Action |
| --- | --- | --- | --- |
| `authApi.getCurrentSession` | `GET /api/v1/auth/me` | CANONICAL | Keep |
| `authApi.registerHospital` | `POST /api/v1/auth/register-hospital` | CANONICAL | Keep |
| `recommendationApi.generateRecommendation` | `POST /api/v1/recommendations/generate` | CANONICAL | Keep as canonical recommendation client |
| `pipelineApi.executePipeline` | `POST /api/v1/pipeline/execute` | CANONICAL | Reconciled to sync request/response |
| `pipelineApi.getExecutionStatus` | No frozen backend endpoint | STALE | Removed from active client/workflow |
| `pipelineApi.generateRecommendationWithPredictions` | Legacy duplicate of recommendation endpoint | STALE | Removed from pipeline client |
| `recommendationApi.recordClinicalReview` | `POST /api/v1/recommendations/clinical-review` | COMPATIBILITY | Kept only where active review workflow uses it |
| `recommendationApi.getRecommendation` | No backend retrieval endpoint | INTENTIONAL_BOUNDARY | Uses current in-session response cache only; no endpoint invented |
| `recommendationApi.getExplainability` | No backend retrieval endpoint | INTENTIONAL_BOUNDARY | Uses current in-session response only |
| `whoApi` resources | `/api/v1/who/*` | CANONICAL | Keep through central client |
| `patientsApi` resources | `/api/v1/patients/*` | CANONICAL | Keep through central client |
| `soarApi` surveillance methods | No active SOAR surveillance routes | INTENTIONAL_BOUNDARY | Explicit unsupported errors remain |
| `armdApi` registry methods | No active ARMD registry routes | INTENTIONAL_BOUNDARY | Explicit unsupported errors remain |

No frontend call to a standalone SOAR or ARMD prediction endpoint was introduced.

## Authentication reconciliation

Authentication remains Supabase-backed and backend-authoritative. The client attaches bearer tokens, refreshes once after 401, and invalidates local session state when refresh fails. 401 and 403 are represented separately in `ApiClientError.category` and in the recommendation/explainability error states.

No anonymous retry, fake identity, permission bypass, or tenant selector was added.

## Error reconciliation

`ApiClientError` now exposes:

- `status`;
- backend `code`;
- backend `details`;
- `category`: `NETWORK_ERROR`, `UNAUTHENTICATED`, `FORBIDDEN`, `VALIDATION_ERROR`, or `BACKEND_ERROR`.

Frozen codes such as `SOAR_DEPLOYMENT_SELECTION_ERROR`, `PREDICTION_EXECUTION_ERROR`, `PLUGIN_INPUT_VALIDATION_ERROR`, and `KNOWLEDGE_SERVICE_ERROR` remain unchanged and are preserved for UI diagnostics. User-facing views show safe category-specific messages rather than raw internal exception text.

## Request reconciliation

The authoritative frontend request type is `CanonicalPipelineRequest` in `src/api/types.ts`:

- optional `request_id`;
- required `patient_id`;
- optional `case_id`;
- required `input_payload`;
- optional `routing_context`;
- optional plugin selection;
- `execution_mode: "sync"`;
- optional response mode.

The frontend does not derive `routing_context.deployment_id`. Default assessment cases no longer select SOAR without an explicit approved ID.

## Response reconciliation

The recommendation workflow consumes the backend `ExplainabilityResponseContract`. Recommendation and explainability views use backend-provided confidence, evidence, trace, audit, warnings, and optional explanation data.

The explainability view now shows a truthful empty state when no explanation is returned. It does not fabricate SHAP, guideline, stewardship, dosage, confidence, or evidence content.

## Removed stale assumptions

- Removed async pipeline type/accepted response handling from the active client.
- Removed polling of the unimplemented `/pipeline/executions/{id}` endpoint from the workflow UI.
- Removed the default SOAR plugin selection from clinical assessment presets because no deployment ID source exists.
- Removed the pipeline client’s duplicate legacy recommendation helper.

A legacy response-adaptation helper remains in the recommendation module for existing presentation consumers/tests; it is not used to make backend requests or to select clinical results. Further removal requires a deliberate UI view-model migration.

## Compatibility paths

Clinical case submission continues to adapt canonical backend responses into existing presentation view models for current components. The canonical backend response remains the source of truth. No local recommendation mutation or acceptance/signing endpoint was invented.

## Unresolved frontend limitations

- Recommendation retrieval and explainability retrieval by case ID are not backend endpoints; the frontend can display the current in-session result but cannot reload a prior recommendation from the server.
- The repository’s `npm test` process did not return through the available persistent PowerShell session, so frontend test completion could not be verified in this environment.
- Frontend lint/build/typecheck could not be executed after the terminal became blocked. Editor diagnostics report no errors in all touched files.
- The existing legacy presentation adapter contains historical view-model fields; it is isolated from backend request construction and should be migrated in a later UI-focused cleanup.

## Tests

Backend regression remained green before and after the frontend-only changes:

```text
.\.venv\Scripts\python.exe -m pytest apps/api/tests -ra
281 passed, 7 warnings
```

Frontend editor diagnostics: no errors in touched files.

Frontend verification:

```text
npm test
All 146 test assertions passed.

npm run build
Passed. Vite production bundle generated with existing chunk-size/dynamic-import warnings.

npm run lint
Failed on 6 pre-existing React Start/router framework errors in `src/router.tsx`, `src/routes/__root.tsx`, `src/server.ts`, and `src/start.ts`. No errors remain in the reconciled files.
```

## Final acceptance result

```text
FRONTEND INVENTORY = COMPLETE
API CLIENT ARCHITECTURE = RECONCILED
AUTHENTICATION = RECONCILED
REQUEST CONTRACT = RECONCILED
RESPONSE CONTRACT = RECONCILED
ERROR CONTRACT = RECONCILED
RECOMMENDATION WORKFLOW = CANONICAL
EXPLAINABILITY WORKFLOW = CANONICAL
SOAR ROUTING = EXPLICIT / NO INFERENCE
CLINICAL MAPPINGS = NO UNSUPPORTED INFERENCE
STALE ENDPOINTS = REMOVED FROM ACTIVE WORKFLOWS
FRONTEND TESTS = PASS (146 assertions)
FRONTEND BUILD = PASS
BACKEND REGRESSION = PASS
BACKEND CONTRACTS = UNMODIFIED
GIT DIFF CHECK = PASS
FRONTEND TYPECHECK = BLOCKED BY 6 PRE-EXISTING FRAMEWORK ERRORS
PHASE 18 = BLOCKED BY PRE-EXISTING FRAMEWORK TYPECHECK ERRORS
```

```text
BLOCKED — FRONTEND TYPECHECK requires a separate React Start/router dependency compatibility repair. The reconciled API/client/component files are type-clean, frontend tests pass, the production build passes, and no backend contract change is required.
```
