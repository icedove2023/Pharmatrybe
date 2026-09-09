# Phase 28C ARMD End-to-End Acceptance

## Verified technical path
ARMD contract validation and adapter execution pass. WP4 preprocessing emits the clinical/transformed frame; `build_feature_frame` adds model-only columns; the selected model predicts. Phase 27 direct execution returned 20/20 successful registry model results, and focused ARMD plugin/adapter tests pass 31/31.

## Fusion boundary
A complete ARMD-specific plugin-to-fusion runtime trace was not executed. Fusion, rules, explainability, and audit components are separately tested, but no claim is made that all these stages were driven by the same authenticated ARMD assessment.

## Feature safety
`Amoxicillin/Clavulanic Acid` and other model-only columns remain internal final-frame features and are not clinician inputs.

## Status
`PARTIAL`: model execution is real and passing; authenticated assessment-to-fusion-to-audit acceptance remains unverified.
