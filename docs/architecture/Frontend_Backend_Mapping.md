# Frontend Backend Mapping

**Project:** PharmaTrybe

**Version:** 1.0

**Status:** Official Architecture

**Last Updated:** August 2026

---

# Purpose

This document defines how every PharmaTrybe frontend screen interacts
with the backend services.

It establishes:

- User roles
- Screen responsibilities
- Backend endpoints
- Services invoked
- Data schemas
- Expected outputs

This document complements:

- Platform_Architecture.md
- Data_Flow_and_Orchestration.md
- Database_Service_Mapping.md

---

# Supported User Roles

PharmaTrybe Version 1 supports four user roles.

| Role | Primary Responsibility |
|-------|------------------------|
| Physician | Clinical decision support |
| Laboratory Scientist | Microbiology workflow |
| Antimicrobial Stewardship Team | Surveillance and stewardship |
| Administrator | Platform management |

Patients are not direct users in Version 1.

---

# Platform Navigation

```

Login

↓

Dashboard

├── Physician Portal

├── Laboratory Portal

├── Stewardship Portal

└── Administrator Portal

```

---

# Physician Portal

Purpose

Provide evidence-supported antimicrobial recommendations.

## Screen

Clinical Case Entry

Backend Endpoint

POST /clinical-case

Schema

Clinical Case Schema

Services

- FastAPI
- SOAR
- ARMD (when required)
- WHO
- Decision Engine
- Explainability

Returns

Recommendation Schema

---

## Screen

Recommendation Results

Backend Endpoint

POST /decision

Displays

- Recommended antibiotics
- Alternatives
- Confidence
- Stewardship notes
- WHO classification

Schema

Recommendation Schema

---

## Screen

Explainability

Backend Endpoint

POST /explainability

Displays

- Why recommended
- Why rejected
- Evidence
- Risk factors
- Confidence
- Stewardship rationale

Schema

Explainability Schema

---

# Laboratory Portal

Purpose

Support microbiology personnel.

---

## Screen

Laboratory Result Viewer

Backend Endpoint

GET /laboratory

Services

ARMD

WHO

Displays

- Organism
- Susceptibility
- Resistance profile
- Previous organism history

---

## Screen

Resistance Profile

Backend Endpoint

POST /armd

Schema

ARMD Schema

Displays

- Previous antibiotics
- Previous organisms
- ICU history
- Resistance probability

---

# Stewardship Portal

Purpose

Support antimicrobial stewardship teams.

---

## Screen

Stewardship Dashboard

Backend Endpoint

GET /stewardship

Services

WHO

Decision Engine

Displays

- AWaRe usage
- Resistance trends
- Stewardship compliance
- Recommendation analytics

---

## Screen

WHO Guidance

Backend Endpoint

GET /who

Displays

- Guidelines
- Evidence
- Stewardship recommendations

Schema

WHO Schema

---

# Administrator Portal

Purpose

Platform administration.

---

## Screen

User Management

Endpoint

GET /users

POST /users

PUT /users

DELETE /users

---

## Screen

Audit Logs

Endpoint

GET /audit

Displays

- User activity
- Recommendation history
- Decision trace
- Model versions

---

## Screen

WHO Database Management

Endpoint

GET /who

PUT /who

Restricted to administrators.

---

# Authentication Flow

Login

↓

Supabase Authentication

↓

JWT

↓

FastAPI

↓

Frontend

---

# Frontend Components

## Shared Components

- Sidebar
- Navigation
- Header
- Notification Panel
- User Profile
- Loading Indicators
- Error Messages

---

## Clinical Components

- Clinical Case Form
- Recommendation Card
- Drug Card
- AWaRe Badge
- Explainability Panel
- Confidence Meter

---

## Laboratory Components

- Organism Card
- Resistance Table
- Antibiotic History
- Culture Timeline

---

## Stewardship Components

- Dashboard Cards
- Charts
- Trend Analysis
- Heatmaps
- Reports

---

## Administrator Components

- User Table
- Audit Viewer
- System Logs
- Model Version Viewer

---

# Backend Responsibilities

FastAPI is responsible for

- Authentication
- Validation
- Routing
- Aggregation
- Logging

Frontend never communicates directly with

- SOAR
- ARMD
- WHO
- Decision Engine
- Explainability

---

# API Summary

| Endpoint | Used By |
|-----------|----------|
| POST /clinical-case | Physician |
| POST /soar | Backend |
| POST /armd | Backend |
| GET /who | Physician, Stewardship |
| POST /decision | Backend |
| POST /explainability | Backend |
| GET /audit | Administrator |
| GET /users | Administrator |

---

# Screen-to-Service Mapping

| Screen | Service |
|---------|----------|
| Clinical Case | FastAPI |
| Recommendation | Decision Engine |
| Explainability | Explainability Engine |
| Laboratory Viewer | ARMD |
| WHO Guidance | WHO Engine |
| Stewardship Dashboard | WHO + Decision |
| Admin Dashboard | FastAPI |

---

# Design Principles

- Minimal clinician data entry
- AI supports—not replaces—clinical judgement
- WHO guidance always visible
- Explainability mandatory
- Mobile-friendly layouts
- Accessibility compliant
- Fast response times
- Secure authentication
- Full auditability

---

# Architecture Status

This document defines the official interaction between the PharmaTrybe
frontend and backend.

All future UI development must conform to these mappings.