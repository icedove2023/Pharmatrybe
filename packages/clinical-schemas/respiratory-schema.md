# Respiratory Prediction Schema (SOAR/GSK)

**Schema Name:** Respiratory Prediction  
**Schema ID:** PT-RS-001  
**Version:** 1.0.0  
**Status:** Official Platform Contract  
**Owner:** SOAR/GSK AI Engine

---

# Purpose

The Respiratory Prediction Schema defines the official output contract of the SOAR/GSK AI model.

Its responsibility is to provide evidence-based predictions regarding respiratory pathogens and antimicrobial susceptibility.

This schema **does not recommend antibiotics**.

Drug recommendation is exclusively the responsibility of the Clinical Decision Engine.

---

# Responsibilities

The SOAR/GSK model is responsible for:

- Predicting likely respiratory pathogens
- Predicting antimicrobial susceptibility
- Estimating prediction confidence
- Reporting model evidence
- Reporting feature importance

---

# Not Responsible For

The SOAR/GSK model must never:

- Recommend antibiotics
- Apply WHO guidelines
- Interpret stewardship policies
- Choose Access/Watch/Reserve drugs
- Rank treatments
- Generate clinician explanations

Those responsibilities belong to downstream services.

---

# Input

Consumes:

Clinical Case Schema

```
ClinicalCase
```

---

# Output Structure

## Metadata

| Field | Type | Required |
|--------|------|----------|
| request_id | UUID | Yes |
| prediction_id | UUID | Yes |
| model_name | String | Yes |
| model_version | String | Yes |
| prediction_timestamp | ISO8601 | Yes |

---

## Respiratory Assessment

| Field | Type | Required |
|--------|------|----------|
| syndrome | String | Yes |
| predicted_pathogens | Array | Yes |
| prediction_confidence | Decimal | Yes |

---

## Predicted Pathogens

Each pathogen contains

| Field | Type |
|--------|------|
| organism |
| probability |
| evidence_score |

Example

```json
[
  {
    "organism":"Streptococcus pneumoniae",
    "probability":0.81,
    "evidence_score":0.88
  },
  {
    "organism":"Haemophilus influenzae",
    "probability":0.62,
    "evidence_score":0.74
  }
]
```

---

# Susceptibility Prediction

| Field | Type |
|--------|------|
| antibiotic |
| prediction |
| probability |

Allowed prediction values

```
Susceptible

Intermediate

Resistant
```

Example

```json
[
 {
   "antibiotic":"Amoxicillin",
   "prediction":"Susceptible",
   "probability":0.91
 },
 {
   "antibiotic":"Azithromycin",
   "prediction":"Intermediate",
   "probability":0.64
 }
]
```

---

# Clinical Severity

Optional section

| Field | Type |
|--------|------|
| predicted_severity |
| confidence |

---

# Feature Contributions

Explainable AI metadata

| Field | Type |
|--------|------|
| feature |
| contribution |

Example

```json
[
 {
   "feature":"Age",
   "contribution":0.18
 },
 {
   "feature":"Respiratory Rate",
   "contribution":0.27
 },
 {
   "feature":"Previous Respiratory Infection",
   "contribution":0.14
 }
]
```

---

# Model Confidence

| Field | Type |
|--------|------|
| overall_confidence |
| calibration_score |
| uncertainty |

---

# Validation Rules

Probabilities

```
0 ≤ probability ≤ 1
```

Confidence

```
0 ≤ confidence ≤ 1
```

Every predicted pathogen must include

- organism
- probability

---

# Example Response

```json
{
  "request_id":"12345",

  "prediction_id":"SOAR-001",

  "model_name":"SOAR-GSK",

  "model_version":"2.1",

  "predicted_pathogens":[
      {
          "organism":"Streptococcus pneumoniae",
          "probability":0.84
      },
      {
          "organism":"Haemophilus influenzae",
          "probability":0.65
      }
  ],

  "susceptibility_predictions":[
      {
          "antibiotic":"Amoxicillin",
          "prediction":"Susceptible",
          "probability":0.90
      },
      {
          "antibiotic":"Azithromycin",
          "prediction":"Intermediate",
          "probability":0.58
      }
  ],

  "overall_confidence":0.89
}
```

---

# Downstream Consumers

The Respiratory Prediction Schema is consumed by:

- Clinical Decision Engine
- Explainability Engine

The Frontend must never consume this schema directly.

---

# Relationship with ARMD

SOAR provides respiratory susceptibility predictions.

ARMD provides hospital resistance predictions.

Neither model knows about the other.

Fusion occurs only inside the Clinical Decision Engine.

---

# Governance

The SOAR/GSK model shall never recommend an antibiotic.

It only predicts microbiological evidence.

Treatment decisions remain the responsibility of the Clinical Decision Engine, informed by WHO guidance and clinician oversight.