# Phase 19 Schema-Driven Plugin UI Architecture

## Status

Implemented generic architecture. Plugin-specific clinical migration remains fail-closed until an approved frontend-visible contract exists.

## Boundary

The frontend distinguishes plugin input contracts from UI presentation and model features. Only an approved, versioned contract with provenance can reach the dynamic form renderer. Model metadata, feature names, artifact names, and registry telemetry are never form sources.

## Flow

```text
Approved plugin contract
  -> deterministic registry resolution
  -> contract validation
  -> generic form renderer
  -> form value validation
  -> plugin adapter
  -> canonical synchronous pipeline request
```

The renderer does not construct clinical meaning or routing. Adapters own plugin-specific payload boundaries. `routing_context` remains separate from `input_payload`.

## Registry and lifecycle

Contracts are registered by explicit `pluginId` and semantic `contractVersion`. Registration validates approval metadata, provenance, supported schema keywords, UI references, and synchronous execution support. Duplicate registrations, unknown contracts, deprecated versions, and unapproved contracts fail closed.

A future production contract must identify its owner, source artifact, artifact version, approving authority, approval time, schema version, and plugin identity. The frontend does not fabricate provenance.

## Current plugin boundaries

- SOAR has no frontend-visible approved input contract. Its exact deployment ID is routing metadata and is never inferred or rendered as a clinical field.
- ARMD has no approved frontend-visible input contract. WP4 features and derived preprocessing fields remain outside the form engine.
- WHO remains a knowledge/retrieval boundary. Its existing explorer is retained; no production query form is invented without an approved query contract.

## Authentication and API

Forms use the existing authenticated API client through adapters and the canonical `/pipeline/execute` path. No second fetch wrapper, token manager, Supabase client, or plugin prediction endpoint is introduced.

## Migration

Legacy static registry schemas and metadata input schemas are compatibility artifacts only. They are not treated as contracts. Existing assessment and retrieval workflows remain available, while plugin-specific dynamic forms stay unavailable until contract ownership and provenance are approved.
