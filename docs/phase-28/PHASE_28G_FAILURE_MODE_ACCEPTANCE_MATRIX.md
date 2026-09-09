# Phase 28G Failure Mode Acceptance Matrix

| Scenario | Component | Expected | Actual | Status | Evidence |
|---|---|---|---|---|---|
| Invalid login | Auth provider/frontend | Authentication denied | Browser attempt not performed | NOT_VERIFIED | Authenticated browser capability unavailable |
| Unauthenticated access | Backend auth dependency | 401/deny | Code requires bearer token | READY_FOR_CONTROLLED_EXECUTION | `get_current_user` and focused auth tests |
| Invalid tenant context | Authorization context | Fail closed | Active membership and exactly one hospital required | READY_FOR_CONTROLLED_EXECUTION | Governance/plugin tests |
| Unauthorized action | RBAC | 403/access denied | Permission and role dependencies enforce denial | READY_FOR_CONTROLLED_EXECUTION | Governance/security tests |
| Missing SOAR input | SOAR resolver | Structured incomplete result | Missing required fields returned; execution blocked | READY_FOR_CONTROLLED_EXECUTION | Phase 23/24 tests |
| Unknown SOAR deployment | SOAR routing | No fallback | Explicit deployment selection raises | READY_FOR_CONTROLLED_EXECUTION | SOAR contract tests |
| Invalid enum | SOAR validation | Validation failure | Invalid region/country rejected | READY_FOR_CONTROLLED_EXECUTION | Phase 24 tests |
| Raw numeric beta value | SOAR contract | Rejected | Numeric bypass returns unsupported mapping | READY_FOR_CONTROLLED_EXECUTION | Phase 24/25 tests |
| Plugin execution failure | Runtime | Controlled error | Model/dependency errors are surfaced by runtime | READY_FOR_CONTROLLED_EXECUTION | Phase 27 dependency closure evidence |
| WHO unavailable | WHO provider | Controlled unavailable state | Missing database configuration raises clearly | READY_FOR_CONTROLLED_EXECUTION | WHO focused test |
| Unsafe candidate | Fusion/rules | Cannot become primary | Contraindication test excludes amoxicillin | READY_FOR_CONTROLLED_EXECUTION | Clinical decision tests |
| Audit persistence failure | Audit boundary | Explicit failure | Dedicated failure-path persistence was not exercised | NOT_VERIFIED | No authenticated failure injection performed |
