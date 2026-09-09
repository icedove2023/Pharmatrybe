# Phase 24C - SOAR Clinical Completion Form

Implemented component: `src/plugins/contracts/SoarClinicalCompletionForm.tsx`.

| Field | Clinical label | Contract key | Validation | Provenance | Rendered when |
|---|---|---|---|---|---|
| Age | Age (years) | `Age` | Number, required | Clinician entered or exact canonical key | Missing |
| Year collected | Year collected | `YearCollected` | Number, required | Clinician entered or exact canonical key | Missing |
| Region | Region | `Region` | Deployment enum | Clinician entered or exact canonical key | Missing |
| Body location | Body location group | `BodyLocation_Group` | Verified enum | Clinician entered or exact canonical key | Missing |
| Country | Country | `Country` | Deployment-specific enum | Clinician entered or exact canonical key | Missing |
| Beta-lactamase | Not rendered as a clinical status control | `Beta_Lactamase_enc` | Unresolved mapping | None accepted | Never while mapping is unresolved |

The selected organism and antimicrobial are read-only verified metadata. Deployment ID is a selector value used for exact routing, not a clinician-entered clinical field. The existing `DynamicClinicalForm` and `validateFormValues` engine perform form validation; no second validation engine or frontend model preprocessing was added.
