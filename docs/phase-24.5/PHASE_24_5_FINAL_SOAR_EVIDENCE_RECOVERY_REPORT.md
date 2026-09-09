# Phase 24.5 - Final SOAR Evidence Recovery Report

## Final status
`PHASE 24.5 = COMPLETE`

`BETA_LACTAMASE_ENCODING = AUTHORITATIVELY_RESOLVED`

## Beta-lactamase
The archive's Phase 9 training source explicitly maps `POS` to `1` and `NEG` to `0`. Phase 10 repeats the same mapping before deployment evaluation/export. This is the authoritative source-to-model transformation for the bundled SOAR_GSK pipeline.

- Negative -> `0`
- Positive -> `1`
- Evidence: `SOAR_GSK.zip:phase9_automated_training.py:85-86` and `SOAR_GSK.zip:phase10_evaluate_and_export.py:76-77`

## Deployment readiness
All 10 deployments are now `READY` for controlled execution, subject to explicit collection of missing raw fields and exact deployment selection. The two Streptococcus deployments use five fields. The eight H. influenzae deployments use those five plus the controlled clinical beta-lactamase status mapping.

## Questions resolved
- Beta polarity and encoded values.
- Source training transformation.
- Runtime feature split across all ten deployments.
- Preprocessing ownership and pipeline order.
- Region/body-location categories.
- Deployment-specific beta requirement.
- Exact relationship between source mapping and passthrough runtime field.

## Remaining genuine gaps
- The original raw training dataset is not bundled in the archive, so raw-column frequency/cross-tab verification was not possible.
- The archive includes historical/prototype artifacts beyond the ten verified runtime deployments; they were not promoted into the active registry because they are not part of the verified deployment set.
- Full TypeScript lint remains unsuccessful because of six unrelated router/React Start errors; no Phase 24.5 contract files are implicated.
- Focused Python SOAR regression was started in `.venv`, but the terminal did not return a pytest completion summary; status is `NOT_CONFIRMED`.

## Verification results
- `npm test`: PASS; 205 assertions.
- `npm run build`: PASS; Vite production build completed with existing bundle/import warnings.
- `npm run lint`: FAIL; six unrelated errors in router/React Start files.
- `git diff --check`: PASS.
- `SOAR_GSK.zip`: inspected as read-only evidence; 1,086 archive entries.
- Python SOAR tests: NOT_CONFIRMED; no completion summary returned from the repository virtual environment command.

## Implementation changes
- Versioned `POSITIVE -> 1`, `NEGATIVE -> 0` mapping in the SOAR contract boundary.
- Controlled clinician-facing beta status field; raw numeric encoding is internal only.
- Resolver rejects direct numeric beta submissions and preserves provenance.
- Eight H. influenzae workflows are enabled by verified evidence.
- Phase 24.5 tests cover both statuses, payload construction, and numeric bypass rejection.

## Safety confirmation
- No guessed mapping.
- No arbitrary fallback.
- No folder-name identity parsing.
- No fuzzy deployment routing.
- No model-feature guessing.
- No fake clinical values.
- No raw numeric encoding exposed as clinician meaning.
- No backend contract or model changes.
- Archive scripts and notebooks were not executed.
