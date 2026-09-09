# Phase 22 ARMD Approved Input Contract

## Decision

`ARMD_STATUS = PARTIALLY_APPROVED`.

The repository supports a narrow contract for direct-identity clinical values that are defined in the official Clinical Case Schema and accepted by the frozen ARMD runtime without frontend semantic translation.

## Admitted fields

- `age`: integer, 0-120; canonical patient age.
- `temperature`: non-negative number; canonical recorded temperature.
- `creatinine`: non-negative number; canonical laboratory measurement.
- `bun`: non-negative number; canonical laboratory measurement.
- `wbc`: non-negative number; canonical laboratory measurement.
- `neutrophils`: non-negative number; canonical laboratory measurement.
- `lymphocytes`: non-negative number; canonical laboratory measurement.
- `lactate`: non-negative number; canonical laboratory measurement.
- `procalcitonin`: non-negative number; canonical laboratory measurement.

All fields are optional at runtime except `age`; backend imputation remains authoritative for omitted optional values and is not recreated in the frontend.

## Excluded fields

`age_group`, `log_days_since_abx`, encoded columns, feature vectors, `adi_score`, `adi_state_rank`, care-setting flags, device flags, history aliases, `weight`, `egfr`, and model metadata are not admitted. They require derivation, renamed semantic mapping, unresolved ownership, or backend preprocessing.

The contract does not claim that a partial input set is clinically sufficient for every use. The UI must make missing values visible and the backend remains authoritative.
