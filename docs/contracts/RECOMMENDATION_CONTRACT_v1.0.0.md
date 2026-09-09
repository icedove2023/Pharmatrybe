# Recommendation Contract v1.0.0

Status: FROZEN for `/api/v1/recommendations/generate`.

Authoritative runtime sources: `RecommendationResult`, `DecisionFusionEngine`, `RecommendationGenerator`, `ResponseFormatter`, and the recommendations API response contract.

## Recommendation object

The backend emits a recommendation object containing:

- `patient_id`
- `primary_recommendation`: antibiotic name, reason, guideline category, ranking, confidence, alternative flag, warnings, and optional dosage/duration notes
- `alternative_recommendations`: same recommendation item shape
- `clinical_rules`: serialized rule results
- `guideline_references`: serialized guideline references
- `stewardship_findings`: serialized stewardship findings
- `warnings`
- `clinical_rationale`
- `confidence`
- `supporting_evidence`
- `generated_at`
- `version`

The recommendation is derived from prediction-plugin probabilities after clinical rule filtering. The pipeline does not invent candidate antibiotics; candidates must originate from prediction outputs.

## API envelope

The canonical recommendation API response also exposes `status`, `patient_id`, `recommendation`, `confidence`, `evidence_ranking`, `evidence_attribution`, `recommendation_trace`, `audit_reference`, `explanation`, `generated_at`, and `trace_id`.

`recommendation_id` is present in evidence/audit structures. It is not a field of `RecommendationResult` itself.

No dosage, prescribing authorization, or autonomous treatment decision is implied. Missing plugin evidence produces an error response rather than a fabricated recommendation.

## Compatibility boundary

`/api/v1/recommendations/generate` is the canonical public recommendation endpoint and returns `ExplainabilityResponseContract`. Legacy recommendation routes remain compatibility paths and are not the canonical frontend boundary. Unresolved plugin-specific mappings are not exposed as universal fields.
