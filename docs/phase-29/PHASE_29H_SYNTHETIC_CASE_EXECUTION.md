# Phase 29H Synthetic Case Execution

All cases are `SYNTHETIC_TEST_DATA`.

| Case | Execution | Fusion | Explanation | Audit | Status |
|---|---|---|---|---|---|
| A Authenticated SOAR | Authenticated browser not available; real backend SOAR trace exists | Local SOAR trace passed | Local trace passed | Event construction passed; retrieval unavailable | PARTIAL |
| B ARMD complete trace | Amikacin real model, WP4 final frame, one shared trace ID | Passed with Amikacin recommendation | Passed with ARMD evidence | SUCCESS event constructed | PARTIAL: auth/SQL retrieval unverified |
| C WHO complete trace | Real WHO provider returned 3 database results | WHO-specific fusion not supported by current knowledge contract | Not claimed | SUCCESS event constructed | PARTIAL |
| D Safety conflict | Supported clinical decision test | Unsafe amoxicillin excluded under penicillin allergy | Rule explanation tested | Shared audit tests pass | READY_FOR_CONTROLLED_EXECUTION |
| E Provider failure | WHO missing database configuration test | No fabricated fallback | Controlled error | Shared failure/audit paths | READY_FOR_CONTROLLED_EXECUTION |
