# Clinical Vocabulary
**PharmaTrybe – Shared Clinical Vocabulary**

Version: 1.0  
Status: Frozen

---

# Purpose

This document defines the controlled clinical vocabulary used across PharmaTrybe.

Every service, API, frontend component, database table, and AI model must use these values.

No free-text values are allowed where a controlled vocabulary exists.

---

# Clinical Syndromes

Allowed values

- CAP
- HAP
- VAP
- COPD Exacerbation
- Bronchiectasis
- Influenza
- COVID-19
- Community Respiratory Infection
- Hospital Respiratory Infection
- Unknown

---

# Infection Source

Allowed values

- Community Acquired
- Hospital Acquired
- Healthcare Associated
- Unknown

---

# Severity

Allowed values

- Mild
- Moderate
- Severe
- Critical

---

# Hospital Location

Allowed values

- ICU
- Emergency
- Inpatient
- Outpatient
- Ward
- Unknown

---

# Specimen Type

Allowed values

- Blood
- Urine
- Sputum
- Bronchoalveolar Lavage
- Endotracheal Aspirate
- Wound
- CSF
- Stool
- Tissue
- Other

---

# Organism Status

Allowed values

- Identified
- Not Identified
- Pending

---

# Susceptibility

Allowed values

- Susceptible (S)
- Intermediate (I)
- Resistant (R)
- Unknown

---

# Resistance Risk

Allowed values

- Low
- Moderate
- High
- Very High

---

# Confidence Level

Allowed values

- Low
- Medium
- High
- Very High

---

# WHO AWaRe Classification

Allowed values

- Access
- Watch
- Reserve
- Not Classified

---

# Recommendation Strength

Allowed values

- Strong
- Conditional
- Expert Opinion
- Insufficient Evidence

---

# Recommendation Status

Allowed values

- Recommended
- Alternative
- Avoid
- Contraindicated

---

# Clinical Decision Outcome

Allowed values

- Accepted
- Alternative Selected
- Manual Review Required
- No Recommendation Available

---

# Allergy Severity

Allowed values

- None
- Mild
- Moderate
- Severe
- Anaphylaxis

---

# Renal Function

Allowed values

- Normal
- Mild Impairment
- Moderate Impairment
- Severe Impairment
- Dialysis
- Unknown

---

# Liver Function

Allowed values

- Normal
- Mild Impairment
- Moderate Impairment
- Severe Impairment
- Unknown

---

# Pregnancy Status

Allowed values

- Pregnant
- Not Pregnant
- Unknown

---

# Immunocompromised Status

Allowed values

- Yes
- No
- Unknown

---

# Previous Antibiotic Exposure

Allowed values

- None
- Within 30 Days
- Within 90 Days
- More Than 90 Days
- Unknown

---

# Previous Resistant Organism

Allowed values

- Yes
- No
- Unknown

---

# ICU Exposure

Allowed values

- Current ICU
- Previous ICU
- Never ICU
- Unknown

---

# Nursing Home Exposure

Allowed values

- Yes
- No
- Unknown

---

# Stewardship Action

Allowed values

- Start Therapy
- Continue Therapy
- De-escalate
- Escalate
- Stop Therapy
- Review in 48 Hours

---

# Referral

Allowed values

- None
- Infectious Disease
- Microbiology
- ICU
- Respiratory Medicine

---

# Follow-up

Allowed values

- None
- Repeat Culture
- Repeat Laboratory Tests
- Repeat Imaging
- Clinical Review
- Stewardship Review

---

# Explainability Level

Allowed values

- Basic
- Standard
- Detailed
- Research

---

# Scenario Type

Scenario 1

Confirmed or suspected resistant infection requiring resistance-guided therapy.

Scenario 2

Empirical prescribing where resistance has not yet been confirmed.

---

# Core Architecture Principle

SOAR and ARMD consume these vocabularies.

WHO uses these vocabularies.

Decision Engine reasons using these vocabularies.

Explainability references these vocabularies.

Frontend displays these vocabularies.

No component may introduce new clinical values without updating this document.