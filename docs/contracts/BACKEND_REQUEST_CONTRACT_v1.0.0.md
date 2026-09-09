# Backend Request Contract v1.0.0

Status: FROZEN.

## Runtime path

`POST /api/v1/pipeline/execute` accepts `PipelineExecutionRequest`:

- `execution_mode`: platform-owned; only `sync` is executable.
- `patient_id`: caller-provided request identity.
- `case_id`: optional caller-provided context identifier.
- `plugin_selection`: optional explicit plugin IDs and metadata.
- `input_payload`: caller-provided dictionary; `case` is unwrapped when it is a dictionary.
- `response_mode`: accepted request metadata; no alternate execution mode is implemented.
- `request_id`: optional caller correlation ID; the platform generates one when omitted.
- `routing_context`: explicit platform/caller routing metadata, including SOAR `deployment_id` when SOAR is selected.

The route creates `ClinicalDecisionRequest`, then `WorkflowManager` creates a generic `PredictionRequest` for prediction plugins or passes payload/context to knowledge plugins.

## Ownership and transformations

- Plugin selection: caller-provided when `plugin_selection` is non-empty; otherwise `PluginRoutingPolicy` may select registered plugins for `AUTO` execution.
- Plugin IDs are canonicalized and checked against the registered plugin set. Unknown requested IDs produce HTTP 422.
- Context: route combines `routing_context` with `case_id`; `WorkflowManager` preserves the routing values through the explicit plugin adapter.
- SOAR `deployment_id`: explicit caller/routing context only; the platform route does not derive it.
- Payload: preserved after optional `case` unwrapping. No universal clinical mapping is performed.
- Patient/case identity: `patient_id` is preserved into pipeline responses and decision context.

## Validation and failures

- Non-sync execution returns HTTP 501.
- Unknown plugins return HTTP 422.
- Plugin runtime initialization failures return HTTP 503.
- Pipeline failures are converted to HTTP 422 by the route when the pipeline returns `status=error`.
- Prediction plugins may reject unsupported requests or plugin-specific missing routing/features.
- Knowledge plugins receive query payload/context through their plugin boundary; they are not prediction inputs.

This contract does not claim that all payload fields are supported by every plugin. Plugin-specific contracts and the clinical adaptation boundary are authoritative after orchestration. Unsupported clinical mappings fail or remain plugin-specific; they are not inferred.
