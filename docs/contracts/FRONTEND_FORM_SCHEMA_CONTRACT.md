# Frontend Form Schema Contract

The form engine supports a deliberately small JSON Schema subset:

- `string`, `number`, `integer`, `boolean`, `array`, and `object` types;
- `properties`, `required`, and `items`;
- `enum`;
- `minimum`, `maximum`;
- `minLength`, `maxLength`, and `pattern`;
- optional `format` metadata.

Unsupported keywords are rejected during contract validation. Objects require `properties`; arrays require `items`. UI schema references must point to declared properties.

## Rendering

Widget selection is explicit or type-based: strings use text inputs, numeric types use numeric inputs, booleans use checkboxes, enums use selects, and arrays/objects are validated recursively. Field names are never interpreted as clinical concepts.

## Validation

Contract validation and form value validation are separate. Contract validation checks structure, approval, provenance, version, supported keywords, and UI references. Value validation checks requiredness, type, enum membership, ranges, string constraints, arrays, and nested objects.

## Safety

There is no automatic terminology mapping, prefill guessing, routing inference, or model-feature introspection. Unsafe mappings and unavailable adapters block submission.
