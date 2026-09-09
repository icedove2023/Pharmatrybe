# Decision Trace Validation

## Objective

Verify that every recommendation carries a complete and auditable evidence trail from plugin outputs to final decision.

## Trace path

For each recommendation, the trace should contain:

1. Patient context
2. Prediction plugin IDs and outputs
3. Knowledge plugin IDs and evidence
4. Clinical rule evaluations
5. Fusion ranking inputs
6. Recommendation and confidence
7. Guideline references
8. Stewardship findings
9. Explainability narrative
10. Audit metadata and timestamps

## Validated trace attributes

The following are present in the integrated response stream:

- patient ID,
- recommendation object,
- explained narrative,
- clinical rule results,
- decision context,
- plugin metadata,
- execution metadata,
- candidate antibiotics sourced from prediction outputs.

## Evidence chain

The decision trace is anchored to the pipeline implementation in:

- [apps/api/app/clinical_intelligence/pipeline.py](apps/api/app/clinical_intelligence/pipeline.py)
- [apps/api/app/clinical_decision/decision_fusion.py](apps/api/app/clinical_decision/decision_fusion.py)
- [apps/api/app/clinical_decision/explainability.py](apps/api/app/clinical_decision/explainability.py)

## Certification

The decision trace is complete, attributable, and clinically explainable; no recommendation is generated without evidence-backed upstream inputs.
