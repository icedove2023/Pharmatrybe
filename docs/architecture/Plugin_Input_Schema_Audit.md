# Plugin Input Schema Contract Audit

**Document Date:** 2026-08-30  
**Phase:** Backend Schema Contract Implementation  
**Status:** Complete

## Overview

This document details the backend plugin input schema contract for the PharmaTrybe clinical decision support platform. The contract exposes JSON Schema (Draft 2020-12) definitions for all registered plugins, enabling dynamic form generation and contract validation at the frontend boundary.

## Contract Components

### 1. Plugin Schema Discovery (`SchemaDiscoveryService`)

**File:** `apps/api/app/plugins/schema/discovery.py`

Provides live schema discovery from the plugin registry:

- **`get_available_plugin_schemas()`**: Returns schemas for all currently loaded plugins
  - Returns list of plugin metadata with JSON Schema definitions
  - Schema format: JSON Schema Draft 2020-12 with `$schema` URI
  
- **`get_plugin_schema(plugin_id: str)`**: Returns schema for a single plugin
  - Normalized schema with default type `object` and `additionalProperties: true`
  - Raises `KeyError` if plugin not registered
  - Raises `ValueError` if plugin doesn't return a valid schema object

### 2. Plugin Schema Composition (`PluginSchemaComposer`)

**File:** `apps/api/app/plugins/schema/composer.py`

Composes multiple plugin schemas into a unified contract:

- **`compose(plugin_ids)`**: Merges input schemas from selected plugins
  - Returns object with three keys:
    - `schema`: Merged JSON Schema
    - `field_provenance`: Field ownership and type information
    - `conflicts`: List of incompatible field definitions across plugins
  
**Field Provenance Structure:**
```json
{
  "field_name": {
    "owners": ["plugin1", "plugin2"],
    "types": ["string", "integer"]
  }
}
```

**Conflict Detection:**
- Incompatible types in same field across plugins are flagged
- Integer/number type coercion is allowed (backward compatible)
- String/boolean/object type conflicts are reported

### 3. Pipeline Schema Endpoint

**File:** `apps/api/app/api/v1/pipeline.py`

New endpoint: `GET /api/v1/pipeline/schema`

Returns the live composed schema for all available plugins:
```json
{
  "plugin_ids": ["who_knowledge", "armd", "soar"],
  "schema": { /* merged JSON Schema */ },
  "field_provenance": { /* field ownership tracking */ },
  "conflicts": [ /* incompatibility list */ ]
}
```

## Plugin Input Schema Definitions

### ARMD Prediction Plugin

**Plugin ID:** `armd`

Input schema properties:
- `age` (integer, min=0, max=120): Patient age in years
- `weight` (number, min=0): Patient weight in kilograms
- `egfr` (number, min=0): Estimated glomerular filtration rate
- `prior_antibiotics` (boolean): Antibiotic exposure in previous 90 days
- `recent_hospitalization` (boolean): Hospitalization in last 90 days
- `organism` (string): Suspected pathogen
- `infection_site` (string): Clinical infection site

**Required fields:** `age`

**Output schema:** Prediction probabilities, confidence, and explainability metadata

### SOAR Prediction Plugin

**Plugin ID:** `soar`

Input schema properties:
- `pathogen` (string): Suspected respiratory pathogen
- `culture` (string): Microbiology culture and sensitivity observations
- `infection_site` (string): Clinical infection site
- `organism` (string): Organism of interest
- `antimicrobial` (string): Target antimicrobial or treatment candidate
- `severity` (string): Clinical severity score or classification

**Required fields:** `pathogen`

**Output schema:** Predicted class, probability, confidence, and deployment metadata

### WHO Knowledge Plugin

**Plugin ID:** `who_knowledge`

Input schema properties:
- `diagnosis` (string): Primary infection diagnosis or syndrome
- `severity` (string): Clinical severity classification
- `infection_site` (string): Site of infection
- `population` (string): Target patient population or age cohort
- `query` (string): Free-text WHO guideline search term

**Required fields:** `diagnosis`

**Output schema:** Guideline recommendations, evidence level, and citations

## Field Provenance and Deduplication

The composer automatically deduplicates field definitions across plugins:

1. **Shared fields** (e.g., `infection_site` in SOAR and ARMD):
   - Single merged property in the output schema
   - Provenance tracks all owning plugins
   - Type is coerced to compatible form or flagged as conflict

2. **Plugin-specific fields** (e.g., `age` in ARMD only):
   - Included in merged schema with single owner
   - Clearly marked in provenance

3. **Type conflicts**:
   - Incompatible types across plugins are flagged
   - Examples: string vs. number, object vs. array
   - Integer/number coercion is allowed as both represent numeric values

## Contract Validation

### Test Suite

**File:** `apps/api/tests/test_plugin_input_schema_contract.py`

Six validation tests verify:

1. **Schema Availability**: All three core plugins return schemas
2. **JSON Schema Validity**: Each schema validates against Draft 2020-12
3. **Composition & Deduplication**: Merged schema correctly handles shared fields
4. **Conflict Detection**: Type conflicts are properly identified
5. **Error Handling**: Unknown and empty plugin selections are rejected
6. **API Contract**: Endpoint returns properly structured metadata

**Test Results:** ✅ 6/6 PASS

## Backward Compatibility

### Frontend Integration

The existing frontend static registry in `src/plugins/registry/pluginDefinitions.ts` can remain unchanged:
- Frontend continues to use hard-coded `formSchema` arrays
- New `/pipeline/schema` endpoint is available for dynamic form generation
- No breaking changes to existing UI

### Runtime Behavior

- Plugin runtime initialization is unaffected
- Prediction and knowledge plugin execution paths unchanged
- Schema exposure is read-only discovery; no schema enforcement on pipeline execution yet

## Future Extensions

1. **Schema Enforcement**: Validate patient payloads against composed schema at pipeline boundary
2. **Dynamic Frontend Forms**: Replace static plugin registry with live `/pipeline/schema` response
3. **Field Mapping**: Track field path mappings between frontend form fields and backend schema
4. **Versioning**: Include schema versions in provenance for compatibility tracking
5. **Conflict Resolution**: Provide automatic coercion rules for compatible type conflicts

## Implementation Notes

### Why JSON Schema Draft 2020-12?

- Industry standard for structured data validation
- Explicit `$schema` URI prevents ambiguity
- Supports complex constraints (min/max, required, additionalProperties)
- Compatible with OpenAPI 3.1 and other modern specifications

### Why Provenance Tracking?

- Enables frontend to display field ownership (e.g., "This field is used by ARMD and SOAR")
- Allows detection of shared fields for duplicate prevention
- Supports conflict resolution strategies
- Provides transparency for clinical auditing

### Why Deduplication?

- Merges redundant field definitions from multiple plugins
- Reduces form complexity and frontend rendering burden
- Prevents duplicate input fields for the same clinical parameter
- Maintains type compatibility across plugins using the same field

## Audit Trail

- **2026-08-30**: Schema contract implementation complete
- All plugins successfully publish JSON Schema input definitions
- Pipeline schema discovery and composition working correctly
- All 6 contract validation tests passing
- No runtime errors in plugin initialization
- Schema endpoint ready for frontend integration

---

**Next Steps:**
1. Frontend reconciliation: Add dynamic form generation from `/pipeline/schema` endpoint
2. Schema-driven validation: Enforce payload compliance at pipeline boundary
3. Extended documentation: Plugin Output Schema Contract (future phase)
