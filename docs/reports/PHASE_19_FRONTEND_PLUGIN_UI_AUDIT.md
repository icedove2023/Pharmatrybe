# Phase 19 Frontend Plugin UI Audit

## Findings

The frontend contains an assessment wizard, clinical case store, WHO retrieval explorer, SOAR/ARMD explorer wrappers, static plugin registry metadata, a central authenticated API client, and a Workflow Manager. The assessment wizard and registry contain legacy presentation schemas. Workflow Manager previously rendered arbitrary `metadata.inputSchema` values.

## Classifications

- Central API client: CANONICAL.
- WHO retrieval explorer and API: CANONICAL retrieval boundary.
- Assessment wizard and case store: COMPATIBILITY / NEEDS_RECONCILIATION.
- Static `formSchema` registry entries: STALE compatibility metadata, not contracts.
- Arbitrary Workflow Manager metadata schemas: UNSUPPORTED and removed from rendering.
- SOAR and ARMD explorer APIs: INTENTIONAL_BOUNDARY; backend capability is unavailable.

## Contract authority

The SOAR contract requires explicit deployment routing and states that no frontend-visible UI inputs are approved. SOAR raw artifact fields have unresolved clinician/platform ownership. ARMD WP4/model fields are not approved clinician inputs. WHO is query/retrieval-oriented and has no registered frontend dynamic query contract.

## Result

A generic contract registry, validator, value validator, renderer, adapter boundary, safety tests, and documentation were added. Plugin-specific migration was intentionally not performed because it would require inventing clinical ownership or mappings.
