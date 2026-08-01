# Recommendation Schema
**PharmaTrybe – Shared Clinical Schema**

Version: 1.0  
Status: Frozen (Phase 2 – Step 3B)

---

# Purpose

The Recommendation Schema defines the **final clinical recommendation** returned to the frontend after the Clinical Decision Engine combines:

- SOAR/GSK prediction
- ARMD prediction (when available)
- WHO Knowledge Base
- Clinical safety rules
- Stewardship rules

This schema is the **only object** displayed to clinicians.

Neither SOAR nor ARMD ever returns a recommendation directly.

---

# Produced By

Clinical Decision Engine

---

# Consumed By

- Frontend (Clinician UI)
- Explainability Engine
- Audit Engine
- Reporting Module

---

# Philosophy

The Recommendation Engine does **not invent medicine.**

Instead it integrates:

Clinical Context

↓

WHO Guidance

↓

AI Evidence

↓

Stewardship Rules

↓

Ranked Recommendations

---

# Recommendation Object

| Field | Type | Required | Description |
|---------|------|----------|-------------|
| recommendation_id | UUID | Yes | Recommendation identifier |
| request_id | UUID | Yes | Links to original request |
| generated_at | DateTime | Yes | Timestamp |
| scenario | Enum | Yes | Scenario 1 or Scenario 2 |
| syndrome | String | Yes | CAP, HAP, UTI etc |
| severity | Enum | Yes | Mild / Moderate / Severe |
| status | Enum | Yes | Complete / Partial / Manual Review |
| confidence | Float | Yes | Overall confidence (0–1) |

---

# Ranked Recommendation List

The system returns multiple options.

Never only one antibiotic.

| Field | Type |
|------|------|
| rank | Integer |
| drug_name | String |
| aware_group | Enum |
| recommendation_level | Enum |
| predicted_susceptibility | Float |
| recommendation_reason | Text |
| stewardship_note | Text |

Example

Rank 1

Drug:
Amoxicillin

WHO:
Access

Predicted Susceptibility:
92%

Reason:
Recommended by WHO guideline and predicted susceptible.

---

# Alternative Recommendations

```text
alternatives[]

Contains:

Drug

Reason

Predicted susceptibility

WHO category
```

---

# Rejected Recommendations

These improve transparency.

| Field | Description |
|---------|-------------|
| drug | Drug rejected |
| reason | Why rejected |

Examples

```text
Rejected

Ciprofloxacin

Reason

Predicted resistance 88%
```

---

```text
Rejected

Meropenem

Reason

WHO Reserve antibiotic
Not indicated
```

---

# Decision Pathway

Documents how the recommendation was produced.

```text
decision_pathway

WHO Guideline

↓

SOAR Prediction

↓

ARMD Prediction

↓

Stewardship Rules

↓

Final Recommendation
```

---

# Recommendation Sources

Every recommendation includes evidence.

```text
sources

WHO recommendation

SOAR prediction

ARMD prediction

Clinical rule

Stewardship policy
```

---

# Clinical Warnings

Optional.

```text
warnings[]

Examples

Penicillin allergy

Renal impairment

Recent carbapenem exposure

Previous MDR organism

ICU admission

Pregnancy

Immunocompromised
```

---

# Referral Recommendation

Optional.

```text
referral

Required

Yes / No

Reason

ICU review

Infectious Disease referral

Microbiology consultation
```

---

# Monitoring Advice

Optional.

```text
monitoring

Repeat cultures

Repeat lactate

Monitor creatinine

Review after 48 hours
```

---

# Follow-up Advice

Optional.

```text
follow_up

72-hour antibiotic review

De-escalate when cultures available

Stop antibiotics if infection excluded
```

---

# Audit Metadata

| Field | Purpose |
|---------|----------|
| contract_version | Schema version |
| decision_engine_version | Decision engine version |
| who_version | WHO KB version |
| soar_model_version | SOAR model version |
| armd_model_version | ARMD model version |
| generated_by | PharmaTrybe Decision Engine |

---

# Scenario Behaviour

## Scenario 1 — Resistance Predicted

Decision Engine:

- Uses SOAR prediction
- Uses ARMD resistance prediction
- Uses WHO guideline
- Excludes resistant drugs
- Ranks safest alternatives

Example

```text
Amoxicillin

↓

Predicted Resistant

↓

Remove

↓

Recommend Ceftriaxone
```

---

## Scenario 2 — No Resistance Predicted

Decision Engine:

- Follows WHO guideline
- Preserves Access antibiotics
- Avoids unnecessary escalation
- Promotes stewardship

Example

```text
WHO recommends Access antibiotic

↓

AI predicts susceptible

↓

Recommend Access drug

↓

Do NOT escalate to Watch
```

---

# Recommendation Principles

The Recommendation Engine:

✔ Never overrides WHO without evidence

✔ Never invents antibiotics

✔ Never ignores stewardship

✔ Never ignores AI evidence

✔ Always provides alternatives

✔ Always explains why options were accepted or rejected

✔ Always records the complete decision pathway for audit and explainability

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

The Recommendation Schema is the single clinical output consumed by the PharmaTrybe interface.