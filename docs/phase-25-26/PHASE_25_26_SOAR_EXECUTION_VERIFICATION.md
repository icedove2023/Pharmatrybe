# Phase 25-26 SOAR Execution Verification

## Contract and routing
- Ten exact deployment contracts are registered by `src/plugins/contracts/soarDeploymentContract.ts`.
- Unknown deployment IDs fail closed.
- Routing metadata is kept outside the clinical payload.
- Focused command: `.\\.venv\\Scripts\\python.exe -m pytest -q apps/api/tests/test_soar_deployment_contract.py apps/api/tests/test_soar_artifact_registry.py`
- Result: `12 passed`.

## Beta-lactamase boundary
- Archive evidence recorded in Phase 24.5 supports `NEG -> 0` and `POS -> 1`.
- The public contract now exposes only `BetaLactamaseStatus` with `POSITIVE|NEGATIVE`.
- Numeric `Beta_Lactamase_enc` clinician input remains rejected.
- Frontend command: `npm test`
- Result: `207 assertions passed`.

## Runtime evidence
The backend `PredictionEngine` performs preprocessing, estimator inference, probability extraction, threshold extraction/application, and label decoding. However, this phase did not complete a separate successful prediction execution and output-semantics verification for all ten deployments.

## Status
`PARTIAL`.

Blocking evidence gap: the deployment registry reports package grade C and integrity 62.5, and a complete ten-deployment execution matrix with independently verified output semantics was not produced. No deployment is promoted to clinical readiness solely from model load or HTTP behavior.
