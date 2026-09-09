# PharmaTrybe Platform Architecture Baseline v1.0

**Status:** Authoritative Platform Architecture

**Scope:** Complete implementation as of Stage 4 completion

**Last Updated:** December 2026

**Document Purpose:** This document is the single authoritative description of the PharmaTrybe platform architecture as implemented. It serves as the baseline for all future development decisions and architectural change justifications.

---

## Table of Contents

1. [Platform Overview](#platform-overview)
2. [Core Design Principles](#core-design-principles)
3. [High-Level Architecture](#high-level-architecture)
4. [Layered Architecture](#layered-architecture)
5. [Plugin Architecture](#plugin-architecture)
6. [Workflow Orchestration](#workflow-orchestration)
7. [Clinical Intelligence Layer](#clinical-intelligence-layer)
8. [Decision Flow](#decision-flow)
9. [Explainability and Audit](#explainability-and-audit)
10. [Plugin Communication Model](#plugin-communication-model)
11. [Dependency Architecture](#dependency-architecture)
12. [Extension Points](#extension-points)
13. [Architectural Constraints](#architectural-constraints)
14. [Production Readiness](#production-readiness)

---

## Platform Overview

**PharmaTrybe** is an Explainable Artificial Intelligence Clinical Decision Support System (CDSS) for antimicrobial stewardship.

### Purpose

PharmaTrybe supports clinicians in antimicrobial prescribing by integrating:

- Predictive machine learning models (SOAR/ARMD)
- Evidence-based clinical knowledge (WHO, NICE, IDSA)
- Patient-specific clinical rules
- Hospital stewardship policies
- Explainable reasoning

### Fundamental Non-Negotiable Properties

1. **Evidence Precedes AI** — Guidelines and clinical knowledge always have higher authority than predictive models.
2. **AI Supports Clinicians** — The system never prescribes autonomously; clinicians retain decision authority.
3. **Every Recommendation is Explainable** — Black-box outputs are architecturally unacceptable.
4. **Knowledge and Prediction Are Independent** — Clinical knowledge is architecturally separate from predictive models.
5. **Every Component is Independently Deployable** — Individual services can be upgraded, replaced, or removed without redesigning the platform.

### Key Roles

| Role | Responsibility | Authority |
|------|-----------------|-----------|
| **Clinician** | Reviews PharmaTrybe recommendations and makes final prescribing decision | Final clinical authority |
| **CDSS** | Synthesizes evidence and generates recommendations | Supporting, not deciding |
| **Prediction Plugins** | Provide machine learning inference | Evidence contribution only |
| **Knowledge Plugins** | Provide structured clinical evidence | Evidence contribution only |
| **Clinical Rules Engine** | Evaluate safety constraints (allergies, renal, pregnancy, etc.) | Rule-based evidence contribution |
| **Decision Fusion Engine** | Rank and fuse all evidence into a unified recommendation | Deterministic synthesis only |
| **Explainability Engine** | Explain every recommendation with auditable reasoning | Transparency and audit |

---

## Core Design Principles

### Principle 1: Evidence-First Architecture

All recommendations must be supported by traceable evidence.

- **WHO Guidelines** are the authoritative source for clinical knowledge.
- **Prediction Plugin Outputs** contribute probabilistic evidence only.
- **Clinical Rules** evaluate patient-specific safety constraints.
- **Knowledge Plugins** provide domain-specific structured evidence.
- **No invented recommendations** — all candidates originate from prediction plugins.

### Principle 2: Strict Separation of Concerns

Each component has a precisely defined boundary and no authority beyond it:

| Component | Authority | Boundary |
|-----------|-----------|----------|
| **Prediction Plugins** | Generate probability predictions | Do not synthesize recommendations |
| **Clinical Rules Engine** | Evaluate safety rules against candidates | Do not invent candidates |
| **Decision Fusion Engine** | Rank fused evidence | Do not perform prediction or invent rules |
| **Explainability Engine** | Explain and audit the entire flow | Does not modify recommendations |
| **Workflow Manager** | Select and orchestrate plugins | Does not perform clinical reasoning |

### Principle 3: Candidate Antibiotic Generation

**Critical Boundary Rule:** Antibiotic candidates originate **exclusively** from Prediction Plugin probability outputs.

- The Clinical Intelligence Pipeline reads prediction plugin `probabilities` dictionaries only.
- No internal or default candidate generation occurs at any other layer.
- All antibiotic candidates must trace back to a named Prediction Plugin.

### Principle 4: Deterministic Clinical Synthesis

The Clinical Intelligence Pipeline and Decision Fusion Engine are **not machine learning models**.

- All clinical reasoning is rule-based and deterministic.
- Every recommendation path is auditable and reproducible.
- No probabilistic thresholds or stochastic components.

### Principle 5: Modular Plugin Integration

Every external capability is integrated through the plugin system.

- Prediction models (SOAR, ARMD, future ML models)
- Clinical knowledge (WHO, NICE, hospital guidelines)
- Clinical scoring systems (NEWS2, SOFA, etc.)
- Hospital-specific systems (EHR integration, billing, referral)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PharmaTrybe Platform                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     FastAPI Backend                      │  │
│  │                                                          │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │            API Router & Endpoints                │  │  │
│  │  │  - POST /recommendation (generate)               │  │  │
│  │  │  - GET /explanation/{id} (retrieve)              │  │  │
│  │  │  - GET /audit/{id} (retrieve trail)              │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │                          ↓                              │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │    Clinical Intelligence Pipeline (Orchestrator)│  │  │
│  │  │  1. Invoke Workflow Manager                      │  │  │
│  │  │  2. Extract prediction-derived candidates       │  │  │
│  │  │  3. Evaluate clinical rules                      │  │  │
│  │  │  4. Fuse evidence → recommendation               │  │  │
│  │  │  5. Generate explanation and audit trail         │  │  │
│  │  │  6. Return formatted response                    │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │                 ↙                    ↘                  │  │
│  │  ┌──────────────────────┐    ┌─────────────────────┐  │  │
│  │  │  Workflow Manager    │    │ Clinical Decision   │  │  │
│  │  │ (Plugin Orchestrator)│    │     Engines         │  │  │
│  │  ├──────────────────────┤    ├─────────────────────┤  │  │
│  │  │ • Route plugins      │    │ • Rules Engine      │  │  │
│  │  │ • Execute in order   │    │ • Decision Fusion   │  │  │
│  │  │ • Build context      │    │ • Explainability    │  │  │
│  │  └──────────────────────┘    └─────────────────────┘  │  │
│  │          ↓                                             │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │           Plugin Manager & Registry             │  │  │
│  │  │                                                 │  │  │
│  │  │  ┌─────────────────┐ ┌────────────────────┐   │  │  │
│  │  │  │  Prediction     │ │  Knowledge         │   │  │  │
│  │  │  │  Plugins        │ │  Plugins           │   │  │  │
│  │  │  │                 │ │                    │   │  │  │
│  │  │  │ • SOAR/GSK      │ │ • WHO AWaRe        │   │  │  │
│  │  │  │ • ARMD          │ │ • NICE Guidelines  │   │  │  │
│  │  │  │ • Custom Models │ │ • Hospital Policy  │   │  │  │
│  │  │  └─────────────────┘ └────────────────────┘   │  │  │
│  │  │                                                 │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Data Layer                         │  │
│  │  • Supabase (PostgreSQL)                            │  │
│  │  • Audit Logs                                       │  │
│  │  • Clinical Metadata                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
                   ┌─────────────────────┐
                   │  Next.js Frontend   │
                   │  (Clinician UI)     │
                   └─────────────────────┘
```

---

## Layered Architecture

### Layer 1: API Layer (FastAPI)

**Responsibility:** HTTP request routing and response formatting

**Components:**
- Request validation via Pydantic v2
- Exception handling and standardized error responses
- Request context management (user, audit trail)
- Response envelope formatting

**Key Files:**
- `apps/api/app/main.py` — FastAPI application bootstrap
- `apps/api/app/api/routes/clinical_decision.py` — Recommendation endpoints
- `apps/api/app/core/exceptions.py` — Exception handling
- `apps/api/app/models/` — Pydantic request/response schemas

### Layer 2: Clinical Intelligence Orchestration

**Responsibility:** Coordinate the clinical reasoning flow end-to-end

**Components:**
- `ClinicalIntelligencePipeline` — Main orchestrator
- `WorkflowManager` — Plugin selection and execution
- `PluginRoutingPolicy` — Routing rules (no clinical logic)

**Flow:**
1. Receive `ClinicalDecisionRequest`
2. Route to selected plugins via `WorkflowManager`
3. Extract candidate antibiotics from prediction plugin outputs
4. Evaluate clinical rules
5. Fuse evidence via `DecisionFusionEngine`
6. Generate explanation and audit trail
7. Format and return response

**Key Files:**
- `apps/api/app/clinical_intelligence/pipeline.py`
- `apps/api/app/plugins/manager/workflow_manager.py`
- `apps/api/app/plugins/manager/plugin_routing_policy.py`

### Layer 3: Clinical Decision Engines

**Responsibility:** Evaluate rules, fuse evidence, explain recommendations

**Sub-Components:**

| Engine | Responsibility |
|--------|-----------------|
| **Clinical Rules Engine** | Evaluate allergies, renal, pregnancy, drug interactions |
| **Decision Fusion Engine** | Rank and fuse all evidence; generate final recommendation |
| **Explainability Engine** | Build explanations and audit trails |

**Key Files:**
- `apps/api/app/clinical_decision/rules/__init__.py`
- `apps/api/app/clinical_decision/decision_fusion.py`
- `apps/api/app/clinical_decision/explainability.py`

### Layer 4: Plugin System

**Responsibility:** Define contracts and manage plugin lifecycle

**Components:**
- `BasePlugin` — Abstract base interface
- `PredictionPlugin` — Abstract prediction contract
- `KnowledgePlugin` — Abstract knowledge contract
- `PluginRegistry` — In-memory plugin catalog
- `PluginManager` — Discovery, loading, health monitoring

**Key Files:**
- `apps/api/app/plugins/base/plugin.py`
- `apps/api/app/plugins/base/prediction_plugin.py`
- `apps/api/app/plugins/base/knowledge_plugin.py`
- `apps/api/app/plugins/manager/plugin_registry.py`
- `apps/api/app/plugins/manager/plugin_manager.py`

### Layer 5: Data Layer (Supabase)

**Responsibility:** Persistent storage, audit logs, clinical metadata

**Schema Domains:**
- `diagnostics` — Clinical diagnoses
- `diseases` — Disease definitions
- `drugs` — Medication database
- `evidence` — Clinical evidence references
- `monitoring` — Patient monitoring data
- `pathogens` — Microorganism definitions
- `recommendations` — Historical recommendations
- `stewardship` — Stewardship policies
- `metadata` — System configuration

---

## Plugin Architecture

### Plugin Types and Contracts

#### Prediction Plugins

**Contract:** `PredictionPlugin`

**Properties:**
- Input: Clinical payload (patient data, context)
- Output: Structured `PredictionResult` with `probabilities` dictionary
- Deployment: Artifact-based (local model) or API-based (external service)
- Cardinality: Multiple prediction plugins can run simultaneously

**Output Contract:**

```python
@dataclass(frozen=True)
class PredictionResult:
    predicted_class: str                    # Top prediction
    probabilities: Dict[str, float]         # Antibiotic → probability
    confidence: float                       # Overall confidence
    model_name: str                         # Model identifier
    model_version: str                      # Version info
    execution_time_ms: float                # Performance metric
    metadata: Optional[Dict[str, Any]]      # Additional context
    raw_output: Optional[Dict[str, Any]]    # Raw model output
```

**Critical Responsibility:** Prediction plugins are the **only** source of antibiotic candidates. The probability dictionary is read to extract candidate antibiotics.

**Examples:**
- SOAR/GSK (respiratory pathogen prediction)
- ARMD (hospital antimicrobial resistance prediction)
- Future domain-specific models

#### Knowledge Plugins

**Contract:** `KnowledgePlugin`

**Properties:**
- Input: Structured query or text search
- Output: Structured clinical evidence
- Cardinality: Multiple knowledge plugins can run simultaneously

**Output Contract:**

```python
List[Dict[str, Any]]  # Search results with:
# - guideline_id
# - guideline_name
# - category
# - evidence_level
# - drug_name
# - recommendations
# - contraindications
# - metadata
```

**Responsibility:** Knowledge plugins provide evidence, not recommendations.

**Examples:**
- WHO AWaRe classification
- NICE guidelines
- IDSA recommendations
- Hospital stewardship policies
- Local treatment protocols

#### Other Plugin Types (Future/Extensible)

- **Risk Plugins** — Clinical risk scoring (NEWS2, SOFA)
- **Rules Plugins** — Configurable clinical rules
- **Reporting Plugins** — Output generation (PDF, HL7)
- **Integration Plugins** — External system connectivity (EHR, LIS)

### Plugin Lifecycle

```
Discovery
   ↓
Load & Validate
   ↓
Initialize
   ↓
Register (PluginRegistry)
   ↓
Ready for Execution
   ↓
Shutdown
```

**Key Files:**
- `apps/api/app/plugins/discovery/plugin_loader.py`
- `apps/api/app/plugins/discovery/plugin_validator.py`

---

## Workflow Orchestration

### Workflow Manager

**Responsibility:** Thin orchestration layer for plugin execution

**Properties:**
- Does NOT perform clinical reasoning
- Does NOT select plugins based on clinical criteria
- Routes plugins according to `PluginRoutingPolicy` only
- Collects plugin outputs into `ClinicalDecisionContext`

### Plugin Routing Policy

**Responsibility:** Determine which plugins are active for a request

**Execution Modes:**

| Mode | Behavior |
|------|----------|
| `AUTO` / `AUTOMATIC` | Infer domain from request; select relevant plugins |
| `PREDICTION_ONLY` | Run prediction plugins only |
| `KNOWLEDGE_ONLY` | Run knowledge plugins only |
| `HYBRID` | Run both prediction and knowledge plugins |
| `USER_SELECTED` | Run explicitly named plugins |
| `WORKFLOW_SELECTED` | Run plugins by type from request |

**Routing Logic:**
1. Check execution mode
2. Filter registry by mode
3. Apply domain-based filtering if `AUTO`
4. Return selected plugins

**Auditable Properties:**
- No clinical criteria used in routing
- Request payload and context only
- Policy is deterministic and reproducible

### ClinicalDecisionContext

**Responsibility:** Shared data structure passed from orchestration to clinical engines

**Structure:**

```python
@dataclass
class ClinicalDecisionContext:
    patient_id: str                              # Patient ID
    prediction_outputs: List[Dict[str, Any]]     # Prediction plugin results
    knowledge_outputs: List[Dict[str, Any]]      # Knowledge plugin results
    plugin_metadata: List[Dict[str, Any]]        # Plugin metadata
    execution_metadata: Dict[str, Any]           # Execution context
```

---

## Clinical Intelligence Layer

### Clinical Intelligence Pipeline

**Responsibility:** Pure orchestration and synthesis of clinical reasoning

**Guarantees:**
- No internal candidate generation
- Candidates extracted only from prediction plugin outputs
- All antibiotic names trace back to a prediction plugin
- Deterministic and fully auditable

**Process Flow:**

```
1. Receive ClinicalDecisionRequest
   ↓
2. Execute Workflow Manager
   → Get ClinicalDecisionContext
   ↓
3. Extract Candidates
   → Read prediction_outputs[].value.probabilities
   → Build candidate list
   ↓
4. Evaluate Clinical Rules
   → Run allergies rule
   → Run renal impairment rule
   → Run pregnancy rule
   → Run drug interaction rules
   ↓
5. Fuse Evidence
   → Extract prediction probabilities
   → Identify contraindications
   → Retrieve guideline evidence
   → Rank antibiotics by evidence
   ↓
6. Generate Recommendation
   → Primary recommendation (top-ranked)
   → Alternative recommendations (ranked)
   → Clinical rationale
   → Warnings and contraindications
   ↓
7. Generate Explanation
   → Rule explanations
   → Guideline explanations
   → Stewardship explanations
   → Evidence drivers (ranked by importance)
   ↓
8. Generate Audit Trail
   → Timestamp
   → Plugin versions
   → Model versions
   → Trace ID
   ↓
9. Format Response
   → Standard envelope
   → Include recommendation, explanation, audit trail
   → Return to API layer
```

**Output Contract:**

```python
Dict[str, Any] = {
    "status": "success" | "error",
    "patient_id": str,
    "recommendation": {
        "primary_recommendation": {
            "antibiotic_name": str,
            "confidence": str,
            "evidence": [...]
        },
        "alternative_recommendations": [...],
        "clinical_rationale": str,
        "warnings": [...]
    },
    "explanation": {
        "evidence_drivers": [...],
        "rule_explanations": [...],
        "guideline_explanations": [...],
        "stewardship_explanations": [...]
    },
    "audit_trail": {
        "timestamp": str,
        "trace_id": str,
        "plugin_versions": {...},
        "model_versions": {...}
    }
}
```

### Clinical Rules Engine

**Responsibility:** Evaluate clinical safety rules against candidates and patient data

**Rules:**

| Rule | Trigger | Output |
|------|---------|--------|
| **Allergy** | Known drug allergy in patient record | CRITICAL severity; affected drugs |
| **Renal Impairment** | eGFR < 60 mL/min/1.73m² | HIGH/MEDIUM/LOW; adjustment needed |
| **Pregnancy** | Patient is pregnant | HIGH severity; category contraindications |
| **Lactation** | Patient is lactating | MEDIUM severity; drug constraints |
| **Drug Interaction** | Drug-drug interaction detected | MEDIUM severity; affected pairs |

**Rule Execution:**
- Independent evaluation (no rule depends on other rules)
- Deterministic and reproducible
- Triggered rules generate evidence for decision fusion

**Key Files:**
- `apps/api/app/clinical_decision/rules/__init__.py`
- `apps/api/app/clinical_decision/rules/allergy_rule.py`
- `apps/api/app/clinical_decision/rules/renal_rule.py`
- `apps/api/app/clinical_decision/rules/pregnancy_rule.py`

### Decision Fusion Engine

**Responsibility:** Rank and fuse all evidence into a final recommendation

**Process:**

1. **Identify Contraindications** — Antibiotics ruled out by critical rules
2. **Retrieve Guideline Evidence** — WHO, NICE, IDSA references
3. **Rank Antibiotics** — Sort by:
   - Prediction probability (primary)
   - Guideline support (secondary)
   - Rule status (constraints)
   - Stewardship alignment (tertiary)
4. **Select Primary** — Top-ranked candidate
5. **Select Alternatives** — Next 2-3 ranked candidates
6. **Generate Rationale** — Explain why this recommendation

**Ranking Algorithm:**

- Contraindicated antibiotics are excluded
- Remaining sorted by `prediction probability × guideline_weight`
- Stewardship penalties applied
- Final ranking auditable and reproducible

**Output:** `RecommendationResult` with primary, alternatives, rationale

### Explainability Engine

**Responsibility:** Generate unified explanations and audit trails

**Explanation Components:**

| Component | Source | Purpose |
|-----------|--------|---------|
| **Rule Explanations** | Clinical Rules | Why safety rules triggered/passed |
| **Guideline Explanations** | Knowledge Plugins | Relevant evidence and references |
| **Stewardship Explanations** | Stewardship Engine | Antimicrobial stewardship context |
| **Evidence Drivers** | All sources | Ranked evidence by importance |
| **Clinical Narrative** | All sources | Human-readable summary |

**Audit Trail Components:**

- Recommendation ID (UUID)
- Timestamp (ISO 8601)
- Patient ID
- Prediction plugin version
- Model versions (per model)
- Rule engine version
- Clinical decision engine version
- Trace ID (distributed tracing)

**Guarantees:**
- Every recommendation includes audit trail
- Every rule result is traceable
- Every antibiotic candidate is traceable to a plugin
- Reproducible: given same inputs, same explanation

---

## Decision Flow

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: ClinicalDecisionRequest                              │
│ (patient_id, payload, execution_mode, plugin_selections)    │
└──────────────────────────┬──────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────────┐
        │   PluginRoutingPolicy.route()        │
        │   (Select plugins for execution)     │
        └──────────────────┬────────────────────┘
                          ↓
    ┌───────────────────────────────────────────────┐
    │   WorkflowManager.execute()                   │
    │   - Execute selected plugins in order         │
    │   - Collect results in PluginExecutionResult  │
    │   - Build ClinicalDecisionContext              │
    └──────────────────┬────────────────────────────┘
                      ↓
    ┌────────────────────────────────────────────────┐
    │ ClinicalIntelligencePipeline.process()         │
    │                                                │
    │  1. Extract candidate antibiotics              │
    │     FROM prediction plugin probabilities       │
    │     ONLY (NO internal generation)              │
    │     → List[str]: antibiotic names              │
    │                                                │
    │  2. Evaluate clinical rules                    │
    │     → rules_engine.evaluate_all()              │
    │     → List[ClinicalRuleResult]                 │
    │                                                │
    │  3. Fuse evidence → Recommendation             │
    │     → decision_fusion_engine.fuse_decision()   │
    │     → RecommendationResult:                    │
    │        - primary_recommendation                │
    │        - alternative_recommendations           │
    │        - warnings                              │
    │                                                │
    │  4. Generate explanation                       │
    │     → explainability_engine.generate_explain() │
    │     → RecommendationExplanation:               │
    │        - rule_explanations                     │
    │        - guideline_explanations                │
    │        - stewardship_explanations              │
    │        - evidence_drivers (ranked)             │
    │                                                │
    │  5. Generate audit trail                       │
    │     → explainability_engine.generate_audit()   │
    │     → AuditTrail:                              │
    │        - timestamp, trace_id, versions         │
    │                                                │
    │  6. Format response                            │
    │     → response_formatter.format()              │
    │     → StandardResponseEnvelope                 │
    │                                                │
    └──────────────────┬─────────────────────────────┘
                      ↓
    ┌────────────────────────────────────────────────┐
    │ OUTPUT: ClinicalDecisionResponse                │
    │ {                                              │
    │   "status": "success",                         │
    │   "patient_id": "...",                         │
    │   "recommendation": {...},                     │
    │   "explanation": {...},                        │
    │   "audit_trail": {...}                         │
    │ }                                              │
    └────────────────────────────────────────────────┘
```

---

## Explainability and Audit

### Explainability Principles

1. **End-to-End Tracing** — Every recommendation traces back to evidence sources
2. **Evidence Ranking** — All evidence is ranked by relevance/importance
3. **Rule Transparency** — Clinical rules are explicit and auditable
4. **Prediction Transparency** — Prediction plugin outputs are included (SHAP, etc.)
5. **Clinician Agency** — Explanations support clinical review and override

### Explanation Structure

```
RecommendationExplanation
├── recommendation_id (UUID)
├── patient_id
├── primary_antibiotic
├── prediction_explanation (SHAP, etc.)
├── rule_explanations (List[str])
│   └── Allergy: triggered, affected drugs
│   └── Renal: eGFR-based adjustment needed
│   └── Pregnancy: contraindicated
├── guideline_explanations (List[str])
│   └── WHO AWaRe recommendation
│   └── NICE guidance
├── stewardship_explanations (List[str])
│   └── First-line vs. second-line
│   └── Resistance risk
│   └── Escalation rationale
├── evidence_drivers (List[ExplainabilityDriver])
│   ├── weight (importance)
│   ├── source (prediction/rule/guideline)
│   ├── evidence (specific finding)
│   └── [sorted by weight descending]
└── clinical_narrative (str)
    └── Human-readable summary
```

### Audit Trail Structure

```
AuditTrail
├── recommendation_id (UUID)
├── patient_id
├── timestamp (ISO 8601)
├── prediction_plugin_version
├── model_versions (Dict)
│   └── soar: "v1.0.0"
│   └── armd: "v1.0.0"
├── rule_versions
├── guideline_engine_version
├── stewardship_engine_version
├── cdss_version
├── algorithm_version
├── trace_id (distributed tracing)
└── metadata (Dict)
    ├── primary_recommendation
    ├── confidence
    ├── alternatives_count
    ├── rules_triggered
    └── warnings_count
```

---

## Plugin Communication Model

### Prediction Plugin Execution

```
WorkflowManager._execute_plugin(PredictionPlugin, ClinicalDecisionRequest)
│
├─ Check: isinstance(plugin, PredictionPlugin)
├─ Create: PredictionRequest(payload=request.payload, context=request.context)
├─ Call: plugin.supports(prediction_request)
│        → bool (does plugin handle this request?)
├─ Call: plugin.predict(prediction_request)
│        → PredictionResult
│           {
│             predicted_class: str,
│             probabilities: {antibiotic: float},
│             confidence: float,
│             model_name: str,
│             model_version: str,
│             execution_time_ms: float,
│             metadata: {...},
│             raw_output: {...}
│           }
├─ Build: PluginExecutionResult
│   {
│     plugin_id: str,
│     plugin_name: str,
│     plugin_type: PREDICTION,
│     success: bool,
│     result: PredictionResult,
│     execution_time_ms: float,
│     evidence: {prediction: result.__dict__}
│   }
└─ Return to Workflow Manager
```

### Knowledge Plugin Execution

```
WorkflowManager._execute_plugin(KnowledgePlugin, ClinicalDecisionRequest)
│
├─ Check: isinstance(plugin, KnowledgePlugin)
├─ Extract: query = request.payload.get("query")
├─ Extract: filters = request.context
├─ Call: plugin.search(query, filters)
│        → List[Dict[str, Any]]
│           [
│             {
│               guideline_id: str,
│               drug_name: str,
│               recommendation: str,
│               evidence_level: str,
│               contraindications: [...],
│               metadata: {...}
│             },
│             ...
│           ]
├─ Build: PluginExecutionResult
│   {
│     plugin_id: str,
│     plugin_name: str,
│     plugin_type: KNOWLEDGE,
│     success: bool,
│     result: List[Dict],
│     execution_time_ms: float,
│     evidence: {knowledge: result}
│   }
└─ Return to Workflow Manager
```

### Data Flow Through Clinical Intelligence

```
ClinicalDecisionContext (from WorkflowManager)
├── prediction_outputs: [
│   {
│     plugin_id: "soar",
│     plugin_name: "SOAR/GSK",
│     value: PredictionResult {
│       probabilities: {
│         "amoxicillin": 0.85,
│         "cephalexin": 0.75,
│         "doxycycline": 0.65
│       },
│       ...
│     }
│   },
│   {
│     plugin_id: "armd",
│     plugin_name: "ARMD",
│     value: PredictionResult {
│       probabilities: {
│         "fluoroquinolone": 0.60,
│         "cephalosporin": 0.55
│       },
│       ...
│     }
│   }
│ ]
│
├── knowledge_outputs: [
│   {
│     plugin_id: "who_aware",
│     plugin_name: "WHO AWaRe",
│     value: [
│       {
│         drug_name: "amoxicillin",
│         category: "Access",
│         recommendation: "First-line for community RTI"
│       },
│       ...
│     ]
│   }
│ ]
│
├── plugin_metadata: [...]
└── execution_metadata: {...}
      ↓
  ClinicalIntelligencePipeline._extract_candidates_from_predictions()
      ↓
  Iterate prediction_outputs:
    1. coerce_prediction_payload(output["value"])
    2. Extract probabilities dict
    3. Collect antibiotic names → List[str]
      ↓
  candidates = ["amoxicillin", "cephalexin", "doxycycline", "fluoroquinolone", "cephalosporin"]
```

---

## Dependency Architecture

### Runtime Dependencies

```
API Endpoints
    ↓
ClinicalIntelligencePipeline
    ├── WorkflowManager
    │   ├── PluginRegistry
    │   ├── PluginRoutingPolicy
    │   └── BasePlugin (selected)
    │       ├── PredictionPlugin
    │       └── KnowledgePlugin
    ├── ClinicalRulesEngine
    │   ├── AllergyRule
    │   ├── RenalImpairmentRule
    │   ├── PregnancyRule
    │   ├── LactationRule
    │   └── DrugInteractionRule
    ├── DecisionFusionEngine
    │   ├── GuidelineEngine
    │   └── StewardshipEngine
    └── ExplainabilityEngine
        ├── ResponseFormatter
        └── AuditTrailBuilder
            ↓
        Supabase (PostgreSQL)
```

### Build and Deployment

```
pyproject.toml (apps/api)
├── Dependencies:
│   ├── fastapi
│   ├── pydantic v2
│   ├── sqlalchemy (future)
│   ├── httpx (plugin APIs)
│   └── uvicorn
├── Test Dependencies:
│   ├── pytest
│   ├── pytest-asyncio
│   └── pytest-cov
```

---

## Extension Points

### Safe Extensions (Plugin-Based)

These extensions do NOT require architectural changes:

1. **New Prediction Models** — Deploy new `PredictionPlugin` implementations
   - Example: UROSEPSIS prediction model
   - Example: Fungal infection prediction
   - No changes to core architecture

2. **New Knowledge Sources** — Deploy new `KnowledgePlugin` implementations
   - Example: Hospital-specific guidelines
   - Example: National stewardship policies
   - No changes to core architecture

3. **New Clinical Rules** — Add rules to `ClinicalRulesEngine`
   - Example: Drug-drug interaction checking
   - Example: Pediatric dosing rules
   - No architectural changes

4. **New Reporting** — Deploy `ReportingPlugin` implementations
   - Example: PDF report generation
   - Example: HL7 message export
   - No architectural changes

### Unsafe Extensions (Require Architectural Review)

These changes require explicit architectural justification:

1. **Modifying plugin selection criteria** — Changes to `PluginRoutingPolicy`
2. **Modifying candidate generation** — Changes to prediction extraction logic
3. **Adding new decision synthesis mechanisms** — Changes to `DecisionFusionEngine`
4. **Modifying clinical rules** — Changes affecting rule evaluation scope
5. **Changing explainability architecture** — Changes to explanation generation

---

## Architectural Constraints

### Immutable Constraints (Non-Negotiable)

| Constraint | Justification | Violation Penalty |
|------------|---------------|--------------------|
| **Candidates from predictions only** | Ensures AI is evidence-based, not invented | Loss of clinical credibility |
| **No prediction in clinical rules** | Rules must be deterministic and clinician-verifiable | Loss of auditability |
| **Clinician retains decision authority** | Regulatory and ethical requirement | System becomes autonomous |
| **Every recommendation explainable** | Clinical safety requirement | Unsafe "black box" system |
| **Knowledge independent of prediction** | Ensures evidence integrity | Bias in recommendation ranking |
| **Plugin system mandatory** | Ensures replaceability and extensibility | System becomes monolithic |

### Architectural Boundaries

| Boundary | Enforcer | Violation Cost |
|----------|----------|-----------------|
| **Plugin → Clinical Logic** | Plugin contracts define output only | Clinical rules become plugin-dependent |
| **Clinical Rules → Prediction** | Rules read candidates, not generate them | Rules become a hidden ML model |
| **Fusion → Invention** | Fusion ranks existing candidates only | New antibiotics appear without justification |
| **Orchestration → Decision** | WorkflowManager routes, doesn't decide | Hidden clinical reasoning in orchestration |
| **Explainability → Modification** | Explanations are read-only views | Audit trails become unreliable |

---

## Production Readiness

### Quality Gates

| Criterion | Status | Evidence |
|-----------|--------|----------|
| **Unit Test Coverage** | ✓ Passing | `apps/api/tests/test_clinical_intelligence_pipeline.py` — 8/8 tests |
| **Integration Testing** | ✓ Passing | End-to-end workflow validation |
| **Clinical Rule Validation** | ✓ Passing | Rule evaluation against test cases |
| **Plugin Contract Compliance** | ✓ Passing | All plugins conform to abstract contracts |
| **Explainability Validation** | ✓ Passing | Explanations traceable to evidence |
| **Audit Trail Completeness** | ✓ Passing | All recommendations auditable |
| **Error Handling** | ✓ Complete | Exception handlers for all layers |
| **Performance Baseline** | ✓ Established | Execution time metrics recorded |
| **Database Schema** | ✓ Stable | Supabase migrations tested |
| **API Documentation** | ✓ Complete | OpenAPI/Swagger generated |

### Deployment Readiness

- **Configuration Management** — Environment-based configuration via `.env`
- **Health Checks** — Endpoints for plugin and system health
- **Logging** — Structured logging with correlation IDs
- **Audit Logging** — All clinical decisions logged to audit table
- **Exception Handling** — Graceful degradation for plugin failures
- **Performance Monitoring** — Execution time metrics per component
- **Scalability** — Stateless API layer, can be horizontally scaled

---

## Architecture Summary

PharmaTrybe is a **modular, plugin-first, evidence-centric Clinical Decision Support System** built on FastAPI with the following characteristics:

### Core Properties

1. **Plugin-First** — All external capabilities are plugins; no monolithic components
2. **Evidence-Based** — All candidates originate from prediction plugins; no invented recommendations
3. **Deterministic** — Clinical reasoning is rule-based, not probabilistic
4. **Explainable** — Every recommendation includes traceable evidence and audit trail
5. **Safe** — Clinicians retain decision authority; system supports, not prescribes
6. **Independently Deployable** — Each service and plugin can be deployed independently
7. **Auditable** — Every decision can be reproduced and explained

### Architectural Guarantees

- ✓ No internal candidate generation
- ✓ No "black box" clinical reasoning
- ✓ No prediction in clinical rules
- ✓ No invented recommendations
- ✓ No autonomous prescribing
- ✓ No hidden clinical logic in orchestration
- ✓ Every antibiotic traces to a prediction plugin
- ✓ Every recommendation is explainable
- ✓ Every clinical decision is auditable

### Version Control

| Component | Version |
|-----------|---------|
| **Platform** | v1.0.0 |
| **API** | v1 (at `/api/v1`) |
| **Clinical Rules Engine** | v0.1.0 |
| **Decision Fusion Engine** | v0.1.0 |
| **Explainability Engine** | v0.1.0 |
| **Plugin System** | v1.0.0 |
| **Prediction Plugin Contract** | v1.0.0 |
| **Knowledge Plugin Contract** | v1.0.0 |

---

## References and Related Documents

### Architecture Documentation
- `docs/architecture/Plugin_Framework.md` — Plugin design philosophy
- `docs/architecture/Plugin_Developer_Guide.md` — Plugin development guide
- `docs/architecture/Data_Flow_and_Orchestration.md` — Detailed data flow

### Implementation Documentation
- `docs/developer/` — Developer setup and contribution guidelines
- `docs/api/` — API endpoint documentation
- `docs/backend/` — Backend service documentation

### Stage Reports
- `STAGE_2B_AUDIT_REPORT.md` — Architectural validation and audit
- `STAGE_3_PHASE_1_REPORT.md` — Plugin framework implementation
- `STAGE_4_PHASE1_CLINICAL_DECISION_REPORT.md` — Clinical decision engine implementation

### Code
- `apps/api/app/` — Complete FastAPI application
- `apps/api/tests/` — Test suite
- `packages/prediction_framework/` — Shared prediction framework

---

## Document Maintenance

This document is the **single authoritative baseline** for the PharmaTrybe platform architecture.

### Updates

Any architectural change must:

1. Update this document first
2. Justify the change against the core principles
3. Identify affected components and dependencies
4. Validate that architectural constraints are preserved
5. Update all related component documentation

### Review Schedule

- **Quarterly** — Review for accuracy and completeness
- **Before Major Releases** — Validate all documented capabilities
- **After Architectural Changes** — Immediately update and validate

---

**End of Document**

*PharmaTrybe Platform Architecture Baseline v1.0*

*This is the authoritative description of the implemented platform as of Stage 4 completion.*
