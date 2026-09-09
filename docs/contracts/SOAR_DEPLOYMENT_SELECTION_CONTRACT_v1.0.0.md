# SOAR Deployment Selection Contract v1.0.0

Status: FROZEN

## Owner and producer

- **Selector owner:** approved caller/platform routing boundary.
- **Producer:** the caller or platform component that owns the validated request context.
- **SOAR plugin role:** exact deployment execution only; it does not infer or choose a replacement deployment.

No backend component currently derives the ID from clinical concepts. Explicit caller ownership is therefore the selected safe architecture.

## Input and allowed values

The only allowed selector is:

```json
{
  "routing_context": {
    "deployment_id": "Ceftriaxone_Haemophilus_influenzae"
  }
}
```

`deployment_id` must be a non-empty string and must exactly match a valid artifact-backed ID in `DeploymentRegistry`. The registry's allowed values are discovered from directories containing both `deployment_info.json` and `feature_schema.json`.

Organism, species, pathogen, antimicrobial, antibiotic, filename tokens, similarity, and first-valid ordering are not selector inputs.

## Validation and propagation

```text
PipelineExecutionRequest.routing_context
    -> ClinicalDecisionRequest.context
    -> WorkflowManager
    -> adapt_prediction_request("soar", ...)
    -> PredictionRequest.context.deployment_id
    -> SOARPredictionPlugin._select_deployment()
    -> DeploymentRegistry.get_by_id()
```

The adapter requires the explicit ID for SOAR and copies only the validated routing key into the plugin context. Clinical payload fields remain separate.

## Failure behavior

- Missing, blank, or non-string ID: `PLUGIN_INPUT_VALIDATION_ERROR` at the adapter boundary or `SOAR_DEPLOYMENT_SELECTION_ERROR` at plugin selection.
- Unknown or invalid ID: `SOAR_DEPLOYMENT_SELECTION_ERROR`.
- No first-deployment fallback.
- No implicit organism/antimicrobial selection.
- No silent deployment substitution.

## Auditability

The request ID, routing context, selected deployment ID, deployment metadata, and execution metadata remain available to the backend execution/audit path. The selector is deterministic: one exact input ID yields one exact registry record.

## Frontend responsibility

Frontend code must not infer or expose a deployment selector as a clinical mapping. A later consumer may submit an approved exact routing context, but the backend remains the validation authority.
