# Prediction Framework Extraction Plan

## Goal
Describe a stepwise, non-invasive extraction plan to create a shared prediction framework from SOAR and ARMD artifacts. The plan focuses on adapters and tests; no code movement or refactors are performed in this stage.

## Phases

### 1. Inventory & Tests (2–3 days)
- Produce exhaustive component inventory (done: SOAR and ARMD core files scanned).
- Add golden fixtures: small example deployment folders (model.pkl, scaler.pkl, threshold.txt, features.json) for test parity.
- Create unit tests asserting current SOAR `model_loader` and ARMD `load_inference_package` produce equivalent `ModelPackage` representations.

### 2. Framework Scaffold (2 days)
- Create `packages/prediction-framework/` with `ModelPackage`, `ModelLoader` interface, `PredictionCore` interface, `Explainability` interface, and `contracts`.
- Implement minimal adapters that call into existing SOAR functions (adapter thin layer).

### 3. ARMD Adapter & Validation (2–4 days)
- Implement `ARMDAdapter` translating `WP4_Decision_Engine` outputs into `ModelPackage`.
- Add tests that assert parity with SOAR adapter for the golden fixtures.

### 4. Runtime Context & Contracts (1–2 days)
- Implement runtime context class and health model in framework.
- Provide lightweight plugin manifest contract and sample plugin shim.

### 5. Documentation & Migration Guide (1–2 days)
- Author `README.md`, API docs for interfaces, developer guide for writing adapters.

### 6. Optional: Gradual Consumption (ongoing)
- Replace internal plugin imports with adapters (one plugin at a time) and run integration tests.
- Plan migration windows and rollbacks (feature flags or config toggles) if runtime changes are needed.

## Risks and Rollback

- **Adapter mismatch**: mitigate with tests that compare outputs from legacy loaders and adapters.
- **Dependency bloat**: keep explainability optional and follow plugin-level opt-in.
- **Runtime regressions**: do not change production code until tests and validation are complete; use shims only.

## Minimal Deliverables for Stage 1

- `packages/prediction-framework/` scaffold
- `tests/fixtures/sample_deployment/` with minimal artifacts
- Unit tests verifying parity between SOAR loader and ARMD loader via framework adapter
- Documentation: short README and integration checklist

## Acceptance Criteria

- All framework unit tests pass locally.
- Parity test demonstrates identical `ModelPackage` for both adapters using sample artifacts.
- No changes to SOAR or ARMD runtime code during Stage 1.
