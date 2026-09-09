# Runtime Call Graph

## Objective

Capture the runtime dependency graph used by both prediction plugins and confirm that the lifecycle contract remains unchanged.

## SOAR runtime graph

```mermaid
graph TD
    A[Platform] --> B[SOARPredictionPlugin]
    B --> C[SOARRuntimeContext]
    C --> D[DeploymentRegistry]
    C --> E[ModelLoader]
    C --> F[PredictionEngine]
    C --> G[ExplainabilityAdapter]
    E --> H[SOAR model artifacts]
    F --> I[SOAR model inference]
    G --> J[SHAP explanation]
    I --> K[PredictionExecution]
    J --> L[PredictionResult]
    K --> L
    L --> M[Platform Response]
```

## ARMD runtime graph

```mermaid
graph TD
    A[Platform] --> B[ARMDPredictionPlugin]
    B --> C[ARMDRuntimeContext]
    C --> D[ARMDAdapter]
    D --> E[WP4_Decision_Engine]
    D --> F[Preprocessing artifacts]
    E --> G[Prediction outputs]
    G --> H[ARMDPredictionEngine]
    H --> I[Plugin response]
    I --> J[Platform Response]
```

## Lifecycle check

### SOAR lifecycle

Platform -> Plugin.initialize -> runtime_context.initialize -> registry initialize -> model-ready state -> plugin.validate -> prediction -> shutdown

### ARMD lifecycle

Platform -> Plugin.initialize -> runtime_context.initialize -> adapter.initialize -> registry/artifacts readiness -> plugin.validate -> prediction -> shutdown

## Runtime integrity conclusion

The parent class refactor changes class inheritance only; the actual runtime dependency graph remains functionally identical and therefore preserves behaviour.

## Final Runtime Certification

Behaviour preserved.
