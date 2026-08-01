# WHO Knowledge Schema

**Schema Name:** WHO Knowledge Response  
**Schema ID:** PT-WHO-001  
**Version:** 1.0.0  
**Status:** Official Platform Contract  
**Owner:** WHO Knowledge Engine

---

# Purpose

The WHO Knowledge Schema defines the official response contract for the PharmaTrybe WHO Knowledge Engine.

Unlike SOAR/GSK and ARMD, the WHO Engine does **not perform machine learning**.

It retrieves structured, evidence-based clinical knowledge from the PharmaTrybe WHO database.

The WHO Knowledge Engine acts as the single authoritative source for antimicrobial stewardship guidance.

---

# Responsibilities

The WHO Knowledge Engine is responsible for:

- WHO AWaRe classification
- Disease-specific recommendations
- Drug information
- Pathogen guidance
- Diagnostic recommendations
- Stewardship recommendations
- Monitoring advice
- Follow-up advice
- Referral recommendations
- Evidence references

---

# The WHO Engine Never

The WHO Engine must never:

- Predict resistance
- Predict pathogens
- Score patient risk
- Recommend based on AI
- Override clinician judgement

It only provides structured evidence.

---

# Input

Consumes:

```
Clinical Case Schema
```

The Decision Engine determines which WHO queries should be executed.

---

# Output Structure

---

# Metadata

| Field | Type | Required |
|--------|------|----------|
| request_id | UUID | Yes |
| knowledge_version | String | Yes |
| database_version | String | Yes |
| retrieval_timestamp | ISO8601 | Yes |

---

# Disease Information

Derived from

```
Diseases
```

| Field | Type |
|--------|------|
| disease_name |
| syndrome |
| severity_category |
| disease_description |

---

# Pathogen Information

Derived from

```
Pathogens
```

| Field | Type |
|--------|------|
| organism |
| organism_group |
| resistance_notes |
| common_presentations |

Example

```json
[
  {
    "organism":"Streptococcus pneumoniae",
    "organism_group":"Gram Positive",
    "common_presentations":[
        "CAP",
        "Otitis Media"
    ]
  }
]
```

---

# Drug Information

Derived from

```
Drugs
```

| Field | Type |
|--------|------|
| drug_name |
| aware_group |
| drug_class |
| spectrum |
| contraindications |
| renal_adjustment |
| pregnancy_category |

---

# WHO Recommendation

Derived from

```
Recommendations

Recommendation_Pathogens
```

| Field | Type |
|--------|------|
| recommendation_level |
| first_line |
| second_line |
| reserve_options |
| recommendation_strength |

Example

```json
{
   "first_line":[
      "Amoxicillin"
   ],
   "second_line":[
      "Amoxicillin-Clavulanate"
   ],
   "reserve_options":[
      "Meropenem"
   ]
}
```

---

# Diagnostics

Derived from

```
Diagnostics
```

| Field | Type |
|--------|------|
| recommended_tests |
| specimen_type |
| timing |
| interpretation_notes |

---

# Monitoring

Derived from

```
Monitoring
```

| Field | Type |
|--------|------|
| laboratory_monitoring |
| toxicity_monitoring |
| treatment_review |
| escalation_criteria |

---

# Follow-up

Derived from

```
Followup
```

| Field | Type |
|--------|------|
| review_interval |
| expected_response |
| failure_definition |
| discharge_criteria |

---

# Stewardship

Derived from

```
Stewardship
```

| Field | Type |
|--------|------|
| aware_group |
| stewardship_message |
| de_escalation_strategy |
| iv_to_oral_switch |
| duration_guidance |

---

# Referral

Derived from

```
Referral
```

| Field | Type |
|--------|------|
| specialist_required |
| referral_reason |
| urgency |

---

# Evidence

Derived from

```
Evidence
```

| Field | Type |
|--------|------|
| guideline |
| publication |
| year |
| evidence_grade |
| citation |

Example

```json
[
 {
    "guideline":"WHO AWaRe",
    "year":2025,
    "evidence_grade":"Strong"
 }
]
```

---

# Metadata

Derived from

```
Metadata
```

Provides

- version
- update date
- contributor
- source organization

---

# Validation Rules

The WHO Engine must always return

- evidence source
- guideline version
- recommendation strength

If evidence cannot be found

Return

```
status = NO_GUIDANCE_AVAILABLE
```

instead of inventing recommendations.

---

# Example Response

```json
{
  "request_id":"PT-001",

  "disease":"Community Acquired Pneumonia",

  "drug_information":[
      {
          "drug_name":"Amoxicillin",
          "aware_group":"Access"
      }
  ],

  "recommendation":{
      "first_line":[
          "Amoxicillin"
      ],
      "recommendation_strength":"Strong"
  },

  "diagnostics":{
      "recommended_tests":[
          "Chest X-Ray",
          "Blood Culture"
      ]
  },

  "stewardship":{
      "aware_group":"Access",
      "duration":"5 days"
  },

  "evidence":[
      {
          "guideline":"WHO AWaRe",
          "year":2025
      }
  ]
}
```

---

# Relationship with SOAR

SOAR predicts respiratory susceptibility.

WHO provides evidence.

SOAR never accesses WHO tables directly.

---

# Relationship with ARMD

ARMD predicts hospital resistance.

WHO provides antimicrobial guidance.

ARMD never accesses WHO tables directly.

---

# Relationship with the Decision Engine

The Clinical Decision Engine is the **only service** permitted to combine:

- SOAR prediction
- ARMD prediction
- WHO knowledge

into a final recommendation.

---

# Supabase Table Mapping

| WHO Table | Schema Section |
|------------|----------------|
| diseases | Disease Information |
| pathogens | Pathogen Information |
| drugs | Drug Information |
| recommendations | Recommendation |
| recommendation_pathogens | Recommendation |
| diagnostics | Diagnostics |
| monitoring | Monitoring |
| followup | Follow-up |
| stewardship | Stewardship |
| referral | Referral |
| evidence | Evidence |
| metadata | Metadata |

These mappings are implementation details and must remain internal to the WHO Knowledge Engine.

---

# Governance

The WHO Knowledge Schema is the official contract for evidence retrieval within PharmaTrybe.

It represents structured clinical knowledge only.

It contains no predictive algorithms and no machine learning outputs.

All evidence returned by this schema must be traceable to a recognised guideline source and version.