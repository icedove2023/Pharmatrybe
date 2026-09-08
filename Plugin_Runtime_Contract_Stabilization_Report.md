# Plugin Runtime Contract Stabilization Report

## Scope

Backend-only stabilization of SOAR, ARMD, WHO, schema discovery/composition, focused tests, and the versioned runtime contract. React/frontend code, model artifacts, ARMD preprocessing, and WHO database contents were not modified.

No clinical validity, external validation, certification, or production approval is claimed.

## SOAR Verdict: PASS WITH UNRESOLVED LIMITATIONS

SOAR deployment selection is internal plugin logic. `DeploymentRegistry` scans deployments; `organism` and `antimicrobial` are parsed from deployment names and used to select a deployment. If no match exists, the first valid deployment is selected. No frontend deployment selector was found in the targeted frontend search.

Ten deployments were inspected. Persisted artifact metadata shows two runtime variants:

- `Age`, `BodyLocation_Group`, `Region`, `Country`, `YearCollected`;
- the same fields plus `Beta_Lactamase_enc`.

`PredictionEngine` requires a non-empty payload and then enforces model `feature_names_in_` or `n_features_in_`. Artifact transformations include numeric scaling, one-hot encoding, target encoding, and deployment-specific passthrough/bin handling.

The exposed schema now represents deployment-specific `anyOf` contracts. It keeps encoded/model fields distinct from internal deployment selection metadata. Generic `pathogen`, `infection_site`, `severity`, and `culture` mappings remain unresolved or plugin-specific rather than being presented as confirmed model inputs.

## ARMD Verdict: PASS

ARMD accepts a payload, filters it through WP4 `FEATURE_WHITELIST`, performs existing cleaning/imputation and `age_group` dummy encoding, aligns to each antibiotic package feature list, scales, and predicts.

The whitelist contains the raw runtime fields. `feature_order.json` contains 36 preprocessed fields, and inspected model metadata contains 56 features per model package. Derived, encoded, and model-internal features are not treated as generic frontend form fields.

The exposed schema now represents raw whitelist fields and labels `age_group`, `log_days_since_abx`, encoded age bins, and 56-feature vectors as derived/model-internal metadata. Existing preprocessing was not changed.

## WHO Verdict: UNRESOLVED

WHO is a `knowledge_query` contract, not a prediction input contract.

- `SearchQuery`: required `query_text`; optional `entity_type`, pagination, sorting, and extra metadata.
- `KnowledgeQuery`: optional `entity_type`, `identifier`, filters, pagination, sorting, and extra metadata.
- Provider retrieval supports disease/guideline/recommendation contexts and populated related knowledge entities.

Read-only inspection of `WHO_DATABASE_URL` found populated WHO tables: diseases (7), drugs (13), evidence (91), recommendations (43), pathogens (9), diagnostics (46), stewardship (34), monitoring (6), follow-up (10), and relationship tables.

The application-selected `DATABASE_URL` lacks the WHO tables. A real repository search through the application session failed with PostgreSQL `UndefinedTable: relation "diseases" does not exist`. Database routing is therefore unresolved.

## Canonical Mapping Verdict: UNRESOLVED

| Concept | Classification | Evidence/status |
| --- | --- | --- |
| `Age` / `age` | `TRANSFORMED` | SOAR artifact age and ARMD age-to-age-group preprocessing are established, but cross-plugin canonical adapter is not frozen |
| `infection_site` | `UNRESOLVED` | No deterministic SOAR/ARMD mapping to `BodyLocation_Group` or a confirmed ARMD site feature |
| `organism` | `CONFLICT` / `PLUGIN_SPECIFIC` | SOAR deployment selection context and ARMD historical aggregate fields are not equivalent |
| `pathogen` | `UNRESOLVED` | WHO pathogen entity data and SOAR routing context do not prove prediction equivalence |
| `species` | `UNRESOLVED` | No explicit cross-plugin mapping established |
| `severity` | `UNRESOLVED` | WHO recommendation metadata does not establish prediction-plugin equivalence |
| `population` | `PLUGIN_SPECIFIC` | WHO recommendation record field, not a prediction input |
| `culture` | `PLUGIN_SPECIFIC` | No confirmed runtime use beyond the prior SOAR placeholder |
| `prior_antibiotics` | `PLUGIN_SPECIFIC` | ARMD uses separate engineered exposure fields; no shared boolean transform proven |

## Schema Composer Verdict: PASS

The composer does not deduplicate by field name alone. It requires canonical identity, compatible type, unit, enum, clinical semantics, and compatible mapping classification. `UNRESOLVED`, `CONFLICT`, and `PLUGIN_SPECIFIC` fields remain separate and are namespaced with provenance/conflict records. SOAR `anyOf` deployment variants are expanded without making variant-only fields universally required.

## Test Verdict: PASS WITH DATABASE ROUTING LIMITATION

Executed in the project `.venv`:

`\.venv\Scripts\python.exe -m pytest apps/api/tests/test_who_knowledge_plugin.py apps/api/tests/test_plugin_input_schema_contract.py apps/api/app/plugins/prediction/armd/tests/test_armd_plugin.py -q`

Result: **58 passed**.

This includes schema discovery, all requested plugin combinations, Draft 2020-12 validation, SOAR contract assertions, ARMD artifact-backed execution, and WHO plugin tests. Warnings remain from Pydantic, SHAP, deprecated UTC timestamps, and serialized XGBoost loading.

A real WHO repository query through the application-selected database was executed and failed because that database lacks WHO tables. The separately configured WHO database was inspected read-only and is populated. This is recorded as an unresolved runtime configuration issue, not hidden.

## Contract Version

`1.0.0` draft stabilization contract: [PLUGIN_RUNTIME_CONTRACT_v1.0.0.md](docs/contracts/PLUGIN_RUNTIME_CONTRACT_v1.0.0.md)

Status: **DRAFT, NOT FROZEN**.

## Remaining Unresolved Issues

- Resolve application routing/session ownership for `WHO_DATABASE_URL` versus `DATABASE_URL`.
- Establish explicit deterministic SOAR/ARMD canonical transformations for `infection_site` if clinically and technically supported.
- Keep `organism`, `pathogen`, and `species` distinct until explicit mapping evidence exists.
- Confirm WHO generic filters, pagination, and sorting execution or remove them from the exposed query contract.
- Decide raw ARMD field ownership between clinician-entered and platform-supplied inputs.
- Confirm SOAR raw input provenance for collection year, region, country, and body location before frontend reconciliation.

## Final Decision

# Frontend Contract Ready = NO

The backend contract is not frozen because WHO application database routing and clinically meaningful cross-plugin mappings remain unresolved. React/frontend reconciliation must not begin.
