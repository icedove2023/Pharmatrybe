# Phase 21E SOAR and ARMD Dynamic Form Migration Report

## Migration status

| Plugin | Status | Contract | Dynamic form |
| --- | --- | --- | --- |
| SOAR | INTENTIONALLY_UNAVAILABLE | None approved | Not migrated |
| ARMD | INTENTIONALLY_UNAVAILABLE | None approved | Not migrated |
| WHO search | Existing Phase 20 migration retained | `who_knowledge@1.0.0` | Unchanged |

## Implementation decision

No SOAR or ARMD production contract, adapter, or form was created because Phase 21A-D found no field with complete ownership, provenance, frontend authority, and safe frozen-boundary mapping.

The Phase 19 registry and renderer remain the only dynamic form architecture. Legacy `formSchema` and arbitrary metadata schemas remain quarantined from active contract resolution. SOAR routing remains explicit and separate. ARMD preprocessing remains backend-owned.
