# Phase 21A Repository Evidence Audit

## Decision

**PHASE_21A = COMPLETE.** The repository-wide review does not establish enough frontend ownership, provenance, editability, or safe semantic mapping to approve SOAR or ARMD clinical form contracts.

## Authority hierarchy applied

1. Executable backend validation and tests.
2. Frozen plugin/runtime contracts.
3. Current request and response models.
4. Current plugin adapters.
5. Explicit architecture decisions.
6. Formal reports.
7. Legacy frontend metadata.
8. Historical documentation.

Conflicts were not merged silently.

## Source classification

| Source | Classification | Finding |
| --- | --- | --- |
| `docs/contracts/PLUGIN_RUNTIME_CONTRACT_v1.0.0.md` | AUTHORITATIVE | Frozen runtime boundaries; explicitly excludes unresolved clinical mappings and does not establish frontend ownership. |
| `apps/api/tests/test_soar_deployment_contract.py` | AUTHORITATIVE | SOAR requires explicit deployment context and exposes no frontend UI inputs. |
| `apps/api/app/plugins/prediction/soar/soar_prediction_plugin.py` | AUTHORITATIVE implementation evidence | Exact deployment lookup and artifact validation; raw fields are runtime inputs, not clinician authority. |
| `apps/api/app/plugins/prediction/armd/armd_prediction_plugin.py` | AUTHORITATIVE implementation evidence | WP4 whitelist and runtime schema; `x-ui-inputs` is not an ownership/provenance approval record. |
| `apps/api/app/plugins/adapters/clinical.py` | AUTHORITATIVE implementation evidence | SOAR requires explicit `context.deployment_id`; no inference. |
| `apps/api/app/plugins/knowledge/who_knowledge_plugin.py` | SUPPORTING | WHO query schema distinguishes SearchQuery and KnowledgeQuery. |
| `apps/api/app/api/v1/who.py` | SUPPORTING | Public routes verify search query `q` and retrieval IDs. |
| `src/plugins/contracts/*` | AUTHORITATIVE frontend architecture | Phase 19 exact registry, approval, provenance, validation, and renderer boundaries. |
| `src/plugins/registry/pluginDefinitions.ts` | LEGACY / COMPATIBILITY | Static `formSchema` fields are not approved contracts. |
| `src/components/assessment/PluginGeneratedForm.tsx` | COMPATIBILITY | Intentionally refuses legacy schemas and displays unavailable-contract state. |
| `src/components/plugins/WorkflowManagerView.tsx` | COMPATIBILITY | No longer renders arbitrary `metadata.inputSchema`. |
| Phase 20 reports | SUPPORTING | Previously established WHO partial migration and SOAR/ARMD ownership gaps. |
| Earlier stabilization/finalization reports claiming frontend readiness | SUPERSEDED / CONTRADICTORY | Reconciled against executable tests and frozen runtime contract; they do not authorize clinical form fields. |

## SOAR evidence conclusion

SOAR has explicit routing metadata and artifact-backed runtime fields. The repository does not identify request-time owner, producer, clinician authority, or safe frontend provenance for the raw artifact fields. `deployment_id` is routing metadata. No SOAR clinical contract is approved.

## ARMD evidence conclusion

ARMD exposes raw WP4 whitelist fields and derived/model features. The repository proves runtime acceptance and preprocessing, but does not prove clinician ownership, producer provenance, editability, or an approved raw clinical input boundary. No ARMD clinical contract is approved.

## Phase 21A acceptance

**COMPLETE.** Source authority is documented. SOAR and ARMD proceed to formal `NOT_APPROVED` decisions. No plugin contract is created from runtime feature evidence alone.
