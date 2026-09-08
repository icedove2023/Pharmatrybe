# SOAR Deployment Runtime Audit

## Scope

SOAR-only audit of runtime selection, deployment artifacts, feature schemas, model metadata, validation, and execution. No React/frontend, ARMD, WHO, preprocessing, or model artifact files were modified.

## Actual Runtime Flow

`PredictionRequest` enters `SOARPredictionPlugin.predict()`.

1. `supports()` requires a non-empty payload and an explicit `context.deployment_id`.
2. `_select_deployment()` resolves that ID through `DeploymentRegistry.get_by_id()`.
3. The selected `DeploymentInfo` is loaded by `ModelLoader`.
4. `PredictionEngine._validate_request()` confirms the payload is a non-empty dictionary.
5. `_preprocess()` uses loaded model `feature_names_in_` when available, otherwise `n_features_in_`, otherwise sorted payload keys.
6. The model predicts and probability/threshold decoding produces the SOAR result.

## Deployment Selection Findings

- Trigger: a supported `PredictionRequest` passed to `SOARPredictionPlugin.predict()`.
- Selection owner: plugin-internal backend logic.
- Public selection input: `request.context.deployment_id`.
- Organism and antimicrobial are not required for selection after stabilization; they are metadata in `deployment_info.json`, not an implicit selector.
- The prior implementation searched organism first, then antimicrobial, then selected the first valid deployment. This was not jointly deterministic.
- The prior parser split deployment IDs on the first separator and misread multi-token names.
- Fallback-to-first deployment was implemented previously, but it is not safe as a public contract because an unrelated model can be selected silently.
- No-match behavior is now a clear `DeploymentSelectionError`.
- Ambiguous organism/antimicrobial matching is not used; explicit deployment ID avoids ambiguity.
- Targeted frontend inspection found no SOAR deployment/model selector. Frontend ownership is therefore not established and the frontend must not infer one.

## Deployment Inventory

Ten artifact-backed deployments were found. The nested `SOAR_GSK` source/data directory was excluded because it has no deployment artifact pair.

| Deployment ID | Metadata identity | Feature variant |
| --- | --- | --- |
| `Cefixime_Haemophilus_influenzae` | Cefixime / Haemophilus influenzae | 6 fields including beta-lactamase |
| `Cefotaxime_Haemophilus_influenzae` | Cefotaxime / Haemophilus influenzae | 6 fields including beta-lactamase |
| `Cefpodoxime_Haemophilus_influenzae` | Cefpodoxime / Haemophilus influenzae | 6 fields including beta-lactamase |
| `Ceftibuten_Haemophilus_influenzae` | Ceftibuten / Haemophilus influenzae | 6 fields including beta-lactamase |
| `Ceftriaxone_Haemophilus_influenzae` | Ceftriaxone / Haemophilus influenzae | 6 fields including beta-lactamase |
| `Doxycycline_Streptococcus_pneumoniae` | Doxycycline / Streptococcus pneumoniae | 5 fields, no beta-lactamase |
| `Levofloxacin_Haemophilus_influenzae` | Levofloxacin / Haemophilus influenzae | 6 fields including beta-lactamase |
| `Tetracycline_Haemophilus_influenzae` | Tetracycline / Haemophilus influenzae | 6 fields including beta-lactamase |
| `Tetracycline_Streptococcus_pneumoniae` | Tetracycline / Streptococcus pneumoniae | 5 fields, no beta-lactamase |
| `Trimethoprim_Sulfa_Haemophilus_influenzae` | Trimethoprim/Sulfa / Haemophilus influenzae | 6 fields including beta-lactamase |

Identity is read from authoritative `deployment_info.json` keys `antibiotic` and `species`, not inferred from filename tokenization.

## Artifact Feature Variants

### Base variant

`Age`, `YearCollected`, `Region`, `BodyLocation_Group`, `Country`

### Beta-lactamase variant

`Age`, `YearCollected`, `Region`, `BodyLocation_Group`, `Country`, `Beta_Lactamase_enc`

Persisted model metadata reports matching `feature_names_in_` arrays and `n_features_in_` values. `feature_schema.json` reports:

- `Age`, `YearCollected`: numeric, standard scaling.
- `Region`, `BodyLocation_Group`: one-hot encoding.
- `Country`: target encoding.
- `Beta_Lactamase_enc`: passthrough/bin handling in applicable deployments.

## Field Classification

| Field | Runtime source | Transformation | Classification | UI exposure |
| --- | --- | --- | --- | --- |
| `Age` | deployment artifact/model | numeric preprocessing | `CONFIRMED` runtime input | Not classified as clinician-entered by current evidence |
| `YearCollected` | deployment artifact/model | numeric preprocessing | `CONFIRMED` runtime input | Platform/context input only until ownership is established |
| `Region` | deployment artifact/model | one-hot encoding | `TRANSFORMED` runtime input | Platform/context input only until ownership is established |
| `BodyLocation_Group` | deployment artifact/model | one-hot encoding | `TRANSFORMED` runtime input | Platform/context input only; no canonical infection-site mapping proven |
| `Country` | deployment artifact/model | target encoding | `TRANSFORMED` runtime input | Platform/context input only until provenance is established |
| `Beta_Lactamase_enc` | deployment artifact/model, variant-specific | passthrough/bin | `TRANSFORMED` runtime input | Deployment-specific platform input; not a generic clinical field |
| `deployment_id` | `PredictionRequest.context` | exact registry lookup | `ROUTING_CONTEXT` | Backend context; no frontend selector established |
| `organism` | `deployment_info.json` | identity metadata only | `PLUGIN_SPECIFIC` | Not a model payload field |
| `antimicrobial` | `deployment_info.json` | identity metadata only | `PLUGIN_SPECIFIC` | Not a model payload field |
| `pathogen` | plugin support routing legacy key | no confirmed transform | `UNRESOLVED` | Not exposed as runtime input |
| `infection_site` | no confirmed runtime field | no deterministic mapping to `BodyLocation_Group` | `UNRESOLVED` | Not exposed as SOAR runtime input |
| `severity` | no artifact/runtime field | none | `UNRESOLVED` | Not exposed |
| `culture` | no artifact/runtime field | none | `UNRESOLVED` | Not exposed |

Encoded columns and model-internal feature vectors are not clinician form fields.

## Canonical Mapping Boundary

- `Age` to canonical age: `TRANSFORMED` at the platform boundary, but ownership/provenance remains unresolved.
- `age_group`: no SOAR evidence; do not merge with `Age`.
- `infection_site` to `BodyLocation_Group`: `UNRESOLVED`; artifact category similarity is not proof of a deterministic clinical transform.
- `organism` versus `pathogen` versus `species`: `CONFLICT`/`UNRESOLVED`; deployment metadata identity is not a universal clinical equivalence.
- `Region` and `Country`: `PLUGIN_SPECIFIC` dataset/model context, not interchangeable demographic concepts.
- `severity`, `culture`, and high-level clinical aliases: `UNRESOLVED`.

## Audit Conclusion

A single universal clinician-facing SOAR schema is not supported by current runtime evidence. The truthful contract is a selector stage using an explicit deployment ID followed by a deployment-specific artifact input contract. The contract remains unfrozen until raw input provenance and canonical mapping boundaries are formally resolved.
