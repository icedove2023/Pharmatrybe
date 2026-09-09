# Audit and Logging Architecture

## Logging Philosophy

PharmaTrybe uses structured logging to ensure that every request and audit event is traceable, machine-readable, and compatible with future SIEM or log aggregation systems.

- Use Python logging with structured key/value fields.
- Log levels supported: `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.
- Core logging configuration is driven from runtime settings.
- Logs are intentionally kept lightweight and portable so that ELK/OpenSearch/Datadog can replace the stream handler later.

## Request Lifecycle

1. Incoming request enters the FastAPI middleware chain.
2. `RequestContextMiddleware` generates a `request_id`, attaches metadata to `request.state`, and exposes `X-Request-ID`.
3. `TimingMiddleware` measures request duration and exposes `X-Process-Time`.
4. `LoggingMiddleware` writes a structured request completion log when the response is returned.
5. An audit hook is available after the request is processed, enabling correlation between request logs and audit events.

## Audit Lifecycle

- Audit events are created through a reusable `AuditService`.
- `AuditLog` is a Pydantic model, not a database entity.
- The service emits structured audit event logs without performing persistence.
- Audit events can be used by any component in the backend, including request middleware, service orchestration, and error handling.

## Event Types

The audit infrastructure supports a broad set of reusable actions, including:

- `CLINICAL_CASE_CREATED`
- `CLINICAL_CASE_UPDATED`
- `CLINICAL_CASE_DELETED`
- `RECOMMENDATION_GENERATED`
- `WHO_QUERY`
- `SOAR_INVOCATION`
- `ARMD_INVOCATION`
- `DECISION_ENGINE_INVOCATION`
- `EXPLAINABILITY_INVOCATION`
- `LOGIN`
- `LOGOUT`
- `FAILED_AUTHORIZATION`
- `VALIDATION_ERROR`
- `INTERNAL_SERVER_ERROR`

Audit events are intentionally generic so additional event actions can be added without changing the service API.

## Correlation IDs

- Every request receives a `request_id` from the request context middleware.
- `request_id` is propagated into request logs and audit events.
- This correlation ID provides a single trace across request lifecycle, errors, and service activity.

## Clinical Governance

- The audit layer is infrastructure-only and does not make clinical decisions.
- Audit events are designed to support auditability, traceability, and governance requirements.
- No clinical content, business rules, or recommendation logic is embedded in this layer.

## Future SIEM Integration

- The logging formatter is intentionally simple and structured.
- Replacing the stream handler with an ELK/OpenSearch/Datadog exporter requires only modifying the logging configuration.
- Audit events are already modeled as structured metadata, enabling direct ingestion by SIEM systems.

## Future Database Persistence

- `AuditLog` is a reusable interface model only.
- Persistence is deliberately excluded from the current implementation.
- Future persistence can be added by implementing a repository or database adapter without changing the audit service API.
