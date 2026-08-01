# Deployment Architecture

**Project:** PharmaTrybe

**Version:** 1.0

**Status:** Official Architecture

**Last Updated:** August 2026

---

# Purpose

This document defines the deployment architecture of PharmaTrybe.

It specifies:

- deployment topology
- runtime environments
- service isolation
- infrastructure responsibilities
- scalability strategy
- security boundaries
- CI/CD readiness

This document complements:

- Platform_Architecture.md
- Data_Flow_and_Orchestration.md
- Database_Service_Mapping.md
- Frontend_Backend_Mapping.md

---

# Deployment Philosophy

PharmaTrybe follows a modular microservice-inspired architecture.

Each major component is independently deployable while communicating
through the FastAPI orchestration layer.

Deployment is designed to support:

- Local development
- Research experimentation
- Clinical testing
- Production deployment

---

# Overall Deployment Architecture

```
                     Internet
                         │
                HTTPS / TLS
                         │
                 Next.js Frontend
                         │
                  FastAPI Backend
                         │
     ┌───────────┬───────────┬────────────┬─────────────┐
     │           │           │            │
     ▼           ▼           ▼            ▼
 SOAR Service  ARMD Service WHO Engine Decision Engine
                         │
                  Explainability Engine
                         │
                    Supabase Platform
                         │
      ┌──────────────┬──────────────┬──────────────┐
      │              │              │
 Authentication   PostgreSQL    Storage / Audit
```

---

# Deployment Components

## 1. Next.js Frontend

Responsibilities

- User interface
- Authentication session
- API communication
- Visualization
- Responsive design

Deployment

Containerized

Technology

Next.js

Node.js

---

## 2. FastAPI Backend

Responsibilities

- API Gateway
- Authentication
- Validation
- Request orchestration
- Audit logging

Deployment

Independent container

Technology

FastAPI

Python

---

## 3. SOAR Service

Responsibilities

- Respiratory AI inference

Deployment

Independent Python container

Contains

- trained SOAR model
- preprocessing
- postprocessing
- inference logic

---

## 4. ARMD Service

Responsibilities

Hospital antimicrobial resistance prediction

Deployment

Independent Python container

Contains

- trained ARMD model
- preprocessing
- feature engineering
- inference

The ARMD training pipeline (WP1–WP6) is **not deployed**.

Only the trained inference model is deployed.

---

## 5. WHO Knowledge Engine

Responsibilities

- WHO guideline lookup
- AWaRe classification
- Drug information
- Stewardship policies

Deployment

Independent Python service

Connected to Supabase.

No machine learning.

---

## 6. Decision Engine

Responsibilities

- Recommendation synthesis
- Clinical rule execution
- Alternative ranking

Deployment

Independent Python container

No AI training.

Deterministic only.

---

## 7. Explainability Engine

Responsibilities

- Recommendation explanation
- Evidence generation
- Confidence explanation

Deployment

Independent Python container

---

## 8. Supabase

Responsibilities

Authentication

Database

Audit logs

WHO Knowledge

Saved cases

Recommendation history

Deployment

Managed Supabase Cloud

---

# Local Development Architecture

```
Developer

↓

VS Code / Cursor

↓

Docker Compose

↓

Next.js

↓

FastAPI

↓

SOAR

↓

ARMD

↓

WHO

↓

Decision

↓

Explainability

↓

Supabase
```

All services execute locally.

---

# Production Architecture

```
Internet

↓

Reverse Proxy

↓

Next.js

↓

FastAPI

↓

Internal Network

↓

SOAR

ARMD

WHO

Decision

Explainability

↓

Supabase Cloud
```

Only FastAPI is publicly accessible.

All AI services remain private.

---

# Docker Deployment

Every service receives its own container.

| Service | Container |
|----------|-----------|
| Frontend | nextjs |
| Backend | fastapi |
| SOAR | soar-service |
| ARMD | armd-service |
| WHO | who-service |
| Decision | decision-service |
| Explainability | explainability-service |

---

# Container Communication

Allowed

```
Frontend

↓

FastAPI

↓

Internal Services
```

Forbidden

Frontend

↓

SOAR

Frontend

↓

ARMD

Frontend

↓

WHO

SOAR

↓

ARMD

ARMD

↓

WHO

Everything passes through FastAPI.

---

# Networking

Public

- HTTPS

Private

- Internal Docker Network

Only FastAPI exposes external endpoints.

---

# Environment Variables

Each service maintains its own environment configuration.

Examples

Frontend

- NEXT_PUBLIC_API_URL

Backend

- SUPABASE_URL
- SUPABASE_KEY
- JWT_SECRET

SOAR

- MODEL_PATH

ARMD

- MODEL_PATH

WHO

- DATABASE_URL

Decision

- RULESET_VERSION

Explainability

- EXPLANATION_VERSION

---

# Security

Authentication

Supabase Auth

Authorization

FastAPI

Encryption

HTTPS

Secrets

Environment Variables

Passwords and API keys are never committed.

---

# Scalability

Each service scales independently.

Example

```
FastAPI

↓

Load Balancer

↓

SOAR x3

ARMD x2

WHO x1

Decision x2

Explainability x2
```

SOAR and ARMD can scale separately depending on demand.

---

# Logging

Every service logs

- request_id
- execution time
- model version
- errors
- timestamp

Centralized through FastAPI.

---

# Monitoring

Metrics collected

- API latency
- model latency
- service uptime
- database health
- recommendation count
- failed requests

Future integration

- Prometheus
- Grafana

---

# Backup Strategy

Supabase

Daily automated backup

WHO database

Version controlled

Model files

Stored in Model Registry

Configuration

Git repository

---

# Disaster Recovery

If SOAR fails

↓

Use ARMD when applicable.

If ARMD fails

↓

Use SOAR when applicable.

If WHO fails

↓

No recommendation produced.

Fail safely.

If FastAPI fails

↓

Entire platform unavailable.

---

# Continuous Integration

Future CI Pipeline

GitHub

↓

Lint

↓

Unit Tests

↓

Integration Tests

↓

Docker Build

↓

Security Scan

↓

Deployment

---

# Continuous Deployment

Deployment Targets

Development

↓

Testing

↓

Staging

↓

Production

Production deployment requires successful validation at every stage.

---

# Research Pipeline Separation

The ARMD research pipeline remains completely separate from production.

Research

WP1

↓

WP2

↓

WP3

↓

WP4

↓

WP5

↓

WP6

↓

Trained ARMD Model

↓

Production Deployment

Only the final validated model is deployed.

No raw datasets or intermediate feature tables are included in production.

---

# Architecture Principles

- Modular deployment
- Independent scalability
- Secure service isolation
- FastAPI as the only public gateway
- AI services remain private
- WHO knowledge remains authoritative
- Research and production remain separated
- Docker-first deployment
- Cloud-ready architecture
- Vendor-neutral design

---

# Deployment Status

This document defines the official deployment architecture of PharmaTrybe.

All future infrastructure, Docker configuration, cloud deployment,
and production environments must conform to this architecture.