# Backend_Architecture_Lock.md

**Project:** PharmaTrybe – Explainable Clinical Decision Support System (CDSS) for Personalized Antimicrobial Prescribing and Stewardship

**Status:** LOCKED

**Version:** 1.0

**Date:** 2026

---

# Purpose

This document formally locks the backend architecture of PharmaTrybe.

Its purpose is to prevent architectural drift during future development while allowing unlimited functional expansion.

From this point onward:

- Providers may be added.
- Decision logic may evolve.
- AI models may improve.
- Explainability may become richer.

However, the backend architecture itself should remain unchanged unless a critical design flaw is discovered.

---

# Architectural Principles

The backend follows the following non-negotiable principles.

## 1. Evidence Before AI

The platform always prioritizes authoritative clinical evidence before AI-generated predictions.

Priority:

WHO/NICE/Clinical Guidelines

↓

Clinical Rules

↓

AI Predictions (SOAR, ARMD, etc.)

↓

Decision Engine

↓

Explainability

AI supports clinicians.

AI never replaces clinical evidence.

---

## 2. Separation of Responsibilities

Each backend layer has exactly one responsibility.

No layer may absorb responsibilities belonging to another layer.

---

## 3. Explainability First

Every recommendation produced by the system must be explainable.

Every clinical decision must be traceable back to:

- evidence
- provider
- confidence
- provenance
- decision pathway

---

## 4. Provider Independence

Knowledge sources must be replaceable.

No provider may require changes to:

- API
- Services
- Router
- Decision Engine
- Explainability Engine

Adding a provider should require registration only.

---

# Locked Backend Architecture

```
FastAPI API Layer
        │
        ▼
Service Layer
        │
        ▼
Knowledge Orchestrator
        │
        ▼
Knowledge Router
        │
        ▼
Routing Strategy
        │
        ▼
Provider Registry
        │
        ▼
Knowledge Provider
        │
        ▼
Repository
        │
        ▼
Database / External Source
```

This architecture is now the permanent backend pipeline.

---

# Layer Responsibilities

## API Layer

Responsibilities

- HTTP endpoints
- Authentication
- Request validation
- Response serialization

Must NOT:

- Query repositories
- Call providers directly
- Perform routing
- Execute clinical rules
- Fuse knowledge
- Generate recommendations

---

## Service Layer

Responsibilities

- Coordinate a single use case
- Build provider queries
- Call Knowledge Orchestrator
- Return API-compatible objects

Must NOT:

- Import repositories
- Import SQLAlchemy ORM models
- Know provider implementations
- Know database details
- Execute clinical reasoning

The service layer depends only on:

- KnowledgeOrchestrator
- KnowledgeQuery
- SearchQuery
- KnowledgePackage
- ProviderResult

---

## Knowledge Orchestrator

Responsibilities

- Execute provider workflows
- Coordinate retrieval
- Aggregate provider execution results

Must NOT:

- Perform routing logic
- Perform clinical reasoning
- Execute SQL
- Generate recommendations

---

## Knowledge Router

Responsibilities

- Select providers

Must NOT:

- Inspect medical content
- Rank antibiotics
- Perform explainability
- Perform fusion

---

## Routing Strategy

Responsibilities

- Decide which providers should execute

Current strategy:

Priority-based provider selection

Future strategies may include:

- parallel routing
- failover
- weighted routing
- specialty routing

Must NOT:

- Read clinical content
- Execute business rules
- Rank treatments

---

## Provider Registry

Responsibilities

- Register providers
- Remove providers
- Discover providers
- Report provider health

Must NOT:

- Execute providers
- Fuse results
- Interpret medical information

---

## Knowledge Provider

Responsibilities

- Retrieve knowledge
- Normalize provider output
- Attach provenance
- Attach metadata
- Attach version information

Must NOT:

- Execute SQL directly
- Perform clinical reasoning
- Generate recommendations
- Perform explainability
- Route requests

Every provider returns only:

- KnowledgePackage

Never ORM models.

---

## Repository

Responsibilities

Persistence only.

Repositories perform:

- CRUD
- SQLAlchemy queries
- Filtering
- Pagination
- Sorting
- Search

Repositories return ORM entities internally.

Repositories never return API objects.

Repositories never contain:

- AI logic
- Routing
- Decision rules
- Explainability
- Provenance

---

# Provider Boundary Rule

The Provider layer is the only layer allowed to translate persistence models into platform models.

```
Repository

↓

SQLAlchemy ORM

↓

Provider

↓

KnowledgePackage

↓

Everything Else
```

Never:

```
Repository

↓

SQLAlchemy ORM

↓

Service
```

Never:

```
Repository

↓

SQLAlchemy ORM

↓

Router
```

Never:

```
Repository

↓

SQLAlchemy ORM

↓

Decision Engine
```

---

# Dependency Rules

Dependencies flow downward only.

```
API

↓

Service

↓

Orchestrator

↓

Router

↓

Registry

↓

Provider

↓

Repository
```

Reverse dependencies are forbidden.

---

# Current Providers

Implemented

- WHOProvider

Planned

- SOARProvider
- ARMDProvider
- NICEProvider
- IDSAProvider
- ESCMIDProvider
- HospitalGuidelineProvider
- VectorKnowledgeProvider
- LocalKnowledgeProvider

Each provider must implement the same KnowledgeProvider contract.

---

# Future Components

The following components are planned but intentionally remain separate from the current provider architecture.

## Knowledge Fusion Engine

Consumes:

- KnowledgePackage

Produces:

- FusedKnowledgePackage

---

## Clinical Decision Engine

Consumes:

- FusedKnowledgePackage

Produces:

- DecisionPackage

---

## Explainability Engine

Consumes:

- DecisionPackage
- PipelineTrace

Produces:

- ExplainabilityPackage

---

## Clinical Rules Engine

Consumes:

- DecisionPackage
- Patient Context

Produces:

- Rule Evaluations

---

# Pipeline Objects

Each layer owns one object.

Knowledge Retrieval

```
KnowledgePackage
```

↓

Knowledge Fusion

```
FusedKnowledgePackage
```

↓

Decision Making

```
DecisionPackage
```

↓

Explainability

```
ExplainabilityPackage
```

No object should bypass its intended layer.

---

# Pipeline Trace

Every clinical request should eventually generate a PipelineTrace containing:

- Request ID
- Provider execution order
- Provider timings
- Provider versions
- Provenance
- Fusion decisions
- Clinical rules fired
- AI confidence
- Recommendation rationale
- Final recommendation

This trace forms the foundation of Explainable AI and clinical auditability.

---

# Architectural Rules for Contributors

When adding new functionality:

✅ Add new providers.

✅ Add new rules.

✅ Add new AI models.

✅ Add new knowledge sources.

Do NOT:

- Modify service architecture
- Bypass the provider layer
- Bypass the router
- Bypass the orchestrator
- Return ORM entities outside providers
- Add business logic to repositories
- Add clinical logic to routing

---

# Architecture Freeze

This document represents the approved backend architecture.

Future work should extend the system through new providers and functional modules rather than introducing new architectural layers.

**Architecture Status:** LOCKED

**Approved By:** PharmaTrybe Architecture Team

**Version:** 1.0