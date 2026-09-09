# Backend Contract Manifest v1.0.0

Status: FROZEN v1.0.0. Frontend reconciliation may begin against the documented public boundaries.

| Contract | Version | Status | Authoritative source | Runtime verification | Freeze |
| --- | --- | --- | --- | --- | --- |
| [Plugin runtime](PLUGIN_RUNTIME_CONTRACT_v1.0.0.md) | 1.0.0 | FROZEN | Plugin schemas, adapters, and runtime classes | Focused schema/plugin tests; full suite | YES |
| [SOAR deployment](../../SOAR_Deployment_Contract.md) | 1.0.0 | FROZEN | SOAR scanner, registry, adapter, plugin, artifacts | SOAR deployment tests; full suite | YES |
| [SOAR upstream ownership](SOAR_Upstream_Routing_and_Input_Ownership.md) | 1.0.0 | FROZEN | Canonical routing context and SOAR adapter | Adapter/orchestration tests | YES |
| [SOAR selection](SOAR_DEPLOYMENT_SELECTION_CONTRACT_v1.0.0.md) | 1.0.0 | FROZEN | Explicit caller/platform routing boundary | Adapter and deployment tests | YES |
| [Clinical adaptation](CLINICAL_ADAPTATION_BOUNDARY_v1.0.0.md) | 1.0.0 | FROZEN | Explicit plugin adapters and validation | Closure adapter tests | YES |
| [ARMD runtime](ARMD_RUNTIME_CONTRACT_v1.0.0.md) | 1.0.0 | FROZEN | WP4 whitelist/preprocessing and ARMD plugin | ARMD focused tests; full suite | YES |
| [WHO query](WHO_QUERY_CONTRACT_v1.0.0.md) | 1.0.0 | FROZEN | Query models, provider, repository, WHO plugin | WHO focused tests; full suite | YES |
| [Backend request](BACKEND_REQUEST_CONTRACT_v1.0.0.md) | 1.0.0 | FROZEN | Pipeline route, request model, adapter, workflow manager | Request/orchestration tests | YES |
| [Recommendation](RECOMMENDATION_CONTRACT_v1.0.0.md) | 1.0.0 | FROZEN | Decision contracts and canonical recommendation endpoint | Recommendation API tests; full suite | YES |
| [Explainability](EXPLAINABILITY_CONTRACT_v1.0.0.md) | 1.0.0 | FROZEN | Canonical recommendation response contract | Explainability API tests; full suite | YES |
| [Backend errors](BACKEND_ERROR_CONTRACT_v1.0.0.md) | 1.0.0 | FROZEN | Global API handlers and typed error registry | Closure error tests; full suite | YES |

The master freeze decision is YES for the explicit public contract. Unresolved clinical mappings remain intentionally unsupported and are isolated behind plugin-specific adapters; they do not require frontend inference.

Verification update: `apps/api/tests` passes with `276 passed, 7 warnings` before closure changes; the closure regression suite and final full suite are recorded in [BACKEND_CONTRACT_FREEZE_REPORT](../reports/BACKEND_CONTRACT_FREEZE_REPORT.md).
