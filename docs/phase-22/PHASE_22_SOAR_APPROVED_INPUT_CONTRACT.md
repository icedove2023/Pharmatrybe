# Phase 22 SOAR Input Contract Decision

## Decision

`SOAR_STATUS = NOT_APPROVED`.

No SOAR clinical input is admitted. The current frozen contract proves artifact runtime requirements but not frontend ownership or request-time provenance. `deployment_id` remains routing metadata and is never a clinical field.

## Rejected inputs

`Age`, `YearCollected`, `Region`, `BodyLocation_Group`, `Country`, and `Beta_Lactamase_enc` are rejected as artifact/runtime or preprocessing fields with no established frontend producer. `pathogen`, `organism`, `antimicrobial`, `infection_site`, `severity`, and `culture` are rejected as unresolved, metadata, or unsupported mappings.

No SOAR contract, deployment selector, or adapter was created.
