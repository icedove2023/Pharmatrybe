# Phase 30 Failure Matrix

## Classification

### PRE_EXISTING_FAILURE
- `npm run lint` fails with six existing React Start/router errors in:
  - `src/router.tsx`
  - `src/routes/__root.tsx`
  - `src/server.ts`
  - `src/start.ts`
- The repository’s previous Phase 29 report classifies these as pre-existing and not a Phase 30 regression.

### TEST_FIXTURE_FAILURE
- The historical backend full-suite identity fixture issue associated with non-UUID `auth-user-id` remains a known issue in earlier evidence and is not a new Phase 30 regression.

### NOT_VERIFIED
- Authenticated browser login
- Clinician session restoration
- Tenant resolution from live signed-in user
- Assessment route access
- SOAR authenticated execution
- ARMD authenticated execution
- WHO authenticated recommendation path
- Audit retrieval
- Sign-out and protected route denial

### PHASE_30_REGRESSION
- No Phase 30 regression was identified in this session because we did not change application code.

### ENVIRONMENT_FAILURE
- The backend health endpoint was not reachable at `http://localhost:8001/health` during this session.
