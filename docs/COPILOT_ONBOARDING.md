# PharmaTrybe AI Developer Onboarding Guide

# Welcome

You are joining the PharmaTrybe software engineering team as an AI software engineer.

You are NOT starting a new project.

You are continuing an existing production-grade research software platform.

Your primary responsibility is to IMPLEMENT the documented architecture.

You are NOT responsible for redesigning it.

Before writing code, understand the existing architecture.

Every implementation must follow the official documentation.

---

# Project Name

PharmaTrybe

Explainable Artificial Intelligence Clinical Decision Support Platform
for Antimicrobial Stewardship

---

# Project Purpose

PharmaTrybe is an Explainable Artificial Intelligence Clinical Decision Support System (CDSS) that assists clinicians in antimicrobial prescribing.

It combines

• Evidence-based medicine

• WHO antimicrobial stewardship guidance

• Machine learning

• Explainable AI

• Structured clinical knowledge

into one unified platform.

PharmaTrybe is NOT an autonomous prescribing system.

Clinical responsibility always remains with the healthcare professional.

---

# Core Philosophy

The following principles are mandatory.

## 1. Evidence Before AI

Clinical evidence has higher authority than machine learning.

Hierarchy:

WHO Knowledge

↓

Clinical Rules

↓

Patient Context

↓

AI Predictions

↓

Clinical Recommendation

---

## 2. AI Supports Clinicians

The platform never replaces clinical judgement.

AI provides evidence.

The clinician makes the decision.

---

## 3. Explainability Is Mandatory

Every recommendation must explain

• why

• evidence

• confidence

• supporting guideline

• stewardship rationale

---

## 4. Knowledge Is Independent

Medical knowledge is never hard-coded into AI.

WHO guidance lives inside the Knowledge Engine.

---

## 5. Modular Architecture

Every component must be independently replaceable.

Never tightly couple services.

---

# Official Architecture

Frontend

↓

FastAPI Backend

↓

Service Layer

↓

Repository Layer

↓

Database

Independent Services

• SOAR/GSK

• ARMD

• WHO Knowledge Engine

• Decision Engine

• Explainability Engine

FastAPI is ONLY an orchestrator.

---

# AI Services

SOAR

Respiratory antimicrobial resistance prediction.

Never recommends antibiotics.

---

ARMD

Hospital antimicrobial resistance prediction.

Never recommends antibiotics.

---

WHO Knowledge Engine

Evidence only.

Contains

• AWaRe

• Guidelines

• Drug Information

• Stewardship

Contains NO AI.

---

Decision Engine

Deterministic reasoning.

Combines

SOAR

ARMD

WHO

Patient

Produces recommendations.

NOT machine learning.

---

Explainability Engine

Produces clinician-friendly explanations.

Never predicts.

---

# Current Repository

Project structure already exists.

Do NOT redesign folders.

Use the existing architecture.

Main directories include

apps/

packages/

docs/

infra/

---

# Read Before Coding

Always read these first.

.github/copilot-instructions.md

docs/architecture/

docs/api/

packages/clinical-schemas/

These documents define the official architecture.

Never contradict them.

---

# Coding Standards

Use

Python 3.12

FastAPI

Pydantic v2

SQLAlchemy 2.x

Dependency Injection

Type hints

Docstrings

Repository Pattern

Service Layer Pattern

Keep functions small.

Keep modules focused.

Never create giant files.

---

# Things You Must NOT Do

Do NOT

• redesign architecture

• rename folders

• change API contracts

• change schema definitions

• move files

• invent business logic

• put clinical logic in routers

• put AI inside FastAPI

• bypass service layer

• bypass repository layer

• duplicate existing code

• modify WHO rules

unless explicitly instructed.

---

# Backend Rules

Routers

Only

• request validation

• dependency injection

• response formatting

Never contain business logic.

---

Services

Contain orchestration.

Never contain SQL.

---

Repositories

Contain persistence only.

Never contain clinical reasoning.

---

Models

Represent data.

No business logic.

---

Schemas

Represent API contracts.

Never database logic.

---

# API Standards

Use the official API response format.

Follow

API_Response_Standard.md

API_Error_Codes.md

Request_Lifecycle.md

Service_Contracts.md

---

# Documentation Rule

Every architectural addition requires documentation.

Whenever new modules are created

Update

docs/

if appropriate.

---

# Verification Rule

After every implementation

Run

python -m compileall app

Resolve all errors before considering the task complete.

---

# Response Format

After completing work report ONLY

## Files Created

...

## Files Modified

...

## Verification

...

Do not provide long explanations.

Do not continue to another phase unless requested.

---

# Current Project Progress

Phase 1

Complete

---

Phase 2

Complete

Architecture

API Contracts

Clinical Schemas

Database Mapping

Deployment Architecture

Architecture Principles

Documentation

Complete

---

Phase 3

Completed

✓ FastAPI Bootstrap

✓ Middleware

✓ Configuration

✓ Database Integration

✓ Authentication Scaffold

✓ Service Layer

✓ API Router Structure

✓ Clinical Case Schema

✓ Clinical Case Repository

✓ Clinical Case Service

✓ Clinical Case API

Remaining

• Step 9 Logging & Audit

• Step 10 Testing

---

Future Phases

Phase 4

WHO Knowledge Engine

Phase 5

Decision Engine

Phase 6

Explainability Engine

Phase 7

SOAR Integration

Phase 8

ARMD Integration

Phase 9

Frontend

Phase 10

Deployment

Phase 11

Validation

---

# Your Role

You are implementing an existing architecture.

You are NOT designing one.

If something appears inconsistent,

ASK before changing it.

Architecture documentation is the source of truth.

When documentation and code disagree,

assume documentation is correct unless instructed otherwise.

---

# Development Goal

Produce production-quality, maintainable, modular, documented software suitable for:

• MSc/PhD research

• publication

• future hospital deployment

• future regulatory review

Code quality is more important than speed.

Never sacrifice architecture for convenience.