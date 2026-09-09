# Phase 24D - SOAR Assessment Workflow Integration

The integration point is the existing `AssessmentWizard` step 2 through `PluginGeneratedForm`.

Flow:

1. The selected SOAR plugin is detected from the registered plugin list.
2. `SoarClinicalCompletionForm` offers only exact verified deployment IDs and displays verified organism/antimicrobial metadata.
3. The Phase 23 resolver checks exact canonical keys, then controlled clinician values.
4. Missing inputs remain visible to the completion form; unresolved beta-lactamase deployments show a truthful blocked state.
5. `buildSoarExecutionPayload` validates the exact contract and returns separate `routing_context.deployment_id` and `input_payload`.
6. The existing server pipeline action uses that payload and refuses execution if SOAR completion has not occurred.

Legacy `pathogen` and `culture` fields remain outside the SOAR model payload. No organism or antimicrobial inference is performed from them.
