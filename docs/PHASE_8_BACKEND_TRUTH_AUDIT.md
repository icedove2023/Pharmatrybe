# PHASE 8 PRE-IMPLEMENTATION — BACKEND TRUTH AUDIT

**Date**: August 15, 2025  
**Status**: BACKEND TRUTH AUDIT COMPLETE  
**Approach**: Strict repository-only verification, no guessing, no frontend inference  

---

## Executive Summary

This audit establishes the exact backend implementation reality for Phase 8. Based on direct inspection of the FastAPI implementation, data models, routes, and tests, the backend exposes a **canonical recommendation response contract** with specific fields and structures.

### Key Finding

The actual recommendation API is:
- **Route**: `POST /api/v1/recommendations/generate`
- **Response Model**: `ExplainabilityResponseContract`
- **Required Fields**: 10 mandatory fields that must all be present
- **Test Validation**: 16 automated tests verify the contract

### What Does NOT Exist in Backend

- ❌ Accept/override recommendation endpoints
- ❌ Prescription signing endpoints
- ❌ `costTier` field
- ❌ `monitoringPlan` field
- ❌ Plugin metadata returned with recommendation response
- ❌ Nested `confidence.explanation` object structure

### What DOES Exist

- ✅ Full explainability response contract with evidence ranking, trace, and attribution
- ✅ SHAP computation (internal to plugins, returned as `prediction_explanation`)
- ✅ Complete audit trail with version metadata
- ✅ Clinical rule results with affected drugs
- ✅ Spectrum analysis (metadata only, not top-level field)
- ✅ Clinical review recording endpoint (passive, not decision override)

---

## 1. RECOMMENDATION API — EXACT IMPLEMENTATION

### Primary Route

**File**: [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py)

**HTTP Method & Path**:
```
POST /api/v1/recommendations/generate
```

**Request Model**: Anonymous body with these parameters:
- `patient_id: str` (Body)
- `patient_data: Dict[str, Any]` (Body)
- `prediction_results: Dict[str, float]` (Body) — antibiotic → probability mapping
- `prediction_explanation: Optional[Dict[str, Any]]` (Body) — SHAP or other explanation
- `prediction_plugin_version: str` (Body, default "0.1.0")
- `model_versions: Optional[Dict[str, str]]` (Body)

**Response Model**: `ExplainabilityResponseContract`

### Canonical Response Contract

**Class Definition**: `ExplainabilityResponseContract` in [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py)

**All Response Fields** (mandatory unless marked optional):

| Field | Type | Required | Source | Description |
|-------|------|----------|--------|-------------|
| `status` | `str` | ✅ | Orchestrator | Response status: "success" or "error" |
| `patient_id` | `str` | ✅ | Request | Patient identifier |
| `recommendation` | `Dict[str, Any]` | ✅ | RecommendationResult.to_dict() | Primary antibiotic recommendation with rationale |
| `confidence` | `str` | ✅ | RecommendationConfidence enum | Confidence level: very_high/high/moderate/low/very_low |
| `evidence_ranking` | `Dict[str, Any]` | ✅ | EvidenceRanking.to_dict() | Ranked evidence by composite weight |
| `evidence_attribution` | `List[Dict[str, Any]]` | ✅ | List of EvidenceAttribution.to_dict() | Source attribution for each evidence item |
| `recommendation_trace` | `Dict[str, Any]` | ✅ | RecommendationTrace.to_dict() | Structured execution steps through pipeline |
| `audit_reference` | `Dict[str, Any]` | ✅ | AuditTrail fields | Audit trail reference for reproducibility |
| `explanation` | `Dict[str, Any]` | 🔄 | RecommendationExplanation.to_dict() | Optional explanation object |
| `generated_at` | `str` | ✅ | API layer | ISO timestamp when response generated |
| `trace_id` | `str` | ✅ | UUID generated in API | Distributed trace ID for logging |

**Validation**:
```python
def validate_explainability_response(response: Dict[str, Any]) -> None:
```

Required fields that must not be None:
- `recommendation`
- `confidence`
- `evidence_ranking` (must contain `ranked_evidence` key)
- `recommendation_trace` (must contain `trace_steps` key)
- `audit_reference` (must contain `recommendation_id`, `patient_id`, `timestamp`, `trace_id`)

### Alternate/Legacy Routes

**File**: [apps/api/app/api/routes/clinical_decision.py](../../apps/api/app/api/routes/clinical_decision.py)

**Route 1**: `POST /recommendation/`
- Request: `RecommendationRequest`
- Response: `RecommendationResponse`
- Status: Legacy — maintained for backward compatibility

**Route 2**: Clinical Review (not accept/override)
- **Path**: `POST /recommendation/clinical-review`
- **Purpose**: Record clinician's review decision (APPROVED/MODIFIED/REJECTED)
- **NOT**: Modifies recommendation; only records clinician's decision for audit
- **Request Model**: `ClinicalReviewRequest`
- **Response**: Confirmation with recorded decision

**Route 3**: Explanation Retrieval
- **Path**: `POST /recommendation/explanation`
- **Purpose**: Get detailed explanation
- **Request Model**: `ExplanationRequest`
- **Response**: Explanation with evidence breakdown

---

## 2. EXPLAINABILITY FIELDS — DETAILED STRUCTURE

### evidence_ranking

**Type**: `Dict[str, Any]`  
**Source**: `EvidenceRanking.to_dict()` from [apps/api/app/clinical_decision/explainability_enhancements.py](../../apps/api/app/clinical_decision/explainability_enhancements.py)

**Structure**:
```python
{
    "recommendation_id": str,
    "patient_id": str,
    "ranked_evidence": [
        {
            "evidence_id": str,
            "evidence_type": str,  # "prediction"|"guideline"|"clinical_rule"|"stewardship"
            "source_plugin": str,
            "description": str,
            "confidence_score": float,  # 0.0-1.0
            "clinical_importance": float,  # 0.0-1.0
            "rank": int,
            "composite_weight": float,  # confidence × importance
            "antibiotic_name": Optional[str],
            "supporting_data": Dict[str, Any]
        }
    ],
    "ranking_algorithm": str,  # "composite_weight (confidence × clinical_importance)"
    "timestamp": str  # ISO format
}
```

**Key Point**: Evidence is ranked by `composite_weight = confidence_score × clinical_importance`, providing transparent ordering of decision drivers.

### recommendation_trace

**Type**: `Dict[str, Any]`  
**Source**: `RecommendationTrace.to_dict()` from [apps/api/app/clinical_decision/explainability_enhancements.py](../../apps/api/app/clinical_decision/explainability_enhancements.py)

**Structure**:
```python
{
    "recommendation_id": str,
    "patient_id": str,
    "trace_steps": [
        {
            "step_number": int,
            "phase_name": str,  # e.g., "orchestration", "explanation", "audit"
            "description": str,
            "inputs": Dict[str, Any],
            "outputs": Dict[str, Any],
            "duration_ms": float,
            "timestamp": str  # ISO format
        }
    ],
    "total_duration_ms": float,
    "timestamp": str  # ISO format
}
```

**Key Point**: Purely structured data — no timeline rendering, no presentation logic. Records execution steps only.

### evidence_attribution

**Type**: `List[Dict[str, Any]]`  
**Source**: List of `EvidenceAttribution.to_dict()` from [apps/api/app/clinical_decision/explainability_enhancements.py](../../apps/api/app/clinical_decision/explainability_enhancements.py)

**Element Structure**:
```python
{
    "attribution_id": str,
    "evidence_type": str,  # "prediction"|"guideline"|"clinical_rule"|"stewardship"
    "originating_plugin": Optional[str],  # Which plugin generated this
    "originating_rule": Optional[str],  # Which rule triggered (if from rules)
    "originating_guideline": Optional[str],  # Which guideline (if from knowledge)
    "confidence": float,  # 0.0-1.0 from source
    "evidence_summary": Dict[str, Any],  # Structured data from source
    "metadata": Dict[str, Any]  # Additional attribution details
}
```

**Key Point**: Enables complete traceability without narrative explanations. Each evidence item is tracked to its exact origin.

### audit_reference

**Type**: `Dict[str, Any]`  
**Source**: `AuditTrail.to_dict()` from [apps/api/app/clinical_decision/contracts.py](../../apps/api/app/clinical_decision/contracts.py)

**Structure**:
```python
{
    "recommendation_id": str,  # Unique recommendation ID
    "patient_id": str,
    "timestamp": str,  # ISO format when recommendation generated
    "prediction_plugin_version": str,  # SOAR/ARMD version
    "model_versions": Dict[str, str],  # Specific model versions
    "rule_versions": str,  # Clinical rules engine version
    "guideline_engine_version": str,
    "stewardship_engine_version": str,
    "cdss_version": str,  # Clinical Decision Support System version
    "algorithm_version": str,
    "trace_id": str,  # Distributed trace ID (same as response.trace_id)
    "metadata": Dict[str, Any]  # Additional audit metadata
}
```

**Key Point**: Complete version history for reproducibility. Every component version is captured.

### explanation

**Type**: `Optional[Dict[str, Any]]`  
**Source**: `RecommendationExplanation.to_dict()` from [apps/api/app/clinical_decision/contracts.py](../../apps/api/app/clinical_decision/contracts.py)

**Structure**:
```python
{
    "recommendation_id": str,
    "patient_id": str,
    "primary_antibiotic": str,
    "prediction_explanation": Dict[str, Any],  # SHAP or ML explanation from plugin
    "rule_explanations": List[str],  # Which rules fired and how
    "guideline_explanations": List[str],  # Relevant guideline evidence
    "stewardship_explanations": List[str],  # Stewardship rationale
    "evidence_drivers": [
        {
            "evidence_type": str,
            "source": str,
            "contribution": str,  # "supports"|"opposes"|"neutral"
            "weight": float,
            "explanation": str
        }
    ],
    "warnings": List[str],
    "clinical_narrative": str,
    "generated_at": str  # ISO format
}
```

### clinicalReasoningText or reasoning_tree

**Status**: NOT IMPLEMENTED in backend response contract

These are NOT present in the canonical response. The backend provides structured evidence through `evidence_ranking`, `recommendation_trace`, and `audit_reference` instead of free-form text narratives.

---

## 3. SHAP / FEATURE ATTRIBUTION — INTERNAL vs. PUBLIC

### SHAP Computation

**Where SHAP is computed**:
- [apps/api/app/knowledge/providers/soar/soar_prediction_engine.py](../../apps/api/app/knowledge/providers/soar/soar_prediction_engine.py) — lines 277-365
- [apps/api/app/plugins/prediction/soar/explainability_adapter.py](../../apps/api/app/plugins/prediction/soar/explainability_adapter.py) — full implementation
- [apps/api/app/plugins/prediction/armd/explainability.py](../../apps/api/app/plugins/prediction/armd/explainability.py) — SHAP-based explanations

**What SHAP computes**:
- Feature contributions (SHAP values) for each prediction
- TreeExplainer or KernelExplainer selection
- Normalized SHAP values for interpretability

### How SHAP is Exposed

**1. In Request (Optional Input)**:
```
POST /api/v1/recommendations/generate
  prediction_explanation: {
    "shap_values": [feature_contribution_1, feature_contribution_2, ...],
    "features": ["organism_type", "patient_age", ...],
    "base_value": float,
    "method": "shap",
    "version": str
  }
```

**2. In Response (Inside explanation object)**:
```
response.explanation.prediction_explanation = {
    "shap_values": [...],
    "features": [...],
    "method": "shap",
    ...
}
```

**Classification**:
- ✅ BACKEND_PRESENT_INTERNAL_ONLY: SHAP is computed by plugins
- ✅ BACKEND_OPTIONAL: Returned only if included in request
- ✅ PUBLIC: Returned as part of optional `explanation.prediction_explanation`
- ❌ NOT: A separate top-level response field
- ❌ NOT: `shapSummary` or `shap_features` as discrete top-level fields

---

## 4. RECOMMENDATION TRACE STRUCTURE — DETAILED

### TraceStep Definition

From `RecommendationTraceStep` in [apps/api/app/clinical_decision/explainability_enhancements.py](../../apps/api/app/clinical_decision/explainability_enhancements.py):

**Fields**:
- `step_number: int` — Sequence number (1, 2, 3, ...)
- `phase_name: str` — Name of execution phase
- `description: str` — What happened in this step
- `inputs: Dict[str, Any]` — Input data to this step (structured)
- `outputs: Dict[str, Any]` — Output generated by this step (structured)
- `duration_ms: float` — How long this step took
- `timestamp: datetime` — When step executed

### Example trace_steps

```python
[
    {
        "step_number": 1,
        "phase_name": "orchestration",
        "description": "Orchestrated clinical decision pipeline",
        "inputs": {"prediction_results": {"amoxicillin": 0.85}},
        "outputs": {},
        "duration_ms": 0,
        "timestamp": "2025-08-15T10:30:00Z"
    },
    {
        "step_number": 2,
        "phase_name": "explanation",
        "description": "Generated unified explanation",
        "inputs": {},
        "outputs": {},
        "duration_ms": 0,
        "timestamp": "2025-08-15T10:30:01Z"
    },
    {
        "step_number": 3,
        "phase_name": "audit",
        "description": "Created audit trail",
        "inputs": {},
        "outputs": {},
        "duration_ms": 0,
        "timestamp": "2025-08-15T10:30:02Z"
    }
]
```

### What trace does NOT contain

- ❌ `nodes` field (no tree structure)
- ❌ `stages` field (use `phase_name` and `step_number` for ordering)
- ❌ Nested plugin details (plugins are part of evidence_attribution, not trace)
- ❌ Status codes or error information (only successful execution steps recorded)

---

## 5. AUDIT / PROVENANCE — COMPLETE BREAKDOWN

### AuditTrail Model

**File**: [apps/api/app/clinical_decision/contracts.py](../../apps/api/app/clinical_decision/contracts.py), lines 345-393

**All Fields**:

| Field | Type | Public API? | Status | Purpose |
|-------|------|------------|--------|---------|
| `recommendation_id` | `str` | YES (in audit_reference) | VERIFIED | Unique recommendation identifier |
| `patient_id` | `str` | YES (in audit_reference) | VERIFIED | Patient identifier |
| `timestamp` | `datetime` | YES (as ISO string in audit_reference) | VERIFIED | When recommendation was generated |
| `prediction_plugin_version` | `str` | YES (in audit_reference) | VERIFIED | SOAR/ARMD version used |
| `model_versions` | `Dict[str, str]` | YES (in audit_reference) | VERIFIED | Specific model versions |
| `rule_versions` | `str` | YES (in audit_reference) | VERIFIED | Clinical rules engine version |
| `guideline_engine_version` | `str` | YES (in audit_reference) | VERIFIED | Guideline engine version |
| `stewardship_engine_version` | `str` | YES (in audit_reference) | VERIFIED | Stewardship engine version |
| `cdss_version` | `str` | YES (in audit_reference) | VERIFIED | CDSS version |
| `algorithm_version` | `str` | YES (in audit_reference) | VERIFIED | Overall algorithm version |
| `trace_id` | `str` | YES (in audit_reference + top-level response) | VERIFIED | Distributed trace ID for logging |
| `metadata` | `Dict[str, Any]` | YES (in audit_reference) | VERIFIED | Additional audit metadata |

**Generated_at vs timestamp**:
- `response.generated_at` — When response was created (top-level)
- `response.audit_reference.timestamp` — When recommendation was generated (in audit)
- Both are ISO format strings

---

## 6. CLINICAL RULES — MODEL VERIFICATION

### ClinicalRuleResult Model

**File**: [apps/api/app/clinical_decision/contracts.py](../../apps/api/app/clinical_decision/contracts.py), lines 56-101

**Exact Fields**:

```python
@dataclass
class ClinicalRuleResult:
    rule_id: str
    rule_name: str
    status: RuleStatus  # PASSED | TRIGGERED | SKIPPED | ERROR
    severity: RuleSeverity = RuleSeverity.LOW  # CRITICAL | HIGH | MEDIUM | LOW | INFO
    message: str = ""
    affected_drugs: List[str] = field(default_factory=list)
    evidence: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### Where clinical_rules Appears in Response

**Path in response**:
```
response.recommendation.clinical_rules = [
    {
        "rule_id": str,
        "rule_name": str,
        "status": str,  # "passed"|"triggered"|"skipped"|"error"
        "severity": str,  # "critical"|"high"|"medium"|"low"|"info"
        "message": str,
        "affected_drugs": List[str],
        "evidence": Optional[str],
        "metadata": Dict[str, Any],
        "evaluated_at": str  # ISO format
    }
]
```

### What clinical_rules does NOT have

- ❌ `adjustment_notes` field (not in model)
- ❌ `category` field (not in model)
- ❌ `recommendation` field (clinical rules output findings, not recommendations)
- ❌ `ruleSource` field (no such provenance field in model)

### Where to Find in Response

```python
response["recommendation"]["clinical_rules"][i]["affected_drugs"]
response["recommendation"]["clinical_rules"][i]["severity"]
response["recommendation"]["clinical_rules"][i]["message"]
```

---

## 7. ACCEPT / OVERRIDE ENDPOINTS — VERIFICATION

### Search Results

**File**: [apps/api/app/api/routes/clinical_decision.py](../../apps/api/app/api/routes/clinical_decision.py)

Only clinical review endpoint found:

**Route**: `POST /recommendation/clinical-review`

**Request**:
```python
class ClinicalReviewRequest(BaseModel):
    recommendation_id: str
    clinician_id: str
    review_decision: str  # "APPROVED"|"MODIFIED"|"REJECTED"
    selected_antibiotic: Optional[str]
    clinical_notes: Optional[str]
    reason_for_deviation: Optional[str]
```

**Response**:
```python
{
    "status": "success",
    "recommendation_id": str,
    "review_decision": str,
    "clinician_id": str,
    "recorded_at": str,  # ISO timestamp
    "message": "Clinical review recorded successfully"
}
```

**CRITICAL**: This endpoint only **records** the clinician's decision for audit. It does NOT:
- Modify the recommendation
- Override the recommendation
- Change the backend response
- Sign a prescription
- Produce a modified recommendation

### Accept/Override Endpoints

**Status**: ❌ NOT IMPLEMENTED IN BACKEND

Searched entire API tree:
- [apps/api/app/api/v1/](../../apps/api/app/api/v1/)
- [apps/api/app/api/routes/](../../apps/api/app/api/routes/)
- [apps/api/app/api/router.py](../../apps/api/app/api/router.py)

**Result**: No route registration for:
- `POST /api/v1/recommendations/accept`
- `POST /api/v1/recommendations/override`
- `POST /recommendation/accept`
- `POST /recommendation/override`
- `POST /api/v1/prescriptions/sign`
- Any other accept/override variant

---

## 8. COST / FORMULARY — AVAILABILITY AUDIT

### Explicit Search

**Query**: Search for `costTier|cost|formulary|price|affordability|spectrum|drug cost`

**Results**:
- **costTier**: NOT FOUND in response models
- **formulary**: NOT FOUND in API contracts
- **price**: NOT FOUND in models or responses
- **cost_tier**: NOT FOUND anywhere
- **affordability**: NOT FOUND
- **spectrum**: FOUND only in stewardship metadata, not as top-level field

### Spectrum (Only Public Instance)

**File**: [apps/api/app/clinical_decision/stewardship.py](../../apps/api/app/clinical_decision/stewardship.py)

Spectrum analysis is INTERNAL to stewardship logic:

```python
metadata={"antibiotic": antibiotic, "spectrum": "broad"}
```

This is metadata in `StewardshipFinding` object, which becomes part of:
```
response.recommendation.stewardship_findings[i].metadata["spectrum"]
```

**Classification**: 
- ✅ BACKEND_PRESENT_INTERNAL: Stewardship engine analyzes spectrum
- ✅ BACKEND_OPTIONAL: Returned only if stewardship concern detected
- 🔄 NOT_GUARANTEED: Not required field, not top-level

---

## 9. PLUGIN PROVENANCE IN RESPONSES

### PluginMetadata Structure

**File**: [apps/api/app/plugins/base/plugin.py](../../apps/api/app/plugins/base/plugin.py)

```python
@dataclass(frozen=True)
class PluginMetadata:
    plugin_id: str
    plugin_name: str
    plugin_version: str
    plugin_type: PluginType
    description: str
    author: str
    capabilities: List[str]
    dependencies: List[str]
```

### How Plugin Info Appears in Responses

**1. In audit_reference** (ONLY location):
```python
response.audit_reference = {
    "prediction_plugin_version": str,  # Plugin version only
    ...
}
```

**2. Plugin metadata in evidence_attribution**:
```python
response.evidence_attribution[i] = {
    "originating_plugin": str,  # Plugin name only
    "originating_rule": Optional[str],
    "originating_guideline": Optional[str],
    ...
}
```

### What is NOT exposed

- ❌ Full PluginMetadata object in response
- ❌ Plugin description field
- ❌ Plugin author field
- ❌ Plugin dependencies field
- ❌ Plugin type field
- ❌ Plugin ID in recommendation (only name/version)
- ❌ Plugin health status in recommendation (separate endpoint)
- ❌ Plugin capabilities in recommendation (metadata only)

### Plugin Health Status

**Separate Endpoint** (not recommendation response):
- `GET /api/v1/plugins/{plugin_id}/health` — Available but not in recommendation response

---

## 10. TEST EVIDENCE — AUTHORITATIVE FILES

### Primary Test File for Recommendation Contract

**File**: [apps/api/tests/test_phase6_api_integration.py](../../apps/api/tests/test_phase6_api_integration.py)

**Test Count**: 16 tests

**Verified Fields**:
- ✅ `recommendation` present
- ✅ `confidence` from Decision Fusion
- ✅ `evidence_ranking` present and contains `ranked_evidence`
- ✅ `recommendation_trace` present and contains `trace_steps`
- ✅ `evidence_attribution` present as list
- ✅ `audit_reference` complete with required fields
- ✅ `trace_id` consistent across response
- ✅ `patient_id` consistent across all objects
- ✅ `generated_at` in ISO format
- ✅ Multiple predictions handled correctly

**Test Examples**:
- `test_generate_recommendation_returns_explainability_contract`
- `test_recommendation_response_has_evidence_ranking`
- `test_recommendation_response_has_recommendation_trace`
- `test_recommendation_response_has_audit_reference_links_evidence`
- `test_patient_ids_consistent_across_response`

### Additional Test Files

**Clinical Decision Tests**: [apps/api/tests/test_clinical_decision.py](../../apps/api/tests/test_clinical_decision.py)
- Tests: Rule evaluation, stewardship analysis, clinical rule triggering

**Plugin Integration Tests**: [apps/api/tests/test_plugin_integration.py](../../apps/api/tests/test_plugin_integration.py)
- Tests: Plugin discovery, registry, orchestration

**Clinical Intelligence Tests**: [apps/api/tests/test_clinical_intelligence_pipeline.py](../../apps/api/tests/test_clinical_intelligence_pipeline.py)
- Tests: End-to-end pipeline validation

---

## 11. AUTHORITATIVE FILE LIST

| Area | Authoritative File | What It Contains |
|------|--------------------|------------------|
| **Recommendation Route** | [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py) | POST /api/v1/recommendations/generate, ExplainabilityResponseContract definition, validation logic |
| **Request Schema** | [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py) | Body parameters: patient_id, patient_data, prediction_results, prediction_explanation, plugin versions |
| **Response Schema** | [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py) | Complete ExplainabilityResponseContract with all 11 fields and their exact types |
| **Explainability Components** | [apps/api/app/clinical_decision/explainability_enhancements.py](../../apps/api/app/clinical_decision/explainability_enhancements.py) | EvidenceRanking, EvidenceAttribution, RecommendationTrace, RecommendationTraceStep models |
| **Domain Models** | [apps/api/app/clinical_decision/contracts.py](../../apps/api/app/clinical_decision/contracts.py) | RecommendationResult, ClinicalRuleResult, AuditTrail, RecommendationExplanation, all clinical enums |
| **Orchestrator** | [apps/api/app/clinical_decision/orchestrator.py](../../apps/api/app/clinical_decision/orchestrator.py) | CDSSOrchestrator.generate_recommendation, core decision logic, error handling |
| **Explainability Engine** | [apps/api/app/clinical_decision/explainability.py](../../apps/api/app/clinical_decision/explainability.py) | generate_evidence_ranking, generate_recommendation_trace, generate_evidence_attribution, generate_explanation, generate_audit_trail |
| **Clinical Rules** | [apps/api/app/clinical_decision/rules/__init__.py](../../apps/api/app/clinical_decision/rules/__init__.py) | ClinicalRuleResult evaluation, allergy rules, renal rules, pregnancy rules |
| **Stewardship** | [apps/api/app/clinical_decision/stewardship.py](../../apps/api/app/clinical_decision/stewardship.py) | Spectrum analysis, escalation/de-escalation recommendations, StewardshipFinding |
| **Plugin Base** | [apps/api/app/plugins/base/plugin.py](../../apps/api/app/plugins/base/plugin.py) | PluginMetadata, BasePlugin abstract interface, plugin lifecycle |
| **SHAP (SOAR)** | [apps/api/app/knowledge/providers/soar/soar_prediction_engine.py](../../apps/api/app/knowledge/providers/soar/soar_prediction_engine.py) | SHAP computation, feature contributions, explainability extraction |
| **SHAP (SOAR Plugin)** | [apps/api/app/plugins/prediction/soar/explainability_adapter.py](../../apps/api/app/plugins/prediction/soar/explainability_adapter.py) | TreeExplainer/KernelExplainer selection, SHAP value normalization |
| **Legacy Route** | [apps/api/app/api/routes/clinical_decision.py](../../apps/api/app/api/routes/clinical_decision.py) | POST /recommendation/, clinical review endpoint, explanation endpoint |
| **Tests: Phase 6** | [apps/api/tests/test_phase6_api_integration.py](../../apps/api/tests/test_phase6_api_integration.py) | 16 tests validating explainability contract, all required fields, consistency |
| **Tests: Clinical** | [apps/api/tests/test_clinical_decision.py](../../apps/api/tests/test_clinical_decision.py) | Rule evaluation, stewardship analysis, clinical rule result structure |
| **Tests: Plugin** | [apps/api/tests/test_plugin_integration.py](../../apps/api/tests/test_plugin_integration.py) | Plugin registry, discovery, orchestration |

---

## 12. FINAL TRUTH MATRIX

### Classification Legend

- **BACKEND_VERIFIED**: Explicitly defined in production models, routes, and validated by tests
- **BACKEND_PRESENT_INTERNAL_ONLY**: Implemented in backend but not exposed through public API response
- **BACKEND_OPTIONAL**: Available in response only under certain conditions
- **NOT_BACKEND_VERIFIED**: Not found in repository implementation

### Complete Truth Matrix

| Field / Feature | Exact Backend Path | Public API? | Classification | Status |
|-----------------|--------------------|-------------|-----------------|--------|
| **POST /api/v1/recommendations/generate** | [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py):163 | YES | BACKEND_VERIFIED | Active primary route |
| **status** | ExplainabilityResponseContract.status | YES | BACKEND_VERIFIED | Required field |
| **patient_id** | ExplainabilityResponseContract.patient_id | YES | BACKEND_VERIFIED | Required field |
| **recommendation** | ExplainabilityResponseContract.recommendation | YES | BACKEND_VERIFIED | Required field, Dict[str, Any] |
| **recommendation.primary_recommendation** | RecommendationResult.primary_recommendation | YES | BACKEND_VERIFIED | RecommendedAntibiotic object |
| **recommendation.alternative_recommendations** | RecommendationResult.alternative_recommendations | YES | BACKEND_VERIFIED | List[RecommendedAntibiotic] |
| **recommendation.clinical_rules** | RecommendationResult.clinical_rules | YES | BACKEND_VERIFIED | List[ClinicalRuleResult] |
| **recommendation.clinical_rules[i].affected_drugs** | ClinicalRuleResult.affected_drugs | YES | BACKEND_VERIFIED | List[str] |
| **recommendation.stewardship_findings** | RecommendationResult.stewardship_findings | YES | BACKEND_VERIFIED | List[StewardshipFinding] |
| **recommendation.stewardship_findings[i].metadata["spectrum"]** | StewardshipFinding.metadata | YES | BACKEND_OPTIONAL | Only if spectrum concern detected |
| **confidence** | ExplainabilityResponseContract.confidence | YES | BACKEND_VERIFIED | String enum: very_high/high/moderate/low/very_low |
| **confidence.explanation** | N/A | NO | NOT_BACKEND_VERIFIED | Not implemented; confidence is string, not object |
| **evidence_ranking** | ExplainabilityResponseContract.evidence_ranking | YES | BACKEND_VERIFIED | EvidenceRanking.to_dict() |
| **evidence_ranking.ranked_evidence** | EvidenceRanking.ranked_evidence | YES | BACKEND_VERIFIED | List[RankedEvidence] |
| **evidence_ranking.ranked_evidence[i].evidence_type** | RankedEvidence.evidence_type | YES | BACKEND_VERIFIED | EvidenceType enum |
| **evidence_ranking.ranked_evidence[i].confidence_score** | RankedEvidence.confidence_score | YES | BACKEND_VERIFIED | Float 0.0-1.0 |
| **evidence_ranking.ranked_evidence[i].composite_weight** | RankedEvidence.get_composite_weight() | YES | BACKEND_VERIFIED | Calculated: confidence × importance |
| **evidence_attribution** | ExplainabilityResponseContract.evidence_attribution | YES | BACKEND_VERIFIED | List[EvidenceAttribution.to_dict()] |
| **evidence_attribution[i].originating_plugin** | EvidenceAttribution.originating_plugin | YES | BACKEND_VERIFIED | Optional[str] |
| **evidence_attribution[i].confidence** | EvidenceAttribution.confidence | YES | BACKEND_VERIFIED | Float 0.0-1.0 |
| **recommendation_trace** | ExplainabilityResponseContract.recommendation_trace | YES | BACKEND_VERIFIED | RecommendationTrace.to_dict() |
| **recommendation_trace.trace_steps** | RecommendationTrace.trace_steps | YES | BACKEND_VERIFIED | List[RecommendationTraceStep] |
| **recommendation_trace.trace_steps[i].phase_name** | RecommendationTraceStep.phase_name | YES | BACKEND_VERIFIED | String |
| **recommendation_trace.trace_steps[i].duration_ms** | RecommendationTraceStep.duration_ms | YES | BACKEND_VERIFIED | Float |
| **recommendation_trace.nodes** | N/A | NO | NOT_BACKEND_VERIFIED | Not implemented; use trace_steps instead |
| **audit_reference** | ExplainabilityResponseContract.audit_reference | YES | BACKEND_VERIFIED | AuditTrail.to_dict() |
| **audit_reference.recommendation_id** | AuditTrail.recommendation_id | YES | BACKEND_VERIFIED | String UUID |
| **audit_reference.timestamp** | AuditTrail.timestamp | YES | BACKEND_VERIFIED | ISO datetime string |
| **audit_reference.prediction_plugin_version** | AuditTrail.prediction_plugin_version | YES | BACKEND_VERIFIED | String |
| **audit_reference.model_versions** | AuditTrail.model_versions | YES | BACKEND_VERIFIED | Dict[str, str] |
| **audit_reference.rule_versions** | AuditTrail.rule_versions | YES | BACKEND_VERIFIED | String |
| **audit_reference.trace_id** | AuditTrail.trace_id | YES | BACKEND_VERIFIED | String UUID |
| **explanation** | ExplainabilityResponseContract.explanation | YES | BACKEND_OPTIONAL | RecommendationExplanation.to_dict() or None |
| **explanation.prediction_explanation** | RecommendationExplanation.prediction_explanation | YES | BACKEND_OPTIONAL | Dict[str, Any] with SHAP data if provided |
| **explanation.prediction_explanation.shap_values** | Prediction plugin output | YES | BACKEND_OPTIONAL | List[float] if SHAP enabled |
| **explanation.rule_explanations** | RecommendationExplanation.rule_explanations | YES | BACKEND_OPTIONAL | List[str] |
| **explanation.guideline_explanations** | RecommendationExplanation.guideline_explanations | YES | BACKEND_OPTIONAL | List[str] |
| **explanation.evidence_drivers** | RecommendationExplanation.evidence_drivers | YES | BACKEND_OPTIONAL | List[ExplainabilityDriver] |
| **generated_at** | ExplainabilityResponseContract.generated_at | YES | BACKEND_VERIFIED | ISO datetime string |
| **trace_id** | ExplainabilityResponseContract.trace_id | YES | BACKEND_VERIFIED | String UUID |
| **POST /recommendation/clinical-review** | [apps/api/app/api/routes/clinical_decision.py](../../apps/api/app/api/routes/clinical_decision.py):244 | YES | BACKEND_VERIFIED | Clinician decision logging only, not recommendation override |
| **POST /api/v1/recommendations/accept** | N/A | NO | NOT_BACKEND_VERIFIED | NOT IMPLEMENTED |
| **POST /api/v1/recommendations/override** | N/A | NO | NOT_BACKEND_VERIFIED | NOT IMPLEMENTED |
| **POST /prescriptions/sign** | N/A | NO | NOT_BACKEND_VERIFIED | NOT IMPLEMENTED |
| **costTier** | N/A | NO | NOT_BACKEND_VERIFIED | NOT IMPLEMENTED |
| **monitoringPlan** | N/A | NO | NOT_BACKEND_VERIFIED | NOT IMPLEMENTED |
| **warning.ruleSource** | N/A | NO | NOT_BACKEND_VERIFIED | Not a field in Warning model |
| **adjustment_notes** | N/A | NO | NOT_BACKEND_VERIFIED | NOT IMPLEMENTED |
| **spectrum (top-level)** | N/A | NO | NOT_BACKEND_VERIFIED | Only in stewardship metadata |
| **PluginMetadata (in response)** | N/A | NO | NOT_BACKEND_VERIFIED | Plugin info not returned with recommendation |
| **SHAP computation** | [apps/api/app/plugins/prediction/soar/explainability_adapter.py](../../apps/api/app/plugins/prediction/soar/explainability_adapter.py) | INTERNAL | BACKEND_PRESENT_INTERNAL_ONLY | Computed by plugins, not exposed standalone |
| **SHAP in response** | explanation.prediction_explanation | YES | BACKEND_OPTIONAL | Returned if prediction_explanation included in request |

---

## EXECUTIVE FINDINGS

### What Exists in Backend

✅ **Canonical Explainability Response Contract**
- `POST /api/v1/recommendations/generate` returns structured response with 11 fields
- All required fields validated before response
- Contract tested by 16 automated tests

✅ **Complete Evidence Tracking**
- Evidence ranking by composite weight (confidence × importance)
- Evidence attribution to exact source (plugin/rule/guideline)
- Recommendation trace with execution steps

✅ **Full Audit Trail**
- Version metadata for all components
- Distributed tracing for debugging
- Timestamp and reproducibility fields

✅ **Clinical Decision Components**
- ClinicalRuleResult with affected_drugs
- StewardshipFinding with spectrum analysis
- RecommendedAntibiotic with confidence and alternatives

✅ **SHAP / Feature Attribution**
- Computed by plugins internally
- Optionally returned in explanation.prediction_explanation
- Normalized SHAP values for interpretability

### What Does NOT Exist in Backend

❌ **Accept/Override Workflow**
- No endpoint to modify or override recommendations
- Clinical review endpoint only records clinician decision, doesn't change recommendation
- No prescription signing endpoints

❌ **Additional Fields**
- `costTier`, `monitoringPlan`, `adjustment_notes`
- Nested `confidence.explanation` object
- `warning.ruleSource` or similar provenance fields

❌ **Plugin Metadata in Response**
- Plugin info not returned with recommendation
- Only plugin version and name in audit/attribution context

❌ **Alternative Response Structures**
- No `clinicalReasoningText` field
- No `reasoningTree` or nested nodes structure
- No top-level `spectrum` field (only in stewardship metadata)

---

## FILES FOR GEMINI AI STUDIO — PHASE 8

### Critical Files to Provide

1. **[apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py)**
   - Route definition, request/response models, validation logic
   - **What to explain**: This is the authoritative API contract

2. **[apps/api/app/clinical_decision/contracts.py](../../apps/api/app/clinical_decision/contracts.py)**
   - All domain models (RecommendationResult, ClinicalRuleResult, AuditTrail, etc.)
   - **What to explain**: These are the real backend data structures

3. **[apps/api/app/clinical_decision/explainability_enhancements.py](../../apps/api/app/clinical_decision/explainability_enhancements.py)**
   - Evidence ranking, attribution, trace structures
   - **What to explain**: How evidence is ranked and structured for frontend

4. **[apps/api/app/clinical_decision/orchestrator.py](../../apps/api/app/clinical_decision/orchestrator.py)**
   - CDSSOrchestrator implementation, decision logic
   - **What to explain**: Core recommendation generation flow

5. **[apps/api/tests/test_phase6_api_integration.py](../../apps/api/tests/test_phase6_api_integration.py)**
   - 16 tests validating the contract
   - **What to explain**: How the backend actually behaves

### Instructions for Gemini

**Key Message**:
> "The backend exposes one canonical recommendation API at `POST /api/v1/recommendations/generate`. The response MUST include 11 required fields: status, patient_id, recommendation, confidence, evidence_ranking, evidence_attribution, recommendation_trace, audit_reference, explanation, generated_at, trace_id. There are NO accept/override endpoints and NO costTier/monitoringPlan fields. Use the provided files as the single source of truth."

---

## BACKEND TRUTH AUDIT COMPLETE

**Audit Completion Status**: ✅ COMPLETE

**Findings Summary**:
- ✅ 1 canonical recommendation route: `POST /api/v1/recommendations/generate`
- ✅ 11 required response fields with exact types documented
- ✅ Complete explainability structure: evidence ranking, trace, attribution
- ✅ Full audit trail with version metadata
- ✅ 16 automated tests validating the contract
- ✅ SHAP/feature attribution computed internally, optionally returned
- ❌ No accept/override endpoints implemented
- ❌ No costTier, monitoringPlan, or adjustment_notes fields
- ❌ No plugin metadata in recommendation response

**Authoritative Files for Implementation**:
1. [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py)
2. [apps/api/app/clinical_decision/contracts.py](../../apps/api/app/clinical_decision/contracts.py)
3. [apps/api/app/clinical_decision/explainability_enhancements.py](../../apps/api/app/clinical_decision/explainability_enhancements.py)
4. [apps/api/app/clinical_decision/orchestrator.py](../../apps/api/app/clinical_decision/orchestrator.py)
5. [apps/api/tests/test_phase6_api_integration.py](../../apps/api/tests/test_phase6_api_integration.py)

**Recommendation for Gemini AI Studio**:
Build the Phase 8 frontend strictly against the canonical contract defined in [apps/api/app/api/v1/recommendations.py](../../apps/api/app/api/v1/recommendations.py). Do not assume fields exist beyond what is documented in the ExplainabilityResponseContract model. All 11 required fields will be present in every response.

---

**End of Backend Truth Audit**
