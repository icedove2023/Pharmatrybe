# ARMD Resistance Prediction Schema

**Schema Name:** ARMD Resistance Prediction  
**Schema ID:** PT-ARMD-001  
**Version:** 1.0.0  
**Status:** Official Platform Contract  
**Owner:** ARMD AI Engine

---

# Purpose

The ARMD Schema defines the official output contract of the Antimicrobial Resistance Model (ARMD).

ARMD predicts **hospital-specific antimicrobial resistance risk** by analysing historical patient exposure, microbiology history, prior antimicrobial use, healthcare exposure, laboratory biomarkers, and clinical context.

The ARMD engine complements the SOAR/GSK respiratory model by supplying resistance intelligence that cannot be inferred from respiratory surveillance alone.

---

# Responsibilities

The ARMD model is responsible for:

- Predicting probability of antimicrobial resistance
- Identifying important resistance risk factors
- Predicting organism-specific resistance
- Estimating prediction confidence
- Producing explainable model outputs
- Supporting antimicrobial stewardship

---

# ARMD Never Does

ARMD must never:

- Recommend antibiotics
- Apply WHO guidelines
- Select Access / Watch / Reserve agents
- Override clinician judgement
- Produce treatment recommendations
- Interpret stewardship policy

Those responsibilities belong to the Clinical Decision Engine.

---

# Input

Consumes:

```
Clinical Case Schema
```

---

# Output Structure

---

# Metadata

| Field | Type | Required |
|--------|------|----------|
| request_id | UUID | Yes |
| prediction_id | UUID | Yes |
| model_name | String | Yes |
| model_version | String | Yes |
| prediction_timestamp | ISO8601 | Yes |

---

# Resistance Assessment

| Field | Type |
|--------|------|
| resistance_risk | Enum |
| resistance_probability | Decimal |
| confidence | Decimal |

Allowed values

```
Low

Moderate

High
```

---

# Predicted Resistant Organisms

Each organism includes

| Field | Type |
|--------|------|
| organism |
| resistance_probability |
| confidence |

Example

```json
[
 {
   "organism":"Escherichia coli",
   "resistance_probability":0.92,
   "confidence":0.88
 },
 {
   "organism":"Klebsiella pneumoniae",
   "resistance_probability":0.74,
   "confidence":0.81
 }
]
```

---

# Antibiotic Resistance Prediction

Each antibiotic prediction includes

| Field | Type |
|--------|------|
| antibiotic |
| prediction |
| probability |

Allowed predictions

```
Susceptible

Intermediate

Resistant
```

Example

```json
[
 {
   "antibiotic":"Ceftriaxone",
   "prediction":"Resistant",
   "probability":0.94
 },
 {
   "antibiotic":"Meropenem",
   "prediction":"Susceptible",
   "probability":0.91
 }
]
```

---

# Historical Risk Summary

This summarizes the major historical factors learned from the ARMD model.

| Field | Type |
|--------|------|
| previous_antibiotic_exposure |
| previous_resistant_isolates |
| previous_mdro |
| previous_organism_history |
| previous_hospitalization |
| icu_history |
| nursing_home_history |
| invasive_procedure_history |

Example

```json
{
  "previous_antibiotic_exposure":true,
  "previous_resistant_isolates":true,
  "icu_history":false,
  "nursing_home_history":false
}
```

---

# Clinical Risk Factors

Derived from WP2 feature engineering.

| Field | Type |
|--------|------|
| renal_impairment |
| inflammatory_burden |
| sepsis_risk |
| healthcare_associated_infection |
| multidrug_resistance_risk |

---

# Feature Importance (XAI)

Top contributing predictors.

| Field | Type |
|--------|------|
| feature |
| contribution |

Example

```json
[
 {
   "feature":"Previous Carbapenem Exposure",
   "contribution":0.31
 },
 {
   "feature":"ICU Admission",
   "contribution":0.19
 },
 {
   "feature":"Previous Resistant Organism",
   "contribution":0.26
 },
 {
   "feature":"Central Venous Catheter",
   "contribution":0.11
 }
]
```

---

# Model Confidence

| Field | Type |
|--------|------|
| calibration_score |
| prediction_uncertainty |
| confidence |

All values range

```
0.0 – 1.0
```

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

At least one resistance prediction must be returned.

Every organism prediction must contain:

- organism
- resistance_probability

---

# Example Response

```json
{
  "request_id":"PT-001",

  "prediction_id":"ARMD-2026-0001",

  "model_name":"ARMD",

  "model_version":"1.0",

  "resistance_risk":"High",

  "resistance_probability":0.91,

  "predicted_organisms":[
      {
          "organism":"Escherichia coli",
          "resistance_probability":0.92
      }
  ],

  "antibiotic_predictions":[
      {
          "antibiotic":"Ceftriaxone",
          "prediction":"Resistant",
          "probability":0.94
      },
      {
          "antibiotic":"Meropenem",
          "prediction":"Susceptible",
          "probability":0.89
      }
  ],

  "historical_risk_summary":{
      "previous_antibiotic_exposure":true,
      "icu_history":true,
      "previous_resistant_isolates":true
  },

  "confidence":0.89
}
```

---

# Relationship with SOAR

SOAR predicts respiratory susceptibility.

ARMD predicts hospital resistance.

Neither engine communicates directly.

Both engines submit their predictions independently to the Clinical Decision Engine.

---

# Relationship with WHO

ARMD never accesses WHO recommendations.

The WHO Knowledge Engine remains the authoritative source for:

- guideline recommendations
- AWaRe classification
- stewardship policy
- antimicrobial information

---

# Downstream Consumers

This schema is consumed only by:

- Clinical Decision Engine
- Explainability Engine

The frontend must never directly interpret ARMD outputs.

---

# WP2 Feature Lineage

The ARMD model is trained using engineered features originating from:

- Prior antibiotic exposure
- Antibiotic class exposure
- Laboratory biomarkers
- Vital signs
- Demographics
- Ward information
- Previous procedures
- Previous infecting organisms
- Historical resistance events
- Nursing home exposure
- Socioeconomic indicators (future)

These originate from the certified WP2 feature engineering pipeline and are abstracted within this schema. The deployment environment must not expose raw feature engineering details to downstream services.

---

# Governance

The ARMD Schema represents the official production interface for the ARMD AI Engine.

It exposes only prediction outputs and explainability metadata.

Model implementation, feature engineering, and training datasets remain internal to the ARMD service.