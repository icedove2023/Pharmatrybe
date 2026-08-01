# PharmaTrybe Platform Architecture

**Version:** 1.0

**Status:** Official Architecture

**Last Updated:** August 2026

---

# PharmaTrybe

## Explainable Artificial Intelligence Clinical Decision Support Platform for Antimicrobial Stewardship

---

# 1. Purpose

PharmaTrybe is a modular Explainable Artificial Intelligence Clinical Decision Support System (CDSS) designed to support clinicians in antimicrobial prescribing while promoting antimicrobial stewardship.

The platform integrates multiple specialised AI models with evidence-based clinical knowledge to produce transparent, explainable, and guideline-supported recommendations.

PharmaTrybe is **not** an autonomous prescribing system.

Clinical decisions always remain under clinician responsibility.

---

# 2. Platform Vision

PharmaTrybe combines

- Explainable AI
- Clinical Knowledge
- Evidence-Based Medicine
- Antimicrobial Stewardship
- Machine Learning
- Clinical Decision Support

into one unified platform.

The platform is designed to support multiple disease domains while maintaining one common architecture.

---

# 3. Core Design Philosophy

The platform follows five fundamental principles.

## Principle 1

Evidence precedes Artificial Intelligence.

Guidelines and clinical knowledge always have higher authority than predictive models.

---

## Principle 2

Artificial Intelligence supports clinicians.

AI never replaces clinicians.

---

## Principle 3

Every recommendation must be explainable.

Black-box recommendations are unacceptable.

---

## Principle 4

Knowledge and AI remain independent.

Clinical knowledge is stored separately from predictive models.

---

## Principle 5

Every component must be replaceable.

Individual AI models can evolve without redesigning the entire platform.

---

# 4. Overall Platform Architecture

```
                         PharmaTrybe
                              │
      ┌───────────────────────┴────────────────────────┐
      │                                                │
 Primary AI                                     Secondary AI
 SOAR/GSK Model                                 ARMD Model
      │                                                │
      └───────────────────────┬────────────────────────┘
                              │
                   Clinical Decision Engine
                              │
                  WHO Knowledge Engine
                              │
                 Explainability Engine
                              │
                       FastAPI Backend
                              │
                    Authentication Layer
                              │
                         Supabase
                              │
                      Next.js Frontend
                              │
                           Clinicians
```

---

# 5. Platform Components

## 5.1 SOAR/GSK Model

### Purpose

Primary Artificial Intelligence model responsible for respiratory antimicrobial stewardship.

### Responsibilities

- Respiratory pathogen prediction
- Resistance probability estimation
- Stewardship evidence generation
- Confidence estimation

### Does NOT

- Prescribe antibiotics
- Apply WHO rules
- Replace clinicians

---

## 5.2 ARMD Model

### Purpose

Secondary Artificial Intelligence model responsible for hospital antimicrobial resistance prediction.

### Responsibilities

Analyse historical hospital risk factors including

- Previous antibiotic exposure
- Previous infecting organisms
- Previous resistance
- ICU admission
- Ward information
- Laboratory markers
- Vital signs
- Procedures
- Demographics
- Healthcare exposure

Generate structured resistance evidence.

### Does NOT

- Recommend antibiotics
- Interpret WHO guidance
- Override SOAR/GSK

---

## 5.3 WHO Knowledge Engine

### Purpose

Central evidence-based medical knowledge repository.

Contains

- WHO AWaRe Classification
- Treatment Guidelines
- Drug Information
- Contraindications
- Renal Dose Adjustment
- Drug Spectrum
- Stewardship Policies

This service contains no Artificial Intelligence.

It serves validated medical knowledge only.

---

## 5.4 Clinical Decision Engine

The Clinical Decision Engine is the reasoning layer of PharmaTrybe.

It combines

- SOAR/GSK evidence
- ARMD evidence
- WHO recommendations
- Patient characteristics
- Clinical rules

into one unified recommendation.

The Decision Engine is deterministic.

It is not a machine learning model.

---

## 5.5 Explainability Engine

Purpose

Transform technical model outputs into clinician-friendly explanations.

Sources of explanation include

- SOAR/GSK
- ARMD
- WHO Knowledge
- Decision Engine

Outputs include

- Why a recommendation was produced
- Supporting evidence
- Confidence
- Stewardship justification
- Risk factors
- Alternative options

---

## 5.6 FastAPI Backend

Acts as the orchestration layer.

Responsibilities

- Authentication
- Authorization
- API Gateway
- Service orchestration
- Audit logging
- Validation
- Response aggregation

The backend performs no machine learning.

---

## 5.7 Supabase

Responsibilities

- Authentication
- User management
- Audit logs
- Saved clinical cases
- Recommendation history
- Feedback
- WHO database
- Model metadata

Supabase is not responsible for AI inference.

---

## 5.8 Next.js Frontend

Provides interfaces for

### Physician

Clinical decision support

### Laboratory Scientist

Microbiology workflow

### Stewardship Team

Population surveillance

### Administrator

Platform management

The frontend contains no clinical reasoning.

---

# 6. Official Clinical Workflows

---

## Case 1

### Respiratory Stewardship

Patient

↓

Clinical Information

↓

SOAR/GSK Model

↓

WHO Knowledge

↓

Clinical Decision Engine

↓

Explainability Engine

↓

Clinician Recommendation

---

## Case 2

### Hospital Antimicrobial Resistance

Patient

↓

Clinical Information

↓

ARMD Model

↓

WHO Knowledge

↓

Clinical Decision Engine

↓

Explainability Engine

↓

Clinician Recommendation

---

## Case 3 (Future)

Combined Decision Support

Patient

↓

Clinical Information

↓

SOAR/GSK

+

ARMD

↓

WHO Knowledge

↓

Clinical Decision Engine

↓

Explainability Engine

↓

Integrated Recommendation

This architecture allows simultaneous respiratory stewardship and hospital resistance prediction.

---

# 7. Data Flow

```
Clinician

↓

Frontend

↓

FastAPI Backend

↓

SOAR/GSK

↓

ARMD

↓

WHO Knowledge

↓

Decision Engine

↓

Explainability Engine

↓

FastAPI

↓

Frontend

↓

Clinician
```

---

# 8. Platform Layers

Layer 1

Presentation

- Next.js

---

Layer 2

Application

- FastAPI

---

Layer 3

Intelligence

- SOAR/GSK
- ARMD

---

Layer 4

Knowledge

- WHO
- Clinical Rules

---

Layer 5

Decision

- Decision Engine

---

Layer 6

Explainability

- XAI

---

Layer 7

Persistence

- Supabase

---

# 9. Extensibility

PharmaTrybe is designed as a modular AI platform.

Future models may include

- Sepsis AI
- Urinary Tract Infection AI
- Neonatal Infection AI
- Surgical Prophylaxis AI
- Tuberculosis AI
- Fungal Stewardship AI

Each future model integrates through the same Decision Engine without changing the overall architecture.

---

# 10. Scientific Position

PharmaTrybe does **not** claim that Artificial Intelligence selects the best antibiotic.

Instead,

SOAR/GSK and ARMD provide predictive evidence.

WHO provides evidence-based guidance.

The Clinical Decision Engine synthesises these sources into clinician-facing recommendations.

The clinician retains full responsibility for the final prescribing decision.

---

# 11. Architectural Principles

The PharmaTrybe platform follows the following principles:

- Evidence before AI
- AI supports clinicians
- Knowledge and prediction remain independent
- Explainability is mandatory
- Every recommendation must be auditable
- WHO remains the authoritative knowledge source
- SOAR/GSK and ARMD complement each other
- Services remain independently deployable
- New AI models must integrate without redesign
- Clinical safety has priority over predictive performance
- Reproducibility and transparency guide all development

---

# 12. Architecture Status

This document defines the official architecture of PharmaTrybe.

All future implementation, API development, AI integration, frontend development, database design, and deployment must conform to this architecture.

Any architectural modifications require formal review and version updates to this document.