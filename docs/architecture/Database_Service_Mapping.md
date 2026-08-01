# Database Service Mapping

**Project:** PharmaTrybe

**Version:** 1.0

**Status:** Official Architecture

**Last Updated:** August 2026

---

# Purpose

This document defines ownership of every database table, service,
schema, API contract and frontend consumer within PharmaTrybe.

It establishes one authoritative source for:

- Data ownership
- Read/write permissions
- Service boundaries
- AI integration
- Schema mapping
- Frontend consumption
- Audit responsibilities

This document complements Platform_Architecture.md.

---

# Architecture Overview

```
Supabase Database
        │
        ▼
FastAPI Backend
        │
 ┌──────┼──────────────┐
 │      │              │
 ▼      ▼              ▼
SOAR   ARMD      WHO Knowledge
 │      │              │
 └──────┴──────────────┘
        │
Decision Engine
        │
Explainability Engine
        │
Next.js Frontend
```

---

# 1. WHO Knowledge Database

The following tables belong exclusively to the WHO Knowledge Engine.

| Table | Purpose | Owner |
|--------|----------|-------|
| diseases | Disease definitions | WHO |
| pathogens | Pathogen reference | WHO |
| drugs | Drug database | WHO |
| diagnostics | Diagnostic guidance | WHO |
| recommendations | Treatment recommendations | WHO |
| recommendation_pathogens | Disease–Pathogen relationships | WHO |
| stewardship | Stewardship policies | WHO |
| monitoring | Monitoring guidance | WHO |
| referral | Referral criteria | WHO |
| followup | Follow-up guidance | WHO |
| evidence | Evidence sources | WHO |
| metadata | Database versioning | WHO |

---

# WHO Table Permissions

| Service | Read | Write |
|----------|------|-------|
| WHO Engine | ✓ | ✓ |
| Decision Engine | ✓ | ✗ |
| Explainability Engine | ✓ | ✗ |
| SOAR | ✓ | ✗ |
| ARMD | ✓ | ✗ |
| Frontend | ✗ | ✗ |
| FastAPI | ✓ | ✗ |

Only the WHO Knowledge Engine owns these tables.

---

# 2. SOAR Model

Produces

- Respiratory resistance prediction
- Prediction confidence
- Predicted pathogens
- Model metadata

Consumes

- Clinical Case
- WHO pathogen information

Never writes to the database.

---

# 3. ARMD Model

Produces

- Previous resistance risk
- Previous organism exposure
- Previous antibiotic exposure
- ICU risk
- Hospital-acquired risk
- Resistance probability
- Model confidence

Consumes

- Certified ARMD Feature Table
- Clinical Case
- WHO pathogen information

Never writes to Supabase.

---

# 4. Decision Engine

Consumes

- SOAR
- ARMD
- WHO Knowledge

Produces

- Final recommendation
- Alternative recommendations
- Decision trace

The Decision Engine never edits WHO data.

---

# 5. Explainability Engine

Consumes

- SOAR output
- ARMD output
- Decision Engine output
- WHO evidence

Produces

- Human-readable explanation
- Recommendation rationale
- Evidence summary
- Confidence explanation

Never edits any database.

---

# 6. FastAPI Backend

Responsible for

- Authentication
- Validation
- Request routing
- API orchestration
- Audit logging
- Response aggregation

FastAPI owns no clinical knowledge.

---

# 7. Supabase Ownership

Supabase stores:

## Authentication

- Users
- Roles
- Sessions

Owner

FastAPI

---

## WHO Knowledge

Owner

WHO Engine

---

## Audit Logs

Owner

FastAPI

---

## Saved Cases

Owner

FastAPI

---

## Recommendation History

Owner

Decision Engine

---

## Feedback

Owner

Frontend → FastAPI

---

# 8. Schema Ownership

| Schema | Owner |
|---------|-------|
| Clinical Case Schema | Backend |
| SOAR Output Schema | SOAR |
| ARMD Output Schema | ARMD |
| WHO Schema | WHO |
| Recommendation Schema | Decision Engine |
| Explainability Schema | Explainability |
| Decision Trace Schema | Decision Engine |

---

# 9. API Ownership

| Endpoint | Service |
|-----------|----------|
| /clinical-case | FastAPI |
| /soar | SOAR |
| /armd | ARMD |
| /who | WHO |
| /decision | Decision Engine |
| /explainability | Explainability |

---

# 10. Frontend Consumption

## Physician Dashboard

Uses

- Recommendation
- Explainability
- WHO guidance

---

## Laboratory Dashboard

Uses

- ARMD
- Culture history
- Resistance profile

---

## Stewardship Dashboard

Uses

- Population resistance
- WHO guidance
- Recommendation analytics

---

## Administrator Dashboard

Uses

- Users
- Audit logs
- Model versions
- WHO metadata

---

# 11. AI Model Ownership

| Component | Purpose |
|-----------|----------|
| SOAR | Respiratory stewardship prediction |
| ARMD | Hospital resistance prediction |
| WHO | Evidence-based knowledge |
| Decision Engine | Clinical reasoning |
| Explainability | Transparent recommendations |

No AI model directly recommends antibiotics.

Only the Decision Engine generates recommendations.

---

# 12. Data Ownership Principles

1. WHO owns all medical knowledge.

2. SOAR owns respiratory prediction.

3. ARMD owns resistance prediction.

4. Decision Engine owns recommendations.

5. Explainability owns explanations.

6. FastAPI owns orchestration.

7. Supabase owns persistence only.

8. Frontend owns presentation only.

---

# 13. Write Permissions Summary

| Component | Can Write Database |
|------------|-------------------|
| WHO Engine | WHO Tables Only |
| FastAPI | Audit, Users, Cases |
| Decision Engine | Recommendation History |
| Frontend | Never Directly |
| SOAR | Never |
| ARMD | Never |
| Explainability | Never |

---

# 14. Architecture Integrity Rules

- WHO data cannot be modified by AI models.
- SOAR and ARMD are prediction engines only.
- Decision Engine is the only recommendation engine.
- Explainability never changes recommendations.
- Frontend never performs clinical reasoning.
- All communication passes through FastAPI.
- Every recommendation must generate a Decision Trace.
- Every recommendation must be reproducible and auditable.

---

# Architecture Status

This document defines the official ownership and mapping of all
database objects, schemas, APIs, services, and consumers within
PharmaTrybe.

Any future database, service, or schema additions must be reflected
here before implementation.