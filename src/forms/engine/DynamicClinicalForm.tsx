import React, { useState } from 'react';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { PluginContractError } from '@/plugins/contracts';
import { validateFormValues } from '@/plugins/contracts';
import type { FormValidationIssue, JsonSchema, PluginInputContract, UiField } from '@/plugins/contracts';

interface DynamicClinicalFormProps {
  contract: PluginInputContract;
  initialValues?: Record<string, unknown>;
  onChange?: (values: Record<string, unknown>) => void;
  onSubmit: (values: Record<string, unknown>) => void | Promise<void>;
  onCancel?: () => void;
  disabled?: boolean;
}

function fieldMetadata(contract: PluginInputContract, field: string): UiField | undefined {
  return contract.uiSchema?.fields.find((item) => item.field === field);
}

function labelFor(field: string, schema: JsonSchema, metadata?: UiField): string {
  return metadata?.label || schema.title || field;
}

function setValue(values: Record<string, unknown>, field: string, value: unknown): Record<string, unknown> {
  return { ...values, [field]: value };
}

function InputField({
  field,
  schema,
  value,
  required,
  issue,
  metadata,
  onChange,
  disabled,
}: {
  field: string;
  schema: JsonSchema;
  value: unknown;
  required: boolean;
  issue?: FormValidationIssue;
  metadata?: UiField;
  onChange: (value: unknown) => void;
  disabled: boolean;
}) {
  const id = `dynamic-field-${field.replace(/[^a-zA-Z0-9_-]/g, '-')}`;
  const label = labelFor(field, schema, metadata);
  const describedBy = issue ? `${id}-error` : schema.description ? `${id}-description` : undefined;
  const className = 'w-full rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset px-3 py-2 text-xs text-slate-text-primary focus-clinical disabled:cursor-not-allowed disabled:opacity-60';

  if (schema.type === 'boolean') {
    return <label htmlFor={id} className="flex items-center gap-2 text-xs font-semibold text-slate-text-primary">
      <input id={id} type="checkbox" checked={Boolean(value)} onChange={(event) => onChange(event.target.checked)} disabled={disabled} aria-invalid={Boolean(issue)} className="h-4 w-4 rounded text-[var(--color-clinical-500)]" />
      <span>{label}{required && <span className="ml-1 text-[var(--color-safety-critical)]">*</span>}</span>
    </label>;
  }

  const options = schema.enum || [];
  const widget = metadata?.widget || (options.length > 0 ? 'select' : schema.type === 'number' || schema.type === 'integer' ? 'number' : 'text');
  const inputType = widget === 'date' ? 'date' : widget === 'date-time' ? 'datetime-local' : schema.type === 'number' || schema.type === 'integer' ? 'number' : 'text';
  const scalarValue = value === undefined || value === null ? '' : String(value);

  return <div className="space-y-1">
    <label htmlFor={id} className="block text-xs font-semibold text-slate-text-secondary">{label}{required && <span className="ml-1 text-[var(--color-safety-critical)]">*</span>}</label>
    {widget === 'textarea' ? <textarea id={id} rows={3} value={scalarValue} onChange={(event) => onChange(event.target.value)} disabled={disabled} aria-invalid={Boolean(issue)} aria-describedby={describedBy} className={className} />
      : options.length > 0 && (widget === 'select' || widget === 'radio') ? <select id={id} value={scalarValue} onChange={(event) => onChange(event.target.value)} disabled={disabled} aria-invalid={Boolean(issue)} aria-describedby={describedBy} className={className}><option value="">Select...</option>{options.map((option) => <option key={String(option)} value={String(option)}>{String(option)}</option>)}</select>
        : <input id={id} type={inputType} value={scalarValue} min={schema.minimum} max={schema.maximum} minLength={schema.minLength} maxLength={schema.maxLength} pattern={schema.pattern} onChange={(event) => {
          const raw = event.target.value;
          if (schema.type === 'number' || schema.type === 'integer') onChange(raw === '' ? undefined : Number(raw));
          else onChange(raw);
        }} disabled={disabled} aria-invalid={Boolean(issue)} aria-describedby={describedBy} className={className} />}
    {schema.description && <p id={`${id}-description`} className="text-[10px] text-slate-text-muted">{metadata?.helpText || schema.description}</p>}
    {issue && <p id={`${id}-error`} role="alert" className="text-[11px] font-medium text-[var(--color-safety-critical)]">{issue.message}</p>}
  </div>;
}

export function DynamicClinicalForm({ contract, initialValues = {}, onChange, onSubmit, onCancel, disabled = false }: DynamicClinicalFormProps) {
  const [values, setValues] = useState<Record<string, unknown>>(initialValues);
  const [issues, setIssues] = useState<FormValidationIssue[]>([]);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const schema = contract.inputSchema;
  const properties = Object.entries(schema.properties || {}).sort(([fieldA], [fieldB]) => (fieldMetadata(contract, fieldA)?.order ?? 0) - (fieldMetadata(contract, fieldB)?.order ?? 0));

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    const result = validateFormValues(schema, values);
    setIssues(result.issues);
    setSubmitError(null);
    if (!result.valid) return;
    try { await onSubmit(values); } catch (error) {
      setSubmitError(error instanceof PluginContractError ? error.message : 'The plugin input could not be submitted.');
    }
  };

  const updateValues = (next: Record<string, unknown>) => {
    setValues(next);
    onChange?.(next);
  };

  return <form onSubmit={submit} noValidate className="space-y-5" aria-describedby={submitError ? 'dynamic-form-error' : undefined}>
    <div>
      <h2 className="text-sm font-semibold text-slate-text-primary">{contract.displayName}</h2>
      {contract.description && <p className="mt-1 text-xs text-slate-text-muted">{contract.description}</p>}
    </div>
    {submitError && <div id="dynamic-form-error"><SafetyAlert level="critical" title="Plugin input unavailable">{submitError}</SafetyAlert></div>}
    {issues.length > 0 && <SafetyAlert level="warning" title="Review required fields">{issues.length} field validation issue(s) must be corrected before submission.</SafetyAlert>}
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      {properties.map(([field, fieldSchema]) => (
        <React.Fragment key={field}>
          <InputField field={field} schema={fieldSchema} value={values[field]} required={(schema.required || []).includes(field)} issue={issues.find((issue) => issue.path === field)} metadata={fieldMetadata(contract, field)} onChange={(value) => updateValues(setValue(values, field, value))} disabled={disabled} />
        </React.Fragment>
      ))}
    </div>
    <div className="flex gap-3">
      <button type="submit" disabled={disabled} className="rounded-[var(--radius-md)] bg-[var(--color-clinical-600)] px-4 py-2 text-xs font-semibold text-white disabled:opacity-60">Submit approved inputs</button>
      {onCancel && <button type="button" onClick={onCancel} disabled={disabled} className="rounded-[var(--radius-md)] border border-slate-border px-4 py-2 text-xs font-semibold text-slate-text-secondary disabled:opacity-60">Cancel</button>}
    </div>
  </form>;
}
