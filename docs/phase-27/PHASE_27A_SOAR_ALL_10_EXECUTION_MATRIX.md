# Phase 27A SOAR All-10 Execution Matrix

Runtime root used: `deployments/SOAR_GSK/SOAR_GSK/deployment`. Fixtures are labelled `SYNTHETIC_TEST_DATA`; no clinical truth is inferred.

Command: `.\\.venv\\Scripts\\python.exe -m pytest -q apps/api/tests/test_phase27_soar_execution.py`
Result: **12 passed**. The ten deployment cases and both beta-lactamase status cases executed real model artifacts.

| Deployment | Contract | Input resolution | Artifact load | Model execution | Output normalization | Result |
|---|---|---|---|---|---|---|
| Cefixime_Haemophilus_influenzae | PASS, 6 features | PASS, exact ID and evidence-backed values | PASS | PASS | PASS, R with probability/threshold | READY_FOR_CONTROLLED_EXECUTION |
| Cefotaxime_Haemophilus_influenzae | PASS, 6 features | PASS | PASS | PASS | PASS, R with probability/threshold | READY_FOR_CONTROLLED_EXECUTION |
| Cefpodoxime_Haemophilus_influenzae | PASS, 6 features | PASS | PASS | PASS | PASS, R with probability/threshold | READY_FOR_CONTROLLED_EXECUTION |
| Ceftibuten_Haemophilus_influenzae | PASS, 6 features | PASS | PASS | PASS | PASS, R with probability/threshold | READY_FOR_CONTROLLED_EXECUTION |
| Ceftriaxone_Haemophilus_influenzae | PASS, 6 features | PASS | PASS | PASS | PASS, R with probability/threshold | READY_FOR_CONTROLLED_EXECUTION |
| Doxycycline_Streptococcus_pneumoniae | PASS, 5 features | PASS | PASS | PASS | PASS, R with probability/threshold | READY_FOR_CONTROLLED_EXECUTION |
| Levofloxacin_Haemophilus_influenzae | PASS, 6 features | PASS | PASS | PASS | PASS, R with probability/threshold | READY_FOR_CONTROLLED_EXECUTION |
| Tetracycline_Haemophilus_influenzae | PASS, 6 features | PASS after SBOM dependency closure | PASS | PASS | PASS, R with probability/threshold | READY_FOR_CONTROLLED_EXECUTION |
| Tetracycline_Streptococcus_pneumoniae | PASS, 5 features | PASS | PASS | PASS | PASS, R with probability/threshold | READY_FOR_CONTROLLED_EXECUTION |
| Trimethoprim_Sulfa_Haemophilus_influenzae | PASS, 6 features | PASS | PASS | PASS | PASS, R with probability/threshold | READY_FOR_CONTROLLED_EXECUTION |

## Beta-lactamase execution
`Ceftriaxone_Haemophilus_influenzae` executed twice with internal values `0` and `1`; both cases returned a valid `S/I/R` output. The clinician-facing mapping remains `NEGATIVE -> 0` and `POSITIVE -> 1`; raw numeric input is not accepted at the frontend resolver boundary.

## Failure trace and remediation
The first active run failed only at `Tetracycline_Haemophilus_influenzae` artifact deserialization with `ModuleNotFoundError: imblearn`. The deployment SBOM declared `imbalanced-learn 0.14.2`; that exact dependency was added to `apps/api/requirements.txt` and installed in `.venv`. The rerun passed.

Recovery-only outer artifacts with unrecoverable thresholds were not used as the active runtime root.
