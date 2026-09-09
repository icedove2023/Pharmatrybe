# SOAR Upstream Routing and Input Ownership

## 1. Scope

This contract documents the evidence-supported upstream ownership boundary for SOAR deployment selection and artifact runtime inputs. It is restricted to the backend SOAR path.

No React/frontend, ARMD, WHO, model artifact, deployment artifact, feature schema, encoder, preprocessing, trained model, or broad canonical-schema changes were made.

This document does not create a clinician-facing SOAR form and does not define mappings among `infection_site`, `BodyLocation_Group`, `organism`, `pathogen`, or `species`.

## 2. Evidence Reviewed

Repository/runtime surfaces reviewed:

- `apps/api/app/api/v1/pipeline.py`
- `apps/api/app/plugins/manager/workflow_manager.py`
- `apps/api/app/plugins/base/prediction_plugin.py`
- `apps/api/app/plugins/prediction/soar/deployment_scanner.py`
- `apps/api/app/plugins/prediction/soar/deployment_registry.py`
- `apps/api/app/plugins/prediction/soar/soar_prediction_plugin.py`
- `apps/api/app/plugins/prediction/soar/prediction_engine.py`
- `apps/api/tests/test_soar_deployment_contract.py`
- `apps/api/tests/test_plugin_orchestration.py`
- `deployments/SOAR_GSK/*/deployment_info.json`
- `deployments/SOAR_GSK/*/feature_schema.json`
- Existing backend clinical/request schemas and references searched for organism, species, pathogen, antimicrobial, antibiotic, susceptibility, culture, specimen, laboratory, infection, age, country, region, collection date, and beta-lactamase.

Representative artifact evidence:

- `Ceftriaxone_Haemophilus_influenzae/deployment_info.json` contains `antibiotic: Ceftriaxone`, `species: Haemophilus influenzae`, and `feature_count: 6`.
- Its `feature_schema.json` requires `Age`, `YearCollected`, `Region`, `BodyLocation_Group`, `Country`, and `Beta_Lactamase_enc`.
- `Doxycycline_Streptococcus_pneumoniae/feature_schema.json` contains the five-field base variant and no beta-lactamase feature.
- `DeploymentScanner` activates only directories containing both `deployment_info.json` and `feature_schema.json`; it reads identity from metadata and feature names from the feature schema.

## 3. Actual Backend Request Flow

```text
POST /pipeline/execute
    -> PipelineExecutionRequest.input_payload
    -> _patient_payload()
    -> ClinicalDecisionRequest(payload, context)
    -> WorkflowManager._execute_plugin()
    -> PredictionRequest(payload=request.payload, context=request.context)
    -> SOARPredictionPlugin.supports()/predict()
    -> context.deployment_id
    -> DeploymentRegistry.get_by_id()
    -> selected DeploymentInfo and artifact
    -> PredictionEngine feature validation
    -> prediction
```

The API route creates context only as `{ "case_id": request.case_id }` when `case_id` is present. `PipelineExecutionRequest` has no `deployment_id` field. The route does not derive deployment identity from organism, antimicrobial, pathogen, species, or any other value.

`WorkflowManager` passes the `ClinicalDecisionRequest` payload and context directly into the generic `PredictionRequest`. It preserves caller-provided values but does not create or transform them.

Consequently, the exposed pipeline route currently has no connected upstream producer for SOAR `deployment_id` or the six raw artifact fields.

## 4. Deployment Selection Ownership

### Current runtime owner

`SOARPredictionPlugin._select_deployment()` is the runtime selection owner. It requires a non-empty string `request.context["deployment_id"]` and performs an exact lookup through `DeploymentRegistry.get_by_id()`.

The registry is authoritative only for the set of artifact-backed IDs discovered from the SOAR deployment directory. `deployment_info.json` supplies metadata identity (`antibiotic` and `species`); the directory name supplies the registered deployment ID. Metadata is not converted into a clinical selector by the current runtime.

### Upstream owner finding

```text
SOAR Deployment Selection Upstream Owner = NOT IMPLEMENTED
```

No existing backend component is connected to the SOAR pipeline and has enough confirmed information to select one deployment safely. Backend schemas containing partial clinical concepts are not runtime producers merely because their field names resemble artifact or routing fields.

Organism/species and antimicrobial/antibiotic metadata are insufficient as an implemented upstream contract because:

- they are stored in deployment metadata rather than supplied by the pipeline request;
- no connected producer supplies both as a validated routing decision;
- no approved mapping from clinical `organism`, `pathogen`, or `species` to deployment ID exists;
- no approved policy selects among multiple deployments without an explicit ID.

### Minimum proposed boundary, not implemented

A future backend-owned SOAR routing boundary would need to:

1. receive an approved, versioned domain evidence object;
2. validate the evidence and its provenance;
3. resolve exactly one registered deployment ID using an explicit deterministic rule;
4. reject missing, conflicting, or ambiguous evidence;
5. write the validated ID to `ClinicalDecisionRequest.context["deployment_id"]`;
6. preserve that context through `WorkflowManager` into `PredictionRequest`;
7. let `SOARPredictionPlugin` perform the final exact registry lookup.

Until an authoritative owner and approved evidence inputs exist, this boundary remains a documented design requirement, not production code.

## 5. SOAR Ownership Matrix

| SOAR runtime field | Current artifact requirement | Existing backend source | Runtime producer | Transformation | Ownership status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `deployment_id` | Exact registered deployment ID in request context | SOAR artifact directory name and registry; no request producer | `SOARPredictionPlugin` consumes it; upstream producer not implemented | Exact `DeploymentRegistry.get_by_id()` lookup | **NO_UPSTREAM_SOURCE** upstream; **PLUGIN_SPECIFIC** runtime owner | `deployment_scanner.py`, `deployment_registry.py`, `soar_prediction_plugin.py`, `pipeline.py` |
| `Age` | Numeric feature in base and beta variants | No connected producer | Only caller-supplied `input_payload` | Artifact numeric preprocessing | **NO_UPSTREAM_SOURCE** | `feature_schema.json`, `pipeline.py`, `prediction_engine.py` |
| `YearCollected` | Numeric feature in base and beta variants | No connected producer | Only caller-supplied `input_payload` | Artifact numeric preprocessing | **NO_UPSTREAM_SOURCE**; possible dataset/model context is **UNRESOLVED** | `feature_schema.json`, `pipeline.py` |
| `Region` | Categorical feature | No connected producer | Only caller-supplied `input_payload` | One-hot encoding in artifact pipeline | **NO_UPSTREAM_SOURCE** | `feature_schema.json`, `pipeline.py` |
| `BodyLocation_Group` | Categorical feature | No connected producer; no proven `infection_site` mapping | Only caller-supplied `input_payload` | One-hot encoding in artifact pipeline | **NO_UPSTREAM_SOURCE** and clinical mapping **UNRESOLVED** | `feature_schema.json`, `pipeline.py` |
| `Country` | Categorical feature | No connected producer | Only caller-supplied `input_payload` | Target encoding in artifact pipeline | **NO_UPSTREAM_SOURCE** | `feature_schema.json`, `pipeline.py` |
| `Beta_Lactamase_enc` | Required only by beta-lactamase deployments | No connected laboratory producer or deterministic transform | Only caller-supplied payload when selected artifact requires it | Deployment-specific passthrough/bin handling | **NO_UPSTREAM_SOURCE** and deployment-specific **PLUGIN_SPECIFIC** | Ceftriaxone `feature_schema.json`, Doxycycline `feature_schema.json`, `prediction_engine.py` |

No field is classified as clinician-entered, patient data, laboratory data, platform context, or confirmed upstream transformation because the connected runtime path provides no such producer evidence.

## 6. Confirmed Producers and Transformations

### Confirmed

- Deployment artifact metadata produces the registry's deployment metadata (`species`/organism and `antibiotic`/antimicrobial).
- The deployment directory name is used as the registered `deployment_id`.
- `DeploymentScanner` produces `DeploymentInfo` records from artifact-backed directories.
- `WorkflowManager` propagates caller-provided payload and context exactly into `PredictionRequest`.
- `PredictionEngine` validates model-declared required feature names when `feature_names_in_` is available.

### Not confirmed

- No connected API producer supplies `deployment_id`.
- No connected API producer supplies any raw SOAR field.
- No laboratory producer supplies `Beta_Lactamase_enc`.
- No deterministic upstream transformation supplies `BodyLocation_Group` from `infection_site`.
- No universal equivalence exists among `organism`, `pathogen`, and `species`.

Artifact preprocessing transformations are model/runtime transformations, not upstream ownership proofs:

- `Age`, `YearCollected`: numeric transformer.
- `Region`, `BodyLocation_Group`: one-hot transformer.
- `Country`: target encoder.
- `Beta_Lactamase_enc`: deployment-specific passthrough/bin handling.

## 7. No-Source and Unresolved Findings

- `deployment_id`: no upstream source connected to the exposed pipeline route.
- `Age`: no connected source; ownership unresolved.
- `YearCollected`: no connected source; dataset/model-context interpretation is not sufficient to establish request provenance.
- `Region`: no connected source.
- `BodyLocation_Group`: no connected source; `infection_site` mapping unresolved.
- `Country`: no connected source.
- `Beta_Lactamase_enc`: no connected laboratory or platform source.
- `organism` versus `pathogen` versus `species`: **CONFLICT/UNRESOLVED** as a universal clinical mapping.
- `infection_site` versus `BodyLocation_Group`: **UNRESOLVED**.
- `culture`, severity, population, and related clinical aliases: **UNRESOLVED** for SOAR artifact runtime.

## 8. Routing Failure Behavior

The current fail-closed behavior is retained:

- missing or blank `context.deployment_id` raises `DeploymentSelectionError`;
- unknown or invalid IDs raise `DeploymentSelectionError`;
- no organism-only or antimicrobial-only selection occurs;
- no first-valid deployment fallback occurs;
- no filename tokenization is used as clinical identity;
- missing model-declared feature fields raise `PredictionError`;
- an unconnected upstream source is not replaced with a guessed value.

A future routing owner must reject ambiguous evidence rather than select a first or merely similar deployment.

## 9. Production Changes

No production routing or input-wiring changes were made. The evidence does not satisfy the required conditions for safe production changes: an authoritative owner, a confirmed runtime path, deterministic transformation, defined ambiguity behavior, and testable failure behavior.

Focused tests document the existing contract:

- exact payload/context propagation through `WorkflowManager`;
- absence of synthesized deployment context;
- artifact metadata-backed deployment identity;
- explicit-ID selection;
- missing and unknown deployment rejection;
- missing artifact-feature rejection.

## 10. Tests Executed

```text
.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_plugin_orchestration.py -q
4 passed

.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_soar_deployment_contract.py -q
7 passed

.\.venv\Scripts\python.exe -m pytest apps/api/tests/test_plugin_input_schema_contract.py -q
9 passed
```

Existing dependency/configuration deprecation warnings were emitted; no failures were reported.

## 11. Final Freeze Decision

The runtime selection mechanism is deterministic once an explicit validated deployment ID exists, but the upstream owner and raw input provenance remain incomplete. Therefore the broader SOAR deployment contract is not frozen.

```text
SOAR Deployment Selection Owner = NOT IMPLEMENTED

SOAR Deployment ID Upstream Source = NOT CONFIRMED

SOAR Raw Input Provenance = INCOMPLETE

SOAR Routing Contract Deterministic = YES

SOAR Deployment Contract Frozen = NO

Plugin Runtime Contract Frozen = NO

Frontend Contract Ready = NO
```
