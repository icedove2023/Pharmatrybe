# Backend Error Contract v1.0.0

Status: FROZEN at the FastAPI public boundary.

## Standard error envelope

The reusable API models are `ApiFailure` and `ApiError`:

- `success: false`
- `metadata`: request ID, timestamp, API version, processing time
- `error.code`: machine-readable code
- `error.message`: human-readable message
- `error.details`: optional structured details

## Runtime failure mapping

| Failure | Current behavior/code status | Safe handling |
| --- | --- | --- |
| Invalid request body | FastAPI/Pydantic HTTP 422 | Reject before plugin execution. |
| Non-sync pipeline mode | HTTP 501 | Do not start unsupported execution. |
| Unknown plugin | HTTP 422 | Do not execute an unregistered plugin. |
| Plugin runtime unavailable | HTTP 503 | Do not execute with incomplete registry. |
| Missing SOAR deployment ID | Adapter emits typed validation failure; public boundary maps it to structured `ApiFailure` | Reject; never infer or fallback. |
| Unknown SOAR deployment ID | `DeploymentSelectionError` internally | Reject exact lookup failure. |
| Missing SOAR artifact feature | `PredictionError` internally | Reject selected deployment request. |
| Model execution failure | `PredictionError`/plugin execution failure | Return safe pipeline error; no substitute model. |
| Knowledge query failure | provider/service failure result or `WHOServiceError` | Return failure/empty result according to the calling boundary; do not fabricate knowledge. |
| WHO database configuration failure | explicit `RuntimeError` when WHO configuration is absent | Fail startup/query path clearly. |
| Internal pipeline failure | pipeline `status=error`, then route HTTP 422 | Return safe error response without stack trace. |

## Normalization boundary

Internal typed exceptions remain intact. The FastAPI exception handlers always emit `ApiFailure`; `map_exception_to_code()` provides stable codes for typed adapter, SOAR, prediction, and WHO service failures. Route-specific status codes remain compatibility behavior, while response shape and stack-trace handling are frozen.
