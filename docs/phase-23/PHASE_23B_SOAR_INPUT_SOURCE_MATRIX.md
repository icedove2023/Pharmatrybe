# Phase 23B - SOAR Input Source Matrix

| Field | Deployments | Required | Automatic source | UI action | Classification |
|---|---|---:|---|---|---|
| Age | All 10 | Yes | None evidenced | Request clinician value | CLINICIAN_REQUIRED |
| YearCollected | All 10 | Yes | None evidenced | Request clinician value | CLINICIAN_REQUIRED |
| Region | All 10 | Yes | None evidenced | Select verified enum | CLINICIAN_REQUIRED |
| BodyLocation_Group | All 10 | Yes | None evidenced | Select verified enum | CLINICIAN_REQUIRED |
| Country | All 10 | Yes | None evidenced | Select deployment enum | CLINICIAN_REQUIRED |
| Beta_Lactamase_enc | 8 H. influenzae deployments | Yes | None; semantic mapping absent | Block until mapping is verified | UNKNOWN |

No direct canonical clinical assessment key was evidenced for these exact model fields. Therefore the current resolver performs no automatic prefill. `infection_site`, `pathogen`, `organism`, `culture`, `species`, and `location` are not substituted for model inputs.

Allowed provenance values are `CANONICAL_CLINICAL_ASSESSMENT`, `CLINICIAN_ENTERED`, and `SYSTEM_CONTEXT`. The current implementation produces canonical provenance only when an exact key is explicitly supplied; it never produces guessed, inferred, fuzzy, or default provenance.
