# PharmaTrybe — Internal Service Contracts

**Phase 2, Step 3A — Architecture specification only**

This document defines the communication contracts between PharmaTrybe's major services. These contracts remain stable even when underlying models, rulesets, or knowledge bases change. The FastAPI backend orchestrates all inter-service communication; services never call each other directly.

**Governing document:** `PROJECT_CONTEXT.md`

---

## Design Rules

1. **Models never talk directly to each other.** SOAR never calls ARMD. ARMD never calls SOAR. Both only respond to requests from the backend orchestrator.
2. **Clinical evidence before AI.** WHO guideline knowledge and stewardship rules outrank model scores.
3. **Explainability is mandatory.** No recommendation is complete without the Explainability Engine.
4. **One recommender.** Only the Clinical Decision Engine generates clinical antibiotic recommendations.
5. **Knowledge is not ML.** The WHO Knowledge Service contains no machine learning.
6. **Clinician-assisted, not autonomous.** The platform provides evidence-supported options — it does not claim to choose the best antibiotic.

---

## Service Overview

| Service | Role | Predicts? | Recommends? | Explains? |
|---------|------|-----------|-------------|-----------|
| SOAR/GSK Model Service | Respiratory stewardship intelligence | Yes | No | No |
| ARMD Model Service | Hospital resistance prediction | Yes | No | No |
| WHO Knowledge Service | Guideline and AWaRe knowledge | No | No | No |
| Clinical Decision Engine | Evidence-supported recommendation synthesis | No | **Yes** | No |
| Explainability Engine | Clinician-facing transparency | No | No | **Yes** |

---

## 1. SOAR/GSK Model Service

### Purpose

Primary AI service for **respiratory antimicrobial stewardship**. Provides syndrome-specific assessment, respiratory infection signals, clinical risk scoring, and **respiratory resistance prediction**.

SOAR/GSK is responsible for respiratory stewardship intelligence only.

### Responsibilities

- Accept clinical respiratory patient information
- Predict respiratory antimicrobial resistance probability
- Return confidence bands and prediction metadata
- Provide syndrome assessment and clinical risk signals
- Supply feature attribution metadata to support downstream explainability
- Expose model identity and version for audit and reproducibility

### Inputs

- **Clinical Case** (respiratory subset): demographics, presentation/syndrome, vitals, laboratory values, antimicrobial history, allergies, clinical setting
- Request correlation metadata (`request_id`, `contract_version`)

### Outputs

- **SOAR Result**: respiratory resistance probability, confidence band, resistance flag (`none` | `predicted` | `confirmed`)
- Syndrome assessment labels and clinical risk score
- Prediction metadata: model name, version, inference timestamp
- Explainability metadata: top contributing features and attribution method

### Dependencies

- None at runtime
- Does not depend on ARMD, WHO, Decision Engine, or Explainability Engine

### What This Service Never Does

- Choose or rank antibiotics
- Recommend therapy
- Call ARMD or any other service
- Query or interpret WHO guidelines
- Generate final clinical recommendations
- Produce clinician-facing narrative explanations
- Make autonomous prescribing decisions

---

## 2. ARMD Model Service

### Purpose

Secondary AI service for **hospital antimicrobial resistance prediction** using hospital microbiology datasets and associated clinical features.

ARMD predicts resistance probability. It supports Scenario 1 workflows where resistance is known or predicted.

**Current development status:** WP2 Feature Engineering. After WP6 completion, ARMD integrates without architectural redesign.

### Responsibilities

- Accept hospital patient feature vectors
- Predict organism-level and antibiotic-class resistance probabilities
- Return organism resistance profiles with confidence bands
- Supply feature contribution metadata for explainability
- Expose model identity, version, and feature schema version

### Inputs

- **Clinical Case** (hospital subset):
  - Previous antibiotic exposure
  - Previous infecting organisms / culture history
  - ICU exposure and hospital ward
  - Laboratory biomarkers
  - Vital signs
  - Procedures
  - Demographics
  - Previous resistance history
- Request correlation metadata (`request_id`, `contract_version`)
- Optional SOAR resistance flag (supplied by backend for context; ARMD does not call SOAR)

### Outputs

- **ARMD Result**: per-organism resistance profile, per-antibiotic-class resistance probabilities, overall resistance risk
- Confidence bands per prediction
- Prediction metadata: model name, version, feature schema version, inference timestamp
- Explainability metadata: top contributing features and attribution method

### Dependencies

- None at runtime
- Does not depend on SOAR, WHO, Decision Engine, or Explainability Engine

### What This Service Never Does

- Recommend antibiotics or therapy
- Interpret WHO guidance or AWaRe classifications
- Call SOAR or any other service
- Generate clinical recommendations
- Rank or reject antibiotic options
- Produce clinician-facing explanations
- Select final treatment

---

## 3. WHO Knowledge Service

### Purpose

Shared **non-ML knowledge engine** providing WHO AWaRe classification, antimicrobial guidance, stewardship recommendations, and antibiotic metadata. Used by every component that requires evidence-based medical knowledge.

This service contains no machine learning.

### Responsibilities

- Serve antibiotic metadata (name, drug class, spectrum, contraindications)
- Provide AWaRe classification (Access / Watch / Reserve)
- Return guideline-linked recommendations for syndromes and organisms
- Supply stewardship advice and rules applicable to clinical context
- Support queries by infection syndrome, organism, and antibiotic identifier

### Inputs

- **Query context**: infection syndrome, target organism, antibiotic identifier(s), resistance flag, clinical setting
- Request correlation metadata (`request_id`, `contract_version`)

### Outputs

- **WHO Result**: antibiotic metadata bundle, AWaRe classifications, guideline recommendations, stewardship advice, contraindication flags
- Knowledge version identifier for audit traceability

### Dependencies

- Internal WHO knowledge datastore (not exposed to other services)
- Does not depend on SOAR, ARMD, Decision Engine, or Explainability Engine

### What This Service Never Does

- Perform machine learning or statistical prediction
- Predict resistance probability
- Choose or rank antibiotics
- Generate final clinical recommendations
- Modify or override AI model outputs
- Produce narrative clinician explanations (structured knowledge only)
- Call any other service

---

## 4. Clinical Decision Engine

### Purpose

The **brain of PharmaTrybe** — the only service authorized to generate clinical antibiotic recommendations. Combines SOAR/GSK outputs, ARMD predictions (when applicable), WHO knowledge, and full patient context into evidence-supported antimicrobial options.

### Responsibilities

- Receive SOAR Result, optional ARMD Result, WHO Result, and Clinical Case from the backend
- Apply stewardship rules (e.g., prefer WHO Access antibiotics when resistance is not predicted)
- Generate ranked recommended antibiotic options with reasons
- Identify rejected or deprioritized options with explicit rationale
- Attach warnings, stewardship notes, and evidence references
- Record the decision pathway steps for audit and explainability
- Include confidence summary derived from input sources

### Inputs

- **Clinical Case** (full patient context)
- **SOAR Result** (required)
- **ARMD Result** (required when resistance is known or predicted; omitted in Scenario 2)
- **WHO Result** (required)
- Clinical scenario indicator (`no_resistance` | `resistance_predicted` | `resistance_confirmed`)
- Request correlation metadata (`request_id`, `contract_version`)

### Outputs

- **Decision Result**:
  - Ranked recommended antibiotic options
  - Rejected or deprioritized options with reasons
  - Ranking reasons per option
  - Warnings and stewardship notes
  - Evidence references traceable to WHO and prediction inputs
  - Decision pathway steps
  - Confidence summary
  - Clinician-assistance disclaimer

### Dependencies

- Receives all inputs pre-fetched by the backend orchestrator
- Does not call SOAR, ARMD, or WHO directly at runtime (preserves audit boundaries and the "models never talk to each other" rule)

### What This Service Never Does

- Train or run ML models
- Perform resistance prediction (delegated to SOAR and ARMD)
- Host or maintain WHO knowledge (delegated to WHO Knowledge Service)
- Produce clinician-facing narrative explanations (delegated to Explainability Engine)
- Call other services directly
- Claim autonomous antibiotic selection
- Skip evidence traceability on any recommendation

---

## 5. Explainability Engine

### Purpose

Mandatory transparency layer. Transforms technical outputs from all prior services into **clinician-friendly explanations** so every recommendation is transparent, auditable, and understandable.

No recommendation is complete without explainability.

### Responsibilities

- Receive outputs from SOAR, ARMD (if present), WHO, Decision Engine, and Clinical Case
- Explain why resistance was predicted or confirmed
- Explain why specific antibiotics were ranked first or rejected
- Explain WHO AWaRe and guideline reasoning (e.g., why Watch instead of Access)
- Surface risk factors and patient-specific contributing factors
- Present AI confidence levels in accessible language
- Summarize the full decision pathway for the clinician

### Inputs

- **Clinical Case**
- **SOAR Result** (required)
- **ARMD Result** (when present)
- **WHO Result** (required)
- **Decision Result** (required)
- Request correlation metadata (`request_id`, `contract_version`)

### Outputs

- **Explainability Result**:
  - Plain-language summary
  - Structured explanation sections (resistance, ranking, WHO context, risk factors)
  - Evidence citations per section
  - Confidence summary across sources
  - Decision pathway narrative

### Dependencies

- Consumes payloads supplied by the backend; no runtime calls to other services

### What This Service Never Does

- Modify, re-rank, or override recommendations
- Run ML predictions
- Query WHO knowledge independently (receives WHO Result as input)
- Generate new antibiotic options not present in the Decision Result
- Make clinical decisions
- Replace clinician judgement

---

## Communication Matrix

Services communicate **only through the backend orchestrator**. Direct inter-service calls are forbidden.

| Caller → Callee | SOAR | ARMD | WHO | Decision | Explainability |
|-----------------|------|------|-----|----------|----------------|
| Backend | ✓ | ✓ | ✓ | ✓ | ✓ |
| SOAR | — | ✗ | ✗ | ✗ | ✗ |
| ARMD | ✗ | — | ✗ | ✗ | ✗ |
| WHO | ✗ | ✗ | — | ✗ | ✗ |
| Decision | ✗ | ✗ | ✗ | — | ✗ |
| Explainability | ✗ | ✗ | ✗ | ✗ | — |

---

## Clinical Scenarios

### Scenario 1 — Known or predicted resistance

```
Clinical Case → SOAR → ARMD → WHO → Decision Engine → Explainability Engine
```

The Decision Engine surfaces **alternative evidence-supported antibiotics** when resistance is known or predicted.

### Scenario 2 — No predicted resistance

```
Clinical Case → SOAR → WHO → Decision Engine → Explainability Engine
```

ARMD is skipped. WHO Access antibiotics are preferred. The Decision Engine produces a **stewardship-first recommendation**.

---

## Contract Stability

All payloads include:

- `request_id` — correlation ID for audit and traceability
- `contract_version` — semantic version of the contract shape (currently `1.0.0`)

Model versions, ruleset versions, and knowledge base versions are carried inside each result payload independently of `contract_version`. Changing a model does not require a contract version bump unless the payload shape changes.

See [request-response-schemas.md](./request-response-schemas.md) for payload definitions and [system-message-flow.md](./system-message-flow.md) for execution sequences.
