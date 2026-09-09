# Phase 20D WHO Query Contract Decision

## Decision

**WHO_QUERY_CONTRACT_PARTIALLY_APPROVED**

`WHO_DYNAMIC_FORM = PARTIAL`.

## Approved query surface

Only the exact `SearchQuery.query_text` field is approved for a frontend query form. It maps directly to the existing authenticated `GET /who/search?q=...` route and is knowledge retrieval input, not predictive clinical input.

The contract does not approve `entity_type` because the public route does not accept it. `KnowledgeQuery`, `identifier`, generic filters, pagination, sorting, and extra metadata remain unsupported for dynamic frontend use until their public execution and ownership are formally established.

## Provenance

- Owner: WHO knowledge plugin.
- Source artifacts: the WHO plugin input schema and the public WHO API route.
- Runtime version: frozen plugin runtime contract v1.0.0.
- Approval authority: Phase 20D governance decision recorded in this document.

## Safety boundary

The WHO query form remains retrieval-oriented. It must not construct prediction payloads, infer antimicrobial concepts, or merge WHO query fields with SOAR or ARMD inputs.

## Implementation outcome

A minimal approved WHO search contract may be registered and used with the existing authenticated WHO API client. No KnowledgeQuery or predictive WHO contract is created.
