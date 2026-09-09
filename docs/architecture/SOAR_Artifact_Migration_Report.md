# SOAR Artifact Migration Report

## Scope

This document audits the PharmaTrybe SOAR prediction plugin against the original SOAR deployment package located in `deployments/SOAR_GSK/`.
It maps every artifact in the package to the current implementation in `apps/api/app/plugins/prediction/soar/` and records integration status, responsibilities, and remaining gaps.

## Package Inventory

The SOAR deployment package contains the following unique artifacts.
For every artifact, the report identifies purpose, platform component integration, status, and future requirement.

| Deployment Artifact | Purpose | Platform Component | Status | Future Requirement |
|---------------------|---------|--------------------|--------|--------------------|
| deployment_index.csv | Package-level index of deployment assets | None | Obsolete | Deprecated |
| deployment_registry.json | Package-level registry snapshot | None | Obsolete | Deprecated |
| deployment_registry.jsonl | Package-level registry snapshot | None | Obsolete | Deprecated |
| phase13d_summary.json | Phase 13 reconstruction summary | None | Obsolete | Deprecated |
| backend_contract.json | Backend-SOAR contract metadata | None | Ignored | Recommended |
| calibration.pkl | Model calibration artifact | None | Ignored | Recommended |
| dependency_report.json | Dependency metadata for the deployment | None | Ignored | Optional |
| deployment_certificate.json | Deployment certification metadata | None | Ignored | Recommended |
| deployment_completion.json | Deployment completion metadata | None | Ignored | Recommended |
| deployment_fingerprint.json | Deployment fingerprint / integrity metadata | None | Ignored | Recommended |
| deployment_info.json | Deployment metadata summary | None | Ignored | Optional |
| deployment_manifest.json | Package manifest describing deployment contents | None | Ignored | Recommended |
| evaluation_metrics.csv | Evaluation metric table for the deployment | `app/plugins/prediction/soar/artifact_registry.py`, `app/plugins/prediction/soar/model_loader.py` | Partially Integrated | Optional |
| feature_schema.json | Feature schema metadata | None | Ignored | Recommended |
| final_model.pkl | Serialized prediction model | `app/plugins/prediction/soar/artifact_registry.py`, `app/plugins/prediction/soar/model_loader.py` | Fully Integrated | Mandatory |
| label_encoder.json | Label encoder metadata in JSON form | None | Ignored | Optional |
| label_encoder.pkl | Serialized label encoder | `app/plugins/prediction/soar/artifact_registry.py`, `app/plugins/prediction/soar/model_loader.py` | Fully Integrated | Recommended |
| metadata.json | Deployment metadata file | `app/plugins/prediction/soar/artifact_registry.py` | Partially Integrated | Recommended |
| model_card.json | Model documentation card | `app/plugins/prediction/soar/artifact_registry.py` (OTHER) | Ignored | Recommended |
| optimal_threshold.json | Threshold data for decision logic | `app/plugins/prediction/soar/artifact_registry.py`, `app/plugins/prediction/soar/model_loader.py`, `app/plugins/prediction/soar/prediction_engine.py` | Fully Integrated | Mandatory |
| package_manifest.json | Package-level asset manifest, hashes, and integrity data | None | Ignored | Recommended |
| pipeline_structure.json | Pipeline structure metadata | None | Ignored | Recommended |
| preprocessing_pipeline.pkl | Preprocessing pipeline artifact | `app/plugins/prediction/soar/artifact_registry.py`, `app/plugins/prediction/soar/model_loader.py` | Partially Integrated | Recommended |
| preprocessing_summary.json | Preprocessing metadata summary | None | Ignored | Recommended |
| README.md | Human-readable deployment documentation | `app/plugins/prediction/soar/artifact_registry.py` | Partially Integrated | Optional |
| reconstruction_metadata.json | Reconstruction metadata from package recovery | None | Ignored | Optional |
| runtime_validation.json | Runtime validation records | None | Ignored | Recommended |
| sbom.json | Software bill of materials | None | Ignored | Optional |
| security_audit.json | Security audit artifacts | None | Ignored | Recommended |
| shap_explainer.pkl | Precomputed SHAP explainer artifact | None | Ignored | Recommended |
| validation_report.json | Model validation report | None | Ignored | Recommended |
| verification_certificate.json | Verification certificate metadata | None | Ignored | Recommended |
| verification_log.txt | Verification execution log | None | Ignored | Optional |
| verification_report.json | Verification report metadata | None | Ignored | Recommended |
| VERSION.json | Package version metadata | None | Ignored | Recommended |

## Integration Summary

### Fully Integrated Artifacts

- `final_model.pkl`
- `label_encoder.pkl`
- `optimal_threshold.json`

These artifacts are directly recognized by the current SOAR plugin implementation, loaded through the deployment artifact pipeline, and consumed by prediction execution.

### Partially Integrated Artifacts

- `preprocessing_pipeline.pkl`
- `evaluation_metrics.csv`
- `metadata.json`
- `README.md`

These artifacts are discovered by `ArtifactRegistry` and classified, but they are not fully consumed by the prediction flow.
`preprocessing_pipeline.pkl` has optional loader support, while the others are currently only categorized.

### Ignored Artifacts

- `backend_contract.json`
- `calibration.pkl`
- `dependency_report.json`
- `deployment_certificate.json`
- `deployment_completion.json`
- `deployment_fingerprint.json`
- `deployment_info.json`
- `deployment_manifest.json`
- `label_encoder.json`
- `model_card.json`
- `package_manifest.json`
- `pipeline_structure.json`
- `preprocessing_summary.json`
- `reconstruction_metadata.json`
- `runtime_validation.json`
- `sbom.json`
- `security_audit.json`
- `shap_explainer.pkl`
- `validation_report.json`
- `verification_certificate.json`
- `verification_log.txt`
- `verification_report.json`
- `VERSION.json`
- `deployment_index.csv`
- `deployment_registry.json`
- `deployment_registry.jsonl`
- `phase13d_summary.json`

These artifacts are present in the original package but are not currently consumed by any SOAR prediction plugin component.

## Artifact Support Details

The current SOAR implementation supports deployment artifacts through these files:

- `apps/api/app/plugins/prediction/soar/deployment_scanner.py`
- `apps/api/app/plugins/prediction/soar/deployment_registry.py`
- `apps/api/app/plugins/prediction/soar/artifact_registry.py`
- `apps/api/app/plugins/prediction/soar/artifact_categories.yaml`
- `apps/api/app/plugins/prediction/soar/model_loader.py`
- `apps/api/app/plugins/prediction/soar/prediction_engine.py`
- `apps/api/app/plugins/prediction/soar/explainability_adapter.py`
- `apps/api/app/plugins/prediction/soar/soar_prediction_plugin.py`
- `apps/api/app/plugins/prediction/soar/runtime_context.py`

The artifact support is driven by the category configuration in `artifact_categories.yaml` and the loaded artifacts listed in `ModelLoader`.

## Architecture Flow

Deployment Package
↓
`app.plugins.prediction.soar.deployment_scanner.DeploymentScanner.scan()`
↓
`app.plugins.prediction.soar.deployment_registry.DeploymentRegistry.initialize()`
↓
`app.plugins.prediction.soar.artifact_registry.ArtifactRegistry.from_deployment_path()`
↓
`app.plugins.prediction.soar.model_loader.ModelLoader.load()`
↓
`app.plugins.prediction.soar.prediction_engine.PredictionEngine.predict()`
↓
`app.plugins.prediction.soar.explainability_adapter.ExplainabilityAdapter.explain()`
↓
`app.plugins.prediction.soar.soar_prediction_plugin.SOARPredictionPlugin.predict()`
↓
`app.plugins.base.prediction_plugin.PredictionResult`

## Component Responsibilities

### Deployment Scanner

- Responsibility: Discover SOAR deployment folders under the configured root.
- Inputs: filesystem path from plugin configuration.
- Outputs: `DeploymentInfo` objects with parsed deployment ID, organism, antimicrobial, path, artifact registry, and status.
- Dependencies: `ArtifactRegistry`.
- Why it exists: It is the first stage of plugin package ingestion and isolates filesystem scanning from the rest of the plugin.

### Deployment Registry

- Responsibility: Cache and expose discovered deployments.
- Inputs: `DeploymentInfo` list from `DeploymentScanner`.
- Outputs: deployment lookup methods (`get_all`, `get_by_organism`, `get_by_antimicrobial`, `get_by_id`).
- Dependencies: `DeploymentScanner`.
- Why it exists: It provides a stable in-memory registry that the plugin can query repeatedly without rescanning the filesystem.

### Artifact Registry

- Responsibility: Enumerate files in a deployment and classify them into artifact categories.
- Inputs: deployment path.
- Outputs: `Artifact` objects grouped by category.
- Dependencies: `ArtifactCategoryConfig`.
- Why it exists: It transforms raw deployment filesystem contents into typed artifacts that the model loader can consume.

### Artifact Categories

- Responsibility: Define file classification rules for deployment artifacts.
- Inputs: filename and file extension.
- Outputs: artifact category labels such as MODEL, ENCODER, PREPROCESSOR, THRESHOLD, METADATA, CONFIG, METRICS, SCHEMA, OTHER.
- Dependencies: none beyond configuration file.
- Why it exists: It standardizes how deployment files are interpreted and which artifacts are required for prediction.

### Runtime Context

- Responsibility: Manage SOAR runtime state, health, startup metadata, reload, and shutdown.
- Inputs: plugin configuration, deployment registry, model loader, prediction engine, explainability adapter.
- Outputs: runtime metadata, health status, and lifecycle control.
- Dependencies: `DeploymentRegistry`, `ModelLoader`, `PredictionEngine`, `ExplainabilityAdapter`.
- Why it exists: It encapsulates runtime readiness and keeps prediction components organized.

### Model Loader

- Responsibility: Load deployment artifacts lazily and cache loaded models.
- Inputs: `DeploymentInfo` with artifact registry.
- Outputs: `LoadedModel` containing model, encoder, preprocessor, threshold, and artifact metadata.
- Dependencies: `ArtifactRegistry`, `ArtifactCategoryConfig`.
- Why it exists: It separates artifact loading from prediction logic and avoids repeated deserialization.

### Prediction Engine

- Responsibility: Execute inference, gaze at feature ordering, extract probabilities, apply thresholds, and decode labels.
- Inputs: loaded model artifacts and prediction request.
- Outputs: `PredictionExecution` with prediction metadata.
- Dependencies: `LoadedModel`, `PredictionRequest`.
- Why it exists: It centralizes prediction execution semantics independent of plugin orchestration.

### Explainability Adapter

- Responsibility: Convert execution context into standardized `PredictionResult` with explainability metadata.
- Inputs: `PredictionExecution`.
- Outputs: `PredictionResult`.
- Dependencies: SHAP library when available, model, request payload.
- Why it exists: It decouples explainability generation from raw prediction execution.

### Prediction Plugin

- Responsibility: Implement the PharmaTrybe prediction plugin contract, including initialization, configuration, health, metadata, validation, and prediction.
- Inputs: plugin configuration and prediction requests.
- Outputs: plugin lifecycle behavior and `PredictionResult` outputs.
- Dependencies: `SOARRuntimeContext`, `DeploymentRegistry`, `ModelLoader`, `PredictionEngine`, `ExplainabilityAdapter`.
- Why it exists: It is the entrypoint for platform integration and enforces the plugin contract.

### Plugin Manifest

- Responsibility: Define plugin identity, capabilities, deployment type, and configuration schema.
- Inputs: manifest file at `apps/api/app/plugins/prediction/soar/plugin.yaml`.
- Outputs: plugin metadata used by discovery and validation.
- Dependencies: `PluginValidator`, `PluginLoader`.
- Why it exists: It enables automatic plugin discovery and ensures the plugin is registered with the platform.

### Plugin Manager Integration

- Responsibility: Discover and load the SOAR plugin into the PharmaTrybe runtime.
- Inputs: plugin root directory, platform version, SDK version.
- Outputs: registered `SOARPredictionPlugin` instance in `PluginRegistry`.
- Dependencies: `PluginLoader`, `PluginRegistry`, `PluginValidator`.
- Why it exists: It provides the platform-level integration point for all plugins, including SOAR.

## Architecture Assessment

### Deployment completeness

**Can PharmaTrybe load a brand-new SOAR deployment package without modifying platform code?**

**Answer: YES**

**Explanation:**
The current implementation discovers deployments by scanning subdirectories under the configured `deployments_root`.
It does not require package-level registry files or special manifest inputs in order to load a package.
As long as the package contains deployment subdirectories with actual files, `DeploymentScanner` and `DeploymentRegistry` will discover them.

However, this applies only to the core model package subset; many package metadata artifacts are present but not consumed.

### Artifact coverage

**Fully supported artifacts**

- `final_model.pkl`
- `label_encoder.pkl`
- `optimal_threshold.json`

**Partially supported artifacts**

- `preprocessing_pipeline.pkl`
- `evaluation_metrics.csv`
- `feature_schema.json`
- `metadata.json`
- `README.md`

**Currently ignored artifacts**

- `backend_contract.json`
- `calibration.pkl`
- `dependency_report.json`
- `deployment_certificate.json`
- `deployment_completion.json`
- `deployment_fingerprint.json`
- `deployment_info.json`
- `deployment_manifest.json`
- `label_encoder.json`
- `model_card.json`
- `package_manifest.json`
- `pipeline_structure.json`
- `preprocessing_summary.json`
- `reconstruction_metadata.json`
- `runtime_validation.json`
- `sbom.json`
- `security_audit.json`
- `shap_explainer.pkl`
- `validation_report.json`
- `verification_certificate.json`
- `verification_log.txt`
- `verification_report.json`
- `VERSION.json`
- `deployment_index.csv`
- `deployment_registry.json`
- `deployment_registry.jsonl`
- `phase13d_summary.json`

**Artifacts that should be supported in the future**

- `calibration.pkl`
- `feature_schema.json`
- `shap_explainer.pkl`
- `deployment_manifest.json`
- `package_manifest.json`
- `deployment_certificate.json`
- `validation_report.json`
- `verification_report.json`
- `VERSION.json`
- `model_card.json`
- `backend_contract.json`
- `runtime_validation.json`
- `security_audit.json`

### Missing capabilities

The audit reveals the following genuine gaps before SOAR can serve as a complete reference prediction plugin:

- **Calibration artifact support**: `calibration.pkl` is present in the package but not consumed.
- **Preprocessing schema validation**: `feature_schema.json` is discovered but never validated.
- **SHAP explainer artifact support**: `shap_explainer.pkl` is not loaded; explainability is generated at runtime instead.
- **Deployment manifest/package manifest ingestion**: `deployment_manifest.json` and `package_manifest.json` are currently ignored despite containing package metadata.
- **Model documentation ingestion**: `model_card.json` is not categorized as metadata and is effectively ignored.
- **Version compatibility**: `VERSION.json` is not used for deployment version tracking or compatibility checks.
- **Deployment verification artifacts**: verification, validation, and certificate files are ignored even though they exist in the package.
- **Package-level registration files**: `deployment_registry.json`, `deployment_registry.jsonl`, and `deployment_index.csv` are not consumed by the plugin and thus not part of the current plugin architecture.

### Reference Plugin Assessment

**Assessment:** Ready with minor improvements

**Explanation:**
The core SOAR prediction path is implemented correctly and supports the essential prediction artifacts required for inference.
`final_model.pkl`, `label_encoder.pkl`, and `optimal_threshold.json` are fully integrated, and the plugin lifecycle is well structured.
However, the package contains a broad set of metadata and verification artifacts that are currently ignored or only partially supported.
Those gaps must be addressed before SOAR can serve as the definitive reference implementation for all future PharmaTrybe prediction plugins.

## Remaining work before Stage 1 can be closed

These items genuinely block final certification of SOAR as the platform reference plugin:

1. Add explicit support for package metadata artifacts such as `deployment_manifest.json` and `package_manifest.json`.
2. Add support for `calibration.pkl` and decide whether it should be consumed by prediction probability calibration.
3. Add or document support for `shap_explainer.pkl` if precomputed explainers are to be part of the deployment contract.
4. Add feature schema validation for `feature_schema.json` so that input payloads can be checked against deployment schema metadata.
5. Add version compatibility handling for `VERSION.json` or equivalent deployment version metadata.
6. Add ingestion or validation support for deployment verification artifacts (`validation_report.json`, `verification_report.json`, `deployment_certificate.json`).
7. Extend artifact categorization to include common metadata artifacts such as `model_card.json` and `backend_contract.json`.

Once these gaps are addressed, SOAR can be certified as the official PharmaTrybe Prediction Plugin reference implementation.
