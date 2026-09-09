# Phase 25-26 Open Limitations

- Do not classify SOAR as ready until each of the ten deployments has an independently recorded model-load, feature-alignment, prediction, output-decoding, threshold, and semantic-output result.
- SOAR artifact registry evidence reports package grade C and integrity 62.5; this remains a readiness limitation.
- ARMD model metadata and preprocessing output disagree on `Amoxicillin/Clavulanic Acid`; the correct authoritative mapping is unresolved.
- WHO database connectivity and authenticated result rendering were not verified in a live browser session.
- Full backend pytest is not green because three identity tests use a non-UUID Supabase fixture ID and receive HTTP 404 validation errors.
- TypeScript lint remains blocked by six pre-existing React Start/router errors.
- No real patient data or production credentials were used. Synthetic fixtures in tests are technical fixtures only.
- Fusion, explainability, and audit contracts exist in the repository, but a credentialed full workflow trace was not confirmed in this phase.
