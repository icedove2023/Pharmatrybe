# Data Flow and Orchestration

**Project:** PharmaTrybe

**Version:** 1.0

**Status:** Official Architecture

**Last Updated:** August 2026

---

# Purpose

This document defines how data moves throughout the PharmaTrybe platform.

It specifies:

- service orchestration
- execution order
- synchronous and asynchronous communication
- decision pathways
- AI interaction
- WHO knowledge integration
- explainability generation
- audit trail creation

This document complements:

- Platform_Architecture.md
- Database_Service_Mapping.md
- Service Contracts

---

# Core Principle

All clinical requests pass through the FastAPI Backend.

No service communicates directly with another service.

```
                Frontend
                    │
                    ▼
             FastAPI Backend
                    │
        ┌───────────┼────────────┐
        │           │            │
      SOAR       ARMD        WHO Engine
        │           │            │
        └───────────┼────────────┘
                    │
           Decision Engine
                    │
         Explainability Engine
                    │
             FastAPI Backend
                    │
                Frontend
```

---

# Service Execution Order

The orchestration layer determines which services should execute.

The execution depends on the clinical scenario.

---

# Scenario 1

## Respiratory Stewardship

Clinical Case

↓

FastAPI Validation

↓

SOAR Prediction

↓

WHO Knowledge Lookup

↓

Decision Engine

↓

Explainability Engine

↓

Clinician

---

# Scenario 2

## Hospital Resistance

Clinical Case

↓

FastAPI Validation

↓

ARMD Prediction

↓

WHO Knowledge Lookup

↓

Decision Engine

↓

Explainability Engine

↓

Clinician

---

# Scenario 3

## Integrated Decision Support

Clinical Case

↓

FastAPI Validation

↓

SOAR

+

ARMD

↓

WHO Knowledge

↓

Decision Engine

↓

Explainability

↓

Clinician

---

# Request Lifecycle

## Step 1

Clinician submits a case.

---

## Step 2

FastAPI

- validates payload
- authenticates user
- assigns request_id
- records audit entry

---

## Step 3

Backend determines required AI services.

Possible execution:

- SOAR only
- ARMD only
- SOAR + ARMD

---

## Step 4

Selected AI services execute independently.

Neither service communicates with the other.

---

## Step 5

WHO Knowledge Engine retrieves

- disease guidance
- drug information
- stewardship policy
- contraindications
- evidence

---

## Step 6

Decision Engine combines

- clinical information
- SOAR evidence
- ARMD evidence
- WHO knowledge

into a structured recommendation.

---

## Step 7

Explainability Engine generates

- recommendation rationale
- evidence summary
- confidence explanation
- stewardship justification
- alternative options

---

## Step 8

FastAPI aggregates all outputs.

---

## Step 9

Frontend renders the recommendation.

---

# Service Responsibilities

## FastAPI

Responsible for

- routing
- validation
- orchestration
- logging
- aggregation

Never performs AI inference.

---

## SOAR

Produces

- respiratory prediction
- resistance probability
- confidence

Consumes

- clinical case

---

## ARMD

Produces

- resistance prediction
- exposure history analysis
- hospital risk

Consumes

- WP2 model-ready features
- clinical case

---

## WHO Engine

Produces

- guideline information
- AWaRe classification
- stewardship guidance
- evidence

Consumes nothing from AI.

---

## Decision Engine

Produces

- ranked recommendations
- rejected options
- decision trace

Consumes

- SOAR
- ARMD
- WHO

---

## Explainability Engine

Produces

- clinician explanation

Consumes

- Decision Engine
- WHO
- SOAR
- ARMD

---

# Communication Rules

Services never call each other directly.

Allowed communication:

Frontend

↓

FastAPI

↓

Service

↓

FastAPI

↓

Frontend

Forbidden communication:

SOAR → ARMD

ARMD → SOAR

Decision → WHO

WHO → Decision

Explainability → SOAR

Explainability → ARMD

Everything passes through FastAPI.

---

# Parallel Execution

When both AI engines are required,

SOAR and ARMD execute simultaneously.

```
             FastAPI

            /      \

         SOAR      ARMD

            \      /

        Decision Engine
```

This reduces response latency.

---

# Failure Handling

If SOAR fails

↓

Continue using ARMD + WHO if clinically valid.

---

If ARMD fails

↓

Continue using SOAR + WHO if clinically valid.

---

If WHO fails

↓

No recommendation is produced.

The request fails safely.

---

If Decision Engine fails

↓

Recommendation is aborted.

---

If Explainability fails

↓

Recommendation is withheld.

Explainability is mandatory.

---

# Audit Trail

Every request generates

- request_id
- timestamp
- clinician
- executed services
- model versions
- WHO version
- recommendation version
- explanation version

---

# Logging

Every service logs

Input

↓

Execution

↓

Output

↓

Duration

↓

Errors

↓

Version

---

# Version Control

Every response includes

- contract_version
- model_version
- knowledge_version
- explanation_version

---

# Security

Only FastAPI may communicate externally.

AI services remain internal.

WHO remains read-only.

Decision Engine cannot modify WHO data.

---

# Architecture Principles

- Central orchestration
- Parallel AI execution
- Deterministic decision making
- Explainability first
- Fail-safe recommendations
- Immutable audit trail
- Modular services
- Replaceable AI models
- Independent knowledge base

---

# Architecture Status

This document defines the official execution flow and orchestration
strategy of PharmaTrybe.

Future services must integrate through the FastAPI orchestration layer
without bypassing the established workflow.