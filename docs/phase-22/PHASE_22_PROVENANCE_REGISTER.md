# Phase 22 Provenance Register

## ARMD admitted contract

- Contract: `armd@1.0.0` (`armd-direct-clinical-inputs`)
- Owner: PharmaTrybe clinical case contract and ARMD runtime boundary.
- Source artifacts: `docs/contracts/ARMD_RUNTIME_CONTRACT_v1.0.0.md`, `packages/clinical-schemas/clinical-case.schema.md`, and `apps/api/app/plugins/prediction/armd/armd_prediction_plugin.py`.
- Artifact version: `1.0.0`.
- Approval record: Phase 22 repository evidence admission decision, 2026-09-06.
- Frontend authority: direct identity only for the nine admitted raw fields.
- Backend boundary: cleaning, imputation, age grouping, encoding, feature alignment, scaling, and prediction remain backend-owned.

## SOAR

No frontend contract is registered. Artifact metadata and feature schemas prove deployment/runtime provenance only. `deployment_id` provenance is explicit caller/platform routing and is excluded from clinical forms.
