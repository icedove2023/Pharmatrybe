# Backend_Database_Standards.md

---

# PharmaTrybe

## Backend Database Standards

### Version 1.0

**Project**

An Explainable Clinical Decision Support System (CDSS) for Personalized Antimicrobial Prescribing and Antimicrobial Stewardship

---

# Purpose

This document defines the official database engineering standards for the PharmaTrybe backend.

Every database object, repository, migration, API endpoint, AI module, and future knowledge source must comply with these standards.

The goals are to ensure:

* Clinical safety
* Explainability
* High performance
* Data consistency
* Scalability
* Maintainability
* Auditability
* Easy integration of future knowledge sources

These standards are mandatory for all future development.

---

# Database Philosophy

The database is not merely storage.

It is the central clinical knowledge layer of PharmaTrybe.

The application logic must never hardcode clinical recommendations.

Instead,

Knowledge → Database

Decision Engine → Reads Knowledge

Explainability Engine → Reads Knowledge

Frontend → Reads Structured Results

---

# Guiding Principles

## 1. Clinical data must never be duplicated.

Knowledge is stored once.

Referenced everywhere.

---

## 2. Database stores facts.

Never opinions.

Never AI hallucinations.

---

## 3. Every recommendation must be traceable.

Every recommendation must link back to

WHO

SOAR

ARMD

Future sources

---

## 4. Every record must be explainable.

Every recommendation must answer

Why?

Where?

Who published it?

When?

Confidence?

---

# Database Technology

Official stack

Database

PostgreSQL

Hosted on

Supabase PostgreSQL

ORM

SQLAlchemy 2.x

Migration

Alembic

Python

3.12+

---

# Naming Convention

Tables

Lowercase plural

Example

```
diseases

recommendations

pathogens

drugs

diagnostics
```

Never

```
Disease

DiseaseTable

tblDisease
```

---

Columns

snake_case

Example

```
disease_id

chapter_number

care_level

source_pages
```

---

Primary Keys

Always

```
tablename_id
```

Example

```
disease_id

drug_id

recommendation_id

pathogen_id
```

---

Foreign Keys

Reference primary key exactly

Example

```
disease_id

drug_id

recommendation_id
```

---

Indexes

Always prefix

```
idx_
```

Example

```
idx_disease_name

idx_pathogen_name

idx_recommendation_population
```

---

Constraints

Prefix

```
chk_
```

Example

```
chk_positive_age

chk_duration_days
```

---

Unique Constraints

Prefix

```
uq_
```

---

Foreign Keys

Prefix

```
fk_
```

---

# UUID Policy

Every primary key is UUID.

Never auto-increment integers.

Reason

Distributed architecture

Easy synchronization

Safer APIs

Future offline support

---

# Relationships

Always explicit.

Example

Disease

↓

Recommendations

↓

Drug

↓

Evidence

↓

Pathogens

Never ambiguous joins.

---

# ORM Standards

Always use

```
Mapped[]

mapped_column()

relationship()
```

Never use legacy SQLAlchemy syntax.

---

Every relationship must define

```
back_populates

passive_deletes
```

when appropriate.

---

# Nullability Rules

Clinical identifiers

Never nullable

Example

```
disease_id

drug_id

pathogen_id
```

Optional metadata

Nullable

Example

```
notes

comments

population

pregnancy_notes
```

---

# Clinical Knowledge Sources

Each recommendation must indicate

WHO

SOAR

ARMD

Future Knowledge Source

Example

```
knowledge_source

knowledge_version

source_document

source_page
```

---

# Evidence Hierarchy

Every recommendation links to evidence.

Structure

```
Recommendation

↓

Evidence

↓

Publication

↓

Source
```

---

Never store evidence as free text only.

Always structured.

---

# Normalization

Target

Third Normal Form (3NF)

Avoid duplicated

drug names

pathogen names

guideline names

recommendation text

---

# Join Tables

Many-to-many relationships use bridge tables.

Example

```
recommendation_pathogens

recommendation_drugs

disease_pathogens
```

Never store arrays of IDs.

---

# Lookup Tables

Use lookup tables whenever possible.

Examples

Severity

Care Level

Recommendation Type

Population

Pregnancy Category

Renal Function

Stewardship Category

---

# Text Storage

Long clinical text

TEXT

Names

VARCHAR

Codes

VARCHAR

UUID

UUID

Numbers

INTEGER

DECIMAL

NUMERIC

---

# Clinical Safety Rules

Never delete

WHO knowledge

SOAR knowledge

ARMD knowledge

Instead

Archive

Deactivate

Version

---

# Versioning

Every knowledge source includes

```
version

publication_date

effective_date

review_date
```

Future guideline updates must create new versions.

Never overwrite historical knowledge.

---

# Auditability

Every change must record

Who

When

What

Old Value

New Value

Reason

Tables

```
audit_log

knowledge_versions
```

---

# Explainability Support

Every recommendation stores

Knowledge Source

Evidence Strength

Confidence

Publication

Guideline Page

Clinical Notes

Reasoning Metadata

Explainability never reconstructs missing information.

Everything required should already exist in the database.

---

# Performance Standards

Index

Primary Keys

Foreign Keys

Disease Names

Drug Names

Pathogen Names

Search Columns

Recommendation Type

Population

Severity

Knowledge Source

---

Avoid

SELECT *

Always retrieve only required columns.

---

Repository Pattern

Application never queries SQL directly.

Flow

```
Controller

↓

Service

↓

Repository

↓

Database
```

---

Repositories

One repository per entity.

Example

```
DiseaseRepository

DrugRepository

RecommendationRepository

EvidenceRepository

PathogenRepository
```

---

Transactions

Multi-table operations

Always transactional.

Either

Everything succeeds

or

Everything rolls back.

---

Migration Standards

All schema changes

Alembic only.

Never modify production tables manually.

Every migration

Named

Reviewed

Versioned

Documented

---

Soft Delete Policy

Clinical knowledge

Never permanently deleted.

Use

```
is_active

deleted_at
```

where appropriate.

---

Clinical Data Integrity

Every recommendation must satisfy

Existing disease

Existing drug

Existing source

Existing evidence

Existing pathogen

No orphan records allowed.

---

Future Knowledge Sources

Database must support

WHO

SOAR

ARMD

NICE

IDSA

ESCMID

Local Hospital Guidelines

National Formularies

Research Papers

LLM-derived validated knowledge

without redesigning the schema.

---

Scalability

Database must support

Millions of patients

Millions of recommendations

Multiple hospitals

Multiple countries

Multiple guideline editions

Without architectural redesign.

---

# Security Standards

Never expose internal IDs unnecessarily.

Parameterized queries only.

No dynamic SQL.

No raw SQL in controllers.

Principle of least privilege for database users.

---

# Backup Strategy

Daily automated backups.

Point-in-time recovery enabled.

Schema version tagged with each release.

---

# Database Quality Checklist

Before any schema is accepted:

* Primary keys use UUID.
* Table names are lowercase plural.
* Columns use snake_case.
* Relationships are normalized.
* Foreign keys are defined.
* Constraints are present.
* Indexes are added where required.
* Knowledge source is traceable.
* Explainability fields exist.
* Audit support is included.
* Alembic migration created.
* Repository implemented.
* Unit tests written.
* Documentation updated.

---

