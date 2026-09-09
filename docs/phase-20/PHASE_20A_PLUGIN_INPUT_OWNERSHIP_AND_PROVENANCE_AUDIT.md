# Phase 20A Plugin Input Ownership and Provenance Audit

## Acceptance decision

**PHASE_20A = COMPLETE.** No production frontend contract is approved by this audit alone. The runtime contracts establish plugin behavior and field shapes, but frontend authority requires ownership, producer, provenance, and editability evidence that is absent for SOAR and ARMD and incomplete for WHO.

## Scope and evidence classes

Evidence was reviewed from the frozen runtime contract, SOAR deployment contract and tests, ARMD plugin schema and WP4 references, WHO plugin query schema and public routes, canonical adapters, the Phase 19 registry/renderer, legacy frontend registry definitions, and existing tests.

Evidence classes:

- **AUTHORITATIVE**: frozen backend contract or executable contract test.
- **IMPLEMENTATION EVIDENCE**: runtime code that proves what the system accepts or executes.
- **COMPATIBILITY EVIDENCE**: existing frontend behavior retained for compatibility.
- **LEGACY**: historical frontend fields or metadata not governed as contracts.
- **STALE**: behavior/documentation contradicted by current contract evidence.
- **UNRESOLVED**: ownership, provenance, meaning, or authority is not established.

## Plugin inventory

| Plugin | Runtime contract | Frontend contract status | Phase 20A result |
| --- | --- | --- | --- |
| SOAR | `prediction`, explicit deployment routing, deployment-specific artifact fields | No registered contract; legacy fields conflict with `x-ui-inputs: []` and `frontend_visible: false` | No frontend form authority |
| ARMD | `prediction`, WP4 raw whitelist plus derived/model-internal fields | Backend exposes `x-ui-inputs`, but ownership/provenance/editability are not established | No frontend form authority |
| WHO | `knowledge_query`, `SearchQuery` and `KnowledgeQuery` shapes | Query shape is implementation evidence; public UI/API is retrieval-oriented and no frontend provenance/approval record exists | No production dynamic form authority |

## Field ownership matrix

Primary classes are mutually exclusive: clinician-entered, patient-record derived, laboratory derived, platform generated, routing metadata, derived clinical value, or model/preprocessing feature.

### SOAR

| Field | Semantic meaning | Source / producer | Primary class | Runtime/model/preprocessing/routing | Frontend visible/editable/authority | Approved | Evidence / reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `deployment_id` | Exact artifact deployment selector | Caller/platform context; exact registry lookup | Routing metadata | Routing | Not frontend-visible; not clinician-editable; caller/platform authority only | No | SOAR adapter and contract require explicit `context.deployment_id`; no inference or selector is approved |
| `Age` | Artifact runtime numeric field described as age | Artifact `feature_schema.json`; request-time producer not established | Unresolved ownership | Runtime feature; scaling/passthrough | No known frontend authority | No | Runtime support does not prove clinician or patient-record ownership |
| `YearCollected` | Collection year | Artifact feature schema; request-time producer not established | Unresolved ownership | Runtime feature; preprocessing | No | No | Dataset/model context may not be a clinician input |
| `Region` | Collection region | Artifact feature schema; request-time producer not established | Unresolved ownership | Runtime feature; one-hot transformed | No | No | No producer or frontend authority established |
| `BodyLocation_Group` | Artifact body-location category | Artifact feature schema; no approved mapping from `infection_site` | Model/preprocessing feature | Runtime feature; one-hot transformed | No | No | Semantic mapping is explicitly unresolved |
| `Country` | Collection country | Artifact feature schema; request-time producer not established | Unresolved ownership | Runtime feature; target encoded | No | No | Artifact presence is not clinical ownership |
| `Beta_Lactamase_enc` | Deployment-specific encoded field | Deployment artifact; no approved laboratory producer | Model/preprocessing feature | Variant-specific runtime feature | No | No | No laboratory provenance or frontend authority |
| `organism` | Deployment metadata identity | Deployment manifest/scanner | Routing/plugin metadata | Plugin-specific metadata | No | No | Not a universal clinical input or selector |
| `antimicrobial` | Deployment metadata identity | Deployment manifest/scanner | Routing/plugin metadata | Plugin-specific metadata | No | No | Never used for frontend deployment inference |
| `pathogen` | Legacy support/routing concept | Legacy `supports()` key; no confirmed runtime field | Unresolved | Plugin-specific routing only | No | No | No confirmed payload meaning |
| `infection_site` | Clinical site | Legacy frontend case field | Unresolved | No SOAR runtime field or mapping | No | No | No deterministic mapping to `BodyLocation_Group` |
| `severity` | Clinical severity | Legacy frontend case field | Unresolved | Not in SOAR runtime contract | No | No | Not a SOAR input |
| `culture` | Culture observation | Legacy frontend field | Unresolved | Not in SOAR runtime contract | No | No | No confirmed SOAR use |

### ARMD

| Field group / field | Semantic meaning | Source / producer | Primary class | Runtime/model/preprocessing/routing | Frontend visible/editable/authority | Approved | Evidence / reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `age` | Patient age | WP4 raw payload key; producer/ownership not specified | Unresolved ownership | Runtime input; derives age encodings | Backend schema lists as UI candidate, but frontend authority is not approved | No | Runtime acceptance and `x-ui-inputs` do not establish owner or editability |
| `gender_male` | Encoded sex indicator | WP4 whitelist | Model/preprocessing feature unless explicit source contract exists | Runtime numeric feature | No | No | Encoded representation is not an approved clinician field |
| care-context flags (`inpatient`, `outpatient`, `emergency`, `icu`) | Encounter/care setting indicators | WP4 whitelist; producer not specified | Unresolved ownership | Runtime/preprocessing input | No | No | No ownership/provenance contract |
| procedure/device flags | Procedure or device context | WP4 whitelist; producer not specified | Unresolved ownership | Runtime/preprocessing input | No | No | No clinical source or frontend authority established |
| laboratory/vital fields | Measurements such as `creatinine`, `wbc`, `temperature`, `heartrate` | WP4 whitelist; laboratory/record producer not established at frontend boundary | Laboratory-derived or patient-record derived, unresolved | Runtime/preprocessing input | Not editable without approved source and authority | No | Field names alone do not authorize manual entry |
| exposure/history fields | `n_prior_meds`, `n_prior_classes`, `days_since_last_antibiotic`, `n_abx_classes_exposed` | WP4 whitelist; producer not specified | Unresolved ownership | Runtime/preprocessing input | No | No | No approved boolean or semantic mapping from legacy `prior_antibiotics` |
| organism-history fields | `n_prior_organisms`, `days_since_last_prior_organism` | WP4 whitelist; producer not specified | Unresolved ownership | Runtime/preprocessing input | No | No | Not equivalent to organism/pathogen/species text |
| `adi_score`, `adi_state_rank` | Aggregate context features | WP4 whitelist; source not specified | Model/preprocessing feature | Runtime/preprocessing input | No | No | Aggregate model inputs lack frontend authority |
| `age_group`, `log_days_since_abx` | Derived values | WP4 preprocessing | Derived clinical value / model-derived | Derived preprocessing | No | No | Frontend must not recreate backend preprocessing |
| `age_group_*` and model vectors | Encoded/model columns | Saved feature order and model metadata | Model/preprocessing feature | Model-internal | No | No | Explicitly excluded from clinician forms |

### WHO

| Field | Semantic meaning | Source / producer | Primary class | Runtime/model/preprocessing/routing | Frontend visible/editable/authority | Approved | Evidence / reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `query_text` | Knowledge search text | WHO `SearchQuery`; public `/who/search?q` route | Clinician-entered candidate | Knowledge query | Existing search UI uses equivalent query text; no Phase 20 production contract provenance record yet | Not yet | Backend execution is verified, but formal frontend approval/provenance is not recorded |
| `entity_type` in `SearchQuery` | Optional knowledge entity scope | WHO query model; public search route does not expose it as a parameter | Clinician-entered candidate | Knowledge query | Not approved | No | Internal query shape is broader than public frontend API |
| `entity_type` in `KnowledgeQuery` | Retrieval entity type | WHO query model/provider | Clinician-entered or workflow-selected, unresolved | Knowledge routing/query metadata | Not approved | No | Supported values and frontend authority are not formalized |
| `identifier` | Exact knowledge entity identifier | WHO provider retrieval | Patient/record derived or clinician/workflow supplied, unresolved | Knowledge query | Not approved | No | Existing UI uses disease IDs from retrieved records, not a governed form contract |
| filters/pagination/sort/extra | Query controls | Generic query model | Platform/query metadata | Not confirmed in executed WHO methods | No | No | Frozen contract reports execution as unconfirmed |

## Routing metadata analysis

`deployment_id`, plugin selection, execution mode, request IDs, tenant context, and trace identifiers remain outside clinical form values. The Phase 19 adapter preserves `routing_context` separately. No Phase 20 evidence authorizes frontend inference or clinician editing of SOAR deployment routing.

## Derived and model-feature exclusion

The following are explicitly excluded from frontend clinical forms unless a future contract provides ownership and authority: SOAR encoded artifact fields, ARMD `age_group`, `log_days_since_abx`, one-hot columns, feature vectors, model metadata, WP4 aggregate feature names, and any value inferred from field-name similarity. The frontend must not recreate backend preprocessing.

## Legacy and stale frontend evidence

The static `formSchema` entries in `src/plugins/registry/pluginDefinitions.ts` are compatibility metadata, not approved contracts. The SOAR `pathogen`/`culture` and ARMD age/weight/eGFR/history fields lack matching approved runtime ownership. Phase 19 correctly changed the assessment and Workflow Manager paths to fail closed rather than promote these fields.

## Safety blockers

1. SOAR raw artifact field ownership and request-time provenance are unresolved.
2. SOAR deployment routing is platform-owned and not frontend-visible.
3. ARMD raw whitelist ownership and editability are unresolved.
4. ARMD backend `x-ui-inputs` is runtime metadata, not sufficient approval evidence.
5. WHO query shape is verified internally, but public frontend query authority and production provenance are incomplete.
6. No approved plugin-specific Phase 20 adapter exists for a real migrated form.

## Phase 20A conclusion

**COMPLETE: AUDIT ONLY.** No plugin-specific frontend contract is created in Phase 20A. SOAR and ARMD are not approved for dynamic clinical forms. WHO remains a retrieval boundary pending a formal frontend query-contract approval decision.
