# Phase 28H Controlled Synthetic Cases

All cases use technical `SYNTHETIC_TEST_DATA`; no real patient information or credentials are included.

| Case | Synthetic input/path | Fusion | Recommendation | Explainability | Audit | Status |
|---|---|---|---|---|---|---|
| A SOAR Streptococcus | Exact Doxycycline/Streptococcus deployment, real model execution | Real SOAR trace entered DecisionFusionEngine | Doxycycline | Actual prediction/deployment/rules context consumed | SUCCESS audit event constructed | PARTIAL: authenticated UI/retrieval not verified |
| B SOAR Haemophilus | Ceftriaxone; internal beta values 0 and 1 | Real model execution verified; H. influenzae-specific fusion trace not run | Prediction outputs valid | Focused boundary only | Shared audit tests | PARTIAL |
| C ARMD | Approved clinical fields -> WP4 preprocessing -> final frame -> registered models | ARMD-specific fusion trace not run | Not claimed | Focused adapter/plugin explainability tests | Shared audit tests | PARTIAL |
| D WHO | Dynamic provider/database query | WHO-specific fusion trace not run | Not claimed | Focused WHO/provider evidence only | Shared audit tests | PARTIAL |
| E Safety conflict | High score plus supported penicillin allergy rule | Real fusion safety test | Unsafe amoxicillin excluded | Rule explanation path tested | Shared audit tests | READY_FOR_CONTROLLED_EXECUTION |

## Measured focused evidence
- SOAR execution: 12 passed.
- ARMD plugin/adapter: 31 passed.
- WHO/fusion/explainability/integration: 80 passed.
- Audit: 15 passed.
