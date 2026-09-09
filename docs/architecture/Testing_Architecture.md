# PharmaTrybe Backend Testing Architecture

## Testing Philosophy

PharmaTrybe backend testing is built around isolation, reproducibility, and architectural boundary validation.
Tests should verify backend contracts without depending on live databases, external services, or AI components.
The core objective is to keep tests deterministic, maintainable, and aligned with the modular service architecture.

## Unit Testing

Unit tests target individual backend components in isolation.
Each test verifies one behavior or contract, using mocks for dependent services, repositories, and settings.
Unit testing focuses on:

- Service logic and repository interaction patterns.
- Repository method contracts using mocked database sessions.
- Authentication dependency behavior independent of the provider.
- Middleware request/response handling and header behavior.
- Logging and audit helper functions.

## Service Testing

Service layer tests should use mock repositories and mock settings to confirm how domain services transform input and call persistence layers.
Service tests do not require a real database or live dependencies.

## Repository Testing

Repository tests should validate repository entry points with a mock database session.
Mock session fixtures ensure repository methods can be exercised without connecting to Supabase or PostgreSQL.

## API Testing

API tests leverage FastAPI `TestClient` and dependency overrides to validate endpoint wiring, status codes, and response envelopes.
API tests should remain independent from real services by overriding service and repository dependencies.

## Mocking Strategy

A consistent mocking strategy is essential:

- Use `MagicMock` for generic service, repository, and session fixtures.
- Patch application settings through a reusable mock settings fixture.
- Keep mocks shallow and injectable through dependency injection.
- Avoid embedding business logic in fixtures.

## Dependency Overrides

Dependency overrides keep API tests isolated from production dependencies.
Fixtures should support overriding:

- service providers
- repository factories
- database session creation
- authentication context and user identity
- application settings

This enables focused contract tests without introducing real backend state.

## Future Integration Testing

Future integration tests can layer real infrastructure onto the backend.
These tests should exercise:

- database connectivity with Supabase/PostgreSQL
- repository persistence behavior
- service orchestration with AI and knowledge engines
- authentication provider integration

Integration tests are separate from unit tests and should run against controlled test environments.

## Future End-to-End Testing

End-to-end testing should validate complete clinical workflows across interface boundaries.
Key areas include:

- clinical case creation through recommendation generation
- explainability output and audit trace continuity
- frontend-backend API contract preservation

E2E tests should be designed for staging environments and not included in the core unit test suite.

## Continuous Integration Readiness

The backend testing foundation is CI-ready when:

- tests are discovering under `apps/api/tests`
- pytest is configured with a minimal `pytest.ini`
- fixtures are independent and reusable
- no live database or external service dependencies are required
- test artifacts remain deterministic across environments
