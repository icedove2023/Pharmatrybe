# Phase 23E - Controlled SOAR Input Completion Form

The controlled workflow is:

1. Resolve explicit deployment ID.
2. Load that deployment's verified contract.
3. Resolve only exact canonical keys when present.
4. Render only missing required raw fields.
5. Validate values against the contract, including categorical enums.
6. Preserve clinician provenance.
7. Construct separate routing context and input payload.
8. Refuse execution if the resolution is incomplete or unsupported.

The form must show verified organism and antimicrobial identity, but must not expose model vectors, encoded values, preprocessing columns, or deployment IDs as clinical fields. H. influenzae deployments remain blocked until `Beta_Lactamase_enc` semantics are confirmed.
