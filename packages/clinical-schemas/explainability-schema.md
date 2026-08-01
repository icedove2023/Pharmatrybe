# Explainability Schema
**PharmaTrybe – Shared Clinical Schema**

Version: 1.0  
Status: Frozen (Phase 2 – Step 3B)

---

# Purpose

The Explainability Schema defines how PharmaTrybe communicates **why** a recommendation was made.

It converts technical outputs from the AI models and the Clinical Decision Engine into transparent, clinician-friendly explanations.

The Explainability Engine never changes recommendations.

It only explains them.

---

# Produced By

Explainability Engine

---

# Consumed By

- Clinician Dashboard
- Recommendation Screen
- Audit Module
- Research Module
- PDF Export
- API Clients

---

# Explainability Philosophy

Every recommendation must answer five questions:

1. Why was this antibiotic recommended?
2. Why were other antibiotics rejected?
3. Which evidence influenced the recommendation?
4. How confident is the prediction?
5. What should the clinician pay attention to?

No recommendation may be displayed without an accompanying explanation.

---

# Explainability Object

| Field | Type | Required | Description |
|--------|------|----------|-------------|
| explanation_id | UUID | Yes | Explanation identifier |
| request_id | UUID | Yes | Links to Clinical Case |
| recommendation_id | UUID | Yes | Links to Recommendation |
| generated_at | DateTime | Yes | Timestamp |
| explanation_version | String | Yes | Explainability schema version |

---

# Executive Summary

A short, clinician-readable explanation.

| Field | Type |
|--------|------|
| summary | Text |

Example

```
The recommended antibiotic is supported by WHO guidance and has a high predicted likelihood of susceptibility while preserving antimicrobial stewardship.
```

---

# Prediction Evidence

Explains what the AI models predicted.

## SOAR Evidence

| Field | Description |
|--------|-------------|
| predicted_pathogen |
| susceptibility_probability |
| confidence |
| respiratory_risk |

Example

```
SOAR predicts:

Organism:
Streptococcus pneumoniae

Predicted susceptibility:
94%

Confidence:
High
```

---

## ARMD Evidence

Only available when ARMD is used.

| Field | Description |
|--------|-------------|
| previous_antibiotic_exposure |
| previous_resistance |
| ICU_history |
| previous_organism |
| resistance_probability |
| confidence |

Example

```
Previous carbapenem exposure increases resistance risk.

Predicted resistance:
68%
```

---

# WHO Evidence

Shows why WHO supports the recommendation.

| Field | Description |
|--------|-------------|
| guideline |
| aware_group |
| recommendation_strength |
| stewardship_message |

Example

```
WHO recommends:

Access antibiotic

Strong recommendation

Five-day treatment course
```

---

# Decision Trace

Explains how the Decision Engine combined evidence.

Decision Flow

```
Clinical Case

↓

SOAR Prediction

↓

ARMD Prediction

↓

WHO Guidance

↓

Safety Rules

↓

Stewardship Rules

↓

Final Recommendation
```

---

# Accepted Factors

Positive contributors to the recommendation.

Example

```
accepted_factors

• Predicted susceptible

• WHO first-line therapy

• No allergy

• Normal renal function

• Community-acquired infection
```

---

# Rejected Factors

Factors that reduced confidence or excluded drugs.

Example

```
rejected_factors

• Previous fluoroquinolone exposure

• ICU admission

• Previous MDR organism

• High resistance probability
```

---

# Drug Acceptance Explanation

Explains each recommended antibiotic.

Structure

| Field | Description |
|--------|-------------|
| drug |
| accepted |
| explanation |

Example

```
Amoxicillin

Accepted

Reason

Predicted susceptible.

WHO Access antibiotic.

No contraindications identified.
```

---

# Drug Rejection Explanation

Documents why drugs were excluded.

Example

```
Meropenem

Rejected

Reason

Reserve antibiotic.

No indication for escalation.
```

---

```
Ciprofloxacin

Rejected

Reason

Predicted resistance probability 82%.
```

---

# Clinical Risk Factors

Lists patient-specific contributors.

Possible entries

- Age
- Renal impairment
- ICU admission
- Previous organism
- Previous resistance
- Allergy
- Nursing home residence
- Recent antibiotics
- Immunocompromised status

---

# Stewardship Explanation

Explains stewardship decisions.

Example

```
Access antibiotic preserved.

No escalation to Watch group required.

Reserve antibiotics avoided.
```

---

# Confidence Assessment

| Field | Type |
|--------|------|
| confidence_level |
| confidence_score |
| confidence_reason |

Example

```
Confidence

High

Reason

WHO recommendation aligns with both SOAR prediction and available patient history.
```

---

# Limitations

Every explanation must disclose important limitations.

Possible entries

```
Culture results pending.

ARMD unavailable.

Incomplete laboratory information.

Previous antibiotic history unavailable.

Recommendation based on available evidence only.
```

---

# Evidence Sources

Every explanation must reference its evidence.

Possible sources

- WHO AWaRe Guideline
- WHO Essential Medicines List
- SOAR Model
- ARMD Model
- Clinical Decision Engine
- Local Stewardship Policy

---

# Audit Metadata

| Field | Purpose |
|--------|----------|
| explainability_version | Version |
| decision_engine_version | Version |
| who_version | Version |
| soar_model_version | Version |
| armd_model_version | Version |
| generated_by | Explainability Engine |

---

# Explainability Principles

The Explainability Engine:

✔ Never changes recommendations

✔ Never invents evidence

✔ Never hides uncertainty

✔ Always references evidence sources

✔ Always explains rejected options

✔ Always discloses limitations

✔ Always records confidence

✔ Always preserves the complete audit trail

---

# Relationship to Other Schemas

Clinical Case

↓

SOAR Schema

↓

ARMD Schema

↓

WHO Schema

↓

Recommendation Schema

↓

Explainability Schema

The Explainability Schema is the final clinician-facing layer of PharmaTrybe.

Its purpose is to ensure every recommendation is transparent, evidence-based, auditable, and clinically defensible.