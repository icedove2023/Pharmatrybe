# Prediction Call Path Verification

## Objective

Verify the call path for each prediction plugin is identical before and after inheritance refactoring.

## SOAR Call Path

```mermaid
sequenceDiagram
    participant Platform
    participant Plugin as SOARPredictionPlugin
    participant Engine as PredictionEngine
    participant Loader as ModelLoader
    participant Registry as DeploymentRegistry
    participant Explain as ExplainabilityAdapter
    participant SOAR as SOAR artifacts/models
    participant Response

    Platform->>Plugin: PredictionRequest
    Plugin->>Plugin: supports(request)
    Plugin->>Registry: get deployment candidates
    Plugin->>Loader: load deployment model if needed
    Loader->>SOAR: read model + encoder + threshold
    Plugin->>Engine: predict(loaded_model, request)
    Engine->>Engine: validate request
    Engine->>Engine: preprocess payload
    Engine->>SOAR: model.predict / predict_proba
    Engine->>Engine: apply threshold / decode class
    Engine-->>Plugin: PredictionExecution
    Plugin->>Explain: explain(execution)
    Explain->>SOAR: compute SHAP values
    Explain-->>Plugin: PredictionResult
    Plugin-->>Response: PredictionResult
```

### SOAR verification outcome

- request validation still occurs in the plugin and engine
- deployment loading still occurs via registry and model loader
- inference still flows through the same engine method
- explanation still flows through the same SHAP adapter method
- final response remains `PredictionResult`

## ARMD Call Path

```mermaid
sequenceDiagram
    participant Platform
    participant Plugin as ARMDPredictionPlugin
    participant Runtime as ARMDRuntimeContext
    participant Engine as ARMDPredictionEngine
    participant Adapter as ARMDAdapter
    participant WP4 as WP4_Decision_Engine
    participant Response

    Platform->>Plugin: PredictionRequest
    Plugin->>Runtime: validate()
    Plugin->>Engine: predict(request)
    Engine->>Runtime: validate adapter readiness
    Engine->>Adapter: predict_all_antibiotics(patient_data)
    Adapter->>WP4: load registry / preprocessing / inference
    WP4-->>Adapter: prediction outputs
    Adapter-->>Engine: execution results
    Engine-->>Plugin: plugin response
    Plugin-->>Response: result payload
```

### ARMD verification outcome

- runtime readiness gate remains enforced
- adapter call sequence remains the same
- inference still occurs through the WP4-backed adapter path
- response mapping remains consistent with the engine output contract

## Final Call-Path Verdict

The call paths for both plugins remain functionally identical to their pre-inheritance structure. The inheritance refactor has not changed the sequence of operations that produces prediction output.
