# ARMD Runtime Contract v1.0.0

Status: FROZEN for the existing WP4 runtime boundary.

ARMD is an artifact prediction plugin. Its runtime accepts a payload, filters to the WP4 `FEATURE_WHITELIST`, performs the existing cleaning/imputation and age-group encoding, aligns to the package feature order, scales, and predicts.

## Ownership boundary

- Raw whitelist keys are plugin runtime inputs.
- `age_group`, `age_group_*`, `log_days_since_abx`, aligned vectors, and model feature columns are derived or model-internal.
- High-level aliases such as `prior_antibiotics`, `recent_hospitalization`, `organism`, and `infection_site` are not claimed as deterministic transformations unless the WP4 runtime explicitly proves them.
- Explainability and risk-profile fields are ARMD-specific extensions.

## Failure behavior

Missing runtime context, missing adapter, invalid payload, preprocessing failure, or model failure rejects execution through the plugin/workflow failure boundary. No model artifact or preprocessing behavior is changed by this contract.

## Boundary decision

Raw whitelist ownership is explicit to the ARMD caller/platform boundary. Cross-plugin canonical mappings remain unsupported and are not required by this frozen ARMD runtime contract.
