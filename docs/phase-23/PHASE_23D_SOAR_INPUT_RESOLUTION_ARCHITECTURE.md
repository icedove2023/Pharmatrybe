# Phase 23D - SOAR Input Resolution Architecture

`resolveSoarInputs()` first resolves the explicit deployment ID against the verified registry. It then checks each contract field using an exact key from canonical data or clinician-entered data, records the source, and returns `missingRequiredInputs` plus `isComplete`.

`buildSoarExecutionPayload()` refuses incomplete resolutions and keeps `routing_context.deployment_id` separate from `input_payload`. Unknown deployment IDs raise `PluginContractError`; no fallback, similarity, or first-deployment selection exists.

The resolver does not perform model preprocessing, categorical encoding, semantic mapping, or defaulting. Those remain backend/model responsibilities where verified. Unsupported beta-lactamase mapping is reported as `UNSUPPORTED_MAPPING` rather than defaulted.
