import { FormValidationIssue, FormValidationResult, JsonSchema, PluginInputContract } from './types';
import { PluginContractError } from './errors';

const SUPPORTED_SCHEMA_KEYS = new Set([
  '$schema', 'type', 'title', 'description', 'properties', 'required', 'enum', 'items',
  'minimum', 'maximum', 'minLength', 'maxLength', 'pattern', 'format', 'additionalProperties',
]);
const SUPPORTED_TYPES = new Set(['string', 'number', 'integer', 'boolean', 'array', 'object']);
const VERSION_PATTERN = /^\d+\.\d+\.\d+$/;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function schemaIssues(schema: unknown, path = 'inputSchema'): string[] {
  if (!isRecord(schema)) return [`${path} must be an object.`];
  const issues: string[] = [];
  Object.keys(schema).forEach((key) => {
    if (!SUPPORTED_SCHEMA_KEYS.has(key)) issues.push(`${path}.${key} is unsupported.`);
  });
  if (schema.type !== undefined && (typeof schema.type !== 'string' || !SUPPORTED_TYPES.has(schema.type))) {
    issues.push(`${path}.type is unsupported.`);
  }
  if (schema.required !== undefined && (!Array.isArray(schema.required) || schema.required.some((field) => typeof field !== 'string'))) {
    issues.push(`${path}.required must be an array of strings.`);
  }
  if (schema.properties !== undefined) {
    if (!isRecord(schema.properties)) issues.push(`${path}.properties must be an object.`);
    else Object.entries(schema.properties).forEach(([key, value]) => issues.push(...schemaIssues(value, `${path}.properties.${key}`)));
  }
  if (schema.items !== undefined) issues.push(...schemaIssues(schema.items, `${path}.items`));
  if (schema.enum !== undefined && (!Array.isArray(schema.enum) || schema.enum.length === 0)) issues.push(`${path}.enum must be a non-empty array.`);
  if (schema.type === 'array' && schema.items === undefined) issues.push(`${path}.items is required for arrays.`);
  if (schema.type === 'object' && schema.properties === undefined) issues.push(`${path}.properties is required for objects.`);
  if (typeof schema.pattern === 'string') {
    try { new RegExp(schema.pattern); } catch { issues.push(`${path}.pattern is invalid.`); }
  }
  return issues;
}

export function validatePluginContract(contract: unknown): string[] {
  if (!isRecord(contract)) return ['Contract must be an object.'];
  const requiredStrings = ['pluginId', 'contractId', 'contractVersion', 'schemaVersion', 'displayName'];
  const issues = requiredStrings.flatMap((key) => typeof contract[key] === 'string' && contract[key] ? [] : [`${key} is required.`]);
  if (contract.status !== 'approved') issues.push('Contract status must be approved.');
  if (typeof contract.contractVersion !== 'string' || !VERSION_PATTERN.test(contract.contractVersion)) issues.push('contractVersion must use semantic version format.');
  if (contract.supportedExecutionMode !== 'sync') issues.push('Only synchronous execution is supported.');
  if (!isRecord(contract.provenance)) issues.push('provenance is required.');
  else ['owner', 'source', 'artifact', 'artifactVersion', 'approvedBy', 'approvedAt'].forEach((key) => {
    if (typeof contract.provenance?.[key] !== 'string' || !contract.provenance[key]) issues.push(`provenance.${key} is required.`);
  });
  issues.push(...schemaIssues(contract.inputSchema));
  if (contract.uiSchema !== undefined) {
    if (!isRecord(contract.uiSchema) || !Array.isArray(contract.uiSchema.fields)) issues.push('uiSchema.fields must be an array.');
    else contract.uiSchema.fields.forEach((field, index) => {
      if (!isRecord(field) || typeof field.field !== 'string' || !field.field) issues.push(`uiSchema.fields[${index}].field is required.`);
      else if (!isRecord((contract.inputSchema as JsonSchema).properties) || !Object.prototype.hasOwnProperty.call((contract.inputSchema as JsonSchema).properties, field.field)) issues.push(`uiSchema.fields[${index}] references an undeclared field.`);
    });
  }
  return issues;
}

export function assertValidPluginContract(contract: PluginInputContract): void {
  const issues = validatePluginContract(contract);
  if (issues.length > 0) throw new PluginContractError('CONTRACT_INVALID', 'Plugin input contract is invalid.', issues);
}

function typeMatches(schema: JsonSchema, value: unknown): boolean {
  if (value === null) return false;
  switch (schema.type) {
    case 'string': return typeof value === 'string';
    case 'number': return typeof value === 'number' && Number.isFinite(value);
    case 'integer': return typeof value === 'number' && Number.isInteger(value);
    case 'boolean': return typeof value === 'boolean';
    case 'array': return Array.isArray(value);
    case 'object': return isRecord(value);
    default: return true;
  }
}

function validateValue(schema: JsonSchema, value: unknown, path: string, issues: FormValidationIssue[]): void {
  if (!typeMatches(schema, value)) { issues.push({ path, message: `Expected ${schema.type}.`, keyword: 'type' }); return; }
  if (schema.enum && !schema.enum.some((allowed) => Object.is(allowed, value))) issues.push({ path, message: 'Value is not an allowed option.', keyword: 'enum' });
  if (typeof value === 'number') {
    if (schema.minimum !== undefined && value < schema.minimum) issues.push({ path, message: `Value must be at least ${schema.minimum}.`, keyword: 'minimum' });
    if (schema.maximum !== undefined && value > schema.maximum) issues.push({ path, message: `Value must be at most ${schema.maximum}.`, keyword: 'maximum' });
  }
  if (typeof value === 'string') {
    if (schema.minLength !== undefined && value.length < schema.minLength) issues.push({ path, message: `Value must contain at least ${schema.minLength} characters.`, keyword: 'minLength' });
    if (schema.maxLength !== undefined && value.length > schema.maxLength) issues.push({ path, message: `Value must contain at most ${schema.maxLength} characters.`, keyword: 'maxLength' });
    if (schema.pattern !== undefined && !new RegExp(schema.pattern).test(value)) issues.push({ path, message: 'Value has an invalid format.', keyword: 'pattern' });
  }
  if (schema.type === 'array' && Array.isArray(value) && schema.items) value.forEach((item, index) => validateValue(schema.items as JsonSchema, item, `${path}[${index}]`, issues));
  if (schema.type === 'object' && isRecord(value)) Object.entries(schema.properties || {}).forEach(([key, child]) => {
    if (value[key] !== undefined) validateValue(child, value[key], `${path}.${key}`, issues);
  });
}

export function validateFormValues(schema: JsonSchema, values: unknown): FormValidationResult {
  const issues: FormValidationIssue[] = [];
  if (!isRecord(values)) return { valid: false, issues: [{ path: '', message: 'Form values must be an object.', keyword: 'type' }] };
  (schema.required || []).forEach((field) => {
    if (values[field] === undefined || values[field] === null || values[field] === '') issues.push({ path: field, message: 'This field is required.', keyword: 'required' });
  });
  Object.entries(schema.properties || {}).forEach(([key, child]) => {
    if (values[key] !== undefined && values[key] !== '') validateValue(child, values[key], key, issues);
  });
  return { valid: issues.length === 0, issues };
}
