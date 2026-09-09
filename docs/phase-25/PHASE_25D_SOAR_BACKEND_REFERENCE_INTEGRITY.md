# Phase 25D: SOAR Backend Reference Integrity

`SOARModelLoader` exists at `app/knowledge/providers/soar/soar_model_loader.py` and is exported by `app.knowledge.providers.soar`. `SOARProvider.__init__` referenced it in an annotation without importing it, producing the sole non-ORM F821.

The fix imports the existing `SOARModelLoader` directly into `soar_provider.py`. No loader was created, renamed, or replaced. Focused SOAR deployment and artifact-registry tests completed with **12 passed**.

The Phase 22-24.5 SOAR architecture was not changed: deployment selection, metadata identity, fail-closed unknown deployment behavior, artifact contracts, and deterministic beta-lactamase mapping remain outside this fix.
