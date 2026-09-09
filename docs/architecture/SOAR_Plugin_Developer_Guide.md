# SOAR Plugin Developer Guide

## Introduction

This guide explains how to extend, configure, and test the SOAR prediction plugin within PharmaTrybe.
It is intended for engineers who work on the SOAR prediction delivery path and for teams onboarding new artifact-based prediction plugins.

## Plugin Manifest

The SOAR plugin manifest is defined in `apps/api/app/plugins/prediction/soar/plugin.yaml`.
It must include at least:

- `plugin_id`
- `plugin_name`
- `plugin_version`
- `plugin_type`
- `deployment_type`
- `description`
- `author`
- `entrypoint_module`
- `entrypoint_class`
- `capabilities`
- `supported_domains`
- `configuration_schema`
- `minimum_platform_version`
- `sdk_version`

Example manifest values:

```yaml
plugin_id: soar
plugin_name: SOAR Prediction Plugin
plugin_version: 0.1.0
plugin_type: prediction
deployment_type: artifact
description: SOAR artifact-based prediction plugin for respiratory antimicrobial forecasting.
author: PharmaTrybe
entrypoint_module: soar_prediction_plugin
entrypoint_class: SOARPredictionPlugin
capabilities:
  - respiratory_prediction
dependencies: []
supported_domains:
  - respiratory
configuration_schema:
  deployments_root:
    type: str
    default: null
  artifact_categories:
    type: dict
    default: {}
minimum_platform_version: 1.0.0
sdk_version: 1.0.0
```

## Configuration Keys

The SOAR plugin supports these configuration keys:

- `deployments_root` (string): filesystem path containing SOAR deployment folders.
- `artifact_categories` (dict): optional artifact category mapping used by `ArtifactCategoryConfig`.

The plugin reads configuration in `SOARPredictionPlugin._get_deployments_root_from_config()` and
`SOARPredictionPlugin._load_category_config_from_config()`.

### Example configuration

```python
plugin.configure({
    "deployments_root": "C:/data/soar_deployments",
    "artifact_categories": {
        "MODEL": ["final_model.pkl", "model.pkl"],
        "THRESHOLD": ["optimal_threshold.json"],
    },
})
```

## Runtime and Initialization

The SOAR plugin is initialized by calling `initialize()` or `load()`.
During initialization:

- `DeploymentRegistry` is created and prepared using the configured root
- `ModelLoader` is built with artifact category mapping
- `SOARRuntimeContext` is created to manage runtime state
- `SOARRuntimeContext.initialize()` scans deployments and records startup metadata

If the plugin is already configured but not initialized, `load()` will create the runtime context automatically.

## Deployment Discovery

Deployment discovery is handled by `DeploymentScanner` and `DeploymentRegistry`.
The scanner iterates directories under `deployments_root` and constructs `DeploymentInfo` objects.
Deployment IDs are parsed into organism and antimicrobial values using separators like `__`, `-`, and `_`.

A valid SOAR deployment folder contains one or more artifacts. Typical files include:
- `final_model.pkl`
- `label_encoder.pkl`
- `optimal_threshold.json`
- `evaluation_metrics.csv`

If a deployment folder is empty, the status is marked as `empty`.

## Artifact Classification

`ArtifactRegistry` classifies files by filename pattern and extension.
Artifact categories used by the plugin include:
- `MODEL`
- `ENCODER`
- `PREPROCESSOR`
- `THRESHOLD`
- `METADATA`
- `CONFIG`
- `METRICS`
- `SCHEMA`
- `OTHER`

To customize classification, provide `artifact_categories` in the plugin configuration.

## Lazy Model Loading

Model artifacts are not loaded until prediction time.
`ModelLoader` caches loaded deployments after the first prediction.

A loaded deployment contains:
- `model`
- `label_encoder`
- `preprocessor` (optional)
- `optimal_threshold`
- `artifact_registry`

This behavior reduces startup time and avoids loading unused deployments.

## Prediction Execution

Prediction is performed by `PredictionEngine.predict()`.
The engine:
- validates the request payload
- determines feature order using `feature_names_in_` or sorted keys
- calls model inference (`predict` or `predict_proba`)
- extracts probability data when available
- applies threshold decisions
- decodes class labels using a label encoder if present

The plugin delegates post-processing to `ExplainabilityAdapter.explain()`.

## Explainability

The default explainability adapter uses SHAP when installed.
It supports:
- tree-based models with `TreeExplainer`
- fallback explainability with `KernelExplainer`

If SHAP is not available, the default adapter raises `ExplainabilityError`.
For testing or deployment environments without SHAP, override `_explainability_adapter`
with a custom adapter that implements `explain(execution)`.

## Health and Validation

The SOAR plugin exposes health at the plugin and runtime levels.

- `SOARRuntimeContext.health()` checks registry, loader, prediction engine, explainability adapter, configuration, and error state.
- `SOARPredictionPlugin.health()` wraps runtime health and reports deployment and model counts.
- `SOARPredictionPlugin.validate()` returns success only when the plugin is initialized, health is healthy, and deployments exist.

## Extending SOAR

### Add support for more artifact types

Update `ArtifactCategoryConfig.DEFAULT_CATEGORIES` or override via `artifact_categories`.
If your deployment uses a new artifact extension, add classification patterns accordingly.

### Add new prediction selection logic

Modify `SOARPredictionPlugin._select_deployment()` to support additional routing keys or clinical rules.
Keep the selection strategy deterministic and fallback to the first valid deployment.

### Add structured schemas

Implement `input_schema()` and `output_schema()` with explicit expected fields.
This helps the platform validate request payloads before prediction.

### Replace explainability adapter

Create a subclass of `ExplainabilityAdapter` and assign it to `_explainability_adapter` during plugin initialization.
This enables custom explainability pipelines without changing plugin wiring.

## Testing Checklist

The SOAR plugin is certified by tests that cover:
- plugin manifest discovery and validation
- plugin loader discovery and registration
- deployment scanner discovery and metadata parsing
- artifact registry classification
- lazy model loading and cache behavior
- prediction execution and explainability adapter invocation
- plugin shutdown and model unload behavior
- plugin health reporting after initialization

Add tests for any new runtime or deployment selection behavior.

## Deployment Notes

The SOAR plugin is designed for artifact-based deployment in PharmaTrybe.
Deployment artifacts should be provisioned under the configured `deployments_root`.

The platform may use the plugin registry and manager to load the plugin automatically from the `apps/api/app/plugins/prediction/soar` folder.

## Certification Status

This guide documents the current certified architecture for SOAR.
Any future changes to the plugin should preserve:
- the plugin contract
- runtime initialization and shutdown semantics
- manifest-based discovery
- artifact classification and lazy loading
- explainability adapter abstraction
- health and validation behavior
