# PharmaTrybe Plugin Runtime Contract v1.0.0

Status: FROZEN for the documented plugin-specific runtime boundaries

This backend contract describes runtime reality and exposed schema boundaries. It does not claim clinical validity, external validation, certification, or production approval.

## SOAR

- `plugin_id`: `soar`
- `contract_type`: `prediction`
- Deployment selection: explicit caller/platform routing context validated by the SOAR adapter and exact plugin registry lookup. `organism` and `antimicrobial` remain artifact metadata only; no frontend selector is required.
- Runtime validation: non-empty payload, followed by model `feature_names_in_` or `n_features_in_` validation.
- Deployment variants:
  - Base: `Age`, `YearCollected`, `Region`, `BodyLocation_Group`, `Country`.
  - Beta-lactamase: the base fields plus `Beta_Lactamase_enc`.

| Field | Clinical meaning | Runtime name | UI name | Type | Required | Transformation | Classification | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Age | Patient age | `Age` | `Age` | number | yes | passthrough/scaling in artifact pipeline | `CONFIRMED` | SOAR `feature_schema.json`, `metadata.json` | runtime-supported |
| Collection year | Year collected | `YearCollected` | `YearCollected` | number | yes | numeric scaling | `CONFIRMED` | SOAR `feature_schema.json` | runtime-supported |
| Region | Collection region | `Region` | `Region` | string | yes | one-hot encoding | `TRANSFORMED` | SOAR `feature_schema.json` | runtime-supported |
| Body location group | Specimen/body location group | `BodyLocation_Group` | `BodyLocation_Group` | string | yes | one-hot encoding | `TRANSFORMED` | SOAR `feature_schema.json` | runtime-supported |
| Country | Collection country | `Country` | `Country` | string | yes | target encoding | `TRANSFORMED` | SOAR `feature_schema.json` | runtime-supported |
| Beta-lactamase encoding | Deployment-specific encoded feature | `Beta_Lactamase_enc` | `Beta_Lactamase_enc` | number | variant-dependent | passthrough/bin | `TRANSFORMED` | SOAR `feature_schema.json` | runtime-supported for some deployments |
| Organism | Deployment selection context | internal deployment metadata | none | string | no | scanner matching | `PLUGIN_SPECIFIC` | `DeploymentScanner`, `DeploymentRegistry` | not a model feature |
| Pathogen | Support/routing context | none confirmed | none | string | no | none established | `UNRESOLVED` | plugin `supports()` | not a confirmed runtime input |
| Infection site | Clinical site | none confirmed | none | string | no | no mapping to `BodyLocation_Group` established | `UNRESOLVED` | artifact/runtime comparison | unresolved |
| Severity | Clinical severity | none confirmed | none | string | no | none established | `UNRESOLVED` | artifact/runtime comparison | unresolved |
| Culture | Culture observation | none confirmed | none | string | no | none established | `PLUGIN_SPECIFIC` | artifact/runtime comparison | no confirmed runtime use |

Derived/encoded model columns are not generic clinician inputs. Exact deployment feature sets remain dynamic.

## ARMD

- `plugin_id`: `armd`
- `contract_type`: `prediction`
- Raw payload is filtered by the WP4 `FEATURE_WHITELIST`.
- Existing preprocessing performs cleaning/imputation, saved `age_group` dummy encoding, feature alignment, scaling, and prediction.
- `feature_order.json` contains 36 preprocessed fields; inspected model metadata contains 56 model features per model package.

Raw whitelist fields are the runtime input surface. The schema marks derived and model-internal values separately. `age_group`, `log_days_since_abx`, and `age_group_*` encoded columns are not direct clinician form fields. High-level aliases such as `prior_antibiotics`, `recent_hospitalization`, and `organism` are not asserted as deterministic mappings to engineered fields.

| Field | Clinical meaning | Runtime name | UI name | Type | Required | Transformation | Classification | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Age | Patient age | `age` | `age` | numeric | runtime accepts optional payload key | derives `age_group` and encoded bins | `TRANSFORMED` | WP4 preprocessing, feature order | runtime-supported |
| Age group | Age band | `age_group` | none | string | no | one-hot encoding | `DERIVED` | WP4 preprocessing | internal |
| Encounter/context fields | Encounter and care context | whitelist fields | same raw names | numeric/binary | optional to adapter | imputation/alignment | `CONFIRMED` | `FEATURE_WHITELIST` | runtime-supported |
| Lab/vital fields | Patient measurements | whitelist fields | same raw names | numeric | optional to adapter | imputation/alignment/scaling | `CONFIRMED` | `FEATURE_WHITELIST` | runtime-supported |
| Antibiotic history | Exposure history | `n_prior_meds`, `n_prior_classes`, timing/count fields | same raw names | numeric | optional to adapter | imputation/alignment/scaling | `PLUGIN_SPECIFIC` | WP4 whitelist/preprocessing | no proven boolean alias |
| Organism history | Historical organism exposure | `n_prior_organisms`, `days_since_last_prior_organism` | same raw names | numeric | optional to adapter | imputation/alignment/scaling | `PLUGIN_SPECIFIC` | WP4 whitelist/preprocessing | no string alias proven |
| `age_group_*` | Encoded age bands | `age_group_*` | none | numeric | no | one-hot encoding | `MODEL_INTERNAL` | `feature_order.json` | internal |
| Model vector | Antibiotic-specific feature vector | 56 model features | none | numeric | generated | alignment and scaling | `MODEL_INTERNAL` | model metadata and `features.json` | internal |
| Infection site | Clinical site | none confirmed | none | string | no | no deterministic transform | `UNRESOLVED` | whitelist/preprocessing comparison | unresolved |

## WHO

- `plugin_id`: `who_knowledge`
- `contract_type`: `knowledge_query`
- WHO is not a prediction input contract.
- `SearchQuery`: required `query_text`; optional `entity_type`, `pagination`, `sort`, `extra`.
- `KnowledgeQuery`: optional `entity_type`, `identifier`, `filters`, `pagination`, `sort`, `extra`.
- Provider-supported retrieval entity types: `disease`, `guideline`, `recommendation`.
- Database entities include diseases, drugs, recommendations, pathogens, evidence, diagnostics, stewardship, monitoring, follow-up, and referrals.
- `filters`, pagination, and sort exist in query models, but generic execution was not confirmed in repository methods.

The configured `WHO_DATABASE_URL` contains populated WHO tables. The application-selected `DATABASE_URL` does not contain the WHO tables, so application database routing is unresolved.

## Canonical Mapping Rules

The registry uses exactly these classifications:

- `CONFIRMED`
- `TRANSFORMED`
- `PLUGIN_SPECIFIC`
- `CONFLICT`
- `UNRESOLVED`

`organism`, `pathogen`, and `species` remain distinct. `infection_site` remains unresolved across prediction plugins. `severity` and `population` are not equivalent; WHO uses them as recommendation record metadata, not prediction features. `prior_antibiotics` remains ARMD-specific because no shared transformation was proven.

## Composition Rules

The composer may merge fields only when canonical identity, clinical semantics, type, unit, allowed values, constraints, transformation semantics, and classification are compatible. `UNRESOLVED`, `CONFLICT`, and `PLUGIN_SPECIFIC` fields never merge automatically. Incompatible fields are namespaced and retain provenance/conflict records. SOAR deployment variants are expanded without treating variant-only requirements as universally required.

## Runtime Validation

The existing `GET /api/v1/pipeline/schema` endpoint exposes composed schema, canonical metadata, plugin mappings, runtime mappings, provenance, and conflicts. Composed schemas declare JSON Schema Draft 2020-12.

## Contract Status

This contract is `FROZEN` version `1.0.0` for plugin runtime boundaries. Unresolved clinical mappings are explicitly unsupported and do not alter the public plugin contracts.
