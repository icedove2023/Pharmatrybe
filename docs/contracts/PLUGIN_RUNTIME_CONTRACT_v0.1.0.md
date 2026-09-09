# PharmaTrybe Plugin Runtime Contract

**Contract version:** 0.1.0

**Status:** Draft, not frozen

This is a backend runtime contract draft. Runtime code, deployed artifacts, preprocessing, and the populated WHO database are authoritative. It does not claim clinical validity, external validation, certification, production approval, or frontend readiness.

## SOAR

**Plugin identity:** `soar`, prediction, version `0.1.0`.

**Deployment selection:** Plugin-internal backend logic. `DeploymentRegistry` scans deployment directories. `organism` and `antimicrobial` may select matching deployments; otherwise the first valid deployment is selected. The frontend currently has no SOAR deployment/model selector. The frontend is not an authority for deployment selection.

**Deployment contracts:** Ten active deployments were inspected. All use one of these artifact feature sets:

- `Age`, `BodyLocation_Group`, `Region`, `Country`, `YearCollected`
- The same fields plus `Beta_Lactamase_enc`

| Field | Clinical meaning | Plugin | Runtime name | UI name | Type | Required | Allowed values | Transformation | Classification | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Patient age | Age at observation | SOAR | `Age` | `Age` | number | Yes | Artifact-defined numeric | Numeric preprocessing/scaling | `CONFIRMED` | `feature_schema.json`, `metadata.json` | Supported |
| Collection year | Year associated with isolate/observation | SOAR | `YearCollected` | `YearCollected` | number | Yes | Artifact-defined numeric | Numeric preprocessing/scaling | `CONFIRMED` | `feature_schema.json`, `metadata.json` | Supported |
| Region | Dataset/model region category | SOAR | `Region` | `Region` | string | Yes | Artifact categories | One-hot encoding | `TRANSFORMED` | `feature_schema.json` | Supported |
| Body location group | Artifact body-location category | SOAR | `BodyLocation_Group` | `BodyLocation_Group` | string | Yes | Artifact categories | One-hot encoding | `TRANSFORMED` | `feature_schema.json` | Supported |
| Country | Dataset/model country category | SOAR | `Country` | `Country` | string | Yes | Artifact categories | Target encoding | `TRANSFORMED` | `feature_schema.json` | Supported |
| Beta-lactamase encoding | Deployment-specific encoded input | SOAR | `Beta_Lactamase_enc` | `Beta_Lactamase_enc` | number | Variant-dependent | Artifact-defined | Passthrough/bin handling | `TRANSFORMED` | `feature_schema.json` | Supported only for five-feature-plus-beta deployments |
| Organism | Deployment selection context | SOAR | scanner metadata | Not frontend-selected | string | No | Deployment IDs | Internal matching | `PLUGIN_SPECIFIC` | `deployment_scanner.py`, `deployment_registry.py` | Supported internally |
| Antimicrobial | Deployment selection context | SOAR | scanner metadata | Not frontend-selected | string | No | Deployment IDs | Internal matching | `PLUGIN_SPECIFIC` | `deployment_scanner.py`, `deployment_registry.py` | Supported internally |
| Pathogen | Support/routing context | SOAR | No confirmed model field | None | string | No | Unresolved | None established | `UNRESOLVED` | `supports()` and artifact mismatch | Not frozen |
| Culture | Generic clinical placeholder | SOAR | No confirmed model field | None | string | No | Unresolved | None established | `UNRESOLVED` | No artifact/runtime mapping | Not frozen |
| Infection site | Clinical anatomical site | SOAR | Possible relation to `BodyLocation_Group` only | None | string | No | Unresolved | No deterministic adapter established | `UNRESOLVED` | Artifact field is not proof of clinical mapping | Not frozen |
| Severity | Clinical severity | SOAR | No confirmed model field | None | string | No | Unresolved | None established | `UNRESOLVED` | Not in artifact feature metadata | Not frozen |

`PredictionEngine` validates a non-empty payload, then uses model `feature_names_in_` where available, otherwise model feature count or sorted keys. Encoded/model-internal columns must not be inferred as generic clinical concepts.

## ARMD

**Plugin identity:** `armd`, prediction, version `0.1.0`.

**Raw runtime contract:** WP4 accepts dictionary keys in `FEATURE_WHITELIST`, then applies existing preprocessing, imputation, `age_group` dummy encoding, model feature alignment, scaling, and prediction. Twenty model metadata packages were inspected; each reports 56 model features. Those model features are internal and are not 56 frontend fields.

| Field | Clinical meaning | Plugin | Runtime name | UI name | Type | Required | Allowed values | Transformation | Classification | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Age | Patient age | ARMD | `age` | `age` | numeric | Runtime accepts optional keys | Non-negative numeric | Also derives `age_group` | `TRANSFORMED` | `FEATURE_WHITELIST`, preprocessing | Supported |
| Sex/context | Existing dataset indicator | ARMD | `gender_male` | `gender_male` | numeric/binary | Optional | Dataset-defined | Imputation/alignment | `PLUGIN_SPECIFIC` | `FEATURE_WHITELIST` | Supported as raw runtime key |
| Encounter context | Encounter indicators | ARMD | `inpatient`, `outpatient`, `emergency`, `icu` | Same raw names | numeric/binary | Optional | Dataset-defined | Imputation/alignment | `PLUGIN_SPECIFIC` | `FEATURE_WHITELIST` | Supported |
| Clinical measurements | Labs/vitals | ARMD | Existing whitelist names | Same raw names | numeric | Optional | Dataset-defined | Imputation/alignment/scaling | `PLUGIN_SPECIFIC` | `FEATURE_WHITELIST` | Supported |
| Prior antibiotic exposure | Historical exposure aggregates | ARMD | `n_prior_meds`, `n_prior_classes`, `days_since_last_antibiotic`, `n_abx_classes_exposed` | Same raw names | numeric | Optional | Dataset-defined | `log_days_since_abx` is derived | `PLUGIN_SPECIFIC` | WP4 preprocessing and whitelist | Supported as aggregates |
| Prior organism history | Historical organism aggregates | ARMD | `n_prior_organisms`, `days_since_last_prior_organism` | Same raw names | numeric | Optional | Dataset-defined | Imputation/alignment | `PLUGIN_SPECIFIC` | `FEATURE_WHITELIST` | Supported as aggregates |
| `age_group` | Age bin | ARMD | `age_group` | Not a direct form field unless supplied as raw runtime input | string | Optional | Artifact bins | One-hot dummy encoding | `DERIVED` | WP4 preprocessing, `feature_order.json` | Internal derivation |
| `log_days_since_abx` | Log antibiotic timing | ARMD | `log_days_since_abx` | Not a direct form field | numeric | Optional | Dataset-defined | Existing preprocessing/feature path | `DERIVED` | `FEATURE_WHITELIST`, feature order | Internal |
| Age-group columns | Encoded age bins | ARMD | `age_group_*` | Not a form field | numeric/binary | No | Saved dummy columns | One-hot encoding | `ENCODED` | `feature_order.json` | Model internal |
| Model vector | Per-antibiotic model features | ARMD | 56 model features | Never a generic form | numeric | Model-specific | `features.json` | Alignment and scaling | `MODEL_INTERNAL` | Per-package metadata | Internal |
| Weight / eGFR | High-level clinical concepts | ARMD | No whitelist field | None | numeric | No | N/A | No runtime mapping | `UNRESOLVED` | Absent from whitelist | Not exposed |
| Organism | Named organism | ARMD | No string input mapping | None | string | No | N/A | No mapping to history aggregates | `CONFLICT` | Runtime consumes aggregate history fields | Not shared |
| Infection site | Anatomical site | ARMD | No confirmed whitelist mapping | None | string | No | N/A | No deterministic transform | `UNRESOLVED` | Absent from confirmed transformation | Not frozen |

The existing ARMD preprocessing and model artifacts were not changed.

## WHO Knowledge Query

**Plugin identity:** `who_knowledge`, knowledge, version `0.1.0`.

**Contract type:** `knowledge_query`, never prediction input.

### Required and optional query fields

- `SearchQuery.query_text` is required for text search. `entity_type`, pagination, sorting, and `extra` are optional query-model fields.
- `KnowledgeQuery` has no universally required field at the dataclass level. `entity_type` and `identifier` are required by particular retrieval paths: disease/guideline retrieval uses entity type; identifier is required for exact disease/recommendation lookup and optional for list retrieval.
- `filters` exists as a query-model structure, but generic filter execution was not established in the repository path.
- Pagination, sorting, and `extra` exist in query models; generic repository application was not established.

### Supported entities and database evidence

The WHO provider advertises disease, recommendation, diagnostic, monitoring, pathogen, evidence, stewardship, follow-up, and referral entities. The repository implements disease search/listing, exact disease and drug lookup, recommendation lookup, and complete guideline relationship retrieval.

Read-only PostgreSQL inspection of `WHO_DATABASE_URL` found populated tables:

- `diseases`: 7 rows, identifiers and name/description fields;
- `drugs`: 13 rows, identifiers, generic names, AWaRe groups, classes, routes;
- `evidence`: 91 rows;
- `recommendations`: 43 rows, including `population` and `severity` columns;
- `pathogens`: 9 rows;
- `diagnostics`: 46 rows;
- `stewardship`: 34 rows;
- `monitoring`: 6 rows;
- `follow_up`: 10 rows;
- relationship tables for disease/pathogen and recommendation/pathogen.

The application-selected `DATABASE_URL` does not contain the WHO tables. A real repository search through `SessionLocal` failed with `UndefinedTable: relation "diseases" does not exist`. No database writes were performed. Application WHO database routing is therefore `UNRESOLVED`.

WHO database columns such as recommendation `severity` and `population` are record/refinement data, not generic patient prediction inputs. `diagnosis`, `infection_site`, `severity`, and `population` are not exposed as WHO query fields unless supported by the actual query path.

## Canonical Registry and Mapping Rules

Canonical concepts currently registered are `age`, `infection_site`, `organism`, `pathogen`, `severity`, `culture`, and `prior_antibiotics`.

Classifications are exactly:

- `CONFIRMED`: direct runtime/artifact/database evidence.
- `TRANSFORMED`: explicit existing transformation into runtime features.
- `PLUGIN_SPECIFIC`: valid only for a plugin’s internal/runtime context.
- `CONFLICT`: same-looking concepts have incompatible semantics/runtime roles.
- `UNRESOLVED`: evidence is insufficient; no merge or invented mapping is allowed.

`organism`, `pathogen`, and `species` remain distinct. `infection_site` remains unresolved across prediction plugins. `prior_antibiotics` remains ARMD-specific because no shared boolean-to-aggregate transformation is implemented. Demographic concepts `age`, `gender_male`, `age_group`, `Country`, and `Region` are not merged by name.

## Schema Composition

`PluginSchemaComposer` does not deduplicate by name alone. Sharing requires matching canonical identity, type, unit, enum constraints, clinical semantics, and compatible classification. `UNRESOLVED`, `CONFLICT`, and plugin-specific mappings never merge automatically. Conflicts are namespaced and retained in provenance/conflict metadata.

SOAR `anyOf` deployment variants are expanded for composition while their deployment-specific requiredness remains explicit in `x-deployment-contracts`. The existing `GET /api/v1/pipeline/schema` endpoint exposes the composed schema, provenance, conflicts, canonical metadata, canonical mappings, and plugin runtime mappings.

## Runtime Validation

- SOAR: non-empty payload plus artifact model feature-name/count validation.
- ARMD: non-empty payload support plus WP4 whitelist, preprocessing, feature alignment, scaling, and model execution.
- WHO: plugin connection/repository/provider readiness plus query-specific provider/repository behavior.
- JSON Schema: exposed schemas identify Draft 2020-12 and are checked by the focused schema suite.

## Test Evidence

Executed in the repository `.venv`:

`\.venv\Scripts\python.exe -m pytest apps/api/tests/test_who_knowledge_plugin.py apps/api/tests/test_plugin_input_schema_contract.py apps/api/app/plugins/prediction/armd/tests/test_armd_plugin.py -q`

Result: **PASS — 58 passed**.

The suite covers plugin discovery, all schema combinations, Draft 2020-12 validation, real ARMD artifact-backed execution, WHO plugin behavior, and schema provenance/conflict handling. Warnings remain from dependency deprecations and serialized XGBoost loading.

A direct WHO repository query through application `DATABASE_URL` was executed and **FAIL/UNRESOLVED** because that database lacks WHO tables. `WHO_DATABASE_URL` was inspected read-only and is populated.

## Contract Status and Frontend Gate

**Contract version:** `0.1.0`

**Contract status:** Draft stabilization contract, not frozen.

# Frontend Contract Ready = NO

Reasons: unresolved SOAR canonical adapter mappings, unresolved ARMD high-level clinical transformations, unresolved WHO application database routing, and unresolved query-model filter/pagination/sort execution. React/frontend code was not modified. Frontend reconciliation must wait until these backend runtime boundaries are explicitly resolved.
