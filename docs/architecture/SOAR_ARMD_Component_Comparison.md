# SOAR ↔ ARMD Component Comparison

## Purpose
Component-by-component mapping between the SOAR prediction plugin (apps/api/app/plugins/prediction/soar/) and the legacy ARMD WP5/WP4 implementation (ML_MODELS/ARMD/...). Each component is classified as one of: Shared Platform Infrastructure, Prediction Framework (reusable), ARMD-specific, or SOAR-specific. Short rationale and recommended extraction target are provided.

## Summary Matrix

### Artifact discovery & classification
- **SOAR**: artifact_registry.py, artifact_categories.yaml
- **ARMD**: WP4/WP3 artifact folders + WP4_Decision_Engine helpers (load_wp3_artifacts, load_inference_package)
- **Classification**: Prediction Framework (reusable)
- **Rationale**: Both systems need canonical artifact classification and a way to locate model, scaler, threshold, schema, etc.

### Deployment discovery & registry
- **SOAR**: deployment_scanner.py, deployment_registry.py
- **ARMD**: registry file + WP4 helper functions (REGISTRY_PATH / model_registry.json)
- **Classification**: Shared Platform Infrastructure / Prediction Framework
- **Rationale**: Runtime registry and scanning are common requirements; a shared registry API is extractable.

### Model loading & artifact I/O
- **SOAR**: model_loader.py (lazy load, caching, typed LoadedModel)
- **ARMD**: load_inference_package, load_registry, load_wp3_artifacts
- **Classification**: Prediction Framework
- **Rationale**: Loading model/scaler/threshold/features and converting artifacts to runtime objects is shared logic.

### Prediction execution / inference engine
- **SOAR**: prediction_engine.py (validation, preprocessing contract, probability extraction, threshold application)
- **ARMD**: engine/inference.py + WP4_Decision_Engine (predict_all_antibiotics, rank_predictions)
- **Classification**: Prediction Framework core + ARMD-specific orchestration
- **Rationale**: Core model invocation and probability handling are generic; ARMD applies domain ranking and reporting.

### Preprocessing / feature alignment
- **SOAR**: prediction_engine._preprocess (relies on model metadata or artifact preprocessors)
- **ARMD**: preprocess_patient_features, build_feature_frame (exact WP3 artifact-based preprocessing)
- **Classification**: Prediction Framework (contracts) + ARMD-specific exactization
- **Rationale**: Feature alignment contract is shared; ARMD requires exact WP3 artifact application.

### Explainability
- **SOAR**: explainability_adapter.py (wraps SHAP, returns structured metadata)
- **ARMD**: generate_shap_explanation, ExplainabilityService (narrative, figures)
- **Classification**: Prediction Framework interface + ARMD-specific explainability implementation
- **Rationale**: SHAP computation is shared; presentation/narrative is domain-specific.

### Runtime context / lifecycle / health
- **SOAR**: runtime_context.py (dependency container, init/reload/shutdown, health)
- **ARMD**: FastAPI main + ad-hoc lifecycle in scripts
- **Classification**: Shared Platform Infrastructure
- **Rationale**: Runtime container and health endpoints are reusable.

### Prediction orchestration & business logic
- **SOAR**: plugin manifest, soar_prediction_plugin.py (plugin glue)
- **ARMD**: services/prediction_service.py, api/routes.py (clinical orchestration, risk_profile)
- **Classification**: ARMD-specific (business) + plugin contract (shared)
- **Rationale**: Clinical rules and stewardship logic are ARMD business logic; plugin plumbing belongs to platform.

## Detailed Notes & Recommendations

### artifact_registry.py (SOAR)
- Declarative category config for artifacts. Recommend extracting as canonical artifact classifier and scanner API.

### model_loader.py (SOAR) vs load_inference_package (ARMD)
- **Recommendation**: Define a `ModelPackage` contract (model, scaler, threshold, feature_names, artifacts, metadata) with adapters for both formats.

### prediction_engine / inference
- **Recommendation**: Extract a `PredictionCore` handling: input validation, feature alignment, inference invocation, probability extraction, thresholding, and basic metadata; keep ARMD ranking and report generation as layered services.

### explainability
- **Recommendation**: Provide a normalized Explainability API returning contributions, positive/negative drivers, optional figure references, and an optional narrative. ARMD can implement narrative extension.

## Classification Legend
- **Shared Platform Infrastructure**: runtime, registry, plugin discovery, health.
- **Prediction Framework (reusable)**: model/artifact contracts, loader, inference core, explainability interface.
- **ARMD-specific**: clinical orchestration, risk rules, clinician narratives, reporting.
- **SOAR-specific**: plugin manifest, deployment scanning tuned to plugin layout.
