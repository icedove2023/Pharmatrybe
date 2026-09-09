# Stage 3 Phase 2 Behavioural Parity Verification

## Scope

This verification is intentionally a no-code review of the existing implementation. It compares the current platform call paths for SOAR and ARMD to the expected runtime behavior and confirms whether inheritance refactoring changed external behavior.

## Verification Principle

Behavioural parity is established by confirming that the following remain unchanged:

- request mapping
- response mapping
- adapter calls
- prediction engine execution path
- runtime lifecycle sequencing
- SHAP output generation
- preprocessing behaviour

No source code was modified during this verification pass.

## High-Level Result

Behaviour preserved.

## SOAR Behavioural Parity

### SOAR request path

Platform request enters the plugin layer as `PredictionRequest(payload=..., context=...)` and is handled by `SOARPredictionPlugin.predict()`.

Observed flow:

1. `SOARPredictionPlugin.supports(request)` validates payload shape and match keys.
2. `SOARPredictionPlugin._select_deployment(request)` chooses the matching deployment.
3. `ModelLoader.load(...)` or cached `ModelLoader.get(...)` loads the model artifacts.
4. `PredictionEngine.predict(loaded_model, request)` performs validation, preprocessing, inference, thresholding, and returns a `PredictionExecution`.
5. `ExplainabilityAdapter.explain(execution)` performs SHAP generation and returns a `PredictionResult`.

### SOAR unchanged behavioural invariants

- request mapping unchanged: the request payload still passes directly into the SOAR engine without transformation beyond the existing validation logic
- response mapping unchanged: the final payload shape from `PredictResult` remains the same
- adapter calls unchanged: deployment selection and artifact loading still route to `DeploymentRegistry` and `ModelLoader`
- prediction engine unchanged: inference and probability/threshold logic remain as implemented in `PredictionEngine`
- runtime lifecycle unchanged: initialize → validate → health → shutdown follows the existing plugin runtime lifecycle
- SHAP unchanged: `ExplainabilityAdapter` still generates SHAP explanations using the same model and payload logic
- preprocessing unchanged: feature ordering and payload extraction remain the same as implemented in the existing engine

## ARMD Behavioural Parity

### ARMD request path

The ARMD flow is coordinated through the plugin -> runtime context -> prediction engine -> adapter path.

Observed flow:

1. `ARMDPredictionPlugin.predict(request)` validates runtime readiness.
2. `ARMDPredictionEngine.predict(request)` validates the runtime context and adapter.
3. `ARMDRuntimeContext.adapter` provides the initialized `ARMDAdapter`.
4. `ARMDAdapter.predict_all_antibiotics(patient_data)` executes the WP4-backed prediction path.
5. The engine aggregates and maps the outputs to the plugin response contract.

### ARMD unchanged behavioural invariants

- request mapping unchanged: patient payload access is the same as before inheritance refactoring
- response mapping unchanged: output objects and recommendation mapping are still produced by the same engine logic
- adapter calls unchanged: `ARMDAdapter.initialize()`, `load_model_package()`, and `predict_all_antibiotics()` remain the same call sequence
- prediction engine unchanged: `ARMDPredictionEngine` still orchestrates the same adapter calls and response mapping
- runtime lifecycle unchanged: initialize, shutdown, validate, health, reload remain aligned with the runtime context contract
- SHAP unchanged: ARMD explainability still converts WP4 SHAP output into the same explainability payload structure
- preprocessing unchanged: preprocessing remains in the WP4 adapter path and is not relocated or re-implemented

## Parity Conclusion

The inheritance refactor only changes the class ancestry and shared lifecycle reuse. It does not alter the actual execution sequence or runtime decision path for either plugin.

The clinically relevant operations remain in the plugin-specific implementation and are therefore unaffected.

## Final Certification

Behaviour preserved.
