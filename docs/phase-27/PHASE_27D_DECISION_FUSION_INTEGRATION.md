# Phase 27D Decision/Fusion Integration

## Actual path
`PredictionRequest -> SOAR/ARMD plugin execution -> PredictionResult/knowledge evidence -> DecisionFusionEngine.fuse_decision -> ClinicalRulesEngine + GuidelineEngine + StewardshipEngine -> RecommendationResult`.

The fusion engine receives plugin probabilities as evidence and evaluates clinical rules before ranking. A focused test with penicillin allergy confirms a high-scoring amoxicillin prediction is not selected when contraindicated.

## Controlled runtime evidence
A synthetic SOAR Streptococcus case executed a real Doxycycline model, then passed its probability into `DecisionFusionEngine`; the result was a governed Doxycycline recommendation with clinical rules evaluated. `ExplainabilityEngine` then consumed the recommendation, and `build_audit_event` produced a SUCCESS audit event labelled `SYNTHETIC_TEST_DATA`.

## Tests
- `test_clinical_decision.py`: 65 passed in the combined focused run, including contraindication behavior and fusion.
- Combined WHO/plugin/explainability/fusion command: 80 passed.
- Audit persistence/logging command: 15 passed.

## Status
`READY_FOR_CONTROLLED_EXECUTION` for the repository-supported local decision/fusion path. No plugin directly prescribes or bypasses safety rules.
