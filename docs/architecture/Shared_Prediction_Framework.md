# Shared Prediction Framework — Proposal

## Objective
Propose a small, non-invasive shared prediction framework that extracts reusable concerns from SOAR and ARMD without changing existing implementations. The framework is architecture-only: no refactors or code moves are performed yet.

## Core Modules to Extract

### artifact_registry
Canonical artifact categories, scanner, and registry model.

### deployment_registry
Pluggable registry interface and on-disk/JSON implementations.

### model_loader / ModelPackage
Standardized ModelPackage contract, loaders for pkl/json/csv, caching semantics.

### prediction_core
Validation, feature alignment contract, inference invocation, probability extraction, threshold application, execution metadata.

### explainability
Normalized explainability API returning contributions, drivers, figures, and optional narrative hooks.

### runtime_context
Lightweight dependency container for plugin runtimes, with health, init/reload/shutdown.

### contracts
`PredictionRequest`, `PredictionResult`, `LoadedModel` / `ModelPackage` dataclasses, and JSON schemas for API-level interoperability.

## Design Principles

- **Non-invasive**: provide adapters so existing ARMD WP4/WP5 and SOAR code can use framework without immediate moves.
- **Backwards-compatible**: preserve existing file formats (WP4 registry JSON, WP3 artifacts) via adapter layers.
- **Small surface area**: clear, minimal interfaces for loader, inference, and explainability.
- **Testable**: include unit tests to validate adapters against existing ARMD loader and SOAR model_loader behavior.

## API Sketch (conceptual)

### ModelPackage
- fields: id, model, scaler, threshold, feature_names, artifacts, metadata

### ModelLoader (interface)
- load(deployment_info) -> ModelPackage
- get(id) -> Optional[ModelPackage]
- unload(id)

### PredictionCore
- predict(model_package, payload) -> PredictionExecution / PredictionResult

### ExplainabilityProvider
- explain(prediction_execution) -> ExplainabilityPayload

## Integration Strategy

1. **Create framework repo/package** under `packages/prediction-framework/` in workspace.
2. **Implement adapters**:
   - `SOARAdapter` wrapping `artifact_registry`, `model_loader`, `prediction_engine`, `explainability_adapter`.
   - `ARMDAdapter` wrapping WP4 loader functions and WP5 orchestration methods.
3. **Provide shims** in `apps/api/app/plugins/prediction/armd/` that import the framework adapters (no code movement yet; adapters call legacy code paths).
4. **Validate behavior** via tests in `packages/prediction-framework/tests/` using small fixtures.

## Risk & Mitigation

- **Risk**: Behavioral drift if adapters incorrectly translate registry/artifact semantics.
  - **Mitigation**: adapter unit tests that assert identical outputs for sample deployments.
- **Risk**: SHAP / plotting dependencies can be heavy and cause packaging issues.
  - **Mitigation**: keep explainability optional (pluggable) and fail gracefully when not present.

## Next Steps (low-effort)

1. Draft `packages/prediction-framework` scaffold and interface README.
2. Implement `ModelPackage` dataclass and `ModelLoader` interface with two adapters (SOAR, ARMD). Add one unit test ensuring parity for one sample artifact set.
