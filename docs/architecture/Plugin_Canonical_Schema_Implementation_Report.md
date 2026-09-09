# Plugin Canonical Schema Implementation Report

## Status

- PASS: Backend schema implementation is limited to the requested schema, plugin, composer, API, and focused-test surfaces.
- PASS: Edited Python files compile and VS Code reports no diagnostics in the edited files.
- UNRESOLVED: Focused pytest execution was blocked before collection by the installed pytest environment interrupting during `py` / `_pytest._py.path` import.
- UNRESOLVED: Direct Draft 2020-12 validation was unavailable in the selected interpreter because `jsonschema` is not installed there.
- No clinical validity or certification is claimed.

## What Changed

Added `apps/api/app/plugins/schema/clinical_registry.py` as the canonical backend registry. It contains only concepts demonstrated by the current plugin contracts and audit:

- `age`
- `infection_site`
- `organism`
- `pathogen`
- `severity`
- `culture`
- `prior_antibiotics`

Each field records canonical identity, display name, description, data type, unit, and clinical semantics. Explicit plugin mappings use:

`SAFE_TO_SHARE`, `SHARE_WITH_TRANSFORMATION`, `PLUGIN_SPECIFIC`, `SEMANTIC_CONFLICT`, and `UNRESOLVED`.

Plugin schemas now annotate UI/input fields with canonical identity, mapping classification, and runtime mapping metadata. Runtime model features remain metadata and the existing preprocessing/model artifacts were not changed.

## Plugin Mappings

### SOAR

- `pathogen`: deployment lookup/model-specific context, `UNRESOLVED`.
- `culture`: plugin-specific placeholder, runtime mapping not established.
- `infection_site`: `SHARE_WITH_TRANSFORMATION`; deployment `BodyLocation_Group` or equivalent remains unresolved.
- `organism`: `SEMANTIC_CONFLICT` because deployment species/organism context is not established as equivalent to other plugin meanings.
- `severity`: `UNRESOLVED`.
- `antimicrobial`: plugin-specific deployment selection field.
- Deployment feature names and model `feature_names_in_` requirements are exposed as runtime metadata, not generic clinical form fields.

### ARMD

- `age`: `SAFE_TO_SHARE`; maps to `age` and derived `age_group`.
- `infection_site`: `SHARE_WITH_TRANSFORMATION`; the exact engineered site mapping is unresolved.
- `organism`: `SEMANTIC_CONFLICT`; maps only to existing organism-history features such as `n_prior_organisms` and `days_since_last_prior_organism`.
- `prior_antibiotics`: `PLUGIN_SPECIFIC`; maps to existing exposure count/timing features.
- The existing `FEATURE_WHITELIST` is exposed as runtime metadata, including encounter, laboratory, vital-sign, access-device, social-risk, antibiotic-history, organism-history, and engineered age features.
- Existing ARMD preprocessing remains unchanged.

### WHO

WHO is explicitly a `knowledge_query` contract, not a prediction input contract. Its schema represents the existing:

- `SearchQuery`: required `query_text`, optional `entity_type`, `pagination`, `sort`, and `extra`.
- `KnowledgeQuery`: optional `entity_type`, `identifier`, `filters`, `pagination`, `sort`, and `extra`.

WHO query fields are not forced into the prediction schema and have no canonical clinical-field mappings.

## Composition Rules

`PluginSchemaComposer` no longer deduplicates by property name alone. Fields merge only when all of the following are true:

- canonical field IDs match;
- data types match;
- units match;
- enum constraints match;
- clinical semantics match;
- mapping classifications are explicitly compatible.

Incompatible same-name fields are retained under a plugin-qualified name such as `armd__organism`. The conflict record includes the field name, owners, namespaced field, existing/incoming identities, classifications, and reason. Provenance records owners, source field names, canonical identity, classification, and types. Plugin-level provenance is retained for knowledge-only contracts.

The existing `GET /api/v1/pipeline/schema` endpoint remains in place and now exposes `composed_schema`, `schema` for compatibility, `field_provenance`, `conflicts`, `canonical_field_metadata`, `canonical_plugin_mappings`, and `plugin_runtime_mappings`.

The composed schema identifies JSON Schema Draft 2020-12.

## Tests Executed

Focused file updated:

`apps/api/tests/test_plugin_input_schema_contract.py`

Coverage added or retained for:

- SOAR alone;
- ARMD alone;
- WHO alone;
- SOAR + ARMD;
- SOAR + WHO;
- ARMD + WHO;
- SOAR + ARMD + WHO;
- schema discovery;
- canonical IDs and provenance;
- compatible `infection_site` sharing;
- non-silent `organism` conflict preservation;
- WHO knowledge-query separation;
- Draft 2020-12 schema checks;
- unknown and empty plugin selection rejection.

Executable syntax validation passed with `python -m py_compile` over all edited backend and focused-test files. Full focused pytest and runtime JSON Schema checks remain `UNRESOLVED` for the environment limitations stated above.

## Unresolved Clinical Mappings

- SOAR deployment-specific artifact feature transformations cannot be represented as a single static clinical schema.
- The exact canonical normalization for `infection_site` is unresolved.
- `organism`, `pathogen`, and deployment `species` are not treated as interchangeable.
- Severity vocabulary and normalization are unresolved.
- WHO clinical record metadata is not a prediction input mapping.

## Next Task

The next task is to reconcile the actual React frontend dynamic form workflow against this validated backend schema contract. Frontend reconciliation was intentionally not performed in this implementation.
