# ARMD Migration Map

## Purpose

This document maps the legacy ARMD WP5 Clinical Intelligence architecture onto the PharmaTrybe SOAR plugin baseline.
It is a migration planning artifact only and does not propose code changes in the SOAR implementation.

## Approach

The migration strategy uses the existing SOAR plugin architecture as the integration baseline.
ARMD should be treated as a specialized WP5 wrapper around the validated WP4 Decision Engine, with the SOAR artifact-based plugin layering providing the runtime and deployment structure.

## High-level migration goals

1. Preserve the validated WP4 inference and SHAP workflow as-is.
2. Align ARMD API / service orchestration with the SOAR plugin lifecycle.
3. Reuse SOAR deployment discovery, artifact loading, and runtime health semantics.
4. Keep ARMD-specific outputs (clinical risk profile, stewardship guidance, structured explainability) as optional extensions layered on top of the baseline.
5. Avoid modifying SOAR core plugin behavior unless necessary for ARMD-specific configuration or additional artifact categories.

## ARMD legacy component inventory

### Core ARMD runtime components

- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/main.py`
- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/api/routes.py`
- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/api/dependencies.py`
- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/schemas/request.py`
- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/schemas/response.py`
- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/schemas/structuredexplainability.py`
- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/services/prediction_service.py`
- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/services/explainability_service.py`
- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/services/risk_profile_service.py`
- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/engine/preprocessor.py`
- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/engine/inference.py`
- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/engine/explainability_engine.py`
- `ML_MODELS/ARMD/WP5_Clinical_Intelligence/utils/risk_rules.py`

### Legacy WP4 inference core

- `ML_MODELS/ARMD/WP4_Decision_Engine.py`

## SOAR baseline architecture

The SOAR plugin architecture is organized around:

- Deployment scanning: `apps/api/app/plugins/prediction/soar/deployment_scanner.py`
- Deployment registry: `apps/api/app/plugins/prediction/soar/deployment_registry.py`
- Artifact classification: `apps/api/app/plugins/prediction/soar/artifact_registry.py` + `artifact_categories.yaml`
- Lazy model loading: `apps/api/app/plugins/prediction/soar/model_loader.py`
- Prediction execution: `apps/api/app/plugins/prediction/soar/prediction_engine.py`
- Explainability conversion: `apps/api/app/plugins/prediction/soar/explainability_adapter.py`
- Runtime lifecycle: `apps/api/app/plugins/prediction/soar/runtime_context.py`
- Plugin entrypoint: `apps/api/app/plugins/prediction/soar/soar_prediction_plugin.py`

## ARMD-to-SOAR mapping

| ARMD component | Role | SOAR equivalent | Migration note |
|---|---|---|---|
| `main.py` | FastAPI application entrypoint and lifecycle | `SOARPredictionPlugin` + platform plugin loader | Replace standalone API startup with plugin registration; keep app health semantics via platform plugin health. |
| `api/routes.py` | API routing and error handling | `SOARPredictionPlugin.predict()` + platform API adapter | Map `/v1/armd/predict` semantics into plugin request routing. |
| `api/dependencies.py` | DI singleton service | `SOARPredictionPlugin._runtime_context` and plugin initialization | ARMD DI should be replaced by the plugin runtime context and configuration-driven instantiation. |
| `schemas/request.py` | Request contract | `app.plugins.base.prediction_plugin.PredictionRequest` | Align ARMD request body with platform plugin request format. |
| `schemas/response.py` | Response contract | `PredictionResult` / plugin output format | Keep ARMD-specific response fields as plugin output extensions or enriched explainability payloads. |
| `services/prediction_service.py` | Orchestrates preprocessing, inference, explainability, and clinical risk profile | `PredictionEngine` + `ExplainabilityAdapter` + optional `RiskProfileService` | Treat as an orchestration wrapper; the plugin should delegate core inference to a SOAR-style prediction engine and use ARMD service layers for additional structured outputs. |
| `engine/preprocessor.py` | WP5 preprocessing wrapper | `PredictionEngine` preprocessing stage / model loader input validation | Preserve this as a feature conversion layer if the SOAR plugin is extended to support raw patient data input. |
| `engine/inference.py` | WP5 inference wrapper around WP4 | `PredictionEngine` | Map directly: ARMD inference is the domain-specific wrapper around the validated WP4 engine. |
| `engine/explainability_engine.py` | Explainability orchestration | `ExplainabilityAdapter` | Map SHAP orchestration and figure collection through the plugin explainability adapter. |
| `services/explainability_service.py` | Convert WP4 SHAP output to structured explainability | `ExplainabilityAdapter` + plugin-specific output shaping | Keep as a layer that translates WP4 results into PharmaTrybe API-friendly explainability. |
| `services/risk_profile_service.py` | Deterministic clinical risk profile | non-SOAR extension service | This is ARMD-specific functionality that can be integrated as an optional plugin extension rather than baseline plugin behavior. |
| `utils/risk_rules.py` | Clinical heuristic rules | ARMD domain extension | Treat this as an optional rules engine outside the SOAR migration baseline. |
| `WP4_Decision_Engine.py` | Validated prediction and SHAP engine | External inference backend | Preserve this as the core machine learning engine; do not migrate its internal predictive semantics into SOAR. |

## Migration phases

### Phase 1: Architecture alignment

- Confirm that the SOAR plugin is the architectural baseline for runtime, artifact discovery, plugin lifecycle, and health.
- Identify ARMD components that act as wrappers, not engines.
- Classify ARMD features into:
  - core inference backend (`WP4_Decision_Engine.py`)
  - plugin orchestration (`services/*`, `api/*`, `schemas/*`)
  - domain extensions (`risk_profile_service.py`, `utils/risk_rules.py`)
  - explainability adapters (`engine/explainability_engine.py`, `services/explainability_service.py`).

### Phase 2: Deployment and artifact integration

- Review whether ARMD WP4 artifacts can fit into the SOAR artifact categories.
- If necessary, extend `artifact_categories.yaml` with ARMD-specific deployment file patterns while keeping `MODEL`, `ENCODER`, `PREPROCESSOR`, `THRESHOLD`, `METADATA`, `METRICS`, `SCHEMA`, and `OTHER` as the baseline categories.
- Keep deployment discovery as filesystem scanning of package folders.
- Retain the SOAR lazy load and cache semantics for deployed model artifacts.

### Phase 3: API and orchestration mapping

- Map ARMD API endpoints to the plugin request/response contract.
- Use `PredictionService` semantics only as a service layer in the plugin runtime, not as a standalone FastAPI app.
- Ensure error translation aligns with the platform plugin adapter rather than route-level HTTP exceptions.

### Phase 4: Explainability and domain extension layering

- Keep the SOAR `ExplainabilityAdapter` as the baseline explainability handling layer.
- Use ARMD structured explainability and clinical risk profile generation as optional enrichments on top of prediction results.
- Ensure the plugin can function with core prediction only, and optionally augment outputs with ARMD structured explainability.

### Phase 5: Runtime health and certification

- Validate runtime health uses SOAR `SOARRuntimeContext` semantics:
  - deployment registry ready
  - model loader available
  - prediction engine available
  - explainability adapter available
  - configuration valid
- Confirm `validate()` returns success only when at least one valid deployment is present.
- Keep model loading lazy and ensure shutdown unloads caches.

## Architectural principles for ARMD migration

- Preserve the SOAR plugin as the core runtime boundary and avoid making ARMD-specific logic part of the base plugin contract.
- Treat ARMD prediction, explainability, and risk profile generation as layered outputs instead of changing the SOAR deployment lifecycle.
- Keep artifact discovery and loading declarative and metadata-driven; extend categories only when a clear ARMD artifact type cannot be mapped to existing SOAR categories.
- Maintain separation between:
  - generic plugin runtime/health (`SOARRuntimeContext`, deployment scanner, registry)
  - core inference backend (`WP4_Decision_Engine.py`)
  - ARMD domain extensions (`risk_profile_service.py`, `utils/risk_rules.py`)
- Ensure compatibility by preserving the current SOAR plugin request/response flow and using ARMD API semantics only as an adapter layer.
- Prioritize safety: do not refactor or reimplement the validated WP4 engine as part of this migration plan.
