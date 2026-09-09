# PharmaTrybe Backend Architecture

**Project:** PharmaTrybe — An Explainable Clinical Decision Support System (CDSS) for Personalized Antimicrobial Prescribing and Stewardship

Version: 1.0

Status: Master Backend Architecture

---

# 1. Purpose

This document defines the complete backend architecture of PharmaTrybe.

It serves as the engineering reference describing:

- overall backend structure
- responsibilities of every module
- request lifecycle
- service interactions
- knowledge source integration
- explainability pipeline
- AI orchestration
- scalability strategy

This document is architecture only.

Implementation details belong elsewhere.

---

# 2. Backend Philosophy

The backend is designed around five principles.

## Evidence First

Clinical evidence is always evaluated before AI reasoning.

Priority:

WHO Guidelines

↓

Knowledge Sources
(SOAR, ARMD, Future Sources)

↓

Clinical Rules

↓

LLM Reasoning

↓

Recommendation

---

## Explainability First

Every recommendation must explain:

- why it exists
- supporting evidence
- confidence
- guideline source
- knowledge source
- uncertainty

Predictions without explanations are never acceptable.

---

## Modular Intelligence

No module depends tightly on another.

Each service has a single responsibility.

Modules communicate through APIs and schemas.

---

## Knowledge is Replaceable

Knowledge sources must be swappable.

Today:

- WHO
- SOAR
- ARMD

Future:

- IDSA
- NICE
- ESCMID
- Local Guidelines
- Hospital Guidelines
- Custom Institutional Knowledge

The backend should require no architectural redesign when new knowledge sources are added.

---

## AI Assists

The AI never prescribes.

The clinician remains responsible.

---

# 3. High-Level Architecture

```
                Frontend

                    │

                    ▼

             FastAPI Gateway

                    │

        ┌───────────┼───────────┐

        ▼           ▼           ▼

Clinical API   WHO API    Authentication

        │

        ▼

Clinical Decision Pipeline

        │

        ▼

Knowledge Fusion Engine

        │

        ▼

Explainability Engine

        │

        ▼

Recommendation Engine

        │

        ▼

Response Builder

```

---

# 4. Major Backend Modules

## API Layer

Responsibilities

- receive requests
- validate payloads
- authentication
- routing
- serialization
- error handling

Contains

```
app/api/
```

---

## Clinical Case Module

Stores

- demographics

- symptoms

- vitals

- laboratory

- diagnosis

- medications

- allergies

- risk factors

Outputs

Standard Clinical Case Schema

---

## WHO Knowledge Module

Responsible for

- diseases

- diagnostics

- recommendations

- stewardship

- follow-up

- referral

- monitoring

- evidence

WHO is always queried.

Always.

---

## Knowledge Connector Layer

Responsible for external knowledge.

Current connectors

WHO

SOAR

ARMD

Future connectors

IDSA

NICE

Hospital Guidelines

Local Stewardship

Institution Guidelines

Custom Knowledge Bases

---

# 5. Knowledge Fusion Engine

The Fusion Engine combines knowledge from multiple sources.

Example

Respiratory Infection

↓

WHO

+

SOAR

+

ARMD

↓

Unified Recommendation

Example

UTI

↓

WHO

+

ARMD

↓

Recommendation

Example

Future

↓

WHO

+

Local Guideline

+

Hospital Protocol

+

Model A

↓

Recommendation

The fusion engine never hardcodes combinations.

It decides dynamically.

---

# 6. Dynamic Knowledge Selection

Knowledge selection depends on:

Disease

Patient

Region

Organism

Resistance

Clinical Question

Available Sources

Example

```
Respiratory

WHO
SOAR
ARMD

```

Example

```
UTI

WHO
ARMD

```

Example

```
Future

WHO
IDSA
Hospital Guideline

```

The pipeline decides which knowledge sources participate.

---

# 7. Clinical Rules Engine

The Rules Engine performs deterministic reasoning.

Examples

Allergy

Pregnancy

Age

Renal impairment

Liver impairment

Weight

Contraindications

Drug interactions

Maximum dose

Stewardship restrictions

The AI never bypasses clinical rules.

---

# 8. AI Orchestration Layer

The AI layer performs reasoning only after evidence has been collected.

Responsibilities

Interpret complex cases

Resolve conflicting evidence

Personalize recommendations

Generate explanations

Estimate confidence

Generate clinician summaries

Future

SHAP

Attention Maps

Confidence Calibration

Counterfactual explanations

---

# 9. Explainability Engine

Every recommendation returns

Clinical reasoning

Supporting evidence

Knowledge sources

Confidence

Alternative therapies

Rejected therapies

Guideline citations

Stewardship warnings

Example

Recommendation

↓

Amoxicillin

Reason

WHO recommendation

Supported by SOAR susceptibility

Resistance acceptable

Patient no allergy

Confidence

94%

---

# 10. Recommendation Engine

Produces

Drug

Dose

Route

Frequency

Duration

Monitoring

Warnings

Stewardship Advice

Alternative Therapy

---

# 11. Response Builder

Converts internal objects into API responses.

No business logic exists here.

Only formatting.

---

# 12. Database Layer

Uses SQLAlchemy.

Contains

WHO Knowledge

Clinical Cases

Users

Audit Logs

Explainability Logs

AI Outputs

Knowledge Metadata

Version History

---

# 13. Logging Layer

Everything important is logged.

Clinical requests

Knowledge retrieval

AI reasoning

Rule execution

Recommendations

Errors

Latency

Audit trail

---

# 14. Security Layer

Authentication

Authorization

Audit logging

Role-based permissions

Encryption

Secure headers

Future

Hospital SSO

OAuth

OpenID

MFA

---

# 15. Scalability

Each module should eventually become its own service.

Possible future services

Clinical Service

WHO Service

Knowledge Service

Decision Service

Explainability Service

AI Service

Authentication Service

Audit Service

Notification Service

---

# 16. Backend Request Lifecycle

```
Frontend

↓

API

↓

Validate

↓

Clinical Schema

↓

Knowledge Selection

↓

WHO

↓

Additional Knowledge Sources

↓

Clinical Rules

↓

AI Reasoning

↓

Explainability

↓

Recommendation

↓

Response

```

---

# 17. Future AI Architecture

Current

WHO

SOAR

ARMD

↓

LLM

↓

Recommendation

Future

WHO

+

Knowledge Source A

+

Knowledge Source B

+

Knowledge Source C

↓

Fusion Engine

↓

AI Reasoning

↓

SHAP

↓

Counterfactual Explanation

↓

Clinician

The backend is designed so additional knowledge sources can be plugged in without changing the core architecture.

---

# 18. Architectural Principles

The backend must always satisfy the following:

- Evidence before AI
- Explainability before prediction
- Modular services
- Replaceable knowledge sources
- Rule-based clinical safety
- Dynamic knowledge fusion
- Versioned knowledge
- Complete auditability
- API-first architecture
- Future-proof extensibility

---

# Backend Vision

PharmaTrybe is not a traditional clinical application.

It is a modular, explainable, knowledge-driven intelligent platform where clinical evidence, multiple knowledge sources, deterministic rules, and AI reasoning are fused dynamically to produce personalized antimicrobial recommendations while maintaining transparency, stewardship principles, and clinician trust.