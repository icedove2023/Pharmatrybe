# Phase 25-26 ARMD Execution Verification

## Verified
- ARMD clinical contract admits direct clinical fields only and excludes derived/model-internal vectors.
- ARMD plugin initialization, validation, registry discovery, and plugin prediction tests execute against the local WP4 artifacts.
- Focused command: `.\\.venv\\Scripts\\python.exe -m pytest -q apps/api/app/plugins/prediction/armd/tests/test_armd_plugin.py packages/prediction-framework/tests/test_armd_adapter.py`
- Result: `30 tests collected; 29 passed, 1 failed`.

## Failure
`test_preprocessing_parity_with_wp4` reports that model metadata requires `Amoxicillin/Clavulanic Acid`, while `preprocess_patient_features` returns the clinical/transformed frame without that model-specific column. The existing prediction path uses `build_feature_frame` to align model features; the mismatch is not resolved by guessing a clinical mapping.

## Status
`PARTIAL`.

Blocking evidence gap: authoritative alignment between the ARMD model package feature list and WP3/WP4 preprocessing output must be established and tested before ARMD can be classified ready.
