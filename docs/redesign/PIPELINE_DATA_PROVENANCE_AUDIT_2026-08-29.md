# End-to-End Assessment Pipeline Data Provenance Audit

**Date:** 2026-08-29  
**Scope:** Assessment wizard submission through `/pipeline/execute`, plugin orchestration, prediction artifacts, WHO knowledge access, decision fusion, and displayed recommendation.  
**Method:** Read-only code audit plus one live signed-in browser submission against the local Vite frontend and FastAPI backend.

## Executive Conclusion

The assessment result is **not a static frontend mockup**. The live request reached the backend, initialized the plugin runtime, loaded ARMD and SOAR runtime assets, connected to the configured PostgreSQL host, executed the pipeline, and returned a recommendation page.

However, the displayed result is **not fully source-pure**. It is a mixture of:

- real runtime outputs from local ARMD/SOAR artifacts;
- live database-backed WHO plugin infrastructure, although the submitted case does not currently provide a WHO query and therefore does not produce WHO plugin search results for this request;
- deterministic backend rule and fusion logic;
- placeholder in-memory WHO AWaRe guideline references;
- generated presentation text and default metadata;
- a dormant frontend contract fixture containing hard-coded clinical examples, which was not used by the audited `submitCase` path.

Therefore the correct status is: **the pipeline is live and operational, but the displayed recommendation must not yet be described as wholly database-verified or clinically production-ready.**

## Live Validation Evidence

The audited browser submission completed successfully at `http://localhost:3000/` and navigated to the Clinical Decision Support result page.

Observed live output included:

- primary recommendation: Ceftriaxone;
- 19 alternative antimicrobial recommendations;
- WHO AWaRe evidence entries;
- model confidence and recommendation rationale;
- an execution trace and recommendation ID;
- no active browser alert after completion;
- no frontend console error for the successful submission.

The backend plugin manager independently loaded:

```text
who_knowledge: True
armd: True
soar: True
```

ARMD initialization logged a registry containing **20 antibiotics**, loaded WP3 preprocessing artifacts, and loaded a WP2 table with shape **(118767, 68)**. SOAR initialization logged **10 deployments**. The API process also had an established PostgreSQL connection to the configured remote database on port 5432 during the live request.

The focused integration suite passed:

```text
9 passed
```

Warnings were deprecation/configuration warnings, not data-source failures.

## Provenance Trace

### 1. Frontend submission

[recommendationApi.ts](../../src/api/recommendationApi.ts) `submitCase` calls `executePipeline` with:

- `execution_mode: "sync"`;
- the patient ID from the assessment case;
- selected plugins, defaulting to `soar`, `armd`, and `who_knowledge`;
- `input_payload: { case: clinicalCase }`;
- `response_mode: "full"`.

The frontend does not generate the audited result locally in this path. It receives the backend response and adapts it for display.

### 2. API route and orchestration

[pipeline.py](../../apps/api/app/api/v1/pipeline.py) loads the governed internal plugin catalog, checks the requested plugin IDs, creates a `ClinicalDecisionRequest`, and calls `ClinicalIntelligencePipeline.process`.

[clinical_intelligence/pipeline.py](../../apps/api/app/clinical_intelligence/pipeline.py) states and implements this sequence:

1. execute selected plugins;
2. extract candidate antibiotics only from prediction plugin outputs;
3. evaluate clinical rules;
4. fuse prediction, rule, guideline, and stewardship data;
5. generate explanation and audit data;
6. format the canonical response.

This is a real backend execution path, not a frontend-only fixture path.

### 3. ARMD data

[armd_prediction_plugin.py](../../apps/api/app/plugins/prediction/armd/armd_prediction_plugin.py) delegates prediction to `ARMDPredictionEngine`.

[armd/prediction_engine.py](../../apps/api/app/plugins/prediction/armd/prediction_engine.py) calls `adapter.predict_all_antibiotics(patient_data)` and maps successful executions into antibiotic probabilities.

The adapter is initialized against the ARMD deployment under `deployments/ARMD`; the live runtime loaded the registry, WP3 artifacts, and WP2 table. This supports the conclusion that ARMD candidates are generated from local runtime assets rather than a UI hard-coded list.

**Qualification:** the final API response does not expose a per-candidate artifact checksum, model file, or model execution record sufficient to independently prove which model produced every displayed probability. The runtime path does load real assets, but response-level provenance is incomplete.

### 4. SOAR data

[soar_prediction_plugin.py](../../apps/api/app/plugins/prediction/soar/soar_prediction_plugin.py) initializes a deployment registry, model loader, prediction engine, and runtime context.

The live runtime reported 10 SOAR deployments and completed initialization. The loader resolves deployment metadata and required model, preprocessing, calibration, and SHAP artifact paths under the SOAR deployment tree.

This is evidence of real SOAR artifact-backed runtime initialization.

**Qualification:** there are also unused/skeleton SOAR provider classes elsewhere in the repository. The audited pipeline uses the plugin under `app/plugins/prediction/soar`, not the placeholder service client or skeleton provider. Those inactive classes must not be used as evidence that every SOAR API surface is implemented.

### 5. WHO data

[who_knowledge_plugin.py](../../apps/api/app/plugins/knowledge/who_knowledge_plugin.py) wraps `WHOKnowledgeRepository` and `WHOProvider`.

[who_knowledge_repository.py](../../apps/api/app/database/repositories/who_knowledge_repository.py) uses SQLAlchemy `select()` statements against the application models for diseases, drugs, recommendations, evidence, diagnostics, monitoring, pathogens, stewardship, follow-up, and referral data.

[who.py](../../apps/api/app/api/v1/who.py) creates a `SessionLocal` session and routes WHO requests through the knowledge orchestrator/service. The live API process had an established PostgreSQL connection to the configured database host.

The WHO implementation is therefore database-backed in its infrastructure and direct WHO endpoints.

**Critical active-path finding:** [workflow_manager.py](../../apps/api/app/plugins/manager/workflow_manager.py) invokes `who_knowledge.search()` using `request.payload.get("query")`. The assessment payload contains the clinical case but no `query` field. [who_knowledge_plugin.py](../../apps/api/app/plugins/knowledge/who_knowledge_plugin.py) returns an empty list when the query is blank. Thus, for the audited assessment submission, WHO plugin search output is not the source of the displayed AWaRe entries.

### 6. Guideline and AWaRe data displayed in the result

[guideline_engine.py](../../apps/api/app/clinical_decision/guideline_engine.py) explicitly describes itself as initially using placeholder data and calls `_load_placeholder_guidelines()` during initialization. The table contains hard-coded antibiotic names, categories, descriptions, and a WHO URL.

[decision_fusion.py](../../apps/api/app/clinical_decision/decision_fusion.py) retrieves guideline references from this `GuidelineEngine` while fusing the prediction results.

This means the WHO AWaRe labels and guideline references visible in the audited result are **not proven to have come from the live WHO database for that request**. They are currently generated from the placeholder in-memory guideline table.

### 7. Clinical safety rules

[clinical_decision/rules/__init__.py](../../apps/api/app/clinical_decision/rules/__init__.py) registers allergy, renal impairment, and pregnancy rules and evaluates them against the patient payload and prediction candidates.

The live displayed result reported these rules as not evaluated and said no allergy/eGFR data were available, even though the wizard visibly contained a penicillin allergy and eGFR 55. This is a real pipeline data-mapping defect, not evidence of mock data. The values are being lost or placed under a payload shape the rules do not read. This issue is outside the requested audit-only change but is a release blocker for clinical use.

### 8. Generated response metadata and wording

The response formatter and explainability layers generate recommendation narratives, audit identifiers, trace structures, labels, and display text. Generated text is not inherently fake, but it must not be interpreted as an independent clinical source.

The active pipeline sets `model_info={"version": "0.1.0"}`, passes an empty model-version map to the audit generator, and does not expose complete artifact-level provenance in the final response. The result page consequently displays values such as “Not reported by backend” for some engine metadata.

## Mock/Fallback Code Found

### Dormant frontend fixture

[recommendationApi.ts](../../src/api/recommendationApi.ts) contains `buildCanonicalResponse`. It includes hard-coded defaults such as:

- Community-Acquired Pneumonia (CAP);
- age 68;
- Male;
- eGFR 55;
- hard-coded guideline references;
- hard-coded evidence weights and narrative claims.

This is explicitly documented as a contract-test fixture. The audited `submitCase` function calls `/pipeline/execute` and does not call this helper. It is therefore not the source of the successful live result, but its presence creates a future risk if another UI path calls it.

### Backend fallback recommendation logic

[decision_fusion.py](../../apps/api/app/clinical_decision/decision_fusion.py) contains fallback/default recommendation methods for cases where no ranked candidate is available. The normal pipeline is intended to stop with an error when prediction candidates are absent, but fallback code should be treated as a provenance risk until covered by tests proving it cannot create a recommendation from empty prediction output.

### Placeholder guideline table

The `GuidelineEngine` placeholder table is active in the audited pipeline and is the most direct source of non-database clinical display data.

## Finding Classification

| Area | Finding | Classification |
|---|---|---|
| Frontend submission | Calls live `/pipeline/execute`; no local fixture used in audited path | Real live execution |
| ARMD | Loads registry, WP3/WP2 assets and produces candidate probabilities | Real artifact-backed runtime, incomplete response provenance |
| SOAR | Loads deployment registry and runtime artifacts | Real artifact-backed runtime, incomplete response provenance |
| WHO infrastructure | SQLAlchemy repository and PostgreSQL connection are real | Real database-backed capability |
| WHO data in this assessment | Blank WHO search query yields no WHO plugin search results | Not proven to contribute to this result |
| AWaRe/guideline labels | Active `GuidelineEngine` uses `_load_placeholder_guidelines()` | Placeholder-derived |
| Safety rules | Backend rule engine exists, but live form values were not recognized | Real rule engine with broken input mapping |
| Recommendation text | Generated by backend explainability/fusion layers | Derived/generated, not a source record |
| Frontend `buildCanonicalResponse` | Contains hard-coded demo defaults but is not called by audited submit path | Dormant fixture / risk |
| Audit/model metadata | Some versions and algorithm fields are defaults or absent | Incomplete provenance |

## Final Verdict

The system is **working as a live software pipeline**, and the recommendation page is not merely a mockup. Real prediction runtime components and real database connectivity are involved.

The system is **not yet demonstrably producing a wholly real-data clinical recommendation** because:

1. the active AWaRe guideline source is an explicitly placeholder in-memory table;
2. the WHO plugin receives no meaningful query from the assessment case and returns no search results for this submission;
3. safety-rule inputs shown in the form are not reaching the rule evaluator correctly;
4. the response lacks complete per-plugin artifact/database provenance;
5. dormant frontend fixture code contains plausible-looking hard-coded clinical data.

The clinical-data mapping issue and placeholder guideline source should be resolved before production claims that the displayed recommendation is fully grounded in WHO database evidence and correctly individualized to the submitted patient.
