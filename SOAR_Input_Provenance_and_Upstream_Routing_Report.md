# SOAR Input Provenance and Upstream Routing Report

## Scope and Evidence Boundary

This audit is restricted to the SOAR backend slice. It covers the backend API pipeline entrypoint, workflow orchestration, the generic `PredictionRequest` boundary, SOAR deployment selection, and the artifact feature validation path. No frontend, ARMD, WHO, model artifact, feature schema, encoder, preprocessing, or deployment artifact files were modified.

Evidence reviewed:

- `apps/api/app/api/v1/pipeline.py`
- `apps/api/app/plugins/manager/workflow_manager.py`
- `apps/api/app/plugins/base/prediction_plugin.py`
- `apps/api/app/plugins/prediction/soar/soar_prediction_plugin.py`
- `apps/api/app/plugins/prediction/soar/prediction_engine.py`
- `apps/api/tests/test_soar_deployment_contract.py`
- `apps/api/tests/test_plugin_orchestration.py`

## 1. `deployment_id` Provenance

### Confirmed runtime owner

`SOARPredictionPlugin` owns deployment selection at runtime. It reads `request.context["deployment_id"]` and performs an exact `DeploymentRegistry.get_by_id()` lookup. The registry obtains valid IDs from artifact-backed deployment metadata. It does not derive an ID from organism, antimicrobial, pathogen, filenames, or other payload values.

### Upstream producer result

No clinical inference producer was found in the backend. The closure decision is explicit caller/platform ownership: the canonical request supplies `routing_context.deployment_id`, and the SOAR adapter validates it before plugin execution.

The actual pipeline API accepts `PipelineExecutionRequest.input_payload`, extracts the case payload, and creates `ClinicalDecisionRequest`. Its context is constructed only as `{ "case_id": request.case_id }` when a case ID is present. There is no `deployment_id` field in `PipelineExecutionRequest`, and the route does not add one. Therefore the exposed pipeline route cannot provide SOAR's required deployment selector.

`WorkflowManager` constructs `PredictionRequest(payload=request.payload, context=request.context)` by pass-through. It can preserve a caller-provided deployment ID, but it cannot create one. No API, request builder, orchestration component, or plugin invocation path was found that derives or supplies a SOAR deployment ID upstream.

Classification: **EXPLICIT_CALLER_INPUT** for the canonical routing boundary; **PLUGIN_SPECIFIC** for exact runtime selection; exact propagation is **CONFIRMED** when a caller supplies the context value.

### Selection behavior

- Explicit known ID: exact deployment selected.
- Missing ID: `DeploymentSelectionError`.
- Unknown ID: `DeploymentSelectionError`.
- Organism/antimicrobial inference: not used.
- First-deployment fallback: not used.

## 2. Raw SOAR Input Provenance

The selected artifacts require these raw fields. The audit found no backend producer that creates them before the generic `PredictionRequest` boundary. The pipeline route passes `input_payload` through as the request payload, without SOAR-specific transformation.

| Raw field | Actual backend evidence | Classification | Decision |
| --- | --- | --- | --- |
| `Age` | May be present only if supplied in `input_payload`; no SOAR API or orchestration producer found. | **NO_UPSTREAM_SOURCE** | No clinician, patient, laboratory, or platform ownership can be confirmed. |
| `YearCollected` | May be present only if supplied in `input_payload`; no producer found. | **NO_UPSTREAM_SOURCE** | Dataset/model-context use is evidenced by the artifact contract, but no request-time owner is established. |
| `Region` | May be present only if supplied in `input_payload`; no producer or transform found. | **NO_UPSTREAM_SOURCE** | No provenance or upstream transformation is confirmed. |
| `BodyLocation_Group` | May be present only if supplied in `input_payload`; no deterministic mapping from `infection_site` found. | **NO_UPSTREAM_SOURCE** / **UNRESOLVED** | Do not equate it with canonical infection site. |
| `Country` | May be present only if supplied in `input_payload`; no producer or transform found. | **NO_UPSTREAM_SOURCE** | Artifact target encoding is runtime/model behavior, not evidence of field ownership. |
| `Beta_Lactamase_enc` | Required only by applicable beta-lactamase deployments; no backend laboratory producer or deterministic transform found. | **NO_UPSTREAM_SOURCE** / **PLUGIN_SPECIFIC** | Deployment-specific artifact input; no generic clinical source is established. |

The artifact and model metadata confirm that these names are runtime features. They do not establish whether values are clinician-entered, patient/context-derived, laboratory-derived, platform/configuration-derived, dataset/model-context-only, or transformed upstream. No such ownership is invented here.

## 3. Actual End-to-End Request Flow

1. `POST /pipeline/execute` receives `PipelineExecutionRequest` with `patient_id`, `plugin_selection`, and `input_payload`.
2. `_patient_payload()` unwraps `input_payload["case"]` when that value is a dictionary; otherwise it preserves `input_payload`.
3. The route creates `ClinicalDecisionRequest(payload=patient_data, context={"case_id": ...} or None, plugin_ids=...)`.
4. `ClinicalIntelligencePipeline.process()` calls `WorkflowManager.execute()`.
5. `WorkflowManager._execute_plugin()` creates `PredictionRequest(payload=request.payload, context=request.context)` without copying, deriving, or transforming SOAR values.
6. `SOARPredictionPlugin.supports()` requires a non-empty dictionary payload and a string `context.deployment_id`.
7. `SOARPredictionPlugin.predict()` resolves that exact ID through `DeploymentRegistry`, loads the matching artifact, and calls `PredictionEngine.predict()`.
8. `PredictionEngine._validate_request()` rejects an empty/non-dictionary payload. `_preprocess()` rejects missing model-declared feature names when `feature_names_in_` is available; otherwise it uses the model's declared feature count or sorted payload keys.
9. Model execution and result explanation occur only after routing and feature validation succeed.

### Created, transformed, and lost values

- `patient_id`: created at the API request boundary and copied into `ClinicalDecisionRequest`; it is not a SOAR model feature.
- `input_payload`: unwrapped at the API boundary and then passed unchanged as `ClinicalDecisionRequest.payload`.
- `case_id`: converted into `ClinicalDecisionRequest.context["case_id"]` only.
- `deployment_id`: never created by the API route or workflow manager; it is lost as an upstream capability because the route has no request field for it. A caller that constructs `ClinicalDecisionRequest` directly can provide it in `context`, and the manager preserves it exactly.
- The six raw fields: never created or transformed by the observed backend path; they survive only when already present in `input_payload`.

## 4. Confirmed Wiring Corrections

No production wiring correction was justified by the evidence. The existing workflow boundary already propagates caller-provided payload and context exactly. Adding deployment-ID derivation or raw-field construction would be speculative and would violate the unresolved provenance boundary.

A focused test was added to `apps/api/tests/test_plugin_orchestration.py` proving that all six representative raw fields and an explicit deployment ID reach the plugin's `PredictionRequest` unchanged. A second focused test proves the manager leaves missing deployment context missing rather than synthesizing it.

## 5. Unresolved and No-Source Findings

- No confirmed upstream producer supplies `context.deployment_id` to the exposed SOAR pipeline route.
- No clinical, laboratory, or patient-domain producer supplies any of the six raw artifact fields. Their public ownership is explicitly caller/platform input at the plugin-specific boundary; no values are fabricated.
- No clinician-entered ownership is established.
- No patient/context-derived ownership is established.
- No laboratory-derived producer is established for `Beta_Lactamase_enc`.
- No platform/configuration-derived producer is established.
- `YearCollected`, `Region`, `Country`, and the other artifact fields may be dataset/model-context fields, but the repository does not prove their request-time provenance.
- No deterministic `infection_site` to `BodyLocation_Group` mapping exists.
- No equivalence among `organism`, `pathogen`, and `species` is established.
- No frontend reconciliation or deployment selector work is authorized by this report.

## 6. Tests Executed

Focused orchestration provenance tests:

```text
.\\.venv\\Scripts\\python.exe -m pytest apps/api/tests/test_plugin_orchestration.py -q
4 passed
```

Existing focused SOAR deployment contract tests:

```text
.\\.venv\\Scripts\\python.exe -m pytest apps/api/tests/test_soar_deployment_contract.py -q
7 passed
```

Existing plugin input schema contract tests:

```text
.\\.venv\\Scripts\\python.exe -m pytest apps/api/tests/test_plugin_input_schema_contract.py -q
9 passed
```

The focused tests cover exact context propagation, exact raw-payload propagation, missing deployment context, unknown deployment rejection, and missing artifact-feature rejection. The test runs completed with existing Pydantic deprecation/config warnings only; no test failures were reported.

## 7. Final Decisions

```text
SOAR Deployment ID Upstream Source = EXPLICIT CALLER/PLATFORM CONTEXT
SOAR Raw Input Provenance = EXPLICIT INPUT OWNERSHIP, CLINICAL PROVENANCE DEFERRED
SOAR Deployment Contract Frozen = YES
Frontend Contract Ready = YES FOR THE DOCUMENTED EXPLICIT CONTRACT
```

The SOAR contract remains runtime-accurate for explicit deployment selection and artifact feature validation, but it is not frozen. The next required dependency is an approved upstream owner and producer for deployment selection and each raw artifact input. No frontend reconciliation begins.
