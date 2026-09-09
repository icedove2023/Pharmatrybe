# Phase 22 Field Admission Matrix

| Plugin | Field | Classification | Frontend allowed | Source / ownership | Transformation | Reason / use |
| --- | --- | --- | --- | --- | --- | --- |
| ARMD | `age` | ADMITTED | Yes | Official Clinical Case Schema; patient record/clinical case | None; backend may derive age groups | Direct identity and frozen runtime key |
| ARMD | `temperature` | ADMITTED | Yes | Clinical Case vital sign | None; backend preprocessing | Direct identity and frozen runtime key |
| ARMD | `creatinine` | ADMITTED | Yes | Clinical Case laboratory biomarker | None; backend preprocessing | Direct identity and frozen runtime key |
| ARMD | `bun` | ADMITTED | Yes | Clinical Case laboratory biomarker | None; backend preprocessing | Direct identity and frozen runtime key |
| ARMD | `wbc` | ADMITTED | Yes | Clinical Case laboratory biomarker | None; backend preprocessing | Direct identity and frozen runtime key |
| ARMD | `neutrophils` | ADMITTED | Yes | Clinical Case laboratory biomarker | None; backend preprocessing | Direct identity and frozen runtime key |
| ARMD | `lymphocytes` | ADMITTED | Yes | Clinical Case laboratory biomarker | None; backend preprocessing | Direct identity and frozen runtime key |
| ARMD | `lactate` | ADMITTED | Yes | Clinical Case laboratory biomarker | None; backend preprocessing | Direct identity and frozen runtime key |
| ARMD | `procalcitonin` | ADMITTED | Yes | Clinical Case laboratory biomarker | None; backend preprocessing | Direct identity and frozen runtime key |
| ARMD | `age_group`, `log_days_since_abx` | REJECTED_DERIVED | No | WP4 preprocessing | Backend-derived | Frontend must not calculate |
| ARMD | encoded/model fields | REJECTED_DERIVED | No | WP4 feature order/model metadata | Encoding/alignment/scaling | Model boundary |
| ARMD | `weight`, `egfr` | REJECTED_UNSUPPORTED_MAPPING | No | Legacy frontend only | No ARMD runtime identity | Kept for other clinical/dosing workflows, not ARMD |
| ARMD | care/device/history aliases | REJECTED_UNPROVEN | No | Runtime whitelist or legacy UI | Would require ownership/mapping | No frontend authority established |
| SOAR | `deployment_id` | REJECTED_ROUTING | No | Explicit caller/platform context | Exact registry lookup | Routing metadata only |
| SOAR | artifact fields | REJECTED_UNPROVEN | No | Deployment feature schemas | Scaling/encoding/passthrough | No request-time frontend provenance |
| SOAR | clinical aliases | REJECTED_UNSUPPORTED_MAPPING | No | Legacy UI/support keys | No deterministic mapping | No safe mapping to artifact fields |
