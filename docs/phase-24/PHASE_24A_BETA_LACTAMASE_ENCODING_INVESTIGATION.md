# Phase 24A - Beta-Lactamase Encoding Investigation

## Decision
`NO_AUTHORITATIVE_MAPPING_FOUND`.

## Search locations inspected
- `deployments/SOAR_GSK/**` runtime models, metadata, feature schemas, preprocessing summaries, README files, verification reports, training/evaluation outputs, CSV exports, and serialized artifact companions.
- `apps/api/app/plugins/prediction/soar/**` runtime scanner, loader, engine, registry, and plugin routing.
- `apps/api/tests/**` SOAR tests.
- `src/plugins/contracts/**`, assessment workflow, plugin registry, and Phase 23 tests.
- `docs/**`, including Phase 20-23 reports and SOAR runtime/input ownership reports.

## Evidence found
The authoritative feature schema identifies `Beta_Lactamase_enc` as a numeric passthrough/bin feature. Direct artifact inspection documented in Phase 22B shows a `FunctionTransformer` identity path and no encoder vocabulary. Repository reports explicitly state that no laboratory producer or deterministic clinical transform exists.

The inspected README/metadata/verification/SHAP files show the feature name, passthrough behavior, or importance only. None establishes whether positive or negative beta-lactamase status maps to `0` or `1`.

## Mapping source/version
No mapping source or mapping version exists in repository evidence. Artifact/model versions do not solve the semantic polarity question.

## Clinical mapping
No safe mapping can be implemented:

- Positive -> unknown numeric value
- Negative -> unknown numeric value

Confidence: insufficient for clinical execution.

## Final safety decision
The eight H. influenzae deployments remain `BLOCKED_BY_UNVERIFIED_ENCODING`. No Yes/No frontend field is exposed, no numeric default is accepted, and direct callers cannot bypass the resolver block.
