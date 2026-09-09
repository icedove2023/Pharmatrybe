# SOAR Plugin Architecture

## Purpose

This document certifies the SOAR prediction plugin architecture for the PharmaTrybe platform.
It describes how `SOARPredictionPlugin` satisfies the platform plugin contract, how artifact-based
deployment is discovered and loaded, and how runtime, health, and explainability are managed.

## Scope

Applies to:
- `apps/api/app/plugins/prediction/soar/soar_prediction_plugin.py`
- `apps/api/app/plugins/prediction/soar/runtime_context.py`
- `apps/api/app/plugins/prediction/soar/deployment_registry.py`
- `apps/api/app/plugins/prediction/soar/deployment_scanner.py`
- `apps/api/app/plugins/prediction/soar/artifact_registry.py`
- `apps/api/app/plugins/prediction/soar/model_loader.py`
- `apps/api/app/plugins/prediction/soar/prediction_engine.py`
- `apps/api/app/plugins/prediction/soar/explainability_adapter.py`
- `apps/api/app/plugins/prediction/soar/plugin.yaml`

## PharmaTrybe Plugin Contract

The SOAR plugin implements the core PharmaTrybe plugin lifecycle.
The contract is defined by `app.plugins.base.plugin.BasePlugin` and `app.plugins.base.prediction_plugin.PredictionPlugin`.

Key requirements:
- `initialize()` / `shutdown()` lifecycle management
- `configure(configuration)` configuration binding
- `validate()` readiness checks
- `metadata()` structured plugin metadata
- `health()` runtime health reporting
- `load()` / `unload()` resource management
- `predict(request)` inference execution
- `supports(request)` request routing
- `input_schema()` / `output_schema()` contract stubs

The plugin is classified as an artifact-deployment prediction plugin with `deployment_type: artifact`.

## High-Level Architecture

```text
Plugin Manager
↓
Plugin Loader
↓
SOARPredictionPlugin
  ├─ SOARRuntimeContext
  │    ├─ DeploymentRegistry
  │    │    └─ DeploymentScanner
  │    │         └─ ArtifactRegistry
  │    ├─ ModelLoader
  │    ├─ PredictionEngine
  │    └─ ExplainabilityAdapter
  ├─ plugin.yaml
  └─ configuration
```

## Component Responsibilities

### SOARPredictionPlugin

`SOARPredictionPlugin` is the plugin entrypoint that:
- exposes plugin metadata and capabilities
- configures artifact discovery and registry paths
- creates the runtime context
- delegates prediction requests to the runtime engine
- implements platform contract methods

It supports lazy model loading, meaning models are only loaded when a prediction request arrives.

### SOARRuntimeContext

`SOARRuntimeContext` is the dependency container and runtime monitor.
It provides:
- initialization of deployment discovery
- runtime metadata and health state
- reload and shutdown behavior
- central access to `deployment_registry`, `model_loader`, `prediction_engine`, and `explainability_adapter`

A healthy runtime requires:
- a ready deployment registry
- a model loader instance
- a prediction engine instance
- an explainability adapter instance
- valid configuration

### DeploymentScanner

`DeploymentScanner` discovers filesystem-backed SOAR deployments.
It scans a configured `deployments_root`, builds `DeploymentInfo` objects,
parses deployment IDs, and classifies deployment status.

`DeploymentInfo` includes:
- `deployment_id`
- `organism`
- `antimicrobial`
- `deployment_path`
- `artifact_registry`
- `status`

### DeploymentRegistry

`DeploymentRegistry` caches discovered deployments.
It exposes query methods:
- `get_all()`
- `get_by_id(deployment_id)`
- `get_by_organism(organism)`
- `get_by_antimicrobial(antimicrobial)`

The registry is initialized lazily and reuses the scanned deployment cache.

### ArtifactRegistry

`ArtifactRegistry` enumerates deployment artifacts and assigns categories using pattern matching.
Artifact categories include:
- `MODEL`
- `ENCODER`
- `PREPROCESSOR`
- `THRESHOLD`
- `METADATA`
- `CONFIG`
- `METRICS`
- `SCHEMA`
- `OTHER`

The category configuration can be overridden through plugin configuration.

### ModelLoader

`ModelLoader` loads deployment artifacts lazily and caches loaded models.
It supports artifact types:
- `.pkl`, `.joblib` → pickle-based serialized objects
- `.json` → JSON documents
- `.csv` → metrics tables

A loaded model includes:
- model object
- label encoder
- optional preprocessor
- optional optimal threshold
- artifact registry metadata

### PredictionEngine

`PredictionEngine` executes inference and probability extraction.
It validates request payloads, preprocesses features, invokes the model, and applies threshold logic.
It also decodes raw model predictions using a label encoder when available.

### ExplainabilityAdapter

`ExplainabilityAdapter` converts prediction execution context into `PredictionResult` output.
The SOAR plugin supports SHAP-based explainability when `shap` is installed.
If SHAP is unavailable, the plugin can be configured to use an alternative adapter through dependency injection.

## Request Routing and Selection

The plugin uses `supports()` to determine whether it can process a request.
It returns `True` if the payload contains matching clinical keys such as:
- `organism`
- `antimicrobial`
- `pathogen`
- `antibiotic`
- `infection_site`

If no explicit routing keys are present, the plugin still accepts requests when deployments exist.

Deployment selection logic prefers:
1. organism-specific deployment
2. antimicrobial-specific deployment
3. the first valid deployment available

## Deployment Artifact Conventions

A SOAR deployment folder should contain at least one model artifact.
Common artifact names include:
- `final_model.pkl`
- `label_encoder.pkl`
- `optimal_threshold.json`
- `evaluation_metrics.csv`

Artifact categories can be overridden via plugin configuration under `artifact_categories`.

## Configuration

The plugin manifest exposes configuration schema:
- `deployments_root`: string path to SOAR deployment folders
- `artifact_categories`: optional mapping for artifact classification patterns

The plugin reads configuration in `SOARPredictionPlugin._get_deployments_root_from_config`
and `SOARPredictionPlugin._load_category_config_from_config`.

## Health and Validation

The SOAR plugin implements health reporting at two layers:
- `SOARRuntimeContext.health()` returns runtime readiness and component state
- `SOARPredictionPlugin.health()` wraps runtime health with plugin-level metadata

`validate()` returns `True` only when:
- the runtime context is initialized
- runtime health is healthy
- at least one discovered deployment is available

## Runtime Lifecycle

The certified lifecycle is:
1. `configure(configuration)`
2. `initialize()` / `load()`
3. `validate()`
4. `predict(request)`
5. `health()` checks
6. `shutdown()` / `unload()`

`configure()` is safe to call before initialization and updates runtime configuration.
`shutdown()` unloads all cached models and resets runtime metadata.

## Certification Summary

The SOAR plugin conforms to the PharmaTrybe prediction plugin standard.
It supports:
- artifact discovery
- lazy model loading
- deployment registry query semantics
- standardized plugin metadata
- health and readiness checks
- explainability adapter integration
- manifest-based discovery and validation

Existing tests confirm:
- artifact registry discovery
- model loader lazy loading
- deployment scanner parsing
- plugin manifest loading and validation
- runtime initialization
- prediction execution and explainability adapter invocation
- plugin shutdown unloading cached models

## Extension Points

Future certified enhancements may include:
- explicit `input_schema()` / `output_schema()` definitions
- additional deployment selection strategies
- runtime caching policies for loaded models
- API-based fallback deployments
- alternative explainability adapters that do not require SHAP
