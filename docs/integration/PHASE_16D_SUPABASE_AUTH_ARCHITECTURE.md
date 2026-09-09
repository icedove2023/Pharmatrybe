# Phase 16D — Supabase Auth Architecture

**Document:** `PHASE_16D_SUPABASE_AUTH_ARCHITECTURE.md`  
**Phase:** 16D  
**Status:** APPROVED AUTHENTICATION BASELINE — IMPLEMENTATION NOT PERFORMED
**Date:** 2026-08-19  
**Parent phase:** `PHASE_16C_ROLE_PERMISSION_MATRIX.md`  
**Previous phase:** `PHASE_16B_IDENTITY_TENANT_DATABASE_SCHEMA.md`  
**Source of truth reference:** `FRONTEND_BACKEND_INTEGRATION_REPORT.md`, `PHASE_16_AUTH_SUPABASE_AUDIT.md`, `PHASE_16A_IDENTITY_TENANT_ARCHITECTURE_DECISION.md`  

**Approval Authority:** `docs/integration/approved_integration_docs.md` explicitly approves Supabase Auth as identity/session authority, provider-managed session lifecycle, Vite/React client integration, bearer access-token use, and FastAPI application authorization. Any decision not covered by that baseline remains unresolved.

---

## 1. Purpose

This document defines the authentication architecture for PharmaTrybe using Supabase Auth as the proposed identity and authentication provider.

It establishes how PharmaTrybe should handle:

* user authentication;
* authenticated identity;
* Supabase Auth users;
* professional profiles;
* hospital memberships;
* invitations;
* account activation;
* sessions;
* access tokens;
* refresh tokens;
* authentication state;
* tenant resolution;
* role resolution;
* backend authentication;
* database access;
* Row Level Security;
* account lifecycle;
* hospital transfer;
* deactivation;
* authentication security boundaries.

This is an architecture document, not an implementation document. No authentication routes, Supabase configuration, migrations, RLS policies, JWT hooks, frontend authentication code, or backend middleware are created by this phase.

---

## 2. Architectural Context

```text
16A — Identity + Tenant Architecture
        ↓
16B — Identity + Tenant Database Schema
        ↓
16C — Role + Permission Matrix
        ↓
16D — Supabase Auth Architecture
        ↓
16E — Backend Authentication + RBAC
        ↓
16F — Implementation
```

The purpose of Phase 16D is therefore to answer:

> **How does an authenticated person become an authorized PharmaTrybe user without allowing authentication to bypass the identity, tenant, role, permission, and clinical-security architecture?**

---

## 3. Platform Security Boundary

Authentication is part of the PharmaTrybe Platform Core. The Plugin Framework explicitly identifies Authentication and Authorization as platform-core responsibilities rather than plugin responsibilities.

```text
                   PharmaTrybe Platform
                             │
            ┌────────────────┼────────────────┐
            │                │                │
     Authentication    Authorization        Audit
            │                │                │
            └────────────────┼────────────────┘
                             │
                        Platform Core
                             │
                      Plugin Manager
                             │
                          Plugins
```

---

## 4. Core Authentication Decision

The proposed authentication provider for PharmaTrybe is **Supabase Auth**.

Supabase Auth provides the authentication layer, while PharmaTrybe retains ownership of:

* professional identity;
* hospital membership;
* roles;
* permissions;
* tenant authorization;
* clinical authorization;
* audit;
* application-level security rules.

```text
Supabase Auth
     ↓
Authenticates the person

PharmaTrybe (FastAPI)
     ↓
Determines what the authenticated person is allowed to do
```

---

## 5. Authentication Is Not Authorization

This phase explicitly preserves the Phase 16C distinction:

* **Authentication:** Who are you?
* **Authorization:** What are you allowed to do?

Therefore:

$$\text{Supabase authentication success} \neq \text{PharmaTrybe authorization success}$$

A successfully authenticated Supabase user may still have:

* no professional profile;
* no hospital membership;
* an invitation that has not been accepted;
* a suspended membership;
* a deactivated membership;
* insufficient permissions.

---

## 6. Identity Architecture

```text
┌─────────────────────────────┐
│       Supabase Auth         │
│         auth.users          │
└──────────────┬──────────────┘
               │ user.id (UUID)
               ▼
┌─────────────────────────────┐
│ PharmaTrybe                 │
│ professional_profiles       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ hospital_memberships        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ membership_roles            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ roles / permissions         │
└─────────────────────────────┘
```

The Supabase user is the authentication identity. The PharmaTrybe profile and membership records provide the application identity and organizational context.

---

## 7. Sources of Truth Matrix

| Information | Source of Truth |
|---|---|
| Authentication identity | Supabase Auth (`auth.users`) |
| Authentication credentials | Supabase Auth |
| Authentication session | Supabase Auth |
| Professional profile | PharmaTrybe database (`professional_profiles`) |
| Hospital / Organisation | PharmaTrybe database (`hospitals`) |
| Hospital membership | PharmaTrybe database (`hospital_memberships`) |
| Membership status | PharmaTrybe database (`status`) |
| Department | PharmaTrybe database |
| Role | PharmaTrybe database (`roles`, `membership_roles`) |
| Permission | PharmaTrybe authorization model (`role_permissions`) |
| Clinical authorization | PharmaTrybe backend (`FastAPI /api/v1/...`) |
| Audit history | PharmaTrybe audit system |

---

## 8. One Active Membership Invariant

A health professional may have **only one active hospital membership at a time**:

* `MAX(active_memberships per professional) = 1`
* Historical memberships are retained for audit and lineage with status `DEACTIVATED` or `TRANSFERRED`.

---

## 9. Hospital Onboarding and Invitations

Hospital onboarding begins with an invitation created by an authorized `HOSPITAL_ADMIN`:

```text
Hospital Admin (Hospital A)
       ↓
Create invitation (via POST /api/v1/professionals/invite)
       ↓
Invitation bound to hospital_id
       ↓
Professional receives invitation
       ↓
Professional authenticates via Supabase Auth
       ↓
Professional profile established
       ↓
Hospital membership activated (status = 'ACTIVE')
```

---

## 10. Request Security & Application Boundary

```text
┌──────────────────────────────────────────────┐
│           Vite + React Frontend              │
│  (Auth UI / Session UI / Presentation Only)  │
└──────────────────────┬───────────────────────┘
                       │
                       │ Authenticate / Session
                       ▼
┌──────────────────────────────────────────────┐
│                Supabase Auth                 │
│  (Account, Login, Session, Bearer JWT)       │
└──────────────────────┬───────────────────────┘
                       │
                       │ Bearer JWT
                       ▼
┌──────────────────────────────────────────────┐
│             FastAPI Backend                  │
│  (Routes at /api/v1/...)                     │
│  - JWT Signature & Expiry Validation         │
│  - Identity Resolution (auth.users -> prof)  │
│  - Active Hospital Membership Resolution     │
│  - Role & Permission Resolution              │
│  - Clinical Rules & Recommendation Engine    │
│  - Audit Logging                             │
└──────────────────────┬───────────────────────┘
                       │
                       │ Tenant-Scoped Queries
                       ▼
┌──────────────────────────────────────────────┐
│           PostgreSQL Database                │
│  - RLS Defence in Depth                      │
│  - Global Knowledge (WHO Diseases/AWaRe)     │
│  - Tenant Data (Cases, Recommendations, etc) │
└──────────────────────────────────────────────┘
```

---

## 11. Security Invariants Summary

1. **Credentials Outside Application DB**: Passwords, salts, and session tokens remain exclusively in Supabase Auth.
2. **FastAPI Is Authoritative**: The frontend never talks directly to clinical PostgreSQL tables; all access passes through `/api/v1/...`.
3. **No Self-Privilege Escalation**: Users cannot self-assign roles, self-select hospitals, or modify JWT claims for authorization.
4. **Service Role Confidentiality**: Supabase service-role keys remain strictly server-side and are never exposed to the frontend.
5. **Plugins Sandboxed**: Plugins do not manage user authentication or bypass backend authorization.

---

## 12. Status

**PHASE 16D — SUPABASE AUTH ARCHITECTURE DEFINED**

**Implementation status:** Not started (architecture specification only)

**Parent phase:** `PHASE_16C_ROLE_PERMISSION_MATRIX.md`

**Next Phase:** `PHASE_16E_BACKEND_AUTHENTICATION_RBAC_DESIGN.md`
