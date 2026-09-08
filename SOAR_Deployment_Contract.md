# SOAR Deployment Contract

## Contract Version

`0.2.0` draft

## Contract Status

Frozen for explicit caller-provided deployment selection and deployment-specific artifact payload shapes. Unresolved clinical mappings remain explicitly unsupported.

## Stage A: Deployment Selection Contract

```json
{
  "context": {
    "deployment_id": "Ceftriaxone_Haemophilus_influenzae"
  }
}
```

`context.deployment_id` is required. It must exactly match an artifact-backed deployment registered by `DeploymentRegistry`. The registry reads identity from `deployment_info.json` and ignores directories that lack both `deployment_info.json` and `feature_schema.json`.

The selector is an explicit caller/platform routing context validated before plugin execution. Organism and antimicrobial metadata identify artifact records but are not implicit request selectors. No frontend inference or selector is required.

### Selection outcomes

- Known artifact-backed ID: select exactly that deployment.
- Missing ID: reject with `DeploymentSelectionError`.
- Unknown ID: reject with `DeploymentSelectionError`.
- Empty/invalid deployment: reject with `DeploymentSelectionError`.
- No first-valid fallback exists in the public contract.

## Stage B: Deployment Runtime Input Contract

### Base deployment

Required raw payload fields:

- `Age`: number
- `YearCollected`: number
- `Region`: string
- `BodyLocation_Group`: string
- `Country`: string

### Beta-lactamase deployment

Required raw payload fields:

- all base fields;
- `Beta_Lactamase_enc`: number

The two contracts are exposed as JSON Schema Draft 2020-12 `anyOf` variants. Variant-only requirements are not universal requirements. Unknown payload properties are rejected by `unevaluatedProperties: false`.

## Runtime Validation and Transformation

The selected model artifact is authoritative. `PredictionEngine` validates the payload against `feature_names_in_` when available, otherwise `n_features_in_`, otherwise sorted payload keys. Artifact transformations are:

| Raw field | Runtime feature | Boundary | Classification |
| --- | --- | --- | --- |
| `Age` | `Age` | numeric preprocessing/scaling | `CONFIRMED` |
| `YearCollected` | `YearCollected` | numeric preprocessing/scaling | `CONFIRMED` |
| `Region` | encoded region features | one-hot encoding | `TRANSFORMED` |
| `BodyLocation_Group` | encoded body-location features | one-hot encoding | `TRANSFORMED` |
| `Country` | target-encoded country feature | target encoding | `TRANSFORMED` |
| `Beta_Lactamase_enc` | same feature | passthrough/bin handling | `TRANSFORMED`, deployment-specific |

Encoded features are not clinician-entered fields. Current repository evidence does not establish whether raw artifact fields are clinician-entered or platform/context-provided, so they must not be presented as a clinical form contract.

## Routing Metadata

| Field | Source | Classification | UI exposure |
| --- | --- | --- | --- |
| `deployment_id` | request context | `ROUTING_CONTEXT` | Backend context only |
| `organism` | `deployment_info.json` species identity | `PLUGIN_SPECIFIC` | Internal metadata |
| `antimicrobial` | `deployment_info.json` antibiotic identity | `PLUGIN_SPECIFIC` | Internal metadata |

## Unsupported/Unresolved Concepts

- `pathogen`: `UNRESOLVED`; no artifact feature or deterministic routing transform.
- `infection_site`: `UNRESOLVED`; no proven mapping to `BodyLocation_Group`.
- `severity`: `UNRESOLVED`; absent from artifact/runtime feature contract.
- `culture`: `UNRESOLVED`; absent from artifact/runtime feature contract.
- `organism` versus `pathogen` versus `species`: `CONFLICT`/`UNRESOLVED`; no universal equivalence.
- `Region` versus `Country`: `PLUGIN-SPECIFIC`; different artifact features and transformations.

## Compatibility Rule

This contract does not authorize a universal clinical form. A caller must provide an explicit deployment ID and a payload satisfying the selected artifact’s exact feature contract. No implicit fallback or name-only clinical mapping is permitted.
