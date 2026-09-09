# Clinical Adaptation Boundary v1.0.0

Status: FROZEN

## Purpose

This boundary separates canonical request identity/context from plugin-specific execution. It performs validation and explicit ownership checks only. It does not invent clinical mappings.

```text
Canonical Clinical Request
    -> Plugin Input Adapter
    -> Plugin-Specific Request
    -> Plugin Runtime
```

## Canonical request fields

- `request_id`: caller-provided or platform-generated correlation identity.
- `patient_id`: caller-owned patient identity.
- `case_id`: caller-owned case context.
- `input_payload`: caller-owned clinical/plugin payload.
- `routing_context`: platform/caller-owned routing metadata, distinct from clinical payload.
- `plugin_selection`: caller-selected plugin IDs, or existing platform routing policy when omitted.
- `execution_mode`: only `sync` is currently executable at the public pipeline route.
- `response_mode`: response preference metadata; canonical response remains the documented endpoint envelope.

## Adapter declarations

### SOAR

- Required canonical fields: non-empty payload and `routing_context.deployment_id`.
- Optional canonical fields: `request_id`, `patient_id`, `case_id`.
- Plugin-specific fields: exact artifact raw features `Age`, `YearCollected`, `Region`, `BodyLocation_Group`, `Country`, and variant-specific `Beta_Lactamase_enc`.
- Transformations: routing context is validated and copied; artifact preprocessing remains inside the selected deployment runtime.
- Unsupported mappings: `infection_site`, `organism`, `pathogen`, `species`, `severity`, and `culture` are not converted.
- Failure: missing routing or artifact fields rejects execution.

### ARMD

- Required canonical fields: payload accepted by the existing WP4 adapter.
- Plugin-specific fields: WP4 `FEATURE_WHITELIST` raw inputs.
- Transformations: existing WP4 whitelist, cleaning/imputation, age-group encoding, feature alignment, scaling, and prediction.
- Unsupported mappings: no unproven high-level aliases are converted.
- Failure: adapter/model validation failure rejects execution.

### WHO

- Required canonical fields: `SearchQuery.query_text` for search or `KnowledgeQuery.entity_type` for retrieval.
- Plugin-specific fields: supported entity type and optional identifier.
- Transformations: query type is routed to the WHO provider capability path.
- Unsupported mappings: WHO knowledge entities are not prediction features.
- Failure: provider/database errors return the knowledge failure boundary.

## Mapping policy

The following remain distinct and unresolved unless a later approved terminology decision says otherwise:

- `organism` / `pathogen` / `species`;
- `antimicrobial` / `antibiotic`;
- `infection_site` / `BodyLocation_Group`;
- `Age` / `age` / `age_group`;
- `Region` / `Country`;
- `culture` / `specimen` / `laboratory`.

No similarity-based transformation is permitted.
