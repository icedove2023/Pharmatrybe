# Framework Usage Report

## Shared Framework Usage

The shared prediction framework was used strictly for infrastructure reuse. It was not used to alter prediction behavior or clinical rules.

### Runtime lifecycle reuse

- PredictionPluginRuntimeContext provides the shared runtime lifecycle and health tracking contract.
- SOARRuntimeContext and ARMDRuntimeContext implement their specific initialization, shutdown, validation, and health metadata hooks while preserving their current runtime semantics.

### Plugin lifecycle reuse

- BasePredictionPlugin provides the shared plugin contract delegation and lifecycle management pattern.
- SOARPredictionPlugin and ARMDPredictionPlugin continue to expose the same public methods expected by the platform while delegating shared boilerplate to the framework base.

### Explainability reuse

- BaseExplainabilityAdapter provides the shared explanation abstraction and graceful error-handling patterns.
- SOAR explainability and ARMD explainability retain their plugin-specific explanation generation paths while inheriting the base adapter contract.

## Scope Guardrails

The following were not extracted or altered:

- prediction algorithm logic
- preprocessing behavior
- SHAP calculation logic
- ranking and thresholding logic
- WHO guidance logic
- stewardship logic
- API contracts
- plugin output schemas
- deployment behavior

## Outcome

This is a minimal infrastructure refactor that centralizes duplicated boilerplate while preserving plugin-specific behavior and deployment semantics.
