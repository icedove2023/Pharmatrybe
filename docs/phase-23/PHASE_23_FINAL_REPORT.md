# Phase 23 - SOAR Deployment Input Contract Extraction & Clinical Input Resolution Report

## 1. Actual deployment count
10 deployments were verified from the repository runtime artifact tree and adjacent authoritative metadata.

## 2. Deployment input matrix
The complete matrix is in [PHASE_23A_SOAR_DEPLOYMENT_INPUT_EXTRACTION.md](PHASE_23A_SOAR_DEPLOYMENT_INPUT_EXTRACTION.md). All deployments require `Age`, `YearCollected`, `Region`, `BodyLocation_Group`, and `Country`. The eight H. influenzae deployments additionally require `Beta_Lactamase_enc`.

## 3. Common inputs
`Age`, `YearCollected`, `Region`, `BodyLocation_Group`, and `Country`.

## 4. Deployment-specific inputs
`Beta_Lactamase_enc` applies only to the eight H. influenzae deployments. Its numeric clinical mapping is not verified, so those deployments are blocked.

## 5. Canonical clinical data reuse
No automatic prefill is approved unless an exact model key is present in canonical data. No semantic aliases are used.

## 6. Clinician completion inputs
The five common fields can be explicitly collected with verified type/enum validation. Beta-lactamase cannot be safely collected as a Yes/No control until its numeric mapping is confirmed.

## 7. Legacy fields
`pathogen` and `culture` are not consumed by the verified model input schemas. They are quarantined from the active SOAR payload. Routing requires explicit `deployment_id`.

## 8. Safety boundaries
No deployment inference, arbitrary fallback, fake clinical values, fuzzy mapping, or model feature guessing is permitted.

## 9. Readiness matrix
| Deployment group | Count | Status | Reason |
|---|---:|---|---|
| Streptococcus pneumoniae | 2 | PARTIAL | Contract and resolver are verified; all five inputs require explicit controlled collection because no canonical direct matches are evidenced. |
| Haemophilus influenzae | 8 | BLOCKED | `Beta_Lactamase_enc` is passthrough numeric and its clinical 0/1 meaning is not recorded in repository evidence. |

## 10. Verification
- `npm test`: PASS, 195 assertions reported by the repository runner.
- Python SOAR tests: NOT CONFIRMED; collection is blocked by missing `jsonschema` in the active Python environment.
- `npm run lint`: NOT PASSING; the repository reports six pre-existing application errors plus one unrelated `DynamicClinicalForm.tsx` error. The Phase 23 registry error found during this run was corrected and has no remaining diagnostic.
- `npm run build`: PASS; Vite production build completed successfully with existing chunk-size and dynamic-import warnings.
- `git diff --check`: PASS; no whitespace errors.
- `npm test`: PASS; exit code 0 and the repository runner completed its full suite, including the Phase 23 resolver suite.
- Backend contracts/model code: not intentionally modified by Phase 23.
