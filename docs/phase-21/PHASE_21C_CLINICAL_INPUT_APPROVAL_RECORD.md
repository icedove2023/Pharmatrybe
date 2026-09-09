# Phase 21C Clinical Input Approval Record

## Decision date

2026-09-06

## SOAR

- **Plugin ID:** `soar`
- **Decision:** `SOAR_STATUS = NOT_APPROVED`
- **Approving evidence:** Frozen runtime contract and executable tests explicitly require caller/platform routing context and expose no frontend UI inputs.
- **Approved fields:** None.
- **Rejected fields:** `deployment_id`, `Age`, `YearCollected`, `Region`, `BodyLocation_Group`, `Country`, `Beta_Lactamase_enc`, `organism`, `antimicrobial`, `pathogen`, `infection_site`, `severity`, `culture`.
- **Unresolved fields:** Request-time ownership/provenance for raw artifact fields and all semantic mappings.
- **Ownership/producer:** `deployment_id` is caller/platform routing; raw fields have no established request-time owner or producer.
- **Provenance:** Artifact/runtime provenance exists, but clinician/frontend provenance does not.
- **Transformation boundary:** Backend deployment lookup and artifact preprocessing remain backend-owned.
- **Adapter boundary:** Existing SOAR adapter requires explicit context and performs no inference.
- **Safety notes:** Never render or infer `deployment_id`; never map infection site, organism, pathogen, or antimicrobial aliases.

## ARMD

- **Plugin ID:** `armd`
- **Decision:** `ARMD_STATUS = NOT_APPROVED`
- **Approving evidence:** Runtime whitelist and preprocessing tests establish execution behavior only, not frontend ownership.
- **Approved fields:** None.
- **Rejected fields:** Raw whitelist fields without ownership evidence; encoded sex/care flags; history aggregates; `age_group`; `log_days_since_abx`; one-hot columns; model vectors; legacy aliases.
- **Unresolved fields:** Clinician versus patient-record/laboratory/platform ownership and provenance for raw WP4 values.
- **Ownership/producer:** Not established at the frontend boundary.
- **Provenance:** Runtime/model provenance exists; frontend clinical provenance is absent.
- **Transformation boundary:** Backend WP4 cleaning, derivation, alignment, scaling, and prediction remain backend-owned.
- **Adapter boundary:** No ARMD frontend adapter is authorized.
- **Safety notes:** Never generate fields from `FEATURE_WHITELIST`, model metadata, feature order, or legacy aliases.

## Formal acceptance

**NO SOAR OR ARMD CLINICAL INPUT CONTRACT IS APPROVED.**
