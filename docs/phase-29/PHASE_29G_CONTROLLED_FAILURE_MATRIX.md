# Phase 29G Controlled Failure Matrix

| Scenario | Expected | Actual evidence | Status |
|---|---|---|---|
| Unauthenticated protected backend access | 401/deny | Auth dependency requires bearer token | READY_FOR_CONTROLLED_EXECUTION |
| Missing tenant/membership | Fail closed | Authorization context requires exactly one active membership | READY_FOR_CONTROLLED_EXECUTION |
| Unauthorized role/permission | 403 | RBAC dependencies and governance tests enforce denial | READY_FOR_CONTROLLED_EXECUTION |
| Missing SOAR field | Structured incomplete result | Resolver returns missing field and blocks payload | READY_FOR_CONTROLLED_EXECUTION |
| Unknown SOAR deployment | No fallback | Exact lookup raises selection error | READY_FOR_CONTROLLED_EXECUTION |
| Invalid SOAR enum | Validation failure | Focused contract tests reject invalid values | READY_FOR_CONTROLLED_EXECUTION |
| Numeric beta-lactamase bypass | Reject | Resolver reports unsupported mapping | READY_FOR_CONTROLLED_EXECUTION |
| WHO provider unavailable | Controlled error | Missing database configuration raises explicit error | READY_FOR_CONTROLLED_EXECUTION |
| Unsafe candidate | Rule precedence | Contraindication test excludes unsafe primary | READY_FOR_CONTROLLED_EXECUTION |
| Invalid interactive login | Authentication denied | Not attempted without browser control | NOT_VERIFIED |
| Audit retrieval failure | Explicit unsupported/unavailable | No supported retrieval endpoint exposed | NOT_VERIFIED |
| Post-sign-out protected route | Denied | Browser sequence not attempted | NOT_VERIFIED |
