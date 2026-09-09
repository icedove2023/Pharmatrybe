# Phase 16E — Backend Authentication / RBAC Design

**Document:** `PHASE_16E_BACKEND_AUTHENTICATION_RBAC_DESIGN.md`  
**Phase:** 16E  
**Status:** APPROVED BACKEND AUTHORIZATION BASELINE — IMPLEMENTATION NOT PERFORMED
**Date:** 2026-08-19  
**Parent phase:** `PHASE_16D_SUPABASE_AUTH_ARCHITECTURE.md`  
**Previous phases:** `16A` → `16B` → `16C` → `16D`  
**Source of truth reference:** `FRONTEND_BACKEND_INTEGRATION_REPORT.md`, `PHASE_16_AUTH_SUPABASE_AUDIT.md`, `PHASE_16A_IDENTITY_TENANT_ARCHITECTURE_DECISION.md`  

**Approval Authority:** `docs/integration/approved_integration_docs.md` approves the Supabase Bearer JWT to FastAPI authentication boundary, backend identity/membership/RBAC resolution, tenant enforcement, and backend authorization authority. This document remains a design specification; implementation still requires the approved downstream slice.

---

## 1. Purpose

This document defines how PharmaTrybe's FastAPI backend will authenticate requests, resolve the authenticated professional, determine the professional's active hospital membership, resolve roles and permissions, enforce tenant boundaries, and authorize protected operations.

This phase translates the architectural decisions from:

* **16A** — Identity + Tenant Architecture
* **16B** — Identity + Tenant Database Schema
* **16C** — Role + Permission Matrix
* **16D** — Supabase Auth Architecture

into a concrete backend security architecture.

This remains a design document. No backend authentication implementation, middleware, dependency wiring, database migration, RLS policy, or Supabase configuration is performed by this document.

---

## 2. Core Architectural Principle

> **The frontend requests access. The backend decides access.**

The authoritative security chain:

```text
Supabase Auth (Bearer JWT)
      ↓
Authenticated Identity (sub / auth_user_id)
      ↓
PharmaTrybe Professional Profile (professional_id)
      ↓
Active Hospital Membership (hospital_id)
      ↓
Canonical Role (HOSPITAL_ADMIN, CLINICIAN, etc.)
      ↓
Resolved Permissions (resource:action)
      ↓
Tenant Scope (hospital_id match)
      ↓
Endpoint Authorization (/api/v1/...)
```

---

## 3. Request Security Pipeline

Every protected FastAPI request follows this conceptual pipeline:

```text
HTTP Request (Authorization: Bearer <token>)
     ↓
Extract Authorization Credential
     ↓
Verify Supabase JWT (signature, issuer, aud, exp)
     ↓
Resolve Auth User ID (auth.users.id)
     ↓
Resolve PharmaTrybe Professional (professional_profiles)
     ↓
Resolve Active Membership (hospital_memberships where status = 'ACTIVE')
     ↓
Resolve Hospital / Tenant Context (hospital_id)
     ↓
Resolve Roles (membership_roles -> roles)
     ↓
Resolve Permissions (role_permissions -> permissions)
     ↓
Build AuthorizationContext
     ↓
Endpoint Authorization (require_permission)
     ↓
Tenant Authorization (require_same_hospital)
     ↓
Business / Clinical Rules Execution
     ↓
Audit Log Event Generation
```

---

## 4. Reusable FastAPI Security Dependencies

```python
# Conceptual Dependency Architecture for FastAPI (/apps/api/app/auth/)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthenticatedUser:
    """Validates Supabase JWT and extracts verified user identity."""
    ...

async def get_authorization_context(
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AuthorizationContext:
    """Resolves professional profile, active membership, hospital_id, roles, and permissions."""
    ...

def require_permission(permission_name: str):
    """Dependency factory enforcing granular permission on AuthorizationContext."""
    async def permission_checker(
        context: AuthorizationContext = Depends(get_authorization_context)
    ):
        if not context.is_active_member:
            raise HTTPException(status_code=403, detail="Active hospital membership required")
        if permission_name not in context.permissions:
            raise HTTPException(status_code=403, detail=f"Permission '{permission_name}' denied")
        return context
    return permission_checker

def require_same_hospital(resource_hospital_id: str):
    """Enforces tenant isolation between current user context and targeted clinical resource."""
    async def tenant_checker(
        context: AuthorizationContext = Depends(get_authorization_context)
    ):
        if context.hospital_id != resource_hospital_id:
            raise HTTPException(status_code=403, detail="Cross-tenant resource access forbidden")
        return context
    return tenant_checker
```

---

## 5. Route Protection Matrix

| Route Category | Example Path | Authentication | Authorization Required | Tenant Scoped? |
|---|---|---|---|---|
| Public / Health | `GET /api/v1/health` | None | None | No |
| Global Knowledge | `GET /api/v1/who/diseases` | Optional / Public | Read WHO Guidelines | No (Global) |
| User Profile | `GET /api/v1/auth/me` | Bearer JWT | Authenticated User | Yes (Own profile) |
| Clinical Cases | `POST /api/v1/clinical-cases` | Bearer JWT | `cases:create` | Yes (`hospital_id`) |
| Recommendations | `POST /api/v1/recommendations/generate` | Bearer JWT | `recommendations:request` | Yes (`hospital_id`) |
| Admin Governance | `GET /api/v1/admin/users` | Bearer JWT | `professionals:view` | Yes (`hospital_id`) |
| Member Invite | `POST /api/v1/professionals/invite` | Bearer JWT | `professionals:invite` | Yes (`hospital_id`) |
| Role Assignment | `POST /api/v1/admin/roles/assign` | Bearer JWT | `roles:assign` | Yes (`hospital_id`) |

---

## 6. Tenant Query Filtering Pattern

For all tenant-owned models, query filtering must be enforced at the repository/database boundary:

```sql
-- Conceptual tenant-isolated query
SELECT * FROM clinical_cases
WHERE id = :case_id 
  AND hospital_id = :current_hospital_id;
```

RLS on PostgreSQL provides an additional defence-in-depth layer using `auth.uid()` mapped to active hospital membership.

---

## 7. Security Invariants Summary

1. **Deny by Default**: Requests without valid credentials or required permissions are rejected with `401 Unauthorized` or `403 Forbidden`.
2. **Fail Closed**: Database lookups for missing profiles or inactive memberships immediately fail closed.
3. **No Frontend Authority**: The React frontend is a presentation client; FastAPI enforces all business and clinical rules.
4. **Tenant Isolation**: Cross-hospital queries are forbidden and return generic access-denied responses to prevent resource enumeration.
5. **Auditable Actions**: All administrative mutations and clinical recommendation reviews produce immutable audit events.

---

## 8. Status

**PHASE 16E — BACKEND AUTHENTICATION & RBAC DESIGN DEFINED**

**Implementation status:** Not started (design specification only)

**Parent phase:** `PHASE_16D_SUPABASE_AUTH_ARCHITECTURE.md`

**Next Phase:** `PHASE_16F — Implementation` (Pending Phase 16A decision approval)
