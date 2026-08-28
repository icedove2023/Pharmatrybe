# PharmaTrybe Configuration Management

## Purpose

This document defines the centralized configuration strategy for the PharmaTrybe backend.
The purpose is to keep environment settings consistent, reusable, and available to the FastAPI application and future service clients.

## Environment Strategy

Configuration is loaded from environment variables through Pydantic Settings.
The backend uses a single Settings object that is shared across the application.

This keeps configuration:

- centralized
- explicit
- easy to document
- suitable for local development and deployment

## Configuration Hierarchy

Configuration values are organized into the following areas:

- Application metadata: name, version, environment, debug
- API runtime: prefix, log level
- Timeout and retry defaults
- Service endpoints for future integrations
- Feature flags for middleware and runtime options
- Placeholder authentication values
- Invitation delivery: `INVITATION_HANDOFF_ENCRYPTION_KEY` and `INVITATION_FRONTEND_ROUTE`

## Feature Flags

The settings model includes feature flags for:

- CORS
- trusted host middleware
- request logging
- security headers

These flags are placeholders for future runtime toggling and remain non-invasive in this phase.

## Deployment

Configuration should be supplied through environment variables in deployment environments.
Developers should define expected values in their local environment without committing secrets.

## Security

Configuration management follows these rules:

- do not commit secrets
- keep placeholder values in example files only
- use environment variables for deployment-specific values
- avoid hardcoding sensitive values in source code

## Invitation Delivery Configuration

The invitation outbox requires deployment-provided values:

- `INVITATION_HANDOFF_ENCRYPTION_KEY`: a valid Fernet key used to encrypt temporary invitation-token handoff material. Never commit this value.
- `INVITATION_FRONTEND_ROUTE`: the approved frontend invitation route used by the delivery worker to construct links. This is configuration, not authorization authority.

Development may leave these values empty until invitation delivery is exercised. Staging and production configuration validation requires both values; the encryption key must be supplied by the deployment secret manager.
