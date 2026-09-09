# Phase 20 Approved Plugin Input Contracts Final Report

## Executive summary

Phase 20A established that SOAR and ARMD runtime fields do not have sufficient frontend ownership/provenance authority. WHO has one narrowly verified public query field: `SearchQuery.query_text`.

## Contract decisions

- `soar@...`: no approved frontend contract.
- `armd@...`: no approved frontend contract.
- WHO SearchQuery: partial approval limited to `query_text`; KnowledgeQuery and `entity_type` remain unsupported.

## Frozen backend boundary

No backend routes, request models, plugin adapters, routing behavior, preprocessing, recommendation, or explainability contracts are changed.

## Migrated frontend workflows

The WHO knowledge search control now resolves `who_knowledge@1.0.0` through the Phase 19 registry, renders `query_text` through the generic form engine, validates the value, and submits through the existing authenticated WHO API client.

## Migration and limitations

SOAR and ARMD remain intentionally unavailable for dynamic forms. WHO `KnowledgeQuery`, `entity_type`, filters, pagination, sorting, and extra metadata remain blocked because their public frontend authority is not established.

## Verification

- Frontend tests: **166 assertions passed**.
- Frontend build: **PASS** (`npm run build`).
- Frontend lint/typecheck: **BLOCKED_BY_PRE_EXISTING_ERROR**. Six errors remain in the existing TanStack Router/Start files: `src/router.tsx`, `src/routes/__root.tsx`, `src/server.ts`, and `src/start.ts`.
- Backend regression: **281 passed, 7 warnings**.
- `git diff --check`: **PASS**.
- Frontend safety search: no model-feature inspection, deployment inference, semantic mapping, or arbitrary registry-schema rendering found.

The current worktree contains unrelated pre-existing changes under `apps/api/**`; Phase 20 did not modify backend files.
