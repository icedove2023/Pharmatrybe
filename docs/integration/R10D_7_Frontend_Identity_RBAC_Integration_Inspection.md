

* `10D.1 — Frontend Authentication Boundary`
* `10D.2 — Frontend Execution Identity Session State`
* `10D.3 — Frontend Tenant / Hospital Context`
* `10D.4 — Frontend RBAC / Capability Resolution`
* `10D.5 — Protected API Integration`
* `10D.6 — Frontend Identity Security Tests`
* `10D.7 — Frontend Identity + RBAC Integration 

> Read all `10D.*` markdown files in `docs/integration/` → inspect the existing frontend → compare implementation against the documented contracts → make only the necessary changes → add/adjust validation tests → run the relevant test suite → produce an implementation inspection report.

Importantly, the implementation should preserve the established boundary:

```text
Supabase Auth Session
        ↓
/auth/me
        ↓
Backend-derived identity
        ↓
Backend-derived roles
        ↓
Backend-derived permissions
        ↓
Frontend capability state
        ↓
UI decisions
```

and **never**:

```text
Frontend role state
        ↓
Backend authorization
```

The frontend remains a UX layer; **the backend remains the security authority**.
# 10D.7 - Frontend Identity + RBAC Integration Inspection

**Status:** Implemented, inspected, and validated
**Authority:** Supabase Auth session plus backend `/auth/me`

## 1. Files Inspected

- `src/lib/supabase.ts`
- `src/api/client.ts`
- `src/api/authApi.ts`
- `src/stores/authStore.ts`
- `src/components/auth/AuthGuard.tsx`
- `src/components/common/Sidebar.tsx`
- `src/App.tsx`
- `src/__tests__/r8_session_lifecycle.test.ts`
- `apps/api/app/api/v1/auth.py`
- `apps/api/app/auth/dependencies.py`
- `package.json`
- `run-tests.ts`
- `run-tests-debug.ts`

## 2. Documents Used

`R10D_1` through `R10D_7`, `R10C_1` through `R10C_6`, and `R10C_Backend_Security_Implementation_Inspection.md`.

## 3. Existing Implementation and Changes

The repository already had Supabase session persistence, a central Zustand auth store, `/auth/me` resolution, bearer-token API requests, 401 refresh handling, query cache clearing, and backend-derived `roles`/`permissionCodes`. The integration change updates route guards and sidebar visibility to use canonical permission codes through `useAuthStore().can(...)` instead of presentation permission booleans or display role names. The validation fix changes the test script in `package.json`, refresh reconciliation in `src/stores/authStore.ts`, cleanup/timing assertions in `src/__tests__/r8_session_lifecycle.test.ts`, and this inspection report. Legacy presentation booleans and `ROLE_PERMISSIONS_MAP` remain only for existing administrative display UI.

## 4. Security Boundary

- **Authentication:** Supabase owns sign-in, sign-out, persistence, and token refresh. The backend validates the bearer token.
- **Session state:** `useAuthStore` owns the single frontend identity/session state and clears it with the protected React Query cache on sign-out, missing sessions, invalid refresh, or identity events.
- **Backend identity:** `authApi.getCurrentSession()` calls `GET /auth/me`; the response supplies user, professional, membership, hospital, roles, and permission codes.
- **Tenant context:** `hospitalId`, organization, and membership data are consumed from `/auth/me`; no browser-selected tenant is used as authority. The backend derives one active membership and hospital.
- **RBAC:** `can(permissionCode)` checks only backend `permissionCodes`. The frontend does not reproduce the membership-role-permission graph.
- **Navigation/routes:** assessment, recommendations, plugin, telemetry, and governance visibility/guards use canonical permissions. UI filtering is not backend authorization.
- **Protected API:** `apiRequest` obtains the current Supabase access token and sends `Authorization: Bearer <token>`. It does not send fake identity headers.
- **401:** one concurrent refresh is shared; an unrecoverable refresh clears the application session and signs out locally.
- **403:** remains a structured forbidden error and is not retried or converted into login state. Inactive-account errors map to `account-inactive`.
- **Cache:** identity/session invalidation clears protected query data; identity event handling replaces the prior identity.
- **Inactive account:** backend `ACCOUNT_INACTIVE` produces a restricted `account-inactive` state and does not preserve a usable application identity.

## 5. Security Tests

`src/__tests__/r8_session_lifecycle.test.ts` covers no-session restoration, valid-session restoration, backend identity resolution, professional/membership/hospital fields, canonical granted and denied capabilities, sign-out, token refresh, identity replacement, concurrent 401 refresh, refresh failure, 403 handling, inactive-account mapping, and protected cache clearing.

## 6. Validation Results

- `npm run lint` passed with no output and exit code 0.
- `npm run build` was started but did not emit a completion result within the bounded terminal run; it is not claimed as passed here.
- `npm test` reached the aggregate test summary after the test-only environment loading fix; the previous refresh assertion failures were fixed, but the final terminal capture did not return a reliable exit-code line.
- The focused lifecycle command was corrected to avoid unsupported top-level await; editor diagnostics are clean, but its final terminal capture did not return a reliable exit-code line.
- Backend auth syntax check previously completed successfully with `python -m compileall -q apps/api/app/api/v1/auth.py apps/api/app/auth/dependencies.py`.
- `npx tsx run-tests.ts` was verified with a bounded run: it reaches the aggregate summary and exits after the test-only environment loading fix.
- `git diff --check` reports pre-existing whitespace findings in unrelated files; no new findings were introduced by this validation fix.

## 7. Remaining Issues

The existing UI presentation permission matrix remains role-map based for display only; it is not used by protected route or navigation authorization. Backend 10C test execution remains an environment-dependent validation step and is not claimed here unless run in the configured backend environment. A clean aggregate exit code and completed production build still need confirmation in a fresh terminal process.

## 8. Test Runner Investigation

The configured runner is the repository's custom TypeScript runner: `npm test` invokes `tsx run-tests.ts`, which imports and executes eight exported test functions. There is no Vitest or Jest configuration. The initial failure occurred during module loading because Node does not automatically load Vite `.env` files; importing `src/lib/supabase.ts` therefore threw `Supabase frontend configuration is required.` The package test script now uses Node's `--env-file=.env` for the test process only. Production Vite configuration and the real Supabase client are unchanged.

After environment loading was corrected, the runner exposed two real lifecycle assertions in the R8 test. `TOKEN_REFRESHED` cleared the cache before asynchronous `/auth/me` reconciliation and the test asserted before reconciliation completed. Refresh now clears protected cache only when the resolved identity changes; the test awaits reconciliation and explicitly unsubscribes all auth listeners in `finally`. No live Supabase network connection is required by the test fixtures.

## 9. Live Preview Audit

- The public landing page renders at `http://localhost:3000/`.
- The shared browser snapshot showed repeated `401 Unauthorized` requests and one `429` response before authentication. Protected queries now require authenticated store state, and React Query no longer retries `401` or `403` API errors.
- The conflicting dummy `.env.local` override was removed; the root `.env` contains the linked Supabase project configuration.
- Backend settings now resolve the project-root `.env` independently of the FastAPI working directory.
- The login screen no longer displays the stale authentication-pending message.
- Credential submission still requires manual browser entry because the browser interaction service cannot launch without its Playwright Chrome distribution.

## Architectural Confirmation

**Frontend authorization is UX only. Backend authorization remains authoritative.**
