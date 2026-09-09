# Phase 27G End-to-End Synthetic Cases

All fixtures are technical `SYNTHETIC_TEST_DATA`; no real patient data or production credentials were used.

| Case | Path | Result |
|---|---|---|
| A WHO | WHO provider/plugin focused execution and structured result tests; no complete WHO-to-fusion runtime trace | PARTIAL |
| B SOAR Streptococcus | Exact Doxycycline deployment -> real model -> fusion -> explanation -> audit event | READY_FOR_CONTROLLED_EXECUTION |
| C SOAR H. influenzae | Exact Ceftriaxone deployment; beta values 0 and 1 -> real model execution | READY_FOR_CONTROLLED_EXECUTION |
| D ARMD | WP4 adapter and all 20 registry models -> preprocessing -> final frame -> prediction; explainability tests, but no complete ARMD-to-fusion runtime trace | PARTIAL |
| E Missing evidence | Existing resolver and contract tests reject missing/unknown/invalid input without fallback | READY_FOR_CONTROLLED_EXECUTION |

## Measured commands
- SOAR cases: 12 passed.
- ARMD plugin/adapter: 31 passed.
- WHO/fusion/explainability/plugin integration: 80 passed.
- Audit tests: 15 passed.
- Direct ARMD registry run: 20 models, 20 success results.

The authenticated browser path was not claimed because manual login is required. Only Case B was exercised as a complete plugin -> fusion -> explanation -> audit runtime trace in this phase.
