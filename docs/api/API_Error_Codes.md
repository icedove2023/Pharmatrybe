# API Error Codes

**Document:** API_Error_Codes.md

**Project:** PharmaTrybe

**Version:** 1.0

**Status:** Official Standard

**Last Updated:** August 2026

---

# Purpose

This document defines the official error codes used throughout the PharmaTrybe platform.

Every backend service must return standardized error codes when an operation fails.

This ensures:

- Consistent API behaviour
- Easier frontend handling
- Better audit logging
- Predictable debugging
- Uniform clinician experience

Error codes are stable contracts and must not be changed without architectural review.

---

# Standard Error Response

All errors must follow the PharmaTrybe API Response Standard.

```json
{
  "success": false,
  "metadata": {
    "request_id": "2b6f1b4e-76e1-4fd6-a88e-5d7ef4b5f7c1",
    "timestamp": "2026-08-01T12:15:03Z",
    "api_version": "v1",
    "processing_time_ms": 24.8
  },
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "WHO Knowledge Engine is currently unavailable.",
    "details": {}
  }
}
```

---

# Error Categories

PharmaTrybe classifies errors into the following groups:

- Client Errors
- Authentication Errors
- Authorization Errors
- Validation Errors
- AI Service Errors
- Knowledge Base Errors
- Decision Engine Errors
- Explainability Errors
- Database Errors
- Infrastructure Errors
- Internal Errors

---

# Standard Error Codes

## Client Errors

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| INVALID_REQUEST | 400 | Request payload is malformed or incomplete. |
| INVALID_PARAMETER | 400 | One or more parameters are invalid. |
| UNSUPPORTED_OPERATION | 400 | Requested operation is not supported. |

---

## Authentication

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| UNAUTHORIZED | 401 | Authentication required. |
| INVALID_TOKEN | 401 | Access token is invalid or expired. |
| TOKEN_EXPIRED | 401 | Authentication token has expired. |

---

## Authorization

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| FORBIDDEN | 403 | User does not have permission. |
| ROLE_NOT_ALLOWED | 403 | User role cannot perform this action. |

---

## Resource Errors

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| NOT_FOUND | 404 | Requested resource does not exist. |
| RESOURCE_ALREADY_EXISTS | 409 | Resource already exists. |

---

## Validation

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| VALIDATION_ERROR | 422 | Request failed schema validation. |
| INVALID_CLINICAL_CASE | 422 | Clinical case does not satisfy required structure. |
| INVALID_SCHEMA | 422 | Internal schema validation failed. |

---

# AI Service Errors

## SOAR/GSK

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| SOAR_SERVICE_UNAVAILABLE | 503 | SOAR service unavailable. |
| SOAR_TIMEOUT | 504 | SOAR service timed out. |
| SOAR_INVALID_RESPONSE | 502 | Invalid response from SOAR model. |

---

## ARMD

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| ARMD_SERVICE_UNAVAILABLE | 503 | ARMD service unavailable. |
| ARMD_TIMEOUT | 504 | ARMD service timed out. |
| ARMD_INVALID_RESPONSE | 502 | Invalid ARMD prediction response. |

---

# WHO Knowledge Engine

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| WHO_ENGINE_UNAVAILABLE | 503 | WHO Knowledge Engine unavailable. |
| WHO_GUIDELINE_NOT_FOUND | 404 | Guideline not found. |
| WHO_LOOKUP_FAILED | 500 | Knowledge lookup failed. |

---

# Clinical Decision Engine

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| DECISION_ENGINE_ERROR | 500 | Decision Engine failed. |
| DECISION_GENERATION_FAILED | 500 | Unable to generate recommendation. |
| DECISION_CONFLICT | 409 | Conflicting clinical rules detected. |

---

# Explainability Engine

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| EXPLAINABILITY_ERROR | 500 | Explainability Engine failed. |
| EXPLANATION_NOT_AVAILABLE | 500 | Explanation could not be generated. |

---

# Database Errors

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| DATABASE_ERROR | 500 | Database operation failed. |
| DATABASE_CONNECTION_FAILED | 503 | Database unavailable. |
| QUERY_FAILED | 500 | Query execution failed. |

---

# Infrastructure Errors

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| SERVICE_UNAVAILABLE | 503 | Requested service unavailable. |
| REQUEST_TIMEOUT | 504 | Upstream request timed out. |
| NETWORK_ERROR | 503 | Network communication failed. |

---

# Internal Errors

| Error Code | HTTP Status | Description |
|------------|------------:|-------------|
| INTERNAL_SERVER_ERROR | 500 | Unexpected server error. |
| UNKNOWN_ERROR | 500 | Unknown system error. |

---

# Error Handling Principles

Every PharmaTrybe service must:

- Return only documented error codes.
- Never expose stack traces.
- Never expose database credentials.
- Never expose API keys.
- Never expose model internals.
- Always include a request identifier.
- Always include a timestamp.
- Always return a human-readable message.
- Optionally include structured details for debugging.

---

# Frontend Behaviour

The Next.js frontend should display clinician-friendly messages while preserving the original error code for logs.

Example:

Displayed:

> WHO guidance is temporarily unavailable. Please try again later.

Logged:

```
WHO_ENGINE_UNAVAILABLE
```

---

# Logging Requirements

Every error must be logged with:

- Request ID
- User ID (if authenticated)
- Timestamp
- Endpoint
- HTTP Status
- Error Code
- Processing Time

---

# Future Extension

Additional AI modules (e.g., Sepsis AI, UTI AI, Tuberculosis AI) must define their own service-specific error codes while conforming to this standard.

---

# Approval

This document defines the official PharmaTrybe API Error Code Standard.

All backend services, middleware, AI services, and frontend clients must conform to this specification.