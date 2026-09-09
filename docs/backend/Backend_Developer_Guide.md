# Backend_Developer_Guide.md

---

# PharmaTrybe
## Backend Developer Guide
### Version 1.0

**Project**

**An Explainable Clinical Decision Support System (CDSS) for Personalized Antimicrobial Prescribing and Antimicrobial Stewardship**

---

# Purpose

This document serves as the primary onboarding guide for backend developers working on PharmaTrybe.

It explains:

- Architecture
- Development workflow
- Coding practices
- Folder structure
- Development lifecycle
- Testing workflow
- Contribution standards
- Best practices

This guide should be read before contributing code to the backend.

---

# Development Philosophy

PharmaTrybe follows several engineering principles.

## 1. Clinical Safety First

No feature should compromise patient safety.

---

## 2. Explainability Before Intelligence

Every recommendation must be explainable.

Prediction without explanation is unacceptable.

---

## 3. Evidence Before AI

Knowledge sources drive decision-making.

AI augments clinical evidence rather than replacing it.

---

## 4. Modular Design

Every component should be independently replaceable.

---

## 5. Separation of Concerns

Business logic

↓

Decision logic

↓

Knowledge

↓

Data

↓

Presentation

must remain independent.

---

# Project Overview

The backend powers

- Clinical Case Management
- Knowledge Retrieval
- Knowledge Fusion
- AI Decision Support
- Explainability
- Clinical Rules
- Security
- Audit Logging

---

# Technology Stack

Language

Python 3.12+

---

Framework

FastAPI

---

Validation

Pydantic

---

ORM

SQLAlchemy

---

Database

PostgreSQL

---

Caching

Redis

---

Authentication

JWT

---

Migration

Alembic

---

Testing

pytest

---

Documentation

OpenAPI

Markdown

---

# Repository Structure

```text
apps/
    api/

packages/

docs/

scripts/

tests/

docker/

.github/
```

---

# Backend Folder Structure

```text
app/

api/

core/

database/

models/

schemas/

services/

repositories/

knowledge/

decision/

fusion/

explainability/

rules/

logging/

security/

utils/

tests/
```

---

# Responsibility of Each Module

## api/

REST endpoints

No business logic.

---

## services/

Application logic.

---

## repositories/

Database access only.

---

## models/

SQLAlchemy models.

---

## schemas/

Pydantic validation.

---

## knowledge/

Knowledge retrieval.

WHO

SOAR

ARMD

Future sources.

---

## fusion/

Knowledge integration.

---

## decision/

Decision engine.

---

## explainability/

Explanation generation.

---

## rules/

Clinical rules.

---

## security/

Authentication

Authorization

Validation

---

## logging/

Audit

Metrics

Tracing

---

# Backend Workflow

Every request follows

```text
API

↓

Validation

↓

Knowledge Retrieval

↓

Knowledge Fusion

↓

Clinical Rules

↓

Decision Engine

↓

Explainability

↓

Response
```

---

# Development Workflow

Every new feature follows

```text
Requirement

↓

Design

↓

Schema

↓

Model

↓

Repository

↓

Service

↓

API

↓

Tests

↓

Documentation
```

---

# Development Rules

Never skip

- Validation
- Tests
- Documentation
- Logging

---

# Branch Strategy

Main

Stable production.

---

Develop

Integration branch.

---

Feature

One feature

One branch.

Example

```text
feature/who-import

feature/recommendation-engine

feature/explainability
```

---

# Commit Style

Use descriptive commits.

Examples

```text
Add WHO guideline importer

Implement recommendation engine

Fix ARMD parser

Improve explainability service
```

Avoid

```text
Update

Fix

Changes
```

---

# Pull Request Rules

Every PR requires

- Description
- Tests
- Documentation
- Review

---

# Code Style

Follow

PEP 8

Black

isort

ruff

---

# Naming Standards

Classes

```python
ClinicalCaseService
```

---

Functions

```python
generate_recommendation()
```

---

Variables

```python
patient_age
```

---

Constants

```python
MAX_RECOMMENDATION_SCORE
```

---

# Dependency Injection

Avoid global dependencies.

Inject

Repositories

Services

Configuration

Clients

---

# Configuration

Never hardcode

Passwords

URLs

Secrets

API Keys

Always use

```text
.env

Settings

Environment Variables
```

---

# Error Handling

Always raise meaningful exceptions.

Example

```python
DiseaseNotFoundError
```

instead of

```python
Exception
```

---

# Logging

Every important operation logs

- Request
- User
- Status
- Duration

Never log

Passwords

JWT

Patient identifiers

---

# Audit Logging

Critical actions create audit records.

Examples

Recommendation generated

Knowledge imported

Configuration changed

User authenticated

---

# Database Rules

Never

Write raw SQL unless necessary.

Prefer

SQLAlchemy ORM.

---

# Repository Pattern

Database code belongs only inside

```text
repositories/
```

Never query the database directly from

API

Services

Decision Engine

---

# Service Layer

Services contain

Business logic

Nothing else.

---

# API Layer

Endpoints

Validate

Call services

Return response

Nothing more.

---

# Knowledge Layer

Knowledge adapters retrieve information only.

Never perform

Clinical reasoning.

---

# Fusion Layer

Fusion combines

WHO

SOAR

ARMD

Future sources

into one unified evidence object.

---

# Decision Layer

Decision engine produces

Recommendation

Confidence

Risk

Warnings

---

# Explainability Layer

Produces

Clinical rationale

Evidence

Source attribution

Confidence explanation

Alternative therapies

---

# AI Development Rules

AI never

Replaces

WHO guidance.

AI always augments

Structured evidence.

---

# Future AI Integration

Additional models should plug into

```text
decision/

models/
```

without changing the remainder of the system.

---

# Knowledge Source Rules

Every knowledge source implements

```text
retrieve()

validate()

normalize()

version()
```

Common interface.

---

# Testing Requirements

Every feature requires

Unit tests

Integration tests

API tests

Clinical validation

---

# Test Coverage

Minimum

80%

Clinical modules

90%

---

# Documentation Requirements

Every new module requires

Purpose

Inputs

Outputs

Dependencies

Examples

---

# Performance Guidelines

Optimize

Database

Caching

Knowledge retrieval

Never optimize

at the expense of explainability.

---

# Security Rules

Never trust

Client input.

Always

Validate

Authenticate

Authorize

Audit

---

# Code Review Checklist

Review

Architecture

Naming

Documentation

Security

Testing

Performance

Clinical safety

Explainability

---

# Clinical Development Rules

Every recommendation must include

Evidence

Clinical reasoning

Confidence

Source attribution

Alternative options

Stewardship considerations

---

# Future Expansion

The backend is designed to support

Additional LLMs

Additional knowledge sources

FHIR

Hospital integration

Laboratory systems

Radiology

Drug interaction engines

Genomic medicine

Predictive analytics

without redesigning the architecture.

---

# Daily Development Workflow

```text
Pull latest changes

↓

Create feature branch

↓

Implement feature

↓

Write tests

↓

Run lint

↓

Run tests

↓

Update documentation

↓

Commit

↓

Open Pull Request
```

---

# Developer Checklist

Before submitting code

- Builds successfully
- Tests pass
- Documentation updated
- Lint passes
- Security reviewed
- No secrets committed
- API documented
- Logging added
- Explainability preserved

---

# Engineering Principles

Every backend developer should remember

- Clinical safety comes first.
- Evidence is the primary source of truth.
- AI supports clinicians rather than replacing them.
- Every recommendation must be explainable.
- Code should be modular, testable, and maintainable.
- Knowledge sources must remain independent.
- New AI models and knowledge sources should integrate through well-defined interfaces.
- Every change must improve reliability without increasing architectural complexity.

---

# Developer Principle

> **The PharmaTrybe backend is built as a modular, explainable, and evidence-driven clinical platform. Every developer contributes not only software but also clinical reliability, transparency, and patient safety. Clean architecture, rigorous testing, comprehensive documentation, and maintainable code are mandatory engineering standards that ensure the platform can evolve into a globally scalable AI-powered antimicrobial stewardship system.**