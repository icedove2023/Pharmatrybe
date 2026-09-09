# Plugin Runtime Contract Stabilization Report

## Scope

This phase inspected only SOAR, ARMD, WHO, their runtime/artifact/database paths, schema registry/discovery/composition, pipeline schema exposure, and focused tests. No React/frontend files, model artifacts, ARMD preprocessing code, or WHO database contents were modified.

No clinical validity, external validation, certification, or production approval is claimed.

## 1. SOAR Status: UNRESOLVED

### Runtime reality

`SOARPredictionPlugin` selects a deployment internally through `DeploymentRegistry`:

- `organism` is parsed from deployment directory names and used for internal deployment selection.
- `antimicrobial` is parsed from deployment directory names and used for internal deployment selection.
- If no matching selection is found, the plugin selects the first valid deployment.
- Deployment selection is therefore currently **D. Plugin internal logic**, not frontend/user selection.

`PredictionEngine._validate_request()` requires a non-empty payload. `_preprocess()` then validates against the loaded model artifact:

- `feature_names_in_` present: every exact artifact feature name is required and preserved in order.
- `n_features_in_` present: payload length must match the model count.
- Otherwise: sorted payload keys are used.

### Artifact evidence

Ten SOAR deployments were inspected. Their persisted `metadata.json` and `feature_schema.json` files use two variants:

- `Age`, `BodyLocation_Group`, `Region`, `Country`, `YearCollected`;
- the same five plus `Beta_Lactamase_enc`.

The artifact feature metadata identifies numeric scaling for `Age`, `YearCollected`; one-hot encoding for `BodyLocation_Group`, `Region`; target encoding for `Country`; and deployment-specific passthrough/bin handling for `Beta_Lactamase_enc`.

No SOAR preprocessing adapter maps the former generic fields `pathogen`, `culture`, `infection_site`, or `severity` into these exact artifact names.

### Corrected exposed schema

The SOAR schema now exposes the two artifact-backed deployment variants and keeps deployment selection internal. Encoded features are represented as runtime transformation metadata, not as invented canonical clinical fields.

The former generic `pathogen` requirement was removed. `pathogen` remains unresolved routing metadata and is not asserted as a model input.

### SOAR field classifications

| Runtime/UI field | Classification | Evidence |
| --- | --- | --- |
| `Age` | `CONFIRMED` | Artifact feature schema and model metadata |
| `YearCollected` | `CONFIRMED` | Artifact feature schema and model metadata |
| `Region` | `TRANSFORMED` | Artifact one-hot transformer metadata |
| `BodyLocation_Group` | `TRANSFORMED` | Artifact one-hot transformer metadata |
| `Country` | `TRANSFORMED` | Artifact target-encoding metadata |
| `Beta_Lactamase_enc` | `TRANSFORMED` | Present only in some deployment artifacts; passthrough/bin metadata |
| `organism` / `antimicrobial` | `PLUGIN_SPECIFIC` | Internal deployment scanner/selection logic |
| `pathogen`, `culture`, `infection_site`, `severity` | `UNRESOLVED` | No confirmed artifact mapping |

SOAR remains `UNRESOLVED` overall because each deployment’s runtime requirements are dynamic and no complete canonical-to-artifact adapter is established.

## 2. ARMD Status: PASS

### Runtime reality

`ARMDPredictionEngine` passes the request payload to `ARMDAdapter.predict_all_antibiotics()`.

The actual pipeline is:

`raw payload -> FEATURE_WHITELIST -> cleaning/imputation -> age_group dummy encoding -> feature alignment -> scaling -> model prediction`

The existing WP4 whitelist contains 32 raw fields. `preprocess_patient_features()` keeps only whitelist keys, uses saved dummy columns for `age_group`, applies existing imputation, and `build_feature_frame()` aligns to each antibiotic model’s feature list.

### Artifact evidence

- `feature_order.json` contains 36 preprocessed columns, including six `age_group_*` columns.
- Twenty ARMD model metadata files were inspected.
- Each reports 56 model features.
- The 56 model features are internal runtime/model features, not 56 frontend form fields.

### Corrected exposed schema

The ARMD schema now exposes the raw whitelist-level payload fields only. It identifies:

- clinician/platform-level raw inputs;
- derived `age_group` and `log_days_since_abx` values;
- encoded age-group columns as internal;
- the 56-feature model vector as `MODEL_INTERNAL` metadata.

Fields previously exposed but absent from the whitelist, including `weight` and `egfr`, were removed from the exposed ARMD input schema. Generic `prior_antibiotics`, `recent_hospitalization`, and `organism` aliases are not treated as confirmed runtime inputs because the runtime consumes separate engineered fields.

### ARMD classifications

- Raw whitelist values: `CLINICIAN_ENTERED`, `PLATFORM_SUPPLIED`, or `UNRESOLVED` depending on source ownership, with no derived features exposed as generic form fields.
- `age_group`: `DERIVED`.
- `log_days_since_abx`: `DERIVED`.
- `age_group_*`: `ENCODED` / `MODEL_INTERNAL`.
- Per-antibiotic 56-feature vectors: `MODEL_INTERNAL`.
- `prior_antibiotics`: `PLUGIN_SPECIFIC`; no proven boolean-to-count transformation exists.
- `infection_site`: `UNRESOLVED`; no confirmed whitelist transformation exists.
- `organism`: `CONFLICT` with the historical aggregate runtime fields; no string-to-history transformation exists.

ARMD status is `PASS` for the stabilized exposed contract and executed runtime tests, with unresolved clinical mappings retained rather than guessed.

## 3. WHO Status: UNRESOLVED

### Query reality

WHO is a `KNOWLEDGE_QUERY_CONTRACT`, not a prediction contract.

The actual query models are:

- `SearchQuery(query_text, entity_type, pagination, sort, extra)`;
- `KnowledgeQuery(entity_type, identifier, filters, pagination, sort, extra)`.

`WHOProvider` supports `disease`, `guideline`, and `recommendation` retrieval for `KnowledgeQuery`, and text search for `SearchQuery`. The provider metadata includes disease, recommendation, diagnostic, monitoring, pathogen, evidence, stewardship, follow-up, and referral entities.

The repository supports exact identifier lookups, disease name/description `ILIKE` search, disease listing, recommendation lookup, and complete guideline relationships. Generic execution of `filters`, pagination, and sort was not established in the inspected repository methods and remains `UNRESOLVED`.

### Read-only database inspection

Two configured PostgreSQL targets were inspected using metadata APIs and read-only `SELECT` queries only:

- `WHO_DATABASE_URL`: contains populated WHO tables: `diseases` (7), `drugs` (13), `evidence` (91), `recommendations` (43), `pathogens` (9), `diagnostics` (46), `stewardship` (34), `monitoring` (6), `follow_up` (10), plus relationship tables.
- `DATABASE_URL`: application-selected database; it contains application/governance tables but no WHO `diseases` table.

A real repository search through the application’s `SessionLocal` failed with PostgreSQL `UndefinedTable: relation "diseases" does not exist`. Therefore the WHO data exists at the separately configured WHO target, but the application-selected session is not proven to route to it.

No WHO database writes were performed.

### Corrected exposed schema

The WHO schema now exposes `SearchQuery` and `KnowledgeQuery` under `x-contract-kind: knowledge_query`. It no longer exposes diagnosis/severity/infection-site/patient-form fields as prediction inputs.

WHO status remains `UNRESOLVED` because database routing for the application runtime is not stable or explicitly resolved.

## 4. Canonical Mapping Status

| Concept | SOAR | ARMD | WHO | Overall |
| --- | --- | --- | --- | --- |
| `age` / `Age` | `CONFIRMED` artifact field, but no canonical adapter | `TRANSFORMED` to age-group encoding | Not a core WHO query field | `UNRESOLVED` for cross-plugin composition |
| `infection_site` | `UNRESOLVED`; no mapping to `BodyLocation_Group` established | `UNRESOLVED`; absent from confirmed whitelist transformation | Not a generic query field; disease metadata is not equivalent | `UNRESOLVED` |
| `organism` | `PLUGIN_SPECIFIC` deployment selection context | `CONFLICT`; runtime uses historical organism aggregates | Distinct from query entity/pathogen records | `CONFLICT` |
| `pathogen` | `UNRESOLVED` routing/context field | No confirmed runtime input | Populated WHO entity type/data relationship | `UNRESOLVED` |
| `species` | Artifact/deployment context not proven as canonical organism | Not a confirmed ARMD input | Not a query parameter in repository methods | `UNRESOLVED` |
| `severity` | No artifact/runtime mapping | No direct model feature | Recommendation database column/refinement | `UNRESOLVED` across contracts |
| `population` | No artifact/runtime mapping | No direct model feature | Recommendation database column/refinement | `PLUGIN_SPECIFIC` to WHO records |
| `culture` | No confirmed artifact/runtime mapping | No confirmed runtime mapping | Not a query parameter | `PLUGIN_SPECIFIC` / `UNRESOLVED` |
| `prior_antibiotics` | No confirmed SOAR mapping | Engineered ARMD exposure history only | Not a WHO query parameter | `PLUGIN_SPECIFIC` |

The composer requires canonical identity, compatible type, unit, enum, clinical semantics, and compatible mapping classification. `UNRESOLVED`, `CONFLICT`, and plugin-specific fields do not merge. Incompatible fields are namespaced and recorded with provenance/conflict reasons.

## 5. Confirmed Corrections Applied

1. SOAR exposed schema now reflects real deployment artifact feature names and variants.
2. SOAR deployment ownership is represented as internal plugin logic.
3. ARMD exposed schema now reflects the raw WP4 whitelist rather than a generic patient placeholder schema.
4. ARMD derived, encoded, and model-internal features are metadata, not generic UI fields.
5. WHO is explicitly represented as a knowledge-query contract.
6. The composer supports SOAR `oneOf` deployment variants and does not drop their properties.
7. Unresolved fields cannot merge automatically.
8. Stale ARMD tests were corrected to the actual immutable `PredictionRequest.payload`, `PluginHealth.healthy`, and `PluginMetadata.plugin_name` interfaces.
9. WHO empty search/criteria behavior and non-iterable mock repository fallback were corrected without changing database contents.

No model artifact or preprocessing implementation was changed.

## 6. Test Results

Project environment was configured at `.venv` and restored with `pytest<9` and `jsonschema`.

Executed command:

`\.venv\Scripts\python.exe -m pytest apps/api/tests/test_who_knowledge_plugin.py apps/api/tests/test_plugin_input_schema_contract.py apps/api/app/plugins/prediction/armd/tests/test_armd_plugin.py -q`

Result: **PASS — 58 passed**.

Coverage includes:

- SOAR, ARMD, and WHO discovery;
- all schema composition combinations;
- Draft 2020-12 schema validation;
- SOAR artifact-backed schema assertions;
- ARMD runtime artifact loading and prediction;
- WHO plugin query/search behavior;
- WHO contract separation;
- provenance and conflict behavior.

Warnings remain from Pydantic compatibility, SHAP, `datetime.utcnow()`, and serialized XGBoost model loading. They did not fail the focused suites.

Real WHO repository query through application `DATABASE_URL`: **FAIL / UNRESOLVED**, because the application-selected database lacks the WHO tables. The separately configured `WHO_DATABASE_URL` was inspected read-only and contains the populated WHO data.

## 7. Remaining Risks

- Application database-session routing between `DATABASE_URL` and `WHO_DATABASE_URL` is unresolved.
- SOAR has no complete canonical-to-deployment adapter; deployment feature names remain dynamic.
- No deterministic, clinically validated `infection_site` normalization is established.
- `organism`, `pathogen`, and `species` remain semantically distinct.
- ARMD high-level aliases do not have proven transformations into exposure/history aggregates.
- WHO generic filters, pagination, and sort are modeled but not confirmed as repository-executed filters.
- The API endpoint’s composed schema is technically validated, but the unresolved runtime mappings mean it must not be treated as a frozen clinician-form contract.

## 8. Contract Version

`0.1.0` draft stabilization contract.

The backend contract is not frozen as `1.0.0` because unresolved mappings and WHO application database routing still affect runtime readiness.

## 9. Final Decision

# Frontend Contract Ready = NO

The React frontend must not be reconciled against this contract yet. The next backend work is to resolve WHO application database routing and establish explicit SOAR/ARMD canonical transformations where evidence supports them. No frontend code was modified in this phase.
