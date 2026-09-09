# Phase 20B SOAR Input Contract Decision

## Decision

**SOAR_FRONTEND_CONTRACT_NOT_APPROVED**

`SOAR_DYNAMIC_FORM = NOT_APPROVED`.

## Evidence

The frozen SOAR runtime contract requires exact caller/platform `context.deployment_id` routing and states that deployment selection is not frontend-visible. The authoritative plugin schema exposes `x-ui-inputs: []` and marks deployment selection `frontend_visible: false`.

Runtime fields are deployment-artifact inputs, but their request-time owner and provenance are not established. `Age`, `YearCollected`, `Region`, `BodyLocation_Group`, `Country`, and variant-specific `Beta_Lactamase_enc` cannot be promoted to clinician fields. `BodyLocation_Group` has no approved mapping from `infection_site`.

## Routing decision

`deployment_id` is routing metadata. The frontend must not render it as a clinical field or infer it from organism, pathogen, antimicrobial, antibiotic, country, location, model name, filename, similarity, or first available deployment.

## Implementation outcome

No SOAR contract is registered. No SOAR dynamic form is migrated. The existing compatibility workflow remains fail-closed with an explicit unavailable-contract state.
