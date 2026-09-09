# Explainability Contract v1.0.0

Status: FROZEN for the canonical recommendation response.

## Runtime output

The recommendation API returns:

- `explanation`
- `evidence_ranking`
- `recommendation_trace`
- `evidence_attribution`
- `audit_reference`
- top-level `trace_id`

The explanation model contains `recommendation_id`, `patient_id`, `primary_antibiotic`, prediction explanation data, rule explanations, guideline explanations, stewardship explanations, evidence drivers, warnings, a clinical narrative, and generation time.

Evidence drivers identify evidence type, source, contribution (`supports`, `opposes`, or `neutral`), weight, and explanation. The audit trail records plugin/model versions, rule/guideline/stewardship versions, CDSS/algorithm versions, trace ID, and metadata.

ARMD and SOAR may also expose plugin-specific model explanations. Those are not silently normalized into a universal feature-ownership claim.

## Missing explanation

The pipeline uses a truthful fallback narrative when no explanation is available. It does not claim SHAP or guideline evidence exists when the runtime did not produce it.

## Compatibility boundary

The canonical public explainability boundary is the `ExplainabilityResponseContract` returned by `/api/v1/recommendations/generate`. Plugin-specific SHAP/model details remain nested evidence and are not promoted to universal clinical semantics. Missing optional explanation data is represented by empty/explicit structures, never fabricated.
