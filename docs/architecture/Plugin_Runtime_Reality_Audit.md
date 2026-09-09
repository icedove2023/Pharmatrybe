# Plugin Runtime Reality Audit

## Scope and Method

This audit inspected only the SOAR, ARMD, WHO, canonical registry, schema discovery/composer, pipeline schema endpoint, focused schema tests, and directly associated artifacts/runtime files. No React/frontend files, model artifacts, preprocessing code, or WHO database contents were modified.

WHO database inspection was read-only. The inspection used SQLAlchemy metadata APIs and `SELECT COUNT(*)` / `SELECT * ... LIMIT 2` only. No `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, or `TRUNCATE` was executed.

No clinical validity, external validation, certification, or production approval is claimed.

## 1. SOAR Runtime Reality

### Actual runtime path

`SOARPredictionPlugin.predict()` selects a deployment, loads its artifacts, and calls `PredictionEngine.predict()`. `PredictionEngine._validate_request()` requires a `PredictionRequest` with a non-empty dictionary payload.

`PredictionEngine._preprocess()` then uses the loaded model artifact:

- If `model.feature_names_in_` exists, every listed model feature must be present in the payload and a DataFrame is created in that exact feature order.
- If `model.n_features_in_` exists, payload length must equal the model feature count.
- Otherwise, payload keys are sorted and used as runtime features.

The engine then calls model prediction/probability methods, extracts the threshold artifact, decodes the prediction, and returns prediction metadata. The generic clinical names in `input_schema()` are not used to construct the artifact feature vector.

### Artifact evidence

Ten SOAR deployment directories were inspected. Their `feature_schema.json` files use two feature sets:

1. `Age`, `YearCollected`, `Region`, `BodyLocation_Group`, `Country`
2. The same five plus `Beta_Lactamase_enc`

The artifact metadata identifies:

- `Age`, `YearCollected`: numeric, `StandardScaler` transformer.
- `Region`, `BodyLocation_Group`: categorical one-hot encoding.
- `Country`: target encoding.
- `Beta_Lactamase_enc`: passthrough/bin category.

The deployments are named using antimicrobial/organism context, for example `Ceftriaxone_Haemophilus_influenzae`. The scanner parses deployment names into `organism` and `antimicrobial` metadata for deployment selection. This does not establish equivalence among `organism`, `pathogen`, or `species` clinical concepts.

### Exposed SOAR fields and evidence classification

| Exposed field | Actual source/runtime field | Transformation | Classification | Evidence |
| --- | --- | --- | --- | --- |
| `pathogen` | No matching artifact feature; used by plugin support/deployment context | No established transform | `UNRESOLVED` | `PredictionEngine._preprocess()` requires artifact names, not `pathogen`; plugin support checks it as a routing key |
| `culture` | No matching artifact feature | None established | `PLUGIN_SPECIFIC` | No use found in the SOAR runtime/artifact feature schemas |
| `infection_site` | Artifact `BodyLocation_Group` may be related | One-hot transformation exists at artifact level, but clinical-to-artifact mapping is not implemented/established | `UNRESOLVED` | Artifact schema proves `BodyLocation_Group`, not that the exposed field maps to it |
| `organism` | Deployment metadata / possible artifact context `species` | No canonical transform established | `CONFLICT` | Deployment scanner uses organism for selection; artifact feature schema does not prove equivalence to `pathogen` |
| `antimicrobial` | Deployment metadata / deployment selection | No generic clinical transformation | `PLUGIN_SPECIFIC` | Deployment scanner parses antimicrobial from deployment ID |
| `severity` | No matching artifact feature | None established | `UNRESOLVED` | Not present in inspected SOAR artifact schemas or preprocessing |

### SOAR contract conclusion

The exposed SOAR schema is a UI-oriented placeholder and is not the deployment/model runtime contract. Runtime requirements are deployment-specific and cannot safely be represented as one generic clinical schema without an explicit adapter/transformer contract.

## 2. ARMD Runtime Reality

### Actual runtime path

`ARMDPredictionEngine.predict()` passes the request payload directly to `ARMDAdapter.predict_all_antibiotics()`. The adapter:

1. Converts the input dictionary to a pandas Series.
2. Calls the existing WP4 `preprocess_patient_features()`.
3. Applies the whitelist.
4. Performs existing imputation and `age_group` dummy encoding.
5. Aligns the result to each antibiotic model package’s `feature_names` using `build_feature_frame()`.
6. Applies the stored scaler.
7. Calls the stored model and threshold.

Missing values are handled by the existing preprocessing/alignment behavior. The plugin schema’s `age` requirement is therefore not the complete model-required feature contract.

### Artifact and preprocessing evidence

The WP4 `FEATURE_WHITELIST` contains 32 raw fields, including:

- `age`, `gender_male`, `age_group`;
- encounter/context fields: `inpatient`, `outpatient`, `emergency`, `icu`;
- procedure/access/social fields;
- laboratory and vital-sign fields;
- antibiotic exposure count/timing fields;
- prior-organism count/timing fields;
- `adi_score` and `adi_state_rank`.

The preprocessing code explicitly:

- keeps only whitelist keys;
- one-hot encodes `age_group` using saved dummy columns when available;
- imputes and aligns data through the existing WP4 path.

`feature_order.json` contains 36 preprocessed columns: the raw numeric/binary features plus six `age_group_*` dummy columns. Twenty ARMD model metadata files were inspected; each reports 56 model features. Model-specific `features.json`/metadata feature names are loaded by `load_inference_package()` and used by `build_feature_frame()`.

### ARMD mapping evidence

| Clinical input | Transformation | Runtime/model feature | Classification | Evidence |
| --- | --- | --- | --- | --- |
| `age` | Direct plus age-group dummy encoding | `age`, `age_group_*` | `TRANSFORMED` | `age_group` dummy logic and `feature_order.json` |
| `weight` | None in inspected whitelist/preprocessing | Not a WP4 whitelist feature | `PLUGIN_SPECIFIC` | Present in exposed schema but absent from `FEATURE_WHITELIST` |
| `egfr` | None in inspected whitelist/preprocessing | Not a WP4 whitelist feature | `PLUGIN_SPECIFIC` | Present in exposed schema but absent from `FEATURE_WHITELIST` |
| `prior_antibiotics` | No boolean-to-count implementation in inspected runtime | `n_prior_meds`, `n_prior_classes`, `days_since_last_antibiotic`, `log_days_since_abx`, `n_abx_classes_exposed` are separate runtime fields | `CONFLICT` | Existing runtime consumes engineered exposure fields; no boolean mapping is implemented |
| `recent_hospitalization` | No single-field mapping | `inpatient`, `outpatient`, `emergency` are separate fields | `CONFLICT` | Existing runtime whitelist has separate encounter indicators |
| `organism` | No string-to-history-count implementation in plugin | `n_prior_organisms`, `days_since_last_prior_organism` | `CONFLICT` | Existing runtime fields are historical aggregates, not a generic organism input |
| `infection_site` | No established transform | No confirmed site feature in the inspected ARMD whitelist | `UNRESOLVED` | The whitelist/preprocessing does not establish a site mapping |

### ARMD contract conclusion

The exposed ARMD schema contains a mixture of valid high-level concepts, fields not consumed by the model path, and fields whose engineered transformations are not implemented by the plugin contract. The runtime model contract remains artifact-specific and preprocessing-owned.

## 3. WHO Plugin, Query, and Database Reality

### Query models and service/provider behavior

The actual query dataclasses are:

- `KnowledgeQuery(entity_type, identifier, filters, pagination, sort, extra)`
- `SearchQuery(query_text, entity_type, pagination, sort, extra)`

`WHOService` creates `KnowledgeQuery` for disease/guideline/recommendation retrieval and `SearchQuery` for disease search. `WHOProvider` supports:

- `KnowledgeQuery` entity types: `disease`, `guideline`, and `recommendation`;
- all `SearchQuery` instances;
- provider entity metadata for `disease`, `recommendation`, `diagnostic`, `monitoring`, `pathogen`, `evidence`, `stewardship`, `follow_up`, and `referral`.

The repository performs exact identifier lookups and disease-name/description search. It retrieves complete guidelines with related pathogens, evidence, diagnostics, stewardship, monitoring, follow-up, referrals, recommendations, drugs, and recommendation pathogens.

### WHO database inspection

Database configuration was present through PostgreSQL configuration (`WHO_DATABASE_URL` or `DATABASE_URL`). Read-only inspection succeeded.

| Table | Columns observed | Rows |
| --- | --- | ---: |
| `diseases` | `disease_id`, `name`, `chapter_number`, `chapter_title`, `care_level`, `description`, `source_pages` | 7 |
| `drugs` | `drug_id`, `generic_name`, `aware_group`, `antibiotic_class`, `route`, `notes` | 13 |
| `evidence` | `evidence_id`, `disease_id`, `type`, `text`, `page` | 91 |
| `recommendations` | identifiers, disease/drug/evidence links, `population`, `severity`, dosing/frequency/duration and criteria fields | 43 |
| `pathogens` | `pathogen_id`, `name` | 9 |
| `diagnostics` | `diagnostic_id`, `disease_id`, `text`, `page` | 46 |
| `stewardship` | `stewardship_id`, `disease_id`, `text`, `page` | 34 |
| `monitoring` | `monitoring_id`, `disease_id`, `text`, `page` | 6 |
| `follow_up` | `follow_up_id`, `disease_id`, `text`, `page` | 10 |

Join tables `disease_pathogens` and `recommendation_pathogens` were present. The database is populated. No table contents were changed.

### WHO exposed contract classification

| Exposed query field | Actual source/query field | Transformation | Classification | Evidence |
| --- | --- | --- | --- | --- |
| `query_text` | Disease name/description search text | SQL `ILIKE` wildcard search | `CONFIRMED` | `SearchQuery` and `WHOKnowledgeRepository.search_diseases()` |
| `entity_type` | Provider-supported entity routing | Provider dispatch | `CONFIRMED` | `WHOProvider.supports()` and `retrieve()` |
| `identifier` | `disease_id` or `recommendation_id` | Exact identifier lookup | `CONFIRMED` | Repository methods and provider retrieval |
| `filters` | `FilterParams` data structure | No generic filter execution found in the inspected WHO repository path | `UNRESOLVED` | Query model exists; repository methods use dedicated arguments instead |
| `pagination` | `PaginationParams` | No pagination execution found in inspected repository methods | `UNRESOLVED` | Query model exists; repository methods shown do not apply it |
| `sort` | `SortParams` | No sort execution found in inspected repository methods | `UNRESOLVED` | Query model exists; repository methods shown do not apply it |
| `extra` | Query metadata/provenance container | Passed as query metadata where applicable | `PLUGIN_SPECIFIC` | Dataclass and provider provenance path |

WHO is therefore a knowledge-query contract, not a prediction-model input contract. The old diagnosis/severity/infection-site/patient-form approximation was not the runtime query contract and was corrected to the `KnowledgeQuery` / `SearchQuery` representation.

## 4. Runtime vs Exposed Contract Comparison

The current path is:

`runtime/artifact/database reality -> plugin runtime mapping -> input_schema() -> canonical registry -> PluginSchemaComposer -> GET /api/v1/pipeline/schema`

Confirmed mismatches corrected in this task state:

1. WHO’s exposed contract now represents `SearchQuery` and `KnowledgeQuery`, including the actual query field structures, instead of a prediction-like diagnosis form.
2. SOAR and ARMD runtime mappings are represented as metadata rather than pretending model features are generic clinical UI fields.
3. `infection_site` is now `UNRESOLVED` for SOAR and ARMD because no actual clinical-to-runtime transformation was established. The composer keeps same-name unresolved fields separate and records a conflict.
4. `organism` and `pathogen` remain distinct; organism mappings are marked conflict/unresolved where the runtime evidence does not establish equivalence.
5. ARMD engineered fields and whitelist information are exposed as runtime metadata without changing preprocessing or artifacts.
6. The existing `/api/v1/pipeline/schema` endpoint now exposes composed schema, canonical metadata, plugin mappings, runtime mappings, provenance, and conflicts.

## 5. Canonical Mapping Evidence

The canonical registry contains only `age`, `infection_site`, `organism`, `pathogen`, `severity`, `culture`, and `prior_antibiotics`.

The registry classifications are conservative:

- `age`: `SAFE_TO_SHARE` only where the runtime mapping is direct or explicitly transformed.
- `infection_site`: `UNRESOLVED` for SOAR/ARMD until a real transform is established.
- `organism`: `SEMANTIC_CONFLICT` across the current plugin contexts.
- `pathogen`: distinct from organism and unresolved for SOAR runtime mapping.
- `severity`: unresolved outside the WHO database’s recommendation metadata context.
- `culture`: SOAR plugin-specific; no ARMD/WHO runtime mapping established.
- `prior_antibiotics`: ARMD-specific; the runtime consumes engineered exposure history, not a proven shared boolean contract.

The composer merges only when canonical identity, JSON type, unit metadata, enum constraints, clinical semantics, and compatible mapping classification all match. `UNRESOLVED`, `SEMANTIC_CONFLICT`, and `PLUGIN_SPECIFIC` fields do not merge. Incompatible same-name fields are namespaced and recorded in conflict/provenance structures.

## 6. Tests and Verification

### Focused schema tests

Command:

`\.venv\Scripts\python.exe -m pytest apps/api/tests/test_plugin_input_schema_contract.py -q`

Result: **PASS — 9 passed**.

The suite covers SOAR alone, ARMD alone, WHO alone, all pair combinations, all three together, discovery, canonical IDs, provenance, conflict preservation, WHO query separation, and JSON Schema Draft 2020-12 checks.

### Smallest relevant existing plugin test

Command:

`\.venv\Scripts\python.exe -m pytest apps/api/app/plugins/prediction/armd/tests/test_armd_plugin.py -q`

Result: **FAIL — 5 failures and 2 setup errors**.

Observed failures are existing test/runtime contract drift, including tests constructing `PredictionRequest()` without its required payload and tests expecting unavailable `PluginHealth.initialized` and `PluginMetadata.name` attributes. These tests were not changed because the task prohibits unrelated runtime/test refactoring.

### Syntax and diagnostics

- Edited backend Python compilation: **PASS**.
- VS Code diagnostics for edited files: **PASS**.
- `git diff --check`: **PASS**.
- Direct Draft 2020-12 validation is executed inside the focused suite: **PASS**.

## 7. Remaining Unresolved Mappings

- SOAR deployment-specific model feature requirements cannot be reduced to one generic clinical input schema.
- No confirmed SOAR `infection_site` to `BodyLocation_Group` adapter exists.
- No confirmed ARMD `infection_site` transform exists.
- `organism`, `pathogen`, and `species` are not proven equivalent.
- ARMD `prior_antibiotics` is not proven equivalent to its multiple exposure count/timing features.
- WHO query `filters`, pagination, sort, and `extra` are represented by query models, but generic repository execution for each was not established.
- WHO clinical recommendation `severity`/`population` are database record fields, not generic prediction input fields.
- Existing ARMD plugin tests remain failing due to unrelated contract drift.

## 8. Frontend Decision

# NOT READY FOR FRONTEND RECONCILIATION

Evidence-based reasons:

- SOAR remains deployment/model-specific and has unresolved mappings for its generic exposed fields.
- ARMD has engineered artifact features and unresolved high-level clinical transformations.
- `infection_site` cannot be shared safely yet.
- Semantic equivalence among organism/pathogen/species is unresolved.
- WHO is stable as a knowledge-query contract but must remain separate from prediction-form composition.
- The focused schema contract passes, but the smallest existing ARMD plugin tests still fail, so broader backend runtime stability is not established.

The next task remains React frontend dynamic-form reconciliation only after these backend mappings and runtime test gaps are resolved. No frontend reconciliation was performed here.
