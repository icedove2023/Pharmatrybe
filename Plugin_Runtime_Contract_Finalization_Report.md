# Plugin Runtime Contract Finalization Report

## 1. Baseline Blockers

The baseline blockers were:

- WHO plugin sessions used application `DATABASE_URL`, while populated WHO data was under `WHO_DATABASE_URL`.
- WHO public schema advertised query-model fields whose repository execution was not confirmed.
- SOAR has deployment-specific artifact contracts and no complete canonical-to-artifact adapter.
- ARMD high-level aliases do not have proven deterministic transformations into engineered features.
- ARMD tests contained stale request and metadata expectations.

## 2. WHO Routing Resolution

Added an explicit WHO database engine/session factory driven by `WHO_DATABASE_URL`. `WHOKnowledgePlugin()` now uses that session when no session is injected; injected sessions remain supported for tests. Owned sessions are closed during shutdown. Non-WHO services continue using `DATABASE_URL`.

Read-only inspection confirmed the WHO database is populated: diseases (7), drugs (13), evidence (91), recommendations (43), pathogens (9), diagnostics (46), stewardship (34), monitoring (6), follow-up (10), and relationship tables.

A real default plugin search for `pneumonia` now succeeds against the configured WHO database. Missing `WHO_DATABASE_URL` raises a clear `RuntimeError`.

Status: **PASS**.

## 3. WHO Query Contract

WHO is explicitly a `knowledge_query` contract, not a prediction input contract.

- `SearchQuery`: required `query_text`; optional `entity_type`.
- `KnowledgeQuery`: `entity_type` required by supported retrieval paths; `identifier` optional for list/retrieval selection.
- Public schema no longer advertises unconfirmed generic filters, pagination, sorting, or extra metadata.
- Confirmed repository behavior includes disease search, disease listing, exact disease/drug lookup, recommendation lookup, and complete guideline relationship retrieval.

Status: **PASS**.

## 4. SOAR Runtime Contract

Ten deployments and their `metadata.json`/`feature_schema.json` files were inspected. Deployment selection is internal plugin logic: scanner metadata parses `organism` and `antimicrobial`; matching deployments are preferred, otherwise the first valid deployment is selected. No frontend SOAR deployment selector was found.

Artifact variants are:

- `Age`, `YearCollected`, `Region`, `BodyLocation_Group`, `Country`;
- the same fields plus `Beta_Lactamase_enc`.

The schema now represents these variants with `anyOf`. Runtime metadata records numeric scaling, one-hot encoding, target encoding, and deployment-specific passthrough/bin behavior. Unsupported generic fields are not presented as confirmed model inputs.

Status: **UNRESOLVED** because deployment selection fallback and canonical-to-artifact input provenance remain insufficient for a frozen universal contract.

## 5. ARMD Runtime Contract

The exposed ARMD schema follows the raw WP4 `FEATURE_WHITELIST`. Existing preprocessing remains unchanged:

`payload -> whitelist -> cleaning/imputation -> age_group encoding -> feature alignment -> scaling -> model prediction`

`feature_order.json` contains 36 preprocessed columns. Inspected per-antibiotic metadata contains 56 model features. Derived, encoded, and model-internal fields are explicitly kept out of generic clinician inputs.

Status: **PASS** for runtime/schema alignment. Remaining clinical ownership and mapping questions remain unresolved.

## 6. Canonical Mapping Decisions

| Concept | Classification | Decision |
| --- | --- | --- |
| `Age` / `age` | `TRANSFORMED` | ARMD derives age-group encodings; SOAR uses artifact `Age`; no frozen cross-plugin adapter |
| `infection_site` | `UNRESOLVED` | No deterministic mapping to SOAR `BodyLocation_Group` or ARMD runtime feature |
| `organism` | `CONFLICT` / `PLUGIN_SPECIFIC` | SOAR deployment context differs from ARMD historical organism aggregates |
| `pathogen` | `UNRESOLVED` | No explicit equivalence with SOAR routing or WHO knowledge entities |
| `species` | `UNRESOLVED` | No explicit cross-plugin mapping |
| `severity` | `UNRESOLVED` | WHO recommendation metadata is not a prediction input scale |
| `population` | `PLUGIN_SPECIFIC` | WHO recommendation record field |
| `culture` | `PLUGIN_SPECIFIC` | No confirmed runtime mapping |
| `prior_antibiotics` | `PLUGIN_SPECIFIC` | ARMD consumes separate exposure counts/timing fields; no shared boolean transformation |

The composer requires canonical identity, clinical semantics, type, units, constraints, transformation semantics, and compatible classification. `UNRESOLVED`, `CONFLICT`, and `PLUGIN_SPECIFIC` fields never merge automatically.

Status: **UNRESOLVED** for cross-plugin clinical mapping.

## 7. ARMD Test/Runtime Drift

The ARMD failures were classified as **STALE TEST** where tests constructed `PredictionRequest()` without required `payload` or expected obsolete `PluginHealth.initialized` / `PluginMetadata.name` attributes. Tests were updated to the authoritative runtime interfaces. No runtime model or preprocessing behavior was changed.

Status: **PASS**.

## 8. End-to-End Verification

- SOAR artifact inspection: **PASS** for 10 deployments and 2 feature variants. Generic end-to-end prediction remains **UNRESOLVED** because no universal canonical payload exists for all deployments.
- ARMD artifact-backed execution: **PASS** through loading, preprocessing, alignment, scaling, and prediction tests.
- WHO read-only database inspection: **PASS**.
- WHO default session routing and populated search: **PASS**.
- WHO missing configuration failure: **PASS**.

No model artifacts or WHO database contents were modified.

## 9. Composition Verification

The focused schema suite covers:

- SOAR alone;
- ARMD alone;
- WHO alone;
- SOAR + ARMD;
- SOAR + WHO;
- ARMD + WHO;
- SOAR + ARMD + WHO;
- provenance and conflict retention;
- WHO query separation;
- Draft 2020-12 schema validation.

Status: **PASS**.

## 10. Actual Test Commands and Results

`\.venv\Scripts\python.exe -m pytest apps/api/tests/test_plugin_input_schema_contract.py apps/api/tests/test_who_knowledge_plugin.py -q`

Result: **PASS — 46 passed**.

`\.venv\Scripts\python.exe -m pytest apps/api/app/plugins/prediction/armd/tests/test_armd_plugin.py -q`

Result: **PASS — 15 passed**.

All edited Python files compiled successfully with `py_compile`. Warnings remain from Pydantic compatibility, SHAP, deprecated UTC timestamps, and serialized XGBoost loading.

## 11. Contract Version and Status

Versioned contract: [PLUGIN_RUNTIME_CONTRACT_v1.0.0.md](docs/contracts/PLUGIN_RUNTIME_CONTRACT_v1.0.0.md)

Contract version: `1.0.0`

Status: **DRAFT, NOT FROZEN**.

## 12. Remaining Risks

- SOAR deployment fallback is not deterministic from a canonical clinical request.
- SOAR raw input provenance for collection year, region, country, and body location is not fully established.
- No deterministic `infection_site` mapping is established.
- `organism`, `pathogen`, and `species` remain semantically distinct.
- ARMD clinician/platform ownership for raw whitelist fields is not fully resolved.
- WHO routing depends on correctly configured `WHO_DATABASE_URL` in each deployment environment.
- WHO query refinements beyond confirmed entity/search/identifier behavior remain unsupported by the public contract.

## 13. Freeze Decision

# Plugin Runtime Contract Frozen = NO

The contract is not frozen because SOAR deployment-specific routing/input provenance and clinically meaningful canonical mappings remain unresolved. WHO routing and query-contract blockers are resolved, but those resolutions do not establish full backend contract stability.

# Frontend Contract Ready = NO

Do not begin React/frontend reconciliation.
