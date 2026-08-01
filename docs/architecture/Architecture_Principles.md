# Architecture Principles

**Project:** PharmaTrybe

**Document:** Architecture Constitution

**Version:** 1.0

**Status:** Official Governance Document

**Last Updated:** August 2026

---

# Purpose

This document defines the fundamental architectural principles of PharmaTrybe.

These principles govern every aspect of the platform, including:

- Software Architecture
- Artificial Intelligence
- Clinical Decision Support
- Knowledge Management
- Security
- Explainability
- Deployment
- Future Expansion

All future development must comply with these principles.

---

# Mission

PharmaTrybe exists to support clinicians in evidence-based antimicrobial prescribing through transparent, explainable, and clinically safe Artificial Intelligence.

The platform is a Clinical Decision Support System (CDSS).

It is **not** an autonomous prescribing system.

---

# Vision

To build a modular Explainable AI platform capable of supporting multiple infectious disease domains while maintaining clinical safety, transparency, and antimicrobial stewardship.

---

# Core Principles

## Principle 1

### Evidence Before Artificial Intelligence

Clinical evidence always has higher authority than predictive models.

WHO guidance, validated clinical knowledge, and stewardship policies take precedence over AI predictions.

---

## Principle 2

### AI Supports Clinicians

Artificial Intelligence assists clinicians.

It never replaces clinical judgement.

The final prescribing decision always belongs to the clinician.

---

## Principle 3

### Explainability is Mandatory

Every recommendation must include:

- Why it was generated
- Supporting evidence
- Confidence
- Stewardship justification
- Alternative options

Recommendations without explanations are unacceptable.

---

## Principle 4

### Knowledge and Prediction are Independent

Clinical knowledge is stored separately from AI models.

WHO guidance must remain independent of prediction algorithms.

AI models cannot modify medical knowledge.

---

## Principle 5

### Decision Making is Deterministic

Only the Clinical Decision Engine produces recommendations.

SOAR and ARMD provide predictive evidence.

WHO provides clinical guidance.

The Decision Engine synthesises these sources into a single recommendation.

---

## Principle 6

### FastAPI is the Orchestration Layer

All services communicate through the FastAPI backend.

Direct communication between AI services is prohibited.

---

## Principle 7

### Modular Services

Each major component is independently deployable.

Examples include:

- SOAR
- ARMD
- WHO Knowledge Engine
- Decision Engine
- Explainability Engine

No component should require redesign of the entire platform.

---

## Principle 8

### Single Responsibility

Each service performs one clearly defined role.

| Service | Responsibility |
|----------|----------------|
| SOAR | Respiratory prediction |
| ARMD | Hospital resistance prediction |
| WHO | Medical knowledge |
| Decision Engine | Recommendation synthesis |
| Explainability | Recommendation explanation |
| FastAPI | Orchestration |
| Next.js | Presentation |

---

## Principle 9

### WHO is the Authoritative Knowledge Source

WHO clinical knowledge remains the single source of truth for:

- AWaRe classification
- Treatment guidance
- Stewardship policy
- Drug information
- Monitoring
- Follow-up
- Referral guidance

AI models must never override WHO guidance.

---

## Principle 10

### Research and Production are Independent

The ARMD research workflow (WP1–WP6) remains separate from the production platform.

Only validated inference models are deployed.

Research datasets are never deployed.

---

## Principle 11

### Transparency

Every recommendation must be reproducible.

Every decision must generate an audit trail.

Every model version must be identifiable.

---

## Principle 12

### Clinical Safety First

Patient safety always takes priority over predictive performance.

When uncertainty exists:

- prefer conservative recommendations
- provide warnings
- defer to clinician judgement

---

## Principle 13

### Fail Safely

If critical services fail:

- recommendations must not be fabricated
- incomplete recommendations must not be displayed
- failures must be clearly communicated

---

## Principle 14

### Security by Design

Authentication

Supabase Auth

Authorization

FastAPI

Transport

HTTPS

Secrets

Environment variables

Least privilege access applies to every service.

---

## Principle 15

### Data Minimisation

Only information necessary for clinical decision support should be collected.

Avoid unnecessary patient information.

Support privacy by design.

---

## Principle 16

### Version Everything

Every release must version:

- AI models
- WHO database
- APIs
- Schemas
- Decision rules
- Explainability engine

Version information must accompany every recommendation.

---

## Principle 17

### Auditability

Every recommendation generates:

- request_id
- model versions
- knowledge version
- decision trace
- explanation version
- timestamp

---

## Principle 18

### Extensibility

Future AI models must integrate without redesigning PharmaTrybe.

Examples:

- Sepsis AI
- Urinary Tract Infection AI
- Tuberculosis AI
- Surgical Prophylaxis AI
- Neonatal Infection AI
- Fungal Stewardship AI

All future models integrate through the Clinical Decision Engine.

---

## Principle 19

### User-Centred Design

Interfaces must minimise clinician workload.

Clinical workflows should require only essential information.

Version 1 supports:

- Physician
- Laboratory Scientist
- Antimicrobial Stewardship Team
- Administrator

Patients are not primary users in Version 1.

---

## Principle 20

### Scientific Integrity

PharmaTrybe does **not** claim that Artificial Intelligence selects the best antibiotic.

Instead:

- SOAR predicts respiratory resistance evidence.
- ARMD predicts hospital resistance evidence.
- WHO provides evidence-based guidance.
- The Decision Engine synthesises these sources.
- The clinician makes the final prescribing decision.

This distinction is fundamental to the scientific validity of the platform.

---

# Governance Rules

Any architectural modification must:

1. Preserve these principles.
2. Be documented.
3. Be version controlled.
4. Be reviewed before implementation.

---

# Development Rules

Every new feature must answer the following questions:

- Does it support clinical safety?
- Does it maintain explainability?
- Does it preserve modularity?
- Does it follow service boundaries?
- Does it generate audit information?
- Does it respect WHO authority?
- Does it maintain research-production separation?

If the answer to any question is "No", the feature must be redesigned.

---

# Architecture Status

This document serves as the official architectural constitution of PharmaTrybe.

All software development, AI integration, database design, API development, frontend implementation, deployment, and future platform expansion must conform to the principles defined in this document.

Any deviation requires formal architectural review and version update.