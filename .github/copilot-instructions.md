# PharmaTrybe Copilot Development Instructions

This file is the permanent development constitution for GitHub Copilot and all contributors working on the PharmaTrybe repository.

## Project Purpose

PharmaTrybe is an Explainable Artificial Intelligence Clinical Decision Support System (CDSS) for antimicrobial stewardship.

- It is not an autonomous prescribing system.
- It supports clinicians using evidence-based medicine, machine learning, explainability, and WHO antimicrobial stewardship guidance.
- The system follows a modular microservice architecture.

## Core Design Principles

Always follow these principles:

1. Evidence precedes artificial intelligence.
2. Artificial intelligence supports clinicians.
3. AI never replaces clinicians.
4. WHO knowledge is the authoritative clinical source.
5. SOAR/GSK predicts resistance evidence only.
6. ARMD predicts hospital resistance risk only.
7. Only the Clinical Decision Engine synthesizes recommendations.
8. The Explainability Engine explains every recommendation.
9. Knowledge and prediction must remain independent.
10. Every recommendation must be auditable.
11. Every component must be independently deployable.
12. Clinical safety has priority over predictive performance.

## Architectural Responsibilities

### Frontend

- Stack: Next.js 15
- Responsibilities: clinician-facing UI, workflow presentation, explanation display
- Must remain independent from backend AI logic

### Backend

- Stack: FastAPI
- Responsibilities: API orchestration, service integration, domain logic
- Must preserve modular boundaries

### Database

- Stack: Supabase
- Contains the following domains:
  - diagnostics
  - diseases
  - drugs
  - evidence
  - followup
  - metadata
  - monitoring
  - pathogens
  - recommendation_pathogens
  - recommendations
  - referral
  - stewardship
- Do not modify database structure unless explicitly instructed.

## Component Boundaries

### SOAR/GSK

Responsible for:

- respiratory stewardship
- susceptibility prediction
- resistance evidence
- confidence estimation

Must never:

- prescribe antibiotics
- interpret WHO guidelines
- replace clinicians

### ARMD

Responsible for:

- previous antibiotic exposure
- previous organisms
- previous resistance
- ICU history
- laboratory indicators
- vital signs
- procedures
- demographics
- healthcare exposure

Must never:

- recommend antibiotics
- interpret WHO guidance
- override SOAR/GSK

### WHO Knowledge Engine

Responsible for:

- WHO AWaRe
- drug knowledge
- guidelines
- contraindications
- renal adjustments
- stewardship rules

This component contains no machine learning.

### Clinical Decision Engine

Responsible for combining:

- SOAR/GSK
- ARMD
- WHO Knowledge
- clinical rules

It produces clinician recommendations.

- It is deterministic.
- It is not an AI model.

### Explainability Engine

Responsible for explaining:

- why a recommendation was made
- supporting evidence
- confidence
- stewardship reasoning
- risk factors
- rejected options

## Repository Rules

- Never move folders.
- Never rename folders.
- Never redesign architecture.
- Never merge services together.
- Never generate placeholder AI logic.
- Never generate fake clinical algorithms.
- Never invent WHO guidance.
- Never hardcode recommendations.
- Always use existing architecture documentation.

## Coding Standards

### Python

- Use FastAPI
- Use Pydantic v2
- Use SQLAlchemy in future work where appropriate
- Use type hints
- Prefer async endpoints where suitable
- Keep code modular and maintainable

### Frontend

- Use Next.js 15
- Use TypeScript
- Use Tailwind CSS
- Prefer reusable components

### Documentation

- Every public class and function should include concise docstrings where appropriate.

## Implementation Style

- Implement only the requested task.
- Never implement future phases automatically.
- Never create extra services.
- Never modify completed documentation.
- Always preserve backwards compatibility.

## Safety and Clinical Guardrails

- Treat clinical safety as the highest priority.
- Favor transparent, auditable reasoning over opaque predictions.
- Keep evidence, recommendations, and explanations traceable.
- Preserve clear separation between data, knowledge, prediction, decision synthesis, and explainability.
