# PharmaTrybe

> An explainable, clinician-facing Clinical Decision Support System (CDSS) for antimicrobial prescribing and antimicrobial stewardship.

[![Status](https://img.shields.io/badge/status-active%20development-blue)](#project-status)
[![Architecture](https://img.shields.io/badge/architecture-clinician--in--the--loop-green)](#clinical-safety-and-governance)
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688)](#technology-stack)
[![Frontend](https://img.shields.io/badge/frontend-React%20%2F%20TypeScript-61DAFB)](#technology-stack)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)](#prerequisites)

---

## Overview

**PharmaTrybe** is an Explainable Artificial Intelligence Clinical Decision Support System designed to assist healthcare professionals with antimicrobial prescribing and antimicrobial stewardship.

The platform combines:

- structured clinical information;
- clinical rules and safety constraints;
- antimicrobial resistance information;
- guideline and knowledge-base evidence;
- machine-learning predictions;
- explainability;
- clinician review and oversight;
- auditability and provenance.

The system is designed as **clinical decision support**, not autonomous prescribing.

The clinician remains responsible for interpreting the recommendation and making the final clinical decision.

---

## Why PharmaTrybe?

Antimicrobial prescribing can require the simultaneous consideration of:

- patient characteristics;
- infection context;
- suspected or identified organisms;
- antimicrobial resistance;
- allergies;
- contraindications;
- renal and other dosing considerations;
- antimicrobial stewardship policies;
- clinical guidelines;
- uncertainty in available evidence.

PharmaTrybe provides an architecture in which these different evidence sources can be brought together while preserving their provenance and making the reasoning behind a recommendation visible.

The central design principle is:

> **Evidence before AI, explainability before automation, and clinical safety before predictive performance.**

---

## Core Objectives

PharmaTrybe is being developed around the following principles:

1. **Support clinicians rather than replace them.**
2. **Make recommendations explainable.**
3. **Prioritise patient safety over predictive performance.**
4. **Use clinical evidence and structured knowledge before machine-learning predictions.**
5. **Keep medical knowledge separate from application logic.**
6. **Use structured clinical data rather than relying on uncontrolled free text.**
7. **Fail closed when required information or evidence is unavailable.**
8. **Preserve provenance for clinical inputs and generated recommendations.**
9. **Make important decisions auditable and reproducible.**
10. **Allow individual knowledge, model, and application components to evolve independently.**

---

# System Architecture

At a high level, PharmaTrybe follows a layered clinical decision-support architecture:

```text
                         ┌──────────────────────────┐
                         │      Clinician / User    │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │    Clinical Assessment   │
                         │                          │
                         │ Structured clinical data │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │ Canonical Clinical Model │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                    ┌────────────────────────────────────┐
                    │       Decision / Fusion Context    │
                    │                                    │
                    │ Guidelines                          │
                    │ Knowledge                           │
                    │ Clinical rules                      │
                    │ Resistance information              │
                    │ ML evidence                         │
                    └───────────────┬────────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────────┐
                    │        Clinical Rules Engine        │
                    │                                    │
                    │ Allergies                           │
                    │ Contraindications                   │
                    │ Dosing constraints                  │
                    │ Stewardship policies                │
                    └───────────────┬────────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────────┐
                    │       Prediction / Plugin Layer    │
                    │                                    │
                    │ SOAR                               │
                    │ ARMD                               │
                    │ Other approved prediction plugins  │
                    └───────────────┬────────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────────┐
                    │       Decision Fusion Engine       │
                    └───────────────┬────────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────────┐
                    │       Explainability Engine        │
                    │                                    │
                    │ Why?                               │
                    │ Evidence?                          │
                    │ Confidence?                        │
                    │ Limitations?                       │
                    └───────────────┬────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────────┐
                         │ Clinical Recommendation │
                         │ + Explanation           │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │    Clinician Review      │
                         └──────────────────────────┘
````

The machine-learning models therefore form **one evidence source within a broader decision-support architecture** rather than acting as autonomous prescribers.

---

# Key Components

## Clinical Assessment

The assessment layer collects and validates structured clinical information.

Examples include:

* patient characteristics;
* infection context;
* specimen information;
* organism information where available;
* antimicrobial information;
* clinical location;
* relevant safety information.

The assessment layer is responsible for producing canonical clinical data consumed by downstream services.

---

## Knowledge Base

Clinical knowledge is maintained separately from application code.

This allows clinical knowledge to be:

* updated;
* reviewed;
* version controlled;
* validated;
* audited;
* independently maintained.

Recommendations should not be hidden inside application logic when they represent clinical knowledge.

---

## Clinical Rules Engine

The clinical rules layer is responsible for deterministic safety and policy constraints.

Examples include:

* allergy checks;
* contraindications;
* renal dosing constraints;
* antimicrobial stewardship policies;
* eligibility rules;
* clinical safety warnings.

Deterministic safety rules should not be replaced by machine-learning predictions.

---

## Prediction Plugin Architecture

Machine-learning systems are integrated through explicit plugin contracts.

Current prediction integrations include:

* **SOAR**
* **ARMD**

The plugin architecture provides boundaries around:

* model discovery;
* deployment selection;
* input contracts;
* input validation;
* prediction execution;
* provenance;
* error handling;
* explainability metadata.

Prediction plugins must not bypass the canonical clinical recommendation pipeline.

---

# SOAR

SOAR is integrated as a deployment-based prediction plugin.

The supplied SOAR package contains ten deployment models covering antimicrobial/organism combinations.

The runtime uses explicit deployment identity rather than inferring a deployment from arbitrary folder names or approximate clinical values.

The SOAR deployment contract currently uses the following raw model inputs:

```text
Age
YearCollected
Region
BodyLocation_Group
Country
```

The eight `Haemophilus influenzae` deployments additionally require:

```text
Beta_Lactamase_enc
```

The authoritative training archive establishes the beta-lactamase encoding:

```text
NEG → 0
POS → 1
```

The clinical interface exposes the controlled clinical values:

```text
NEGATIVE
POSITIVE
```

and converts them deterministically to the model representation internally.

The numeric model representation is not intended to be entered directly by clinicians.

---

# Fail-Closed Design

PharmaTrybe deliberately avoids guessing when a required model input is unavailable.

For example:

```text
SOAR cannot execute because required input X is unavailable.
```

The system should then obtain the missing information through the appropriate controlled clinical workflow.

It must not:

* invent a value;
* silently use a default;
* infer an unsupported value;
* select an arbitrary deployment;
* use fuzzy deployment matching;
* substitute an unrelated clinical field;
* bypass the input contract.

This is especially important for clinical decision support.

---

# Deployment Resolution

SOAR deployment selection is explicit.

Conceptually:

```text
Clinical context
       │
       ▼
Explicit deployment_id
       │
       ▼
Verified deployment contract
       │
       ▼
Input resolver
       │
       ├── Required input available
       │        │
       │        ▼
       │   Validate input
       │
       └── Required input unavailable
                │
                ▼
          Controlled completion
                │
                ▼
          Validate input
                │
                ▼
          Execute deployment
```

Unknown deployment IDs are rejected.

There is no:

```text
first deployment fallback
```

and no:

```text
best matching deployment
```

based on approximate strings.

---

# Explainability

Explainability is a mandatory part of the platform rather than an optional UI feature.

A recommendation should be accompanied by information describing:

* what evidence contributed to the recommendation;
* which clinical rules were applied;
* which model/plugin contributed;
* prediction confidence where available;
* relevant limitations;
* supporting knowledge or guideline information;
* important warnings.

The system should allow a clinician to understand **why** a recommendation was produced.

---

# Clinical Safety and Governance

PharmaTrybe is explicitly designed as a **clinician-facing decision-support system**.

It is not intended to:

* autonomously prescribe antimicrobial therapy;
* replace clinical judgement;
* make unsupported diagnoses;
* conceal uncertainty;
* bypass clinician review.

A technically successful model execution does **not** by itself establish clinical validity.

The current SOAR/ARMD evidence includes historical model-performance information, but this should not be interpreted as prospective clinical validation.

Relevant limitations identified during project audits include:

* historical rather than prospective evaluation;
* dataset quality issues;
* missing data;
* class imbalance;
* domain shift;
* conflicting historical certification records;
* limitations in reconstructed model artifacts;
* incomplete evidence for some clinical assumptions.

Clinical deployment therefore requires appropriate clinical validation, governance, monitoring, and approval.

---

# Technology Stack

| Layer            | Technology                                 |
| ---------------- | ------------------------------------------ |
| Frontend         | React                                      |
| Language         | TypeScript                                 |
| Backend          | FastAPI                                    |
| Backend language | Python                                     |
| Database         | PostgreSQL / Supabase                      |
| Authentication   | Supabase Auth                              |
| API              | REST                                       |
| ML runtime       | Python / scikit-learn ecosystem            |
| Testing          | Vitest / repository test runner / pytest   |
| Static analysis  | ESLint / Flake8                            |
| CI               | GitHub Actions                             |
| Model artifacts  | Pickle / joblib-based deployment artifacts |

---

# Repository Structure

The repository is organised as a multi-component clinical platform.

A simplified structure is:

```text
.
├── apps/
│   └── api/
│       ├── app/
│       ├── tests/
│       └── requirements.txt
│
├── src/
│   ├── api/
│   ├── components/
│   ├── forms/
│   ├── plugins/
│   ├── routes/
│   ├── stores/
│   └── ...
│
├── packages/
│   ├── clinical-schemas/
│   ├── prediction-framework/
│   └── ...
│
├── deployments/
│   └── SOAR_GSK/
│
├── docs/
│   ├── architecture/
│   ├── audits/
│   ├── phase-*
│   └── ...
│
├── .github/
│   └── workflows/
│
├── package.json
└── README.md
```

The exact repository structure may evolve as the platform develops.

---

# API Architecture

The backend API is versioned under:

```text
/api/v1
```

The canonical clinical recommendation endpoint is:

```text
POST /api/v1/recommendations/generate
```

The platform also exposes supporting domains such as:

* authentication;
* clinical cases;
* recommendations;
* knowledge;
* plugin orchestration;
* clinical review;
* health/version information.

Prediction plugins such as SOAR and ARMD are intentionally kept behind the canonical recommendation/pipeline boundary rather than exposed as independent autonomous prescribing endpoints.

Detailed endpoint status and ownership are documented in the repository's endpoint audit.

---

# Prerequisites

Before running the project locally, install:

* Node.js
* npm
* Python 3.11+
* Git
* PostgreSQL/Supabase access where required by the local configuration

For backend development, use the project's Python virtual environment where possible.

Example:

```bash
python -m venv .venv
```

Activate it and install backend dependencies:

```bash
pip install -r apps/api/requirements.txt
```

For the frontend:

```bash
npm install
```


# Running the Project

## Frontend

Install dependencies:

```bash
npm install
```

Start the development server using the repository's configured npm script:

```bash
npm run dev
```

---

## Backend

From the backend directory:

```bash
cd apps/api
```

Activate the project Python environment and start the FastAPI application using the repository's configured startup command.

For example:

```bash
uvicorn app.main:app --reload
```

The exact command should follow the current project configuration.

---

# Testing

## Frontend

Run the frontend test suite:

```bash
npm test
```

Build the production frontend:

```bash
npm run build
```

Run linting:

```bash
npm run lint
```

---

## Backend

From the repository root or `apps/api` directory:

```bash
python -m pytest apps/api/tests -ra
```

For SOAR-specific tests:

```bash
python -m pytest \
  apps/api/tests/test_soar_deployment_contract.py \
  apps/api/tests/test_soar_artifact_registry.py
```

Backend static analysis:

```bash
flake8 apps/api/app apps/api/tests
```

The CI pipeline also performs a critical Python syntax/undefined-name gate.

---

# Continuous Integration

The repository uses GitHub Actions for automated validation.

The backend CI pipeline is responsible for validating the Python backend environment and running:

* dependency installation;
* critical Python static checks;
* broader Flake8 quality checks;
* pytest.

The frontend pipeline validates the TypeScript/React application through the repository's configured test and build commands.

CI should be treated as a required safety gate for changes affecting clinical runtime code.

---

# Current Project Status

PharmaTrybe is under active development.

The following major platform capabilities have been implemented or are under active integration:

* clinician-facing clinical assessment;
* structured clinical data;
* tenant-aware identity architecture;
* authentication and RBAC;
* clinical schemas;
* clinical rules;
* knowledge-base architecture;
* recommendation pipeline;
* explainability architecture;
* prediction plugin framework;
* SOAR deployment contracts;
* SOAR input resolution;
* controlled SOAR completion workflow;
* ARMD integration;
* audit/provenance architecture;
* automated frontend testing;
* backend testing and CI validation.

---

# SOAR Runtime Status

The supplied SOAR deployment package has been inspected and integrated into the platform through explicit deployment contracts.

The current runtime architecture supports:

* ten verified SOAR deployments;
* explicit deployment selection;
* deployment-specific input contracts;
* controlled missing-input completion;
* deterministic beta-lactamase encoding;
* input provenance;
* fail-closed execution;
* separation of routing context from model input payload.

However:

> **Technical runtime readiness must not be interpreted as clinical validation.**

Historical evaluation metrics supplied with the SOAR package are useful for engineering and research purposes but do not constitute prospective clinical validation.

---

# Safety Principles

The following rules are architectural requirements.

### No arbitrary fallback

The system must never silently choose another deployment because the requested deployment is unavailable.

### No fabricated clinical values

Missing clinical information must remain missing until supplied through an approved source.

### No unsupported semantic mapping

A clinical field must not be mapped to a model field unless that mapping is explicitly supported by authoritative evidence.

### No hidden preprocessing in the UI

Clinical forms collect clinical values.

Model preprocessing remains inside the model/runtime boundary.

### No autonomous prescribing

A prediction is an input to clinical decision support, not an autonomous prescription.

### Explainability is mandatory

Recommendations must expose their supporting evidence and relevant limitations.

### Auditability is mandatory

Important clinical and technical decisions must be traceable to their source and version.

---

# Documentation

Detailed technical documentation is maintained separately from this README.

Important documentation areas include:

```text
docs/
├── architecture/
├── audits/
├── phase-*/
└── ...
```

The documentation covers areas such as:

* platform architecture;
* identity and tenancy;
* authentication;
* RBAC;
* clinical schemas;
* knowledge architecture;
* recommendation pipeline;
* explainability;
* SOAR deployment contracts;
* SOAR input resolution;
* ARMD integration;
* endpoint audits;
* CI and verification;
* clinical safety limitations.

The README intentionally provides the project overview rather than duplicating the complete architecture and audit documentation.

---

# Development Principles

Contributors should preserve the following development philosophy:

1. Make the smallest evidence-backed change.
2. Inspect existing architecture before adding new abstractions.
3. Reuse established contracts.
4. Do not introduce duplicate validation engines unnecessarily.
5. Do not bypass the canonical clinical pipeline.
6. Preserve backward compatibility where clinically and technically appropriate.
7. Add regression tests for every safety-critical behaviour.
8. Keep clinical knowledge separate from application code.
9. Document important architectural decisions.
10. Never hide uncertainty behind a successful HTTP response or model execution.

---

# Contributing

Contributions should follow the project's established development and review process.

Before submitting a pull request:

```bash
npm test
npm run build
```

For backend changes, also run:

```bash
python -m pytest apps/api/tests -ra
flake8 apps/api/app apps/api/tests
```

Clinical or model-related changes should additionally include:

* evidence for the change;
* affected clinical contracts;
* provenance/source information;
* regression tests;
* safety implications;
* documentation updates where required.

Do not introduce new clinical mappings, defaults, or model inputs without authoritative evidence.

See the repository's contribution documentation when available.

---

# Security

Do not report security vulnerabilities through public issues.

Security-sensitive information should never be committed to the repository.

This includes:

* authentication secrets;
* API credentials;
* database credentials;
* Supabase service-role keys;
* patient-identifiable information;
* private clinical datasets;
* production configuration.

For production deployments, use appropriate secret-management and access-control mechanisms.

---

# Clinical Disclaimer

PharmaTrybe is a **clinical decision-support research and software platform**.

It is not a substitute for professional medical judgement.

Recommendations, predictions, resistance information, and explanations produced by the system must be interpreted by appropriately qualified healthcare professionals within the applicable clinical and regulatory context.

The presence of a technically functioning machine-learning model does not establish clinical safety, effectiveness, or regulatory approval.

Clinical deployment requires appropriate:

* clinical validation;
* governance;
* monitoring;
* data protection;
* risk management;
* human oversight;
* regulatory assessment.

---

# License


---

# Maintainers

**PharmaTrybe Project**

For project-specific questions, consult the repository documentation and issue tracker.

---

## Project Philosophy

PharmaTrybe is built around a simple principle:

> **AI should augment clinical evidence and clinical judgement — not replace them.**

The system therefore treats:

```text
Clinical Evidence
        ↓
Structured Knowledge
        ↓
Clinical Safety Rules
        ↓
Patient / Case Information
        ↓
Machine-Learning Evidence
        ↓
Decision Fusion
        ↓
Explainable Recommendation
        ↓
Clinician Review
```

as the foundation of the platform.

---

## Acknowledgement

The project incorporates clinical decision-support, antimicrobial stewardship, machine-learning, explainability, structured knowledge, and software-engineering principles.

All model-specific claims should be interpreted according to the evidence and validation documentation supplied with the corresponding model artifacts.

