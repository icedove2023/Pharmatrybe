# PharmaTrybe API Response Standard

## Purpose

This document defines the official response envelope for all PharmaTrybe services.
It ensures that every endpoint, service, and future integration returns a consistent,
auditable, and machine-readable payload.

## Design Goals

The response standard is designed to:

- provide a single response contract across the platform
- keep success and failure handling consistent
- support traceability through request identifiers and timestamps
- enable future middleware and observability integration
- preserve modular boundaries between backend, AI services, and knowledge services

## Standard Success Format

```json
{
  "success": true,
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-08-01T14:00:00Z",
    "api_version": "v1",
    "processing_time_ms": 12.4
  },
  "data": {
    "status": "healthy"
  }
}
```

## Standard Failure Format

```json
{
  "success": false,
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-08-01T14:00:00Z",
    "api_version": "v1",
    "processing_time_ms": 3.1
  },
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "The requested service is unavailable.",
    "details": {}
  }
}
```

## Metadata Definitions

The metadata object is required for every response.

- request_id: Correlation identifier for the request or transaction
- timestamp: UTC response timestamp
- api_version: Version of the PharmaTrybe API contract
- processing_time_ms: Processing duration in milliseconds

## Error Code Philosophy

Error codes should be:

- stable and machine-readable
- short enough to be used consistently across services
- descriptive enough to support diagnostics and monitoring

Examples include:

- INVALID_REQUEST
- SERVICE_UNAVAILABLE
- TIMEOUT
- NOT_FOUND
- INTERNAL_ERROR

## Examples

### Success example

```json
{
  "success": true,
  "metadata": {
    "request_id": "req-001",
    "timestamp": "2026-08-01T14:00:00Z",
    "api_version": "v1",
    "processing_time_ms": 8.7
  },
  "data": {
    "platform": "PharmaTrybe",
    "version": "0.1.0"
  }
}
```

### Failure example

```json
{
  "success": false,
  "metadata": {
    "request_id": "req-002",
    "timestamp": "2026-08-01T14:00:00Z",
    "api_version": "v1",
    "processing_time_ms": 2.3
  },
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request payload is invalid.",
    "details": {
      "field": "request_id"
    }
  }
}
```

## Guidelines for Future Services

All PharmaTrybe services should follow these rules:

- Use the same top-level success and failure envelope.
- Always include metadata.
- Prefer explicit error codes over free-form error strings.
- Keep payloads structured and auditable.
- Do not bypass this standard for internal or external services.

## Scope

This standard applies to:

- FastAPI Backend
- SOAR/GSK
- ARMD
- WHO Knowledge Engine
- Clinical Decision Engine
- Explainability Engine
- Authentication services
- Any future PharmaTrybe service
