# Phase 6 Backend Truth Verification

## Scope

This document is a strict backend-only verification of the Phase 6 explainability and recommendation claims. It intentionally does not treat frontend TypeScript interfaces as proof of backend existence.

The source-of-truth evidence is the real repository implementation under:

- [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py)
- [apps/api/app/clinical_decision/orchestrator.py](../../apps/api/app/clinical_decision/orchestrator.py)
- [apps/api/app/clinical_decision/explainability.py](../../apps/api/app/clinical_decision/explainability.py)
- [apps/api/app/clinical_decision/contracts.py](../../apps/api/app/clinical_decision/contracts.py)
- [apps/api/tests/test_phase6_api_integration.py](../../apps/api/tests/test_phase6_api_integration.py)

## Verification Standard

A field or route is considered backend-verified only if it appears in:

1. an actual FastAPI route or request/response model,
2. a production decision model or contract,
3. a live backend test that exercises the behavior, or
4. the real runtime orchestration path.

If none of the above exists, it is classified as not implemented or frontend-only.

---

## Executive Summary

### Confirmed backend reality

The real recommendation API exposes a canonical response contract at:

- `POST /api/v1/recommendations/generate`

The contract includes these backend fields:

- `status`
- `patient_id`
- `recommendation`
- `confidence`
- `evidence_ranking`
- `evidence_attribution`
- `recommendation_trace`
- `audit_reference`
- `explanation`
- `generated_at`
- `trace_id`

These are defined in [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py) and validated in [apps/api/tests/test_phase6_api_integration.py](../../apps/api/tests/test_phase6_api_integration.py).

### Important architectural point

The orchestrator deliberately does not generate the Phase 6.1 explainability enhancement fields. That work is performed by the recommendation API layer after the orchestrator returns the core recommendation and audit objects.

This is explicitly documented in [apps/api/app/clinical_decision/orchestrator.py](../../apps/api/app/clinical_decision/orchestrator.py): the response includes only the core recommendation, explanation, and audit trail, and the API assembles the explainability-enhancement objects.

### Not found in the backend

No accept or override recommendation endpoints were found in the actual `apps/api/app/api` router tree. Search results across the backend API files showed no route registration for accept/override recommendation workflows.

---

## 1) Actual backend contract: what exists

### Recommendation API route

The actual route is implemented in [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py).

Relevant facts:

- router prefix: `/recommendations`
- endpoint: `POST /generate`
- response model: `ExplainabilityResponseContract`
- validation: `validate_explainability_response()`
- response fields are required before returning from the API

The canonical response contract explicitly requires:

- `recommendation`
- `confidence`
- `evidence_ranking`
- `recommendation_trace`
- `audit_reference`

This is not inferred from the frontend; it is defined in the API layer itself.

### Core recommendation and explanation objects

The real backend domain models are in [apps/api/app/clinical_decision/contracts.py](../../apps/api/app/clinical_decision/contracts.py).

Confirmed model structures include:

- `ClinicalRuleResult`
- `GuidelineReference`
- `StewardshipFinding`
- `RecommendedAntibiotic`
- `RecommendationResult`
- `ExplainabilityDriver`
- `RecommendationExplanation`
- `AuditTrail`

These models define the real backend vocabulary, not frontend TypeScript types.

### Explainability enhancement methods

The enhancement methods are implemented in [apps/api/app/clinical_decision/explainability.py](../../apps/api/app/clinical_decision/explainability.py):

- `generate_evidence_ranking()`
- `generate_recommendation_trace()`
- `generate_evidence_attribution()`

These methods accept optional `recommendation` data and `patient_id`, which is specifically designed for API-layer composition.

This is the critical evidence that the API, not the orchestrator, creates the enhancement payloads.

---

## 2) Field-by-field classification

### A. Confirmed backend fields

These are directly present in the real backend contract or models.

- `recommendation` — confirmed in `ExplainabilityResponseContract` and `RecommendationResult`
- `confidence` — confirmed as a string enum in `RecommendationConfidence`, and as a top-level API field
- `evidence_ranking` — confirmed in `ExplainabilityResponseContract` and `generate_evidence_ranking()`
- `evidence_attribution` — confirmed in `ExplainabilityResponseContract` and `generate_evidence_attribution()`
- `recommendation_trace` — confirmed in `ExplainabilityResponseContract` and `generate_recommendation_trace()`
- `audit_reference` — confirmed in `ExplainabilityResponseContract`
- `explanation` — confirmed as optional API payload and `RecommendationExplanation` model
- `generated_at` — confirmed in response models and audit objects
- `trace_id` — confirmed in response and `AuditTrail`
- `patient_id` — confirmed across response and models
- `prediction_plugin_version` — confirmed as API request value and `AuditTrail.prediction_plugin_version`
- `model_versions` — confirmed as request dict and `AuditTrail.model_versions`
- `rule_versions` — confirmed in the `AuditTrail` model, but not as a top-level API response field
- `affected_drugs` — confirmed in `ClinicalRuleResult` model and used in rule evaluation logic
- `prediction_explanation` / SHAP usage — confirmed in `RecommendationExplanation` and the prediction request payload; raw SHAP is not the final top-level response contract

### B. Backend exists but is not a top-level response field

This is the most important category for frontend/backend contract mismatches.

- `affected_drugs` exists in the backend model, but it is part of `ClinicalRuleResult` metadata, not a top-level recommendation response field.
- `rule_versions` exists in the backend `AuditTrail` model, but it is not part of the canonical `ExplainabilityResponseContract` returned by `/api/v1/recommendations/generate`.
- `prediction_explanation` exists as part of the explanation object and request payload, but not as a separate top-level field in the final API response contract.
- `spectrum` exists as a stewardship metadata value (`metadata={"antibiotic": antibiotic, "spectrum": "broad"}`) in the stewardship logic, but not as a dedicated top-level API field.

### C. Frontend-only or not implemented in backend

These items are not found in the actual backend code or route model.

- `costTier` — not found in the backend API, contracts, or tests
- `adjustment_notes` — not found in backend contract or model search
- `confidence.explanation` — not found; the backend defines `confidence` as a string enum, not a nested object
- `monitoringPlan` — not found in backend route/model implementation
- `warning.ruleSource` — not found in backend model naming or schema
- `accept` recommendation endpoint — not found in API routes
- `override` recommendation endpoint — not found in API routes

### D. Uncertain / speculative items

These are not confirmed as a backend response field unless specifically attached to an internal model or a nested object that is part of a documented backend payload:

- `spectrum` — present only as metadata in stewardship logic; not a top-level response field
- `model_versions` — confirmed at API input and audit model, but not necessarily a top-level recommendation payload field unless included in `audit_reference` in the assembled API response
- `rulesSource`-style provenance fields — not found in the canonical API contract; any such field would be a custom frontend extension, not a backend contract guarantee

---

## 3) Accept / override endpoints: backend truth

A strict search across the backend API files found no actual implementation of recommendation accept/override routes.

### Evidence

The only relevant API route modules are:

- [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py)
- [apps/api/app/api/v1/decision.py](../../apps/api/app/api/v1/decision.py)
- [apps/api/app/api/v1/explainability.py](../../apps/api/app/api/v1/explainability.py)
- [apps/api/app/api/router.py](../../apps/api/app/api/router.py)

These files show:

- recommendations router exposes status and generate endpoint
- decision router is a placeholder service status endpoint
- explainability router is a placeholder service status endpoint
- no `accept` or `override` route registration exists

### Conclusion

There is no backend-verified accept/override recommendation API in the current repository state.

Any frontend workflow that assumes these endpoints exist is making a frontend-only assumption unless additional backend code is added.

---

## 4) Backend validation status

### Source validation

The repository contains real backend validation for the core response contract in [apps/api/tests/test_phase6_api_integration.py](../../apps/api/tests/test_phase6_api_integration.py).

The tests check:

- recommendation response includes `confidence`
- evidence ranking is present and shaped correctly
- recommendation trace is present and shaped correctly
- evidence attribution is present
- audit reference is complete
- IDs are consistent across the response
- patient IDs are consistent across response
- generated timestamps are present
- multiple predictions are handled

### Runtime execution note

I attempted to run the direct backend validation command in the workspace environment:

- `pytest tests/test_phase6_api_integration.py -q`

The command failed because `pytest` is not available in this execution environment (`CommandNotFoundException`). That means the repo has the test file, but this environment cannot execute it. The verdict therefore rests on the actual source-code evidence in the repository, not on a successful local pytest run in this session.

---

## 5) Final classification

### Confirmed backend truth

- recommendation generation API exists
- explainability response contract exists
- evidence_ranking exists
- recommendation_trace exists
- evidence_attribution exists
- audit_reference exists
- model and rule metadata exist in domain contracts
- orchestrator is decoupled from enhancement generation

### Not confirmed backend truth

- accept/override recommendation endpoints
- nested `confidence.explanation` objects
- `costTier`
- `monitoringPlan`
- `warning.ruleSource`
- `adjustment_notes`
- any frontend-only recommendation envelope not defined by the real API contract

### Practical conclusion

The backend truth is narrower and cleaner than many frontend assumptions. The canonical backend response is the recommendation API contract in [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py), and all claims must be validated against that contract and the real service models in [apps/api/app/clinical_decision/contracts.py](../../apps/api/app/clinical_decision/contracts.py). Anything beyond that is not proven backend behavior without a corresponding backend implementation or test.
