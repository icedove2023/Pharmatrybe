# PharmaTrybe Authentication Architecture

## Purpose

This document defines the backend authentication foundation for future PharmaTrybe API protection.
The implementation is intentionally limited to infrastructure and verification scaffolding.
No login, registration, refresh, OAuth, or frontend authentication flows are implemented here.

## Supabase Auth Integration

The backend authentication layer is designed to be compatible with Supabase Auth-issued JWTs.
It expects bearer tokens in the standard Authorization header and provides a reusable verification layer for future protected routes.

## JWT Flow

1. A client presents an access token in the Authorization header.
2. The backend parses the JWT structure and validates its expiry.
3. The backend extracts standard claims such as subject, email, role, and activity state.
4. The request context is enriched with a lightweight authenticated user schema.
5. Future protected endpoints can require a role-based dependency.

## Role-Based Access Control

The authentication package defines the official PharmaTrybe roles:

- Clinician
- Laboratory Scientist
- Stewardship Team
- Administrator

These roles are exposed through reusable dependencies so future endpoints can enforce access in a consistent way.

## Dependency Injection

The authentication package uses FastAPI dependency injection to keep route handlers independent from token parsing details.
Reusable dependencies include:

- get_current_user
- require_clinician
- require_admin
- require_steward
- require_lab_scientist

This keeps the API surface consistent while preserving modular boundaries.

## Protected Endpoints

Protected endpoints should depend on the authentication helpers rather than embedding token logic directly in route handlers.
That allows the backend to remain auditable and easy to extend as future authentication requirements evolve.

## Future Frontend Authentication

The backend remains framework-independent from frontend implementation.
The authentication scaffold is designed to support future web or mobile clients that present bearer tokens to the API.
No frontend-specific authentication behavior is implemented here.
