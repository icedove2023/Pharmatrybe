# Phase 20E Clinical Form Migration Report

## Migration status

| Plugin | Status | Reason |
| --- | --- | --- |
| SOAR | INTENTIONALLY_UNAVAILABLE | No frontend-visible approved fields; routing and artifact ownership unresolved |
| ARMD | INTENTIONALLY_UNAVAILABLE | WP4 raw field ownership and frontend authority unresolved |
| WHO SearchQuery | PARTIALLY_MIGRATED | Only `query_text` is approved and maps to the existing `/who/search` route |
| WHO KnowledgeQuery | BLOCKED_BY_CONTRACT | Internal query shape is broader than the verified public frontend boundary |

## Rules

The Phase 19 registry, validator, renderer, and adapter boundaries are reused. Legacy `formSchema` entries are not promoted. Routing metadata remains separate from query or clinical payloads. No model feature, preprocessing field, or semantic mapping is introduced.
