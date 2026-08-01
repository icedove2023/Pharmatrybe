# PharmaTrybe
## Shared API Versioning & Contract Rules

Version:
v1.0

Status:
Architecture Locked

---

# Purpose

This document defines the universal communication rules used by every
component inside PharmaTrybe.

Every service MUST obey these contracts.

These rules ensure:

• reproducibility
• traceability
• explainability
• interoperability
• future scalability

No service is allowed to invent its own payload format.

---

# Services Covered

The following services MUST follow this specification.

1. FastAPI Backend

2. SOAR/GSK AI Service

3. ARMD AI Service

4. WHO Knowledge Engine

5. Clinical Decision Engine

6. Explainability Engine

7. Frontend

---

# API Version

Current Version

v1

Every payload exchanged between services MUST include

{
    "contract_version":"v1"
}

Future versions

v2

v3

must remain backward compatible whenever possible.

---

# Universal Required Metadata

Every request must contain

request_id

Unique UUID.

Example

"0e93ac5b-d111-4897..."

Purpose

Trace the entire clinical workflow.

---

timestamp

ISO 8601

Example

2026-08-01T13:40:11Z

Purpose

Audit logging

---

source

Which component generated the request.

Possible values

frontend

backend

soar

armd

who

decision

explainability

---

contract_version

Example

v1

---

case_type

Possible values

Scenario_1

Scenario_2

Scenario 1

Existing resistant infection

Scenario 2

Empirical prescribing before resistance known

---

# Required Response Metadata

Every response MUST contain

request_id

status

processing_time_ms

service_name

contract_version

timestamp

Example

{
"request_id":"...",
"status":"success",
"processing_time_ms":242,
"service_name":"SOAR",
"contract_version":"v1"
}

---

# Standard Status Codes

Every service returns

success

partial_success

validation_error

knowledge_not_found

model_error

internal_error

timeout

unsupported_case

No custom status strings.

---

# Validation Rules

Services MUST reject

Missing request_id

Missing patient identifier

Invalid syndrome

Invalid organism

Missing mandatory demographics

Missing timestamp

Unknown contract version

---

# Nullable Rules

Allowed

renal_function

weight

culture_result

MIC

Not Allowed

request_id

patient_id

clinical_syndrome

case_type

contract_version

timestamp

---

# Date Format

Only

ISO 8601 UTC

Example

2026-08-01T12:55:01Z

Never use

local timezone

text timestamps

MM/DD/YYYY

DD/MM/YYYY

---

# Identifier Rules

Patient

patient_id

Encounter

encounter_id

Culture

culture_id

Recommendation

recommendation_id

Explanation

explanation_id

Every identifier must be globally unique.

---

# Data Types

Boolean

true

false

Integer

25

Float

0.87

Date

ISO 8601

Enum

Controlled vocabulary only

No free text when enum exists.

---

# Clinical Terminology

Clinical Syndrome

Controlled list

CAP

HAP

VAP

Bronchiectasis

COPD Exacerbation

Influenza

COVID-19

Unknown

---

Severity

Mild

Moderate

Severe

Critical

---

Susceptibility

S

I

R

Unknown

---

WHO Group

Access

Watch

Reserve

Not Classified

---

Confidence

Low

Medium

High

Very High

---

# Communication Rules

Frontend

↓

Backend

↓

SOAR

↓

ARMD (optional)

↓

WHO

↓

Decision Engine

↓

Explainability

↓

Backend

↓

Frontend

No service calls another service directly.

Everything passes through Backend.

---

# Error Handling

If SOAR fails

Backend returns

503

Model unavailable

If WHO unavailable

Decision Engine returns

No recommendation

instead of inventing one.

If ARMD unavailable

Scenario 1 continues

using SOAR + WHO only.

---

# Logging Rules

Every service logs

request_id

patient_id

service_name

timestamp

execution_time

status

No PHI stored in logs.

---

# Security Rules

Internal APIs only

HTTPS

JWT authentication

Role-based access

Audit trail mandatory

No anonymous service communication.

---

# Explainability Requirement

Every recommendation MUST be explainable.

Every recommendation must reference

SOAR evidence

ARMD evidence (if used)

WHO recommendation

Decision rules

Confidence

No recommendation may exist without an explanation.

---

# Reproducibility Rules

Given identical input

the services MUST produce

identical outputs

unless

knowledge base version

or

model version

changes.

---

# Version Tracking

Every response must include

model_version

knowledge_base_version

decision_engine_version

Example

{
"model_version":"SOAR_v1.0",
"knowledge_base_version":"WHO_2026.1",
"decision_engine_version":"Decision_v1.0"
}

---

# Architecture Principle

SOAR predicts.

ARMD predicts.

WHO recommends.

Decision Engine combines.

Explainability justifies.

Backend orchestrates.

Frontend presents.

No component performs another component's responsibility.

This separation is mandatory throughout PharmaTrybe.