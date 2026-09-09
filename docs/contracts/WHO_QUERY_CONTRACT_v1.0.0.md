# WHO Query Contract v1.0.0

Status: FROZEN for the configured WHO knowledge-query boundary.

## Query kinds

WHO is a knowledge-query plugin, not a prediction plugin.

`SearchQuery` requires non-empty `query_text` and may include `entity_type`.

`KnowledgeQuery` carries `entity_type` and optional `identifier` for supported retrieval paths. The provider/router maps entity types to capabilities such as guidelines, recommendations, monitoring, pathogens, evidence, stewardship, follow-up, and referral.

## Runtime path

`WHOKnowledgePlugin` uses the configured WHO database session, constructs `WHOKnowledgeRepository` and `WHOProvider`, and executes through the knowledge router/orchestrator. The repository is read-only and raises repository/service errors for unsupported operations or database failures.

## Supported retrieval evidence

The repository implements disease search/listing, disease and drug lookup, recommendation retrieval, evidence, diagnostics, monitoring, follow-up, referral, stewardship, pathogens, and complete guideline loading. Provider-supported output is structured knowledge, not a clinical prediction.

## Failure behavior

Empty search returns no results; disconnected plugin search raises `ConnectionError`; missing WHO database configuration raises a clear runtime error; provider failures are represented as failed provider results or service errors at the calling boundary.

## Boundary decision

Only the executed `SearchQuery` and `KnowledgeQuery` fields documented above are public contract fields. Unsupported generic refinements are not required. WHO database configuration is platform-owned and missing configuration fails clearly.
