# SOAR Deployment Contract Finalization Report

## Scope

SOAR-only deployment contract resolution. No React/frontend, ARMD, WHO, model artifact, or preprocessing files were modified.

## Confirmed Corrections

1. `DeploymentScanner` now treats only directories containing both `deployment_info.json` and `feature_schema.json` as active deployments. The nested source/data directory is no longer an empty pseudo-deployment.
2. Deployment identity is read from authoritative `deployment_info.json` fields `species` and `antibiotic`, rather than splitting filenames on the first underscore.
3. `DeploymentInfo` retains artifact feature names from `feature_schema.json`.
4. `SOARPredictionPlugin` now requires `request.context.deployment_id` and resolves that exact ID.
5. Unsafe fallback-to-first-deployment behavior is removed from the public execution path. Missing or unknown IDs raise `DeploymentSelectionError`.
6. The exposed schema represents distinct base and beta-lactamase deployment variants using JSON Schema 2020-12 `anyOf` and `unevaluatedProperties: false`.
7. Artifact features are marked as platform/runtime inputs; no evidence-based clinician ownership was invented.
8. SOAR legacy clinical placeholders remain unresolved or plugin-specific instead of being claimed as model inputs.

## Runtime Findings

- SOAR execution is triggered by `SOARPredictionPlugin.predict()` with a non-empty `PredictionRequest.payload`.
- Deployment selection is plugin-internal and request-context based after stabilization.
- Organism and antimicrobial metadata identify deployment records but are not both required request selectors.
- Explicit deployment selection is supported through `context.deployment_id`.
- No frontend deployment selector was found in the targeted frontend audit.
- The previous organism-first/antimicrobial-second/first-valid fallback was not deterministic and was not clinically or architecturally safe as a public contract.

## Deployment Inventory

Ten active artifact-backed deployments were confirmed:

- Cefixime / Haemophilus influenzae
- Cefotaxime / Haemophilus influenzae
- Cefpodoxime / Haemophilus influenzae
- Ceftibuten / Haemophilus influenzae
- Ceftriaxone / Haemophilus influenzae
- Doxycycline / Streptococcus pneumoniae
- Levofloxacin / Haemophilus influenzae
- Tetracycline / Haemophilus influenzae
- Tetracycline / Streptococcus pneumoniae
- Trimethoprim/Sulfa / Haemophilus influenzae

Two feature variants were confirmed:

- Base: `Age`, `YearCollected`, `Region`, `BodyLocation_Group`, `Country`.
- Beta-lactamase: base fields plus `Beta_Lactamase_enc`.

## Field Classifications

- `Age`: `CONFIRMED` runtime input.
- `YearCollected`: `CONFIRMED` runtime input; ownership unresolved.
- `Region`: `TRANSFORMED` runtime input through one-hot encoding.
- `BodyLocation_Group`: `TRANSFORMED` runtime input through one-hot encoding; not proven equivalent to canonical `infection_site`.
- `Country`: `TRANSFORMED` runtime input through target encoding.
- `Beta_Lactamase_enc`: `TRANSFORMED` deployment-specific runtime input.
- `deployment_id`: `PLUGIN-SPECIFIC` routing context, exact registry lookup.
- `organism`, `antimicrobial`: `PLUGIN-SPECIFIC` deployment metadata.
- `pathogen`, `infection_site`, `severity`, `culture`: `UNRESOLVED` as generic SOAR inputs.
- `organism` versus `pathogen` versus `species`: `CONFLICT`/`UNRESOLVED`.
- `Region` versus `Country`: `PLUGIN-SPECIFIC`, not interchangeable.

## Tests Executed

Focused SOAR deployment tests:

`\.venv\Scripts\python.exe -m pytest apps/api/tests/test_soar_deployment_contract.py -q`

Result: **PASS — 7 passed** after correcting the Draft 2020-12 `anyOf` property evaluation issue.

Existing schema contract tests:

`\.venv\Scripts\python.exe -m pytest apps/api/tests/test_plugin_input_schema_contract.py -q`

Result: **PASS — 9 passed**.

SOAR artifact inventory verification:

`\.venv\Scripts\python.exe -c "...DeploymentScanner..."`

Result: **PASS — 10 deployments discovered, 2 feature variants confirmed**.

Edited SOAR files compile successfully with `py_compile`, and `git diff --check` passes.

No full SOAR model prediction was run because the prior runtime uses artifact-specific preprocessing/model interfaces and the task requires no speculative payload construction. Artifact feature validation is directly tested with a representative `feature_names_in_` model stub.

## Unresolved Issues

- The repository does not establish clinician versus platform ownership for `Age`, `YearCollected`, `Region`, `BodyLocation_Group`, or `Country`.
- No deterministic canonical `infection_site` to `BodyLocation_Group` transformation exists.
- No universal equivalence among `organism`, `pathogen`, and `species` exists.
- Deployment IDs are now explicit, but no approved upstream mechanism supplies them from a canonical clinical request.
- Full model execution for each deployment remains dependent on exact artifact-compatible payload values and preprocessing provenance.
- The `supports()` method retains legacy routing-key recognition but requires an explicit deployment ID for true support.

## Freeze Decision

# SOAR Deployment Contract Frozen = NO

The deployment contract is substantially more truthful and deterministic, but it cannot be frozen because raw input provenance, upstream deployment-ID ownership, and canonical clinical mappings remain unresolved. The unsafe fallback was removed rather than preserved as a contract guarantee.

# Plugin Runtime Contract Frozen = NO

This SOAR-only task does not resolve the broader plugin contract blockers.

# Frontend Contract Ready = NO

No frontend reconciliation may begin. The frontend must not infer deployment selection or clinical mappings from this draft SOAR contract.
