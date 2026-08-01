# PharmaTrybe — Request / Response Schemas

**Phase 2, Step 3A — Architecture specification only**

This document defines every payload exchanged between PharmaTrybe services. JSON examples are documentation only — not implemented APIs. Payload shapes are the frozen contracts for Phase 3 implementation.

**Contract version:** `1.0.0`

---

## Shared Conventions

Every payload includes correlation and versioning fields:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "contract_version": "1.0.0"
}
```

### Enumerations

| Field | Values |
|-------|--------|
| `resistance_flag` | `none`, `predicted`, `confirmed` |
| `confidence_band` | `low`, `moderate`, `high` |
| `aware_category` | `access`, `watch`, `reserve`, `unclassified` |
| `clinical_scenario` | `no_resistance`, `resistance_predicted`, `resistance_confirmed` |
| `care_setting` | `community`, `hospital_inpatient`, `hospital_outpatient`, `icu` |

---

## 1. Clinical Case

The canonical patient context exchanged between the backend and every service. Each service consumes the subset relevant to its responsibility.

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `case_id` | string | Yes | Unique case identifier |
| `demographics` | object | Yes | Age, sex, weight |
| `clinical_setting` | object | Yes | Care setting, ward, ICU exposure |
| `presentation` | object | Yes | Syndrome, onset, severity score |
| `vitals` | object | Recommended | Temperature, heart rate, RR, SpO₂ |
| `laboratory` | object | Recommended | CRP, WBC, creatinine, other biomarkers |
| `microbiology` | object | Recommended | Known organism, confirmed resistance, cultures |
| `antimicrobial_history` | object | Recommended | Prior and current antibiotics |
| `procedures` | array | Optional | Recent procedures |
| `allergies` | array | Recommended | Drug allergies and intolerances |
| `resistance_status` | enum | Yes | Orchestration switch: `none`, `predicted`, `confirmed` |

### Example

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "contract_version": "1.0.0",
  "clinical_case": {
    "case_id": "case-2026-001",
    "demographics": {
      "age_years": 67,
      "sex": "female",
      "weight_kg": 72
    },
    "clinical_setting": {
      "care_setting": "hospital_inpatient",
      "ward": "respiratory",
      "icu_exposure": false
    },
    "presentation": {
      "syndrome": "community_acquired_pneumonia",
      "symptom_onset_days": 4,
      "severity_score": {
        "system": "CURB-65",
        "value": 2
      }
    },
    "vitals": {
      "temperature_c": 38.6,
      "heart_rate": 98,
      "respiratory_rate": 22,
      "spo2_percent": 94
    },
    "laboratory": {
      "crp_mg_l": 85,
      "wbc_10e9_l": 14.2,
      "creatinine_umol_l": 90
    },
    "microbiology": {
      "known_organism": "streptococcus_pneumoniae",
      "known_resistance": [],
      "prior_cultures": []
    },
    "antimicrobial_history": {
      "prior_antibiotics_90d": ["amoxicillin"],
      "current_antibiotics": []
    },
    "procedures": [],
    "allergies": ["penicillin"],
    "resistance_status": "none"
  }
}
```

---

## 2. SOAR Result

Returned by the SOAR/GSK Model Service after respiratory stewardship prediction.

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | object | Yes | Model name, version, inference timestamp |
| `prediction.respiratory_resistance` | object | Yes | Probability, confidence band, resistance flag |
| `prediction.syndrome_assessment` | object | Yes | Primary syndrome and secondary signals |
| `prediction.clinical_risk` | object | Yes | Risk score and level |
| `explainability_metadata` | object | Yes | Top features and attribution method |

### Example

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "contract_version": "1.0.0",
  "soar_result": {
    "model": {
      "name": "SOAR-GSK-respiratory",
      "version": "2.1.0",
      "inference_timestamp": "2026-08-01T11:30:01Z"
    },
    "prediction": {
      "respiratory_resistance": {
        "probability": 0.73,
        "confidence_band": "moderate",
        "resistance_flag": "predicted"
      },
      "syndrome_assessment": {
        "primary_syndrome": "community_acquired_pneumonia",
        "secondary_signals": ["bacterial_likely"]
      },
      "clinical_risk": {
        "score": 0.62,
        "level": "moderate"
      }
    },
    "explainability_metadata": {
      "top_features": [
        {
          "feature": "prior_antibiotic_exposure",
          "direction": "increases_risk",
          "weight": 0.21
        },
        {
          "feature": "crp_mg_l",
          "direction": "increases_risk",
          "weight": 0.14
        }
      ],
      "method": "shap"
    }
  }
}
```

### Scenario 2 variant (no resistance)

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
  "contract_version": "1.0.0",
  "soar_result": {
    "model": {
      "name": "SOAR-GSK-respiratory",
      "version": "2.1.0",
      "inference_timestamp": "2026-08-01T11:45:01Z"
    },
    "prediction": {
      "respiratory_resistance": {
        "probability": 0.12,
        "confidence_band": "moderate",
        "resistance_flag": "none"
      },
      "syndrome_assessment": {
        "primary_syndrome": "community_acquired_pneumonia",
        "secondary_signals": ["bacterial_likely"]
      },
      "clinical_risk": {
        "score": 0.35,
        "level": "low"
      }
    },
    "explainability_metadata": {
      "top_features": [
        {
          "feature": "symptom_onset_days",
          "direction": "increases_risk",
          "weight": 0.09
        }
      ],
      "method": "shap"
    }
  }
}
```

---

## 3. ARMD Result

Returned by the ARMD Model Service after hospital resistance prediction. Omitted entirely in Scenario 2 (no predicted resistance).

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | object | Yes | Model name, version, feature schema version |
| `prediction.target_organism` | string | Yes | Primary organism for resistance profile |
| `prediction.resistance_probabilities` | array | Yes | Per-antibiotic-class probabilities |
| `prediction.overall_resistance_risk` | object | Yes | Aggregate resistance probability |
| `prediction.organism_resistance_profile` | object | Yes | Organism-level resistance summary |
| `explainability_metadata` | object | Yes | Top features and attribution method |

### Example

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "contract_version": "1.0.0",
  "armd_result": {
    "model": {
      "name": "ARMD-hospital-resistance",
      "version": "0.4.0-wp2",
      "feature_schema_version": "1.0.0",
      "inference_timestamp": "2026-08-01T11:30:02Z"
    },
    "prediction": {
      "target_organism": "streptococcus_pneumoniae",
      "resistance_probabilities": [
        {
          "antibiotic_class": "penicillin",
          "probability": 0.81,
          "confidence_band": "high"
        },
        {
          "antibiotic_class": "macrolide",
          "probability": 0.45,
          "confidence_band": "moderate"
        },
        {
          "antibiotic_class": "fluoroquinolone",
          "probability": 0.08,
          "confidence_band": "high"
        }
      ],
      "overall_resistance_risk": {
        "probability": 0.78,
        "confidence_band": "high"
      },
      "organism_resistance_profile": {
        "organism": "streptococcus_pneumoniae",
        "predicted_phenotypes": ["penicillin_resistant"],
        "supporting_features": [
          "prior_antibiotic_exposure_90d",
          "previous_resistance_history"
        ]
      }
    },
    "explainability_metadata": {
      "top_features": [
        {
          "feature": "prior_antibiotic_exposure_90d",
          "direction": "increases_risk",
          "weight": 0.28
        },
        {
          "feature": "previous_resistance_history",
          "direction": "increases_risk",
          "weight": 0.19
        },
        {
          "feature": "hospital_ward_exposure",
          "direction": "increases_risk",
          "weight": 0.11
        }
      ],
      "method": "feature_attribution"
    }
  }
}
```

---

## 4. WHO Result

Returned by the WHO Knowledge Service. Contains structured guideline knowledge — no predictions.

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `knowledge_version` | string | Yes | WHO knowledge base version |
| `antibiotics` | array | Yes | Antibiotic metadata entries |
| `antibiotics[].aware_category` | enum | Yes | Access / Watch / Reserve |
| `antibiotics[].contraindications` | array | Yes | Contraindication flags |
| `guideline_recommendations` | array | Yes | Syndrome/organism-linked guidance |
| `stewardship_advice` | array | Yes | Contextual stewardship rules |

### Example

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "contract_version": "1.0.0",
  "who_result": {
    "knowledge_version": "who-aware-2026.1",
    "antibiotics": [
      {
        "antibiotic_id": "amoxicillin",
        "name": "Amoxicillin",
        "drug_class": "aminopenicillin",
        "spectrum": [
          "streptococcus_pneumoniae",
          "haemophilus_influenzae"
        ],
        "aware_category": "access",
        "contraindications": ["penicillin_allergy"],
        "stewardship_notes": [
          "First-line for uncomplicated CAP when local resistance is low"
        ]
      },
      {
        "antibiotic_id": "levofloxacin",
        "name": "Levofloxacin",
        "drug_class": "fluoroquinolone",
        "spectrum": [
          "streptococcus_pneumoniae",
          "atypical_pathogens"
        ],
        "aware_category": "watch",
        "contraindications": [],
        "stewardship_notes": [
          "Reserve for beta-lactam allergy or documented resistance"
        ]
      },
      {
        "antibiotic_id": "doxycycline",
        "name": "Doxycycline",
        "drug_class": "tetracycline",
        "spectrum": [
          "atypical_pathogens",
          "respiratory_gram_positive"
        ],
        "aware_category": "access",
        "contraindications": [],
        "stewardship_notes": [
          "Alternative when beta-lactams are contraindicated"
        ]
      }
    ],
    "guideline_recommendations": [
      {
        "guideline_id": "who-cap-stewardship-2024",
        "syndrome": "community_acquired_pneumonia",
        "recommendation": "Prefer Access group agents when local resistance is low.",
        "evidence_level": "guideline",
        "source": "WHO AWaRe / CAP stewardship guidance"
      }
    ],
    "stewardship_advice": [
      {
        "code": "PREFER_ACCESS",
        "message": "When resistance is not predicted, prioritize AWaRe Access antibiotics.",
        "applies_when": {
          "resistance_flag": "none"
        }
      },
      {
        "code": "CONSIDER_ALTERNATIVES",
        "message": "When resistance is predicted, avoid agents with high resistance probability.",
        "applies_when": {
          "resistance_flag": "predicted"
        }
      },
      {
        "code": "DOCUMENT_WATCH_USE",
        "message": "Watch agents require documented clinical justification.",
        "applies_when": {
          "aware_category": "watch"
        }
      }
    ]
  }
}
```

---

## 5. Decision Result

Returned by the Clinical Decision Engine — the only payload that contains clinical antibiotic recommendations.

### Input composition

The Decision Engine receives a composite payload assembled by the backend:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "contract_version": "1.0.0",
  "clinical_case": { "case_id": "case-2026-001" },
  "clinical_scenario": "resistance_predicted",
  "soar_result": { "prediction": { "respiratory_resistance": { "resistance_flag": "predicted" } } },
  "armd_result": { "prediction": { "overall_resistance_risk": { "probability": 0.78 } } },
  "who_result": { "knowledge_version": "who-aware-2026.1" }
}
```

### Output schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ruleset` | object | Yes | Stewardship ruleset ID and version |
| `clinical_scenario` | enum | Yes | Scenario applied |
| `recommended_options` | array | Yes | Ranked antibiotic recommendations |
| `rejected_options` | array | Yes | Deprioritized options with reasons |
| `decision_pathway` | array | Yes | Step-by-step decision trace |
| `confidence_summary` | object | Yes | Aggregated confidence from inputs |
| `disclaimer` | string | Yes | Clinician-assistance statement |

### Example

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "contract_version": "1.0.0",
  "decision_result": {
    "ruleset": {
      "id": "pharmatrybe-stewardship-rules",
      "version": "1.0.0"
    },
    "clinical_scenario": "resistance_predicted",
    "recommended_options": [
      {
        "rank": 1,
        "antibiotic_id": "levofloxacin",
        "name": "Levofloxacin",
        "aware_category": "watch",
        "ranking_reasons": [
          "Predicted penicillin resistance (SOAR + ARMD)",
          "Spectrum covers target organism",
          "Avoids documented penicillin allergy"
        ],
        "warnings": [
          "Fluoroquinolone — use stewardship justification",
          "AWaRe Watch agent — document indication"
        ],
        "stewardship_notes": [
          "Alternative to Access agents due to predicted resistance"
        ],
        "evidence_refs": [
          "who-cap-stewardship-2024",
          "soar:respiratory_resistance",
          "armd:penicillin_class"
        ],
        "confidence_band": "moderate"
      },
      {
        "rank": 2,
        "antibiotic_id": "doxycycline",
        "name": "Doxycycline",
        "aware_category": "access",
        "ranking_reasons": [
          "Alternative with lower resistance probability for macrolide class",
          "AWaRe Access agent"
        ],
        "warnings": [],
        "stewardship_notes": [
          "Consider if fluoroquinolone not appropriate"
        ],
        "evidence_refs": [
          "who-cap-stewardship-2024",
          "armd:macrolide_class"
        ],
        "confidence_band": "moderate"
      }
    ],
    "rejected_options": [
      {
        "antibiotic_id": "amoxicillin",
        "name": "Amoxicillin",
        "aware_category": "access",
        "rejection_reasons": [
          "High predicted penicillin-class resistance (ARMD: 81%)",
          "Documented penicillin allergy"
        ],
        "evidence_refs": [
          "armd:penicillin_class",
          "clinical_case:allergies"
        ]
      }
    ],
    "decision_pathway": [
      {
        "step": 1,
        "action": "Assess resistance",
        "result": "Resistance predicted — Scenario 1"
      },
      {
        "step": 2,
        "action": "Apply WHO stewardship rules",
        "result": "Access agents deprioritized due to predicted resistance"
      },
      {
        "step": 3,
        "action": "Rank evidence-supported alternatives",
        "result": "2 recommended options, 1 rejected option"
      }
    ],
    "confidence_summary": {
      "soar": "moderate",
      "armd": "high",
      "overall": "moderate"
    },
    "disclaimer": "Evidence-supported options for clinician review — not an autonomous prescription."
  }
}
```

### Scenario 2 variant (no resistance, Access-preferred)

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
  "contract_version": "1.0.0",
  "decision_result": {
    "ruleset": {
      "id": "pharmatrybe-stewardship-rules",
      "version": "1.0.0"
    },
    "clinical_scenario": "no_resistance",
    "recommended_options": [
      {
        "rank": 1,
        "antibiotic_id": "amoxicillin",
        "name": "Amoxicillin",
        "aware_category": "access",
        "ranking_reasons": [
          "No predicted resistance",
          "WHO Access first-line for uncomplicated CAP",
          "Appropriate spectrum for target syndrome"
        ],
        "warnings": [],
        "stewardship_notes": [
          "Preferred AWaRe Access agent"
        ],
        "evidence_refs": [
          "who-cap-stewardship-2024",
          "soar:respiratory_resistance"
        ],
        "confidence_band": "high"
      }
    ],
    "rejected_options": [
      {
        "antibiotic_id": "levofloxacin",
        "name": "Levofloxacin",
        "aware_category": "watch",
        "rejection_reasons": [
          "AWaRe Watch agent not indicated when Access options are appropriate",
          "No predicted resistance requiring broad-spectrum alternative"
        ],
        "evidence_refs": [
          "who:PREFER_ACCESS",
          "soar:respiratory_resistance"
        ]
      }
    ],
    "decision_pathway": [
      {
        "step": 1,
        "action": "Assess resistance",
        "result": "No resistance predicted — Scenario 2"
      },
      {
        "step": 2,
        "action": "Apply WHO Access preference",
        "result": "Access agents prioritized"
      },
      {
        "step": 3,
        "action": "Rank stewardship recommendation",
        "result": "1 recommended option, 1 rejected option"
      }
    ],
    "confidence_summary": {
      "soar": "moderate",
      "armd": null,
      "overall": "high"
    },
    "disclaimer": "Evidence-supported options for clinician review — not an autonomous prescription."
  }
}
```

---

## 6. Explainability Result

Returned by the Explainability Engine. Required for every completed evaluation — no recommendation is valid without it.

### Input composition

The Explainability Engine receives the full artifact bundle:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "contract_version": "1.0.0",
  "clinical_case": { "case_id": "case-2026-001" },
  "soar_result": {},
  "armd_result": {},
  "who_result": {},
  "decision_result": {}
}
```

### Output schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template_version` | string | Yes | Explanation template version |
| `summary` | string | Yes | One-paragraph clinician overview |
| `sections` | object | Yes | Structured explanation sections |
| `sections.resistance_explanation` | object | Conditional | Present when resistance predicted/confirmed |
| `sections.ranking_explanation` | object | Yes | Why top option was ranked first |
| `sections.who_explanation` | object | Yes | AWaRe and guideline context |
| `sections.rejected_explanation` | object | Recommended | Why options were rejected |
| `sections.risk_factors` | array | Yes | Patient-specific contributing factors |
| `sections.decision_pathway` | array | Yes | Narrative pathway steps |
| `confidence_summary` | object | Yes | Confidence across all sources |

### Example

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "contract_version": "1.0.0",
  "explainability_result": {
    "template_version": "1.0.0",
    "summary": "Resistance is predicted for this respiratory presentation. Levofloxacin is ranked first as an evidence-supported alternative given predicted beta-lactam resistance and penicillin allergy. Amoxicillin was rejected due to high predicted penicillin-class resistance.",
    "sections": {
      "resistance_explanation": {
        "title": "Why resistance is predicted",
        "content": "SOAR estimates a 73% probability of respiratory resistance (moderate confidence). ARMD estimates 81% penicillin-class resistance for Streptococcus pneumoniae, driven mainly by recent antibiotic exposure and prior resistance history.",
        "sources": ["soar", "armd"]
      },
      "ranking_explanation": {
        "title": "Why levofloxacin is ranked first",
        "content": "The decision engine prioritized an agent with appropriate spectrum that avoids predicted penicillin resistance and documented penicillin allergy. AWaRe Watch use is flagged for stewardship documentation.",
        "sources": ["decision", "who"]
      },
      "who_explanation": {
        "title": "WHO AWaRe and guideline context",
        "content": "WHO guidance recommends Access agents when local resistance is low. Because resistance is predicted here, the engine surfaced Watch and alternative options with explicit stewardship warnings rather than defaulting to Access agents.",
        "sources": ["who"]
      },
      "rejected_explanation": {
        "title": "Why amoxicillin was rejected",
        "content": "Despite being an AWaRe Access agent and WHO first-line for uncomplicated CAP, amoxicillin was deprioritized because ARMD predicts 81% penicillin-class resistance and the patient has a documented penicillin allergy.",
        "sources": ["decision", "armd", "who"]
      },
      "risk_factors": [
        {
          "factor": "Prior amoxicillin within 90 days",
          "impact": "Increases resistance risk",
          "source": "armd"
        },
        {
          "factor": "Elevated CRP (85 mg/L)",
          "impact": "Supports bacterial respiratory infection signal",
          "source": "soar"
        },
        {
          "factor": "Penicillin allergy documented",
          "impact": "Contraindication for beta-lactam agents",
          "source": "clinical_case"
        }
      ],
      "decision_pathway": [
        "Respiratory assessment (SOAR) → resistance predicted",
        "Hospital resistance model (ARMD) → high penicillin-class probability",
        "WHO knowledge → alternatives and stewardship rules applied",
        "Decision engine → ranked options with warnings",
        "Amoxicillin rejected → resistance + allergy"
      ]
    },
    "confidence_summary": {
      "soar": "moderate",
      "armd": "high",
      "decision": "moderate",
      "overall": "moderate"
    }
  }
}
```

---

## Payload Exchange Summary

| From → To | Payload | Scenario 1 | Scenario 2 |
|-----------|---------|------------|------------|
| Backend → SOAR | Clinical Case | ✓ | ✓ |
| SOAR → Backend | SOAR Result | ✓ | ✓ |
| Backend → ARMD | Clinical Case | ✓ | ✗ (skipped) |
| ARMD → Backend | ARMD Result | ✓ | ✗ (skipped) |
| Backend → WHO | Query context (syndrome, organism, resistance flag) | ✓ | ✓ |
| WHO → Backend | WHO Result | ✓ | ✓ |
| Backend → Decision | Clinical Case + SOAR + ARMD + WHO | ✓ | ✓ (no ARMD) |
| Decision → Backend | Decision Result | ✓ | ✓ |
| Backend → Explainability | All prior results + Clinical Case | ✓ | ✓ |
| Explainability → Backend | Explainability Result | ✓ | ✓ |
| Backend → Frontend | Decision Result + Explainability Result + service trace | ✓ | ✓ |
