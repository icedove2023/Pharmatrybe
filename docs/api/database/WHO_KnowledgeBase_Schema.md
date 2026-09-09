# WHO_KnowledgeBase_Schema.md

## WHO Respiratory CDSS Knowledge Base

**Version:** 2.1
**Database:** PostgreSQL 16+ (Supabase)
**Purpose:** WHO Respiratory Clinical Decision Support Knowledge Base

---

# 1. Overview

The WHO Knowledge Base is the authoritative repository of structured respiratory clinical guidance used by the PharmaTrybe Clinical Decision Support System (CDSS).

It contains normalized recommendations extracted from the WHO Respiratory Infection Guidelines.

The database is **read-only** during normal CDSS operation.

The application **never edits WHO knowledge**.

Instead, backend services retrieve structured recommendations and present them to the Decision Fusion Engine.

---

# 2. Design Philosophy

The schema follows third normal form (3NF) principles to eliminate duplication and improve maintainability.

The database separates:

* Diseases
* Drugs
* Pathogens
* Recommendations
* Evidence
* Diagnostics
* Stewardship Advice
* Monitoring Guidance
* Follow-up Guidance
* Referral Guidance

This enables independent updates to each knowledge domain while maintaining referential integrity.

---

# 3. Database Architecture

```
WHO Guideline

↓

Knowledge Extraction

↓

Normalization

↓

PostgreSQL Knowledge Base

↓

WHO Retrieval Engine

↓

Decision Fusion Engine

↓

Clinical Recommendation
```

The PostgreSQL database serves as the single source of truth for WHO clinical knowledge.

---

# 4. Entity Relationship Overview

```
Metadata

│

Diseases
│
├────────────── Recommendations ────────────── Drugs
│                     │
│                     │
│                     └──────── Recommendation_Pathogens
│
├────────────── Evidence
│
├────────────── Diagnostics
│
├────────────── Stewardship
│
├────────────── Monitoring
│
├────────────── Follow-up
│
├────────────── Referral
│
└────────────── Disease_Pathogens ───────────── Pathogens
```

---

# 5. Core Tables

## metadata

Stores import information for the WHO knowledge base.

Purpose

* Source tracking
* Version control
* Import audit
* Knowledge base statistics

Primary Key

* metadata_id

---

## diseases

Master list of all respiratory diseases covered by the WHO guideline.

Contains

* disease identifier
* disease name
* chapter information
* care level
* description
* source pages

Primary Key

* disease_id

Relationships

One disease may have:

* many recommendations
* many evidence statements
* many diagnostics
* many stewardship entries
* many monitoring entries
* many follow-up entries
* many referral entries
* many pathogens

---

## pathogens

Master list of unique pathogens.

Examples

* Streptococcus pneumoniae
* Haemophilus influenzae

Primary Key

* pathogen_id

Many-to-many relationship with:

* diseases
* recommendations

---

## drugs

Master list of antimicrobial agents.

Contains

* generic name
* WHO AWaRe group
* antibiotic class
* administration route
* notes

Primary Key

* drug_id

One drug may appear in many recommendations.

---

## evidence

Stores supporting evidence extracted from WHO guidance.

Contains

* evidence type
* evidence statement
* source page

One disease may contain many evidence statements.

Evidence may be linked to treatment recommendations.

---

## recommendations

Core treatment recommendations.

Contains

* linked disease
* linked drug
* linked evidence
* dose
* frequency
* duration
* target population
* severity
* care setting
* contraindications
* allergy criteria
* pregnancy criteria
* renal considerations
* hepatic considerations

This is the central clinical decision table.

---

## diagnostics

Stores WHO diagnostic guidance.

Examples

* Required investigations
* Laboratory tests
* Imaging recommendations

---

## stewardship

Stores antimicrobial stewardship recommendations.

Examples

* Avoid unnecessary antibiotics
* Review therapy after culture results
* De-escalation advice

---

## monitoring

Stores monitoring recommendations.

Examples

* Clinical review
* Oxygen monitoring
* Laboratory follow-up

---

## follow_up

Stores follow-up recommendations.

Examples

* Review intervals
* Reassessment timing
* Treatment completion

---

## referral

Stores referral recommendations.

Examples

* Specialist referral
* Hospital admission
* Escalation criteria

---

# 6. Junction Tables

## disease_pathogens

Associates diseases with likely pathogens.

Relationship

Disease ←→ Pathogen

Many-to-many

---

## recommendation_pathogens

Associates recommendations with the pathogens they target.

Relationship

Recommendation ←→ Pathogen

Many-to-many

---

# 7. Indexing Strategy

Indexes exist to optimise retrieval.

Primary indexes include:

* disease name
* drug generic name
* AWaRe category
* disease foreign keys
* evidence foreign keys
* recommendation foreign keys
* diagnostic foreign keys
* stewardship foreign keys
* monitoring foreign keys
* follow-up foreign keys
* referral foreign keys

These indexes support rapid retrieval by the WHO Retrieval Engine.

---

# 8. Referential Integrity

The schema uses foreign-key constraints throughout.

Examples include:

* Recommendation → Disease
* Recommendation → Drug
* Recommendation → Evidence
* Evidence → Disease
* Diagnostics → Disease
* Stewardship → Disease
* Monitoring → Disease
* Follow-up → Disease
* Referral → Disease

Cascade rules ensure consistent deletion where appropriate.

---

# 9. WHO Retrieval Model

The application does not query tables directly from API endpoints.

Instead:

```
API

↓

WHO Service

↓

WHO Repository

↓

PostgreSQL

↓

WHO Recommendation Bundle
```

Repositories are responsible for database access.

Services assemble complete guideline bundles.

---

# 10. Expected Retrieval Bundle

The WHO Retrieval Engine returns a structured object containing:

* Disease
* Recommendations
* Drugs
* Supporting Evidence
* Diagnostics
* Stewardship Advice
* Monitoring Guidance
* Follow-up Guidance
* Referral Guidance
* Associated Pathogens

This bundle is consumed by the Decision Fusion Engine.

---

# 11. Scope

This database stores structured WHO knowledge only.

It does **not** contain:

* Patient records
* Clinical cases
* Machine learning models
* Prediction results
* SOAR outputs
* ARMD outputs
* Decision Engine logic

Those components exist elsewhere within the PharmaTrybe architecture.

---

# 12. Maintenance

The WHO Knowledge Base should be updated only through the approved extraction and normalization pipeline.

Direct manual modification of production data is discouraged.

Schema changes must remain backward compatible with the Retrieval Engine and SQLAlchemy ORM models.

---

# 13. Future Extensions

The schema is designed to support future enhancements including:

* Additional WHO guideline editions
* Multiple guideline sources
* Versioned recommendations
* Clinical evidence grading
* Local antimicrobial adaptation
* Country-specific treatment guidance
* Explainability metadata

These enhancements should preserve the current normalized architecture wherever possible.
