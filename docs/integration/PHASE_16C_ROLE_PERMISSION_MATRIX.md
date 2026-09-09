# Phase 16C — Role & Permission Matrix

**Document:** `PHASE_16C_ROLE_PERMISSION_MATRIX.md`  
**Phase:** 16C  
**Status:** APPROVED AUTHORIZATION BASELINE — IMPLEMENTATION NOT PERFORMED
**Date:** 2026-08-19  
**Parent decision:** `PHASE_16B_IDENTITY_TENANT_DATABASE_SCHEMA.md`  
**Source of truth reference:** `FRONTEND_BACKEND_INTEGRATION_REPORT.md`, `PHASE_16_AUTH_SUPABASE_AUDIT.md`, `PHASE_16A_IDENTITY_TENANT_ARCHITECTURE_DECISION.md`  

**Approval Authority:** `docs/integration/approved_integration_docs.md` explicitly identifies this role and permission matrix as the canonical authorization model. This document remains an authorization specification; implementation still requires the approved downstream slice.

---

## 1. Purpose

This document defines the proposed authorization model and canonical role-permission matrix for PharmaTrybe.

It establishes:

* application roles;
* permission structure;
* role scope;
* hospital administrative boundaries;
* professional access boundaries;
* clinical-data access principles;
* platform versus tenant responsibilities;
* permission inheritance rules;
* authorization invariants;
* the relationship between authentication, membership, roles, permissions and tenant scope.

This document is an **authorization design specification**. It is **not** an implementation.

---

# 2. Architectural Context

Phase 16C builds directly on the identity and tenant model established in Phase 16B.

The authorization chain is:

```text
Authentication
      ↓
Professional Identity
      ↓
Active Hospital Membership
      ↓
Role
      ↓
Permission
      ↓
Resource
      ↓
Action
      ↓
Authorization Decision
```

The most important architectural principle is:

> **A role has meaning only within an organizational membership context.**

A user's authentication identity alone does not determine what the user can access.

The existing PharmaTrybe architecture places **Authentication and Authorization in the Platform Core**, rather than in plugins. 

The Plugin Framework also explicitly states that plugins must not bypass authentication, authorization, or audit controls. 

Therefore, Phase 16C defines authorization as a **platform-level capability**.

---

# 3. Role Taxonomy Alignment

The Phase 16 audit identified a mismatch between frontend and backend role vocabularies:

* **Frontend UI vocabulary:** `Infectious Disease Specialist`, `General Practitioner`, `Pharmacist`, `Admin`, `Researcher`
* **Backend scaffold vocabulary:** `Clinician`, `Laboratory Scientist`, `Stewardship Team`, `Administrator`

Phase 16C reconciles these into the proposed canonical application roles:

| Canonical Role Identifier | Maps From Frontend | Maps From Backend Scaffold | Primary Responsibility |
|---|---|---|---|
| `HOSPITAL_ADMIN` | `Admin` | `Administrator` | Hospital administration, professional onboarding, governance |
| `CLINICIAN` | `General Practitioner` | `Clinician` | Clinical assessment, case creation, recommendation request |
| `PHARMACIST` | `Pharmacist` | `Stewardship Team` | Medication review, dosing, AWaRe classification, stewardship |
| `LABORATORY_SCIENTIST` | *(Specialist flow)* | `Laboratory Scientist` | Laboratory diagnostics, culture & AST entry, microbiology |
| `INFECTIOUS_DISEASE_SPECIALIST` | `Infectious Disease Specialist` | `Clinician` + `Steward` | Complex AMR case review, reserve antibiotic overrides |
| `RESEARCHER` | `Researcher` | *(Read-only)* | Approved surveillance analytics, de-identified research access |

---

# 4. Permission Model

Permissions use the standard resource-action structure:

```text
<resource>:<action>
```

Standard action vocabulary: `VIEW`, `CREATE`, `UPDATE`, `DELETE`, `INVITE`, `ACTIVATE`, `SUSPEND`, `DEACTIVATE`, `APPROVE`, `EXECUTE`, `EXPORT`, `CONFIGURE`.

---

# 5. Canonical Role-Permission Matrix

| Resource / Capability | Hospital Admin | Clinician | Pharmacist | Lab Scientist | ID Specialist | Researcher |
|---|---:|---:|---:|---:|---:|---:|
| View hospital profile (`hospital:view`) | ✓ | ✓ | ✓ | ✓ | ✓ | Limited |
| Manage hospital profile (`hospital:update`) | ✓ | — | — | — | — | — |
| Invite professionals (`professionals:invite`) | ✓ | — | — | — | — | — |
| View professionals (`professionals:view`) | ✓ | ✓ | ✓ | ✓ | ✓ | Limited |
| Manage membership (`professionals:manage`) | ✓ | — | — | — | — | — |
| Assign roles (`roles:assign`) | ✓ | — | — | — | — | — |
| Suspend/deactivate membership | ✓ | — | — | — | — | — |
| View patients (`patients:view`) | Policy | ✓ | ✓ | Limited | ✓ | Approved |
| Create patients (`patients:create`) | — | ✓ | Policy | — | ✓ | — |
| View clinical cases (`cases:view`) | Policy | ✓ | ✓ | ✓ | ✓ | Approved |
| Create clinical cases (`cases:create`) | — | ✓ | ✓ | — | ✓ | — |
| Update clinical cases (`cases:update`) | — | ✓ | Policy | Lab scope | ✓ | — |
| View lab results (`laboratory:view`) | Policy | ✓ | ✓ | ✓ | ✓ | Approved |
| Enter lab results (`laboratory:create`) | — | — | — | ✓ | — | — |
| View recommendations (`recommendations:view`) | Policy | ✓ | ✓ | Limited | ✓ | Approved |
| Request recommendation (`recommendations:request`) | — | ✓ | ✓ | Policy | ✓ | — |
| Review recommendation (`recommendations:review`) | — | ✓ | ✓ | Limited | ✓ | — |
| View WHO guidelines (`guidelines:view`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Manage hospital guidelines (`guidelines:manage`) | ✓ | — | — | — | — | — |
| View stewardship policies (`stewardship:view`) | ✓ | ✓ | ✓ | ✓ | ✓ | Approved |
| Manage stewardship policies (`stewardship:manage`) | ✓ | — | Policy | — | — | — |
| View plugins (`plugins:view`) | ✓ | — | — | — | — | — |
| Configure plugins (`plugins:configure`) | ✓ | — | — | — | — | — |
| Manage workflows (`workflows:manage`) | ✓ | — | — | — | — | — |
| Execute approved workflows (`workflows:execute`) | — | ✓ | ✓ | ✓ | ✓ | Approved |
| View audit events (`audit:view`) | ✓ | Own scope | Own scope | Own scope | Own scope | Approved |
| Export data (`data:export`) | Controlled | Controlled | Controlled | Controlled | Controlled | Controlled |

---

# 6. Authorization Invariants

1. **Authentication ≠ Authorization**: Being authenticated does not grant clinical or admin access.
2. **Membership Required**: Normal hospital access requires an active membership (`status = 'ACTIVE'`).
3. **Tenant Boundary**: All tenant-owned resources are constrained by `hospital_id`. Cross-tenant requests are denied (`403 Forbidden`).
4. **Deny-by-Default**: Access is denied unless an explicit permission is resolved for the active membership.
5. **Separation of Administrative and Clinical Authority**: `HOSPITAL_ADMIN` manages the tenant; administrative authority does not automatically grant clinical prescribing privileges.
6. **Backend Is Authoritative**: Client UI state (`Zustand`, `AuthGuard`, browser token cache) is presentation-only. FastAPI (`/api/v1/...`) evaluates every request.
7. **Database Defence in Depth**: PostgreSQL RLS enforces tenant boundaries at the database layer.

---

# 7. Status

**PHASE 16C — ROLE & PERMISSION MATRIX DEFINED**

**Implementation status:** Not started (matrix specification only)

**Parent decision:** `PHASE_16B_IDENTITY_TENANT_DATABASE_SCHEMA.md`

**Next Phase:** `PHASE_16D_SUPABASE_AUTH_ARCHITECTURE.md`
