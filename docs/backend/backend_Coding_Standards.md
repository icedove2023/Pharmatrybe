# Backend Coding Standards
## PharmaTrybe
### An Explainable Clinical Decision Support System for Personalized Antimicrobial Prescribing and Stewardship

**Document Version:** 1.0  
**Status:** Engineering Standard  
**Audience:** Backend Engineers, AI Code Assistants, Contributors, System Architects

---

# 1. Purpose

This document defines the official backend engineering standards for PharmaTrybe.

Every backend module, API endpoint, AI component, repository, database model, knowledge pipeline, and integration service must comply with these standards.

These standards ensure that:

- all generated code is consistent
- all modules are maintainable
- clinical safety is preserved
- explainability is preserved
- scalability remains achievable
- AI-generated code follows the same engineering philosophy as human-written code

This document is mandatory.

---

# 2. Core Engineering Principles

The backend must always prioritise:

1. Clinical Safety
2. Explainability
3. Maintainability
4. Reliability
5. Reproducibility
6. Extensibility
7. Performance
8. Security

Prediction accuracy alone is never sufficient.

Every recommendation must remain explainable.

---

# 3. Backend Philosophy

The backend is organised around modular services.

Business logic must never be embedded inside:

- controllers
- API routes
- repositories
- ORM models

Business logic belongs only inside services and decision engines.

---

# 4. Python Version

Official Version

Python 3.12+

Required features

- typing
- dataclasses where appropriate
- match statements
- pathlib
- Annotated typing
- Pydantic v2 compatibility

---

# 5. Backend Framework

Official Framework

FastAPI

Reasons

- asynchronous support

- OpenAPI generation

- dependency injection

- excellent typing

- production ready

No other web framework should be introduced.

---

# 6. API Design Standards

Every endpoint must:

return JSON

return proper HTTP status codes

return unified response structure

Example

{
    "success": true,
    "metadata": {},
    "data": {}
}

Errors must always use

{
    "success": false,
    "metadata": {},
    "error": {}
}

---

# 7. Project Structure

Backend folders must follow

apps/api/app/

api/

services/

repositories/

models/

schemas/

database/

decision_engine/

knowledge/

explainability/

logging/

security/

middleware/

utils/

config/

No additional root folders without architectural approval.

---

# 8. Naming Conventions

Classes

PascalCase

ClinicalDecisionService

Functions

snake_case

generate_recommendation()

Variables

snake_case

patient_age

Constants

UPPER_CASE

DEFAULT_TIMEOUT

---

# 9. File Size Rules

Maximum file length

500 lines

Preferred

300 lines

If exceeded

Split into multiple modules.

---

# 10. Function Size Rules

Maximum

60 lines

Preferred

20–40 lines

Functions must perform one responsibility only.

---

# 11. Type Hints

Every public function must include complete typing.

Example

```python
def recommend_antibiotic(
    patient: ClinicalCase,
    pathogens: list[Pathogen]
) -> Recommendation:
Untyped public functions are prohibited.

12. Docstrings

Every class

Every public method

Every service

Must contain Google-style docstrings.

Example

def predict():
    """
    Generate antimicrobial recommendation.

    Returns:
        Recommendation
    """
13. Pydantic Standards

Use Pydantic v2.

Separate

Request schemas

Response schemas

Internal DTOs

Validation models

Never reuse ORM models as API schemas.

14. SQLAlchemy Standards

SQLAlchemy 2.x only.

Use

Mapped

mapped_column

relationship

No legacy ORM syntax.

15. Repository Pattern

Repositories may only

retrieve

insert

update

delete

No business logic.

Allowed

repository.find_by_id()

repository.list()

repository.save()

Not allowed

repository.calculate_resistance()
16. Service Layer

Business rules belong here.

Examples

ClinicalDecisionService

RecommendationService

ResistanceService

PatientRiskService

ExplainabilityService

17. Decision Engine Standards

Decision engines never access databases directly.

Instead

Decision Engine

↓

Service

↓

Repository

↓

Database

18. Knowledge Sources

Knowledge sources are independent modules.

Examples

WHO

SOAR

ARMD

Future modules

NICE

IDSA

Local Hospital Guidelines

CDC

ESCMID

New knowledge modules must plug into the fusion engine without changing existing code.

19. Knowledge Fusion Rules

Knowledge fusion determines

which sources contribute

how recommendations are weighted

how conflicts are resolved

WHO remains the primary evidence source unless unavailable.

20. Explainability Standards

Every recommendation must include

Evidence used

Guidelines used

Resistance data used

Knowledge source

Confidence

Reasoning

Rule trace

No black-box recommendation is permitted.

21. Logging Standards

Use structured logging.

Never

print()

Use

logging.getLogger()

Required log levels

DEBUG

INFO

WARNING

ERROR

CRITICAL

22. Audit Logging

Every clinical decision generates

timestamp

patient identifier

knowledge sources

recommendation

confidence

user

decision trace

Audit logs are immutable.

23. Security Standards

Never expose

passwords

keys

tokens

stack traces

database credentials

Use environment variables only.

24. Environment Variables

Secrets must never appear in source code.

Always use

.env

GitHub Secrets

Deployment Secrets

25. Exception Handling

Never expose raw exceptions.

Always raise application-specific exceptions.

Example

ClinicalDecisionException

KnowledgeSourceUnavailable

RecommendationConflict

26. Dependency Injection

FastAPI dependency injection must be used throughout.

Avoid global state.

27. Async Rules

Use async only when beneficial.

Examples

database

external APIs

LLM inference

Avoid unnecessary async functions.

28. Database Transactions

All write operations must use transactions.

Rollback on failure.

Never leave partial writes.

29. Performance

Avoid

N+1 queries

duplicate API calls

duplicate guideline parsing

Repeated knowledge extraction

Use caching where appropriate.

30. Caching

Allowed for

WHO knowledge

SOAR data

ARMD resistance

LLM embeddings

Static metadata

31. Validation

Every input

validated

sanitised

typed

before processing.

32. API Versioning

All endpoints use

/api/v1/

Future versions

/api/v2/

/api/v3/

Breaking changes require new API versions.

33. Testing Standards

Every module requires

Unit tests

Integration tests

Repository tests

API tests

Decision engine tests

Knowledge fusion tests

Explainability tests

34. Clinical Safety Rules

When uncertainty exists

show warning

display confidence

request clinician review

Never fabricate recommendations.

35. AI Integration Rules

LLMs assist with

summarisation

reasoning support

natural language explanations

They do not replace evidence.

Structured knowledge remains authoritative.

36. Code Review Checklist

Every Pull Request should verify

✓ typing

✓ documentation

✓ tests

✓ logging

✓ explainability

✓ clinical safety

✓ security

✓ performance

✓ style compliance

37. Future Extensibility

The backend must support future integration of

Additional LLMs

Additional AMR datasets

Hospital-specific guidelines

FHIR

HL7

SNOMED CT

LOINC

ICD-11

Local antibiograms

Machine learning models

without architectural redesign.

38. Definition of Done

Backend work is considered complete only when:

Code follows these standards
Unit tests pass
Integration tests pass
API documentation updates automatically
Explainability is implemented
Logging is complete
Audit logging works
Security review passes
Documentation is updated
No critical linting or typing issues remain
39. Engineering Principle

The PharmaTrybe backend is not merely an API.

It is a clinically safe, explainable, modular decision-support platform designed to integrate multiple evidence sources, resistance intelligence, and AI reasoning into transparent antimicrobial prescribing recommendations.

Every backend contribution must strengthen this vision rather than compromise it.


This document should serve as the definitive coding standard for all backend development throughout the PharmaTrybe