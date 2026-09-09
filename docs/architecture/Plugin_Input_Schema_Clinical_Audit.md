# Plugin Input Schema Clinical/Contract Audit

## 1. Executive Summary

This audit reviewed the actual runtime code paths in the current repository, not the declared `input_schema()` methods alone.

The working source of truth is:

- SOAR runtime contract: `SOARPredictionPlugin.predict()` -> `PredictionEngine._preprocess()` -> model `feature_names_in_` / `n_features_in_` requirement.
- ARMD runtime contract: `deployments/ARMD/WP4_Decision_Engine.py` `FEATURE_WHITELIST`, `preprocess_patient_features()`, `build_feature_frame()`, and `load_inference_package()`.
- WHO runtime contract: `WHOService` + `WHOProvider` + `WHOKnowledgeRepository` using `KnowledgeQuery` and `SearchQuery`.

Summary verdicts:

- SOAR: INCORRECT.
- ARMD: INCORRECT.
- WHO: PARTIAL (knowledge-query contract only; not a prediction-model input contract).

CONFIRMED: the current plugin `input_schema()` declarations are intentionally shallow placeholders and do not match the runtime contracts used by the deployed models and repositories.

UNCERTAIN: any final cross-plugin canonical field merging for clinically shared concepts requires clinical review before it becomes a hard governance rule.

INFERRED: the current schema composer is unsafe because it deduplicates by field name alone.

REQUIRES CLINICAL APPROVAL: any final canonical contract that normalizes `organism`, `pathogen`, `culture`, `infection_site`, or `severity` across plugins.

---

## 2. SOAR Audit

### Runtime contract

SOAR is an artifact-based prediction plugin. Its real runtime contract is model-specific and is enforced by the deployed model artifact metadata and preprocessing logic.

Relevant runtime path:

- `apps/api/app/plugins/prediction/soar/soar_prediction_plugin.py`
- `apps/api/app/plugins/prediction/soar/prediction_engine.py`
- `apps/api/app/plugins/prediction/soar/model_loader.py`
- `deployments/SOAR_GSK/.../feature_schema.json`

The real validation happens in `PredictionEngine._preprocess()`:

- if `model.feature_names_in_` exists, the payload must include exactly those names;
- else if `model.n_features_in_` exists, the payload must match the expected number of features;
- else it falls back to sorted keys.

This means the runtime SOAR contract is not a static generic schema.

### Actual runtime input fields

The deployed SOAR models use artifact-level features with names such as:

- `Age`
- `YearCollected`
- `Region`
- `BodyLocation_Group`
- `Country`
- `Beta_Lactamase_enc`

The associated preprocessing may produce encoded features such as one-hot and target-encoded columns; the actual model is sensitive to transformed feature ordering, not a generic questionnaire field list.

The declared SOAR schema exposes:

- `pathogen`
- `culture`
- `infection_site`
- `organism`
- `antimicrobial`
- `severity`

This does not reflect actual runtime model features.

### Required vs optional fields

The real SOAR requirement is dynamic:

- payload must be non-empty;
- selected model determines the required keys (`feature_names_in_` or feature count).

The declared SOAR schema says only `pathogen` is required. That is not the runtime requirement.

### Types, constraints, values

The actual deployed SOAR feature vectors mix:

- numeric fields,
- one-hot encoded categorical features,
- target-encoded categorical features,
- binary variables.

The declared schema uses generic strings and does not represent the actual model contract.

### Conclusion

SOAR schema status: INCORRECT.

Discrepancies:

- runtime contract is deployment-specific, not a single schema;
- declared required field is `pathogen`, but actual model validation is based on `feature_names_in_` or feature count;
- schema field names are placeholders, not the real artifact fields;
- `organism`, `pathogen`, and `infection_site` are not validated as a coherent runtime model contract.

---

## 3. ARMD Audit

### Runtime contract

ARMD is also artifact-based. Its actual runtime contract comes from the deployed WP4 engine and not from the thin plugin schema declaration.

Relevant runtime path:

- `apps/api/app/plugins/prediction/armd/armd_prediction_plugin.py`
- `apps/api/app/plugins/prediction/armd/prediction_engine.py`
- `packages/prediction-framework/adapters/armd_adapter.py`
- `deployments/ARMD/WP4_Decision_Engine.py`

The source of truth is `FEATURE_WHITELIST`, `preprocess_patient_features()`, and `build_feature_frame()`.

### Actual runtime input fields

The runtime feature whitelist includes fields such as:

- `age`
- `gender_male`
- `age_group`
- `inpatient`
- `outpatient`
- `emergency`
- `icu`
- `has_any_procedure`
- `has_urinary_catheter`
- `has_cvc`
- `nursing_home_visit`
- `creatinine`
- `bun`
- `wbc`
- `neutrophils`
- `lymphocytes`
- `lactate`
- `procalcitonin`
- `heartrate`
- `resp_rate`
- `temperature`
- `sys_bp`
- `dias_bp`
- `n_prior_meds`
- `n_prior_classes`
- `days_since_last_antibiotic`
- `log_days_since_abx`
- `n_abx_classes_exposed`
- `n_prior_organisms`
- `days_since_last_prior_organism`
- `adi_score`
- `adi_state_rank`

The declared ARMD schema exposes only:

- `age`
- `weight`
- `egfr`
- `prior_antibiotics`
- `recent_hospitalization`
- `organism`
- `infection_site`

This is not the runtime contract.

### Required vs optional fields

The real ARMD contract does not use a single fixed required set. It accepts a patient dict, whitelists supported keys, imputes missing values, and aligns the resulting data frame to each model's expected feature list.

This differs materially from the declared schema, which implies a small, generic, high-level patient form.

### Types, constraints, values

ARMD runtime features are dominated by numeric and binary/engineering-transformed fields, not generic open-text organism or infection-site strings. The model outcome is a binary resistance/susceptibility decision based on preprocessed model columns.

### Conclusion

ARMD schema status: INCORRECT.

Discrepancies:

- runtime feature set is broader and more engineered than the declared schema;
- actual preprocessing uses features such as `gender_male`, `age_group`, `has_cvc`, `n_prior_meds`, and `adi_score`;
- declared schema omits several real model features and includes placeholders that are not used in the runtime model contract.

---

## 4. WHO Audit

### Runtime contract

WHO is not a prediction plugin. It is a knowledge plugin backed by a repository and provider layer.

Relevant runtime path:

- `apps/api/app/services/who/who_service.py`
- `apps/api/app/knowledge/providers/who_provider.py`
- `apps/api/app/database/repositories/who_knowledge_repository.py`
- `apps/api/app/knowledge/providers/query_models.py`

The actual query types are:

- `KnowledgeQuery(entity_type, identifier, filters, pagination, sort, extra)`
- `SearchQuery(query_text, entity_type, pagination, sort, extra)`

### WHO knowledge-query inputs

The WHO runtime needs:

- disease or guideline lookup by `entity_type` and `identifier`;
- disease search by `query_text`;
- optional filters and metadata such as `pagination`, `sort`, and repository-level filters;
- disease/recommendation retrieval context such as population and severity represented inside the knowledge model records.

This is a knowledge-query contract, not a prediction input schema.

### WHO declared schema

The declared schema exposes:

- `diagnosis`
- `severity`
- `infection_site`
- `population`
- `query`

This is a UI-oriented approximation for a simple knowledge lookup, but it is not the actual runtime contract used by the WHO repository and provider.

### Distinction: WHO knowledge-query inputs vs prediction-model inputs

WHO knowledge-query inputs are not prediction-model inputs.

Prediction-model inputs are patient and resistance features used by SOAR/ARMD.

WHO knowledge inputs are repository-level queries for disease, recommendation, and evidence lookup.

### Conclusion

WHO schema status: PARTIAL.

The current WHO schema is only partially useful as a UX hint; it does not reflect the actual runtime knowledge contract and it incorrectly blurs the boundary between knowledge lookup and prediction models.

---

## 5. Runtime vs Schema Discrepancies

| Plugin | Runtime requirement | Declared schema | Status |
| --- | --- | --- | --- |
| SOAR | Model-specific payload keys from deployed artifact `feature_names_in_` | `pathogen`, `culture`, `infection_site`, `organism`, `antimicrobial`, `severity` | INCORRECT |
| ARMD | WP4 `FEATURE_WHITELIST` + preprocessing + feature alignment | `age`, `weight`, `egfr`, `prior_antibiotics`, `recent_hospitalization`, `organism`, `infection_site` | INCORRECT |
| WHO | `KnowledgeQuery` / `SearchQuery` + disease metadata lookup | `diagnosis`, `severity`, `infection_site`, `population`, `query` | PARTIAL |

Concrete discrepancies:

- SOAR runtime uses deployment-specific feature names and ordering; declared schema is generic and not model-accurate.
- ARMD runtime uses engineered features like `gender_male`, `age_group`, `has_cvc`, `n_prior_meds`, `adi_score`; declared schema omits them.
- WHO runtime uses knowledge-retrieval structures; declared schema is a patient-diagnosis form that is not how the repository is queried.

---

## 6. Canonical Clinical Field Mapping

This section does not assume same-named fields are equivalent.

| canonical_field_id | clinical meaning | SOAR mapping | ARMD mapping | WHO mapping | type | unit | allowed values | compatibility | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| age | patient age | model `Age` | `age` and `age_group` | not a core clinical knowledge field | integer | years | 0-120, with bins | compatible with transformation | SAFE_TO_SHARE |
| infection_site | site of infection | generic string | runtime `BodyLocation_Group` and site-related engineered variables | disease/infection site metadata | string / categorical | n/a | site names or grouped categories | not equal without normalization | SHARE_WITH_TRANSFORMATION |
| organism | causative organism | deployment `species` / generic `organism` | generic placeholder; not real model feature | pathogen list in WHO disease packages | string | n/a | pathogen names | semantic mismatch across contexts | SEMANTIC_CONFLICT |
| pathogen | pathogen class or species | deployment lookup context | not actual runtime feature | `PathogenKnowledge` objects | string | n/a | taxonomy/species values | not equivalent to `organism` without explicit mapping | SEMANTIC_CONFLICT |
| severity | clinical severity | generic placeholder | not direct runtime model field | recommendation severity metadata | string | n/a | mild/moderate/severe or richer grading | context-dependent | SHARE_WITH_TRANSFORMATION |
| culture | culture / microbiology result | placeholder | not direct runtime feature | not a core WHO query field | string / boolean-like | n/a | culture result or specimen type | plugin-specific | PLUGIN_SPECIFIC |
| prior_antibiotics | recent antibiotic exposure | not a SOAR model field | exposure counts and timing variables | not a WHO knowledge query field | integer / boolean | count / days | non-negative integers, exposure flags | plugin-specific | PLUGIN_SPECIFIC |

Important: field identity must be based on semantics and transformation rules, not on a shared name alone.

---

## 7. Schema Composition Audit

The composer is implemented in `apps/api/app/plugins/schema/composer.py`.

It merges plugin properties by field name, tracks provenance, and merges types heuristically. This is unsafe because:

- same field name can represent different clinical meaning across plugins;
- `infection_site` may not be semantically identical across SOAR, ARMD, and WHO;
- required-field unions are not clinically meaningful when semantics differ;
- deduplication by field name alone is not enough for safe form composition.

CONFIRMED: the current composer is unsafe for a shared canonical form contract unless it uses canonical field identity and compatibility checks instead of name equality alone.

---

## 8. Required Corrections

The required correction is not a frontend redesign; it is a backend contract correction.

1. Stop treating `input_schema()` as the canonical runtime contract for SOAR and ARMD.
2. Distinguish runtime model fields from UI fields and knowledge-query fields.
3. Require explicit canonical field identity before schema composition.
4. Reject deduplication on field name alone when type, unit, enum, or clinical meaning differs.
5. Keep WHO as a knowledge-query plugin and do not merge it into a prediction-model field set without explicit transformation and clinical review.

---

## 9. Validation Results

This audit is validated against the repository code and artifact structure, not by assuming the schema declarations are correct.

The evidence includes:

- SOAR runtime model feature validation in `PredictionEngine._preprocess()`;
- ARMD preprocessing and feature whitelist in `WP4_Decision_Engine.py`;
- WHO runtime retrieval objects in `KnowledgeQuery` and `SearchQuery`.

The minimal focused test file is:

- `apps/api/tests/test_plugin_input_schema_contract.py`

This test is intentionally narrow and documents that the live schema declarations do not equal the actual runtime contracts.

---

## 10. Frontend Contract Readiness

Single-plugin forms: PARTIAL.

Multi-plugin composed forms: NOT READY.

Reason: the backend does not yet have a canonical, semantically validated field registry and compatibility gate. Name-only deduplication is unsafe.

The next task should reconcile the frontend against an audited canonical backend contract, but this task stops at the audit and contract definition.

---

## 11. Open Clinical/Contract Questions

- Is `infection_site` clinically equivalent across SOAR, ARMD, and WHO, or must it remain a transformed canonical field?
- Are `organism`, `pathogen`, and `species` interchangeable, or do they require distinct canonical identities?
- Should global `severity` be shared across plugins or normalized into a controlled vocabulary before use?
- Should WHO knowledge filters remain a separate knowledge-only query contract instead of a merged prediction-form contract?

REQUIRES CLINICAL APPROVAL: any final canonical identity for shared clinical concepts before the backend contract is enforced as a hard form contract.

---

### Final verdict

- SOAR: INCORRECT
- ARMD: INCORRECT
- WHO: PARTIAL
- Schema composer deduplication by name only: UNSAFE
- Canonical shared field mapping: requires explicit semantic compatibility review

This audit documents the actual runtime truth in the current repository and does not invent unsupported clinical assumptions.
