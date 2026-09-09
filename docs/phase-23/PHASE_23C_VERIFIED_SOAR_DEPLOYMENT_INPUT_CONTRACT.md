# Phase 23C - Verified SOAR Deployment Input Contract

The registry is implemented in `src/plugins/contracts/soarDeploymentContract.ts` and exported through `src/plugins/contracts/index.ts`.

It contains exactly 10 deployment contracts. Each contract stores deployment ID, authoritative organism/antimicrobial identity, required raw fields, per-deployment Country enum values, artifact references, and contract version `23.0.0`.

Common verified inputs are `Age`, `YearCollected`, `Region`, `BodyLocation_Group`, and `Country`. `Beta_Lactamase_enc` is deployment-specific to the eight H. influenzae deployments. No optional inputs are currently evidenced.

Contracts containing `Beta_Lactamase_enc` are registered as `unsupported` because the inspected passthrough artifact does not define the clinical-to-0/1 mapping. The two Streptococcus pneumoniae contracts are `approved` at the schema level. Approval does not create clinical values or bypass exact deployment routing.
