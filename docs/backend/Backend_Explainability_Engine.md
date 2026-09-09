# Backend_Explainability_Engine.md

---

# PharmaTrybe
## Backend Explainability Engine
### Version 1.0

**Project**

**An Explainable Clinical Decision Support System (CDSS) for Personalized Antimicrobial Prescribing and Antimicrobial Stewardship**

---

# Purpose

This document defines the official Explainability Engine for PharmaTrybe.

The Explainability Engine transforms AI outputs, clinical rules, and evidence into transparent, clinician-friendly explanations that justify every recommendation produced by the Clinical Decision Support System (CDSS).

Explainability is a core architectural component—not an optional feature.

---

# Design Philosophy

The Explainability Engine follows one fundamental principle:

> **Every recommendation must be fully explainable, traceable, evidence-supported, and auditable.**

No recommendation should ever appear as a "black box."

---

# Objectives

The Explainability Engine must

- Explain every recommendation
- Cite supporting evidence
- Display confidence
- Show reasoning pathway
- Display applied clinical rules
- Highlight resistance information
- Present alternative treatments
- Support SHAP explanations
- Generate clinician-friendly narratives
- Support patient-friendly summaries

---

# Position in System Architecture

```text
Clinical Case

↓

Knowledge Fusion

↓

Clinical Rules Engine

↓

Decision Engine

↓

Recommendation Ranking

↓

Confidence Estimation

↓

Explainability Engine

↓

API Response
```

The Explainability Engine is the final stage before responses are returned to the API.

---

# Explainability Components

The engine combines information from

- Clinical Case
- Knowledge Fusion Engine
- WHO Knowledge
- SOAR Knowledge
- ARMD Knowledge
- Clinical Rules Engine
- AI Decision Engine
- Confidence Engine
- SHAP Feature Importance
- Audit Logs

---

# Core Responsibilities

The engine answers

- Why was this recommendation selected?
- Which evidence supports it?
- Which knowledge sources contributed?
- Which patient characteristics influenced the decision?
- Which resistance data affected the recommendation?
- Why were alternatives not selected?
- How confident is the system?

---

# Explainability Pipeline

```text
AI Recommendation

↓

Collect Evidence

↓

Collect Rules

↓

Collect Knowledge Sources

↓

Collect SHAP Features

↓

Build Clinical Narrative

↓

Generate Structured Explanation

↓

API Response
```

---

# Explainability Layers

The engine produces explanations at multiple levels.

## Layer 1 — Recommendation Summary

Provides

- Selected antimicrobial
- Clinical indication
- Overall confidence

Example

```text
Recommended Drug

Amoxicillin

Confidence

94%
```

---

## Layer 2 — Evidence Explanation

Displays

- WHO recommendation
- Supporting guideline
- Evidence level
- Page references

Example

```text
WHO Recommendation

First-line therapy

Evidence Level

High

Source

WHO AWaRe Book
```

---

## Layer 3 — Knowledge Source Attribution

Displays every knowledge source involved.

Example

```text
WHO

SOAR

ARMD
```

Each source includes

- Version
- Publication
- Contribution

---

## Layer 4 — Patient Context

Displays patient factors influencing the recommendation.

Examples

Age

Sex

Weight

Pregnancy

Renal impairment

Hepatic impairment

Drug allergies

Severity

Comorbidities

Culture results

---

## Layer 5 — Clinical Rules Applied

Displays rules executed by the Rules Engine.

Example

```text
Renal dose adjustment applied

Penicillin allergy check

Pregnancy safety check

Stewardship restriction

Local formulary check
```

---

## Layer 6 — Resistance Explanation

Displays AMR information used.

Example

```text
SOAR

High susceptibility

Haemophilus influenzae

92%

ARMD

Low regional resistance

Streptococcus pneumoniae

89%
```

---

## Layer 7 — Alternative Therapies

Displays alternative options.

Example

```text
Alternative 1

Amoxicillin-Clavulanate

Reason

Second-line

Alternative 2

Ceftriaxone

Reason

Hospital-level therapy
```

---

## Layer 8 — Confidence Explanation

Displays why confidence received its score.

Example

```text
High WHO agreement

High SOAR agreement

Strong evidence

No contraindications

Complete patient information

Final Confidence

96%
```

---

# Explainability Categories

Every recommendation includes

Clinical reasoning

Evidence

Knowledge sources

Clinical rules

Patient factors

Resistance factors

Confidence

Alternatives

Warnings

Audit reference

---

# Clinical Narrative Generator

The Explainability Engine produces human-readable summaries.

Example

```text
Amoxicillin is recommended as first-line therapy because WHO recommends it for mild community-acquired pneumonia. SOAR data demonstrates excellent susceptibility against Streptococcus pneumoniae and Haemophilus influenzae within respiratory infections. No allergy, renal impairment, or pregnancy-related contraindications were detected. Overall confidence is high.
```

---

# Structured Explainability Object

Every API response includes

```json
{
  "recommendation": {},
  "confidence": {},
  "evidence": {},
  "knowledge_sources": [],
  "clinical_rules": [],
  "patient_factors": [],
  "resistance": {},
  "alternatives": [],
  "warnings": [],
  "shap": {}
}
```

---

# SHAP Integration

Future machine learning models must expose SHAP explanations.

Purpose

Explain feature importance.

Example

```text
Age

+0.18

Renal Function

+0.31

Pregnancy

0

Resistance Profile

+0.47

Severity

+0.22
```

The Explainability Engine displays

- Feature
- Contribution
- Direction
- Relative importance

---

# Global Feature Importance

The engine can also display overall model behavior.

Example

```text
Resistance Profile

42%

Disease Severity

23%

Renal Function

14%

Age

9%

Pregnancy

5%

Comorbidities

7%
```

---

# Local Explanation

Each individual prediction has its own explanation.

Example

```text
This patient's recommendation was primarily influenced by

Resistance profile

Severity

Renal function
```

---

# Counterfactual Explanation

Future versions support counterfactual reasoning.

Example

```text
If renal impairment were absent,

Recommended Drug

Amoxicillin

instead of

Amoxicillin-Clavulanate
```

---

# Evidence Traceability

Every explanation includes

Evidence ID

Recommendation ID

WHO chapter

Page reference

Knowledge source version

Guideline publication

This supports complete traceability.

---

# Knowledge Source Contributions

Example

```text
WHO

Treatment recommendation

SOAR

Respiratory susceptibility

ARMD

Resistance intelligence
```

Each contribution is displayed independently.

---

# Warning Generation

The Explainability Engine generates warnings.

Examples

Drug allergy

Renal adjustment

Pregnancy risk

Stewardship restriction

Broad-spectrum alert

Resistance concern

Missing laboratory data

Warnings are always visible.

---

# Stewardship Explanation

Example

```text
Broad-spectrum therapy avoided.

WHO recommends narrow-spectrum therapy.

Antimicrobial stewardship policy satisfied.
```

---

# Patient-Friendly Explanation

Future versions support simplified summaries.

Example

```text
This antibiotic was selected because it is the recommended treatment for your infection and has a high chance of working while reducing unnecessary antibiotic exposure.
```

---

# API Response Example

```json
{
  "recommendation": "Amoxicillin",
  "confidence": 95,
  "reasoning": {
    "guideline": "WHO",
    "knowledge_sources": [
      "WHO",
      "SOAR",
      "ARMD"
    ],
    "patient_factors": [
      "Adult",
      "No allergy"
    ],
    "clinical_rules": [
      "Stewardship compliant"
    ]
  }
}
```

---

# Explainability Performance

Target

Narrative generation

<20 ms

Evidence aggregation

<20 ms

SHAP formatting

<20 ms

API serialization

<20 ms

Total

<100 ms

---

# Audit Integration

Every explanation stores

Recommendation ID

Clinical case ID

Evidence used

Rules applied

Confidence

SHAP output

Knowledge versions

Timestamp

User ID

---

# Future Enhancements

Planned support includes

Interactive reasoning graphs

Evidence timelines

Visual SHAP plots

Counterfactual simulations

Natural-language questioning

Voice explanations

FHIR explanation resources

Multilingual explanations

Patient education mode

Clinician teaching mode

---

# Development Rules

Every Explainability component must

- Be deterministic
- Never fabricate evidence
- Preserve provenance
- Support structured output
- Support narrative output
- Support SHAP integration
- Support audit logging
- Be independently testable
- Be version controlled

---

# Explainability Checklist

Every recommendation must include

- Recommendation summary
- Supporting evidence
- Knowledge sources
- Clinical rules
- Patient factors
- Resistance explanation
- Confidence score
- Alternative therapies
- Warnings
- Audit reference
- SHAP explanation (when applicable)

---

# Explainability Principle

> **The PharmaTrybe Explainability Engine transforms evidence, clinical rules, knowledge fusion, and AI reasoning into transparent, clinician-centered explanations. Every recommendation is fully traceable to its originating evidence, supporting guidelines, patient-specific factors, resistance intelligence, and safety rules, ensuring that antimicrobial prescribing remains explainable, auditable, trustworthy, and aligned with evidence-based medicine.**