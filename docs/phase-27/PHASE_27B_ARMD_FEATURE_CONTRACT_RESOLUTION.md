# Phase 27B ARMD Feature Contract Resolution

## AUTHORITATIVE FEATURE SOURCE

`deployments/ARMD/output/WP3/Registry/model_registry.json` and each loaded `ModelPackage.feature_names` are authoritative for final model features. `WP4_Decision_Engine.py` is authoritative for preprocessing and `build_feature_frame` alignment.

## EXPECTED FEATURE ORDER

The inspected first model package (`Amikacin`) declares 56 final features: 31 clinical/transformed features, 19 model-only antibiotic columns including `Amoxicillin/Clavulanic Acid`, and 6 age-group dummy columns.

## PREPROCESSOR OUTPUT

`preprocess_patient_features` returns a `(1, 37)` frame containing clinical and derived/transformed features. It intentionally does not contain the 19 antibiotic model columns.

## FINAL MODEL FRAME

`build_feature_frame(patient_df, model_package.feature_names)` adds the model-only columns and returns all 56 declared columns in model order. `Amoxicillin/Clavulanic Acid` is present in this final frame.

## MISMATCH LOCATION

The mismatch was in `packages/prediction-framework/tests/test_armd_adapter.py`, which compared the preprocessor frame directly to the final model feature list.

## ROOT CAUSE

`PARITY_TEST_INCORRECT`. The implementation boundary was correct; the test asserted the wrong intermediate stage.

## IMPLEMENTATION DECISION

The parity test was corrected to call the authoritative WP4 `build_feature_frame` before checking feature completeness and missing values. No clinical mapping, model feature, or preprocessing behavior was invented or changed.

## TEST EVIDENCE

- `\.venv\\Scripts\\python.exe -m pytest -q apps/api/app/plugins/prediction/armd/tests/test_armd_plugin.py packages/prediction-framework/tests/test_armd_adapter.py`: **31 passed**.
- Direct adapter execution across the registry: **20 models, 20 success results** using a labelled synthetic technical fixture.

## FINAL STATUS

`READY_FOR_CONTROLLED_EXECUTION` for the verified ARMD WP4 adapter/model-frame path, subject to the existing synthetic-data and clinical-validation limitations.
