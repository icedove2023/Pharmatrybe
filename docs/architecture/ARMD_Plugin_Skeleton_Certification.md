# ARMD Plugin Skeleton Certification

## Overview

This document certifies the ARMD plugin skeleton located at:

- apps/api/app/plugins/prediction/armd/

Stage 2A objective: confirm that the plugin structure matches the certified
SOAR plugin architecture where appropriate, provide ARMD-specific placeholders,
and verify the directory is structurally ready for migration (no implementation).

## Directory tree (current)

- apps/api/app/plugins/prediction/armd/
  - plugin.yaml
  - __init__.py
  - armd_prediction_plugin.py
  - runtime_context.py
  - preprocessing.py
  - artifact_loader.py
  - model_registry.py
  - prediction_engine.py
  - ranking.py
  - explainability.py
  - audit.py
  - contracts/
    - __init__.py
    - schemas.py
  - tests/
    - __init__.py
    - test_structure.py

## Purpose of every file

- `plugin.yaml`: plugin manifest for discovery and configuration.
- `__init__.py`: package marker.
- `armd_prediction_plugin.py`: plugin entrypoint — plugin registration and adapter to the platform plugin API (placeholder).
- `runtime_context.py`: runtime lifecycle, health checks, and plugin metadata (placeholder consistent with SOAR runtime_context).
- `preprocessing.py`: ARMD-specific feature conversion and input validation (placeholder only).
- `artifact_loader.py`: filesystem/package artifact loader; declares expected artifact types and metadata mapping.
- `model_registry.py`: local deployment registry and lightweight index for ARMD artifacts (structural placeholder mirroring SOAR's registry functionality).
- `prediction_engine.py`: orchestrates inference calls into the core `WP4_Decision_Engine` backend (placeholder; no legacy code migrated).
- `ranking.py`: ARMD-specific candidate ranking and prioritization placeholder.
- `explainability.py`: structured explainability adapter placeholder to map SHAP outputs to ARMD response shapes.
- `audit.py`: structural audit helpers for certification and environment checks (placeholder; non-invasive).
- `contracts/`: package containing ARMD request/response contract definitions and mapping helpers.
  - `schemas.py`: placeholder dataclasses for ARMD request/response DTOs.
- `tests/`: lightweight structural tests to validate the presence of required files for Stage 2A.
  - `test_structure.py`: asserts the expected skeleton files/dirs exist.

## Comparison with SOAR

SOAR key files (for reference):
- `artifact_registry.py`, `artifact_categories.yaml` — artifact classification/discovery
- `deployment_scanner.py`, `deployment_registry.py` — deployment discovery and indexing
- `model_loader.py` — lazy model loading and caching
- `prediction_engine.py` — prediction orchestration
- `explainability_adapter.py` — explainability conversion
- `runtime_context.py`, `soar_prediction_plugin.py` — runtime lifecycle and plugin entrypoint

Mapping notes:
- ARMD includes `prediction_engine.py` and `runtime_context.py` matching SOAR responsibilities.
- ARMD's `artifact_loader.py` and `model_registry.py` correspond to SOAR's `artifact_registry.py` and `deployment_registry.py`/`deployment_scanner.py` responsibilities.
- ARMD's `explainability.py` mirrors `explainability_adapter.py` in SOAR.
- `plugin.yaml` and `armd_prediction_plugin.py` provide the plugin manifest and entrypoint similar to `soar_prediction_plugin.py`.

Differences:
- SOAR contains `artifact_categories.yaml` for classification; ARMD currently relies on `artifact_loader.py` and may require an equivalent categories file later (decided in Phase 2 of migration).
- SOAR exposes `model_loader.py` for lazy-loading pattern; ARMD's `model_registry.py` is the structural placeholder — consider adding a `model_loader` module if later needed for identical lazy-loading semantics.

## Responsibilities unique to ARMD

- `ranking.py`: patient/treatment candidate ranking is domain-specific to ARMD and not part of SOAR baseline.
- `contracts/`: ARMD needs domain schemas (clinical request/response shapes, structured explainability) that map onto the platform plugin contract.
- `audit.py`: certification scaffolding for ARMD-specific runtime checks (non-SOAR specific helper).

## Responsibilities inherited from SOAR

- Artifact discovery and classification (artifact_loader ↔ artifact_registry)
- Deployment registration and model indexing (model_registry ↔ deployment_registry)
- Lazy loading and caching semantics for large artifacts (planned to mirror `model_loader`)
- Prediction orchestration and explainability conversion (prediction_engine ↔ prediction_engine; explainability.py ↔ explainability_adapter)
- Plugin lifecycle and health (runtime_context ↔ runtime_context)

## Structural issues found and fixes applied

- Missing ARMD-specific structural placeholders were added for `ranking.py`, `explainability.py`, `audit.py`, `contracts/`, and `tests/`. These files are intentionally skeletons (no legacy WP4/WP5 logic).
- Recommendation: if migration later requires 1:1 lazy-load semantics, add a `model_loader.py` that follows the same API shape as SOAR's `model_loader.py` to minimize friction.

## Certification: readiness confirmation

- The ARMD plugin skeleton now contains placeholders for all expected responsibilities and matches SOAR architecture where appropriate.
- ARMD-unique responsibilities are separated into their own modules (`ranking.py`, `contracts/`, `audit.py`).
- No legacy WP4/WP5 implementation was migrated into this skeleton.

Conclusion: The ARMD plugin skeleton is structurally ready for Stage 2B (migration of legacy implementations). Follow-up tasks:

- Phase 2 planning: map specific ARMD artifacts to SOAR `artifact_categories.yaml` or extend it.
- Implement `model_loader.py` if precise lazy-loading semantics are required.


Document produced by automated certification tooling (Stage 2A).