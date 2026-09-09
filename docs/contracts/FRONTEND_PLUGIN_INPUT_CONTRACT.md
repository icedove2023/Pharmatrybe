# Frontend Plugin Input Contract

A frontend plugin input contract is an approved declaration of data a plugin officially accepts from the frontend workflow.

## Required identity

```text
displayName
`pluginId
contractId
contractVersion
schemaVersion
displayName
status
provenance
inputSchema
supportedExecutionMode`
```

`status` must be `approved`. Provenance must identify owner, source artifact, artifact version, approver, and approval timestamp. Versions use semantic version syntax. Only `sync` execution is supported by the current frontend model.

## Ownership

The input schema owns field identity, types, requiredness, constraints, and allowed values. UI metadata may control labels, help text, order, sections, and widgets, but every UI field must reference a declared schema property.

A model feature, preprocessing column, artifact field, database column, or plugin metadata entry is not a frontend contract.

## Resolution

The registry resolves exact `pluginId@contractVersion` pairs. It never uses fuzzy matching, semantic aliases, first-match behavior, model inspection, or fallback versions.

Missing, duplicate, invalid, deprecated, unapproved, and unsupported contracts fail closed.

## Current status

No frontend-visible approved production contracts are registered for SOAR, ARMD, or WHO. Their current UI surfaces therefore remain compatibility/retrieval surfaces and do not become dynamic clinical forms.
