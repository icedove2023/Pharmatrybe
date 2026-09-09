# Phase 21D Clinical Mapping Register

No clinical mapping is approved in Phase 21.

| Source field | Target field | Evidence | Transformation | Status |
| --- | --- | --- | --- | --- |
| `infection_site` | `BodyLocation_Group` | No authoritative mapping found; explicitly unresolved in frozen runtime contract | None permitted | UNRESOLVED |
| `organism` | `pathogen` | Deployment metadata and support keys are not equivalent clinical concepts | None permitted | NOT_APPROVED |
| `organism` | `species` | No explicit mapping authority | None permitted | NOT_APPROVED |
| `pathogen` | `species` | No explicit mapping authority | None permitted | NOT_APPROVED |
| `prior_antibiotics` | ARMD exposure counts/timing | Boolean alias has no deterministic transform | None permitted | NOT_APPROVED |
| `Age` | `age_group` | Age grouping is backend preprocessing, not frontend authority | Frontend must not calculate | NOT_APPROVED |
| `Country` | `Region` | Distinct SOAR artifact fields and transformations | None permitted | NOT_APPROVED |
| form field | `deployment_id` | Routing context is not a clinical mapping | No inference permitted | NOT_APPROVED |

Any future mapping requires explicit evidence, ownership, provenance, approval, and adapter tests.
