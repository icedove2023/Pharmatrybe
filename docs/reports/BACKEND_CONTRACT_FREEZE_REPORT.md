# Backend Contract Freeze Report

## 1. Contracts frozen

The following public/backend boundaries are frozen at version `1.0.0`:

- Plugin runtime contract, with plugin-specific schemas and explicit adapter boundaries.
- SOAR deployment selection contract.
- SOAR upstream ownership contract.
- Clinical adaptation boundary.
- Canonical backend request contract.
- Canonical recommendation response at `/api/v1/recommendations/generate`.
- Canonical explainability response nested in the recommendation response.
- Public `ApiFailure`/`ApiError` envelope and typed error-code mapping.
- ARMD WP4 runtime boundary.
- WHO knowledge-query boundary.

The master index is [BACKEND_CONTRACT_MANIFEST_v1.0.0.md](../contracts/BACKEND_CONTRACT_MANIFEST_v1.0.0.md).

## 2. Contracts not frozen

No additional public contract is left in a draft state for the documented boundaries. Clinical terminology mappings remain intentionally unsupported/deferred:

- `organism` / `pathogen` / `species` are distinct.
- `infection_site` / `BodyLocation_Group` are distinct.
- `antimicrobial` / `antibiotic` are distinct outside plugin metadata.
- SOAR raw feature provenance is explicit caller/platform input, not claimed clinician or laboratory ownership.

These are excluded from the canonical adapter contract and therefore do not require frontend inference.

## 3. Explicit architectural decisions

The decisions are recorded in [BACKEND_CONTRACT_DECISION_REGISTER.md](../contracts/BACKEND_CONTRACT_DECISION_REGISTER.md).

- SOAR deployment selection is explicit caller/platform ownership.
- The SOAR plugin performs exact registry lookup only.
- The canonical request carries `request_id` and `routing_context`.
- Plugin adapters validate boundaries without semantic guessing.
- `/api/v1/recommendations/generate` is the canonical recommendation/explainability endpoint.
- Global FastAPI handlers emit `ApiFailure`; typed exception names map to stable public codes.
- Legacy routes remain compatibility paths and do not define the canonical frontend contract.

## 4. SOAR routing ownership

The producer is the approved caller/platform routing boundary. It supplies:

```json
{
  "routing_context": {
    "deployment_id": "Ceftriaxone_Haemophilus_influenzae"
  }
}
```

The adapter validates the non-empty string, preserves only the routing key into `PredictionRequest.context`, and the plugin resolves it exactly through `DeploymentRegistry`. Missing, unknown, or invalid IDs fail. No organism-only, antimicrobial-only, filename, approximate, or first-deployment fallback exists.

## 5. Raw SOAR input ownership

`Age`, `YearCollected`, `Region`, `BodyLocation_Group`, `Country`, and variant-specific `Beta_Lactamase_enc` are explicit caller/platform inputs at the plugin-specific boundary. The repository does not establish a clinical or laboratory producer for them. Artifact preprocessing remains the model runtime’s responsibility. Missing required features reject execution.

No clinical mappings were invented.

## 6. Canonical clinical adapter boundary

The canonical request passes through explicit plugin adapters:

```text
Canonical Clinical Request
    -> Plugin Input Adapter
    -> Plugin-Specific Request
    -> Plugin Runtime
```

The adapter validates request shape and SOAR routing context. It does not map infection site, organism, pathogen, species, age groups, laboratory fields, or demographic aliases by similarity. Full boundary details are in [CLINICAL_ADAPTATION_BOUNDARY_v1.0.0.md](../contracts/CLINICAL_ADAPTATION_BOUNDARY_v1.0.0.md).

## 7. Public request contract

`POST /api/v1/pipeline/execute` is the canonical pipeline request boundary. It accepts:

- `request_id`;
- `patient_id`;
- `case_id`;
- `input_payload`;
- `routing_context`;
- `plugin_selection`;
- `execution_mode` (`sync` only);
- `response_mode`.

The route preserves payload, combines routing context with case context, and propagates it through `ClinicalDecisionRequest` and `WorkflowManager`.

## 8. Public recommendation contract

`POST /api/v1/recommendations/generate` returns `ExplainabilityResponseContract`, including recommendation, confidence, evidence ranking, evidence attribution, recommendation trace, audit reference, explanation, generated timestamp, and trace ID. Candidate antibiotics originate from prediction results; absent evidence does not create a recommendation.

## 9. Public explainability contract

The canonical response contains prediction, rule, guideline, stewardship, evidence-driver, warning, narrative, trace, and audit structures. Plugin-specific SHAP/model data remains nested and is not promoted to unsupported clinical semantics. Missing optional explanation data is represented explicitly.

## 10. Public error contract

Public FastAPI failures use `ApiFailure`/`ApiError` with request metadata, stable code, safe message, and optional details. Internal typed exceptions are preserved and mapped through the explicit registry:

- `DeploymentSelectionError` -> `SOAR_DEPLOYMENT_SELECTION_ERROR`;
- `PredictionError` -> `PREDICTION_EXECUTION_ERROR`;
- `AdapterValidationError` -> `PLUGIN_INPUT_VALIDATION_ERROR`;
- `WHOServiceError` -> `KNOWLEDGE_SERVICE_ERROR`.

Stack traces are not exposed.

## 11. Compatibility paths

Existing legacy recommendation, clinical-decision, plugin, WHO, ARMD, and direct plugin callers remain available where covered by the current suite. They are compatibility paths, not the canonical frontend boundary. SOAR callers must now provide explicit routing context; legacy implicit fallback is intentionally not compatible.

## 12. Tests added

- Canonical pipeline request and routing-context validation.
- SOAR adapter missing-ID rejection.
- SOAR adapter payload/context preservation.
- Typed public error-code mapping.
- Contract artifact presence.
- Updated orchestration test for explicit SOAR context.

## 13. Full regression result

Final verification commands:

```text
.\.venv\Scripts\python.exe -m pytest apps/api/tests -ra
281 passed, 7 warnings

.\.venv\Scripts\python.exe -m compileall -q apps/api/app apps/api/tests
exit code 0

git diff --check
exit code 0
```

Focused closure verification:

```text
.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_backend_contract_closure.py apps/api/tests/test_plugin_orchestration.py apps/api/tests/test_soar_deployment_contract.py -q
17 passed
```

Warnings are existing Pydantic, SHAP, and datetime/model-serialization deprecations. No test failures remain.

## 14. Frontend impact

No frontend code was modified. Frontend consumers may reconcile against the canonical request, recommendation, explainability, error, and plugin-specific contracts. They must not infer SOAR deployment IDs or unresolved clinical mappings.

## 15. Final transition decision

```text
FRONTEND_RECONCILIATION_AUTHORIZED
```
