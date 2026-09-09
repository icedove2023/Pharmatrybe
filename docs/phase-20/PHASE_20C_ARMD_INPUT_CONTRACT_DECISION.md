# Phase 20C ARMD Input Contract Decision

## Decision

**ARMD_FRONTEND_CONTRACT_NOT_APPROVED**

`ARMD_DYNAMIC_FORM = NOT_APPROVED`.

## Evidence

The ARMD runtime filters a payload through the WP4 feature whitelist, performs cleaning/imputation, derives age groups and other encoded values, aligns to model-specific feature vectors, scales, and predicts. The backend schema labels raw whitelist keys as `x-ui-inputs`, but it does not establish data owner, producer, clinical ownership, editability, provenance, or frontend approval for those keys.

The following remain outside frontend forms:

- `age_group`, `log_days_since_abx`, and age-bin encodings;
- model feature vectors and feature-order columns;
- encoded sex and care-context representations;
- aggregate WP4 features;
- unapproved aliases such as `prior_antibiotics`, `recent_hospitalization`, `organism`, and `infection_site`.

Raw laboratory, vital, encounter, medication-history, and organism-history fields require explicit source ownership before any manual entry or prefill can be authorized.

## Implementation outcome

No ARMD contract is registered. No ARMD dynamic form is migrated. The existing compatibility workflow remains fail-closed and never inspects model features to generate fields.
