import React from 'react';
import { PluginDefinition, PluginFormField } from '@/plugins/registry/pluginTypes';
import { SafetyAlert } from '@/components/ui/SafetyAlert';

interface PluginGeneratedFormProps {
  plugins: PluginDefinition[];
  caseData: Record<string, any>;
  onChange: (path: string, value: unknown) => void;
}

function readPath(value: Record<string, any>, path: string): unknown {
  return path.split('.').reduce<unknown>((current, key) => (
    current && typeof current === 'object' ? (current as Record<string, unknown>)[key] : undefined
  ), value);
}

function mergeFields(plugins: PluginDefinition[]): Array<PluginFormField & { owners: string[] }> {
  const fields = new Map<string, PluginFormField & { owners: string[] }>();
  plugins.forEach((plugin) => {
    (plugin.formSchema || []).forEach((field) => {
      const existing = fields.get(field.path);
      if (existing) {
        existing.owners.push(plugin.name);
      } else {
        fields.set(field.path, { ...field, owners: [plugin.name] });
      }
    });
  });
  return Array.from(fields.values());
}

export function PluginGeneratedForm({ plugins, caseData, onChange }: PluginGeneratedFormProps) {
  const fields = mergeFields(plugins);

  if (fields.length === 0) {
    return (
      <SafetyAlert level="warning" title="Clinical input schema unavailable">
        The selected plugins did not expose a clinical input schema. Choose a plugin with a declared form schema before continuing.
      </SafetyAlert>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-[var(--radius-md)] border border-[var(--color-clinical-800)] bg-[var(--color-clinical-950)]/60 p-4">
        <p className="text-xs font-semibold text-[var(--color-clinical-100)]">Plugin-generated clinical inputs</p>
        <p className="mt-1 text-[11px] leading-relaxed text-[var(--color-clinical-300)]">
          These fields come from the schemas exposed by the active knowledge and prediction plugins. Shared inputs are shown once and sent to the decision engine as one clinical case.
        </p>
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {fields.map((field) => {
          const value = readPath(caseData, field.path);
          const fieldId = `plugin-field-${field.path.replace(/\./g, '-')}`;
          const commonClass = 'w-full rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset px-3 py-2 text-xs text-slate-text-primary focus-clinical';

          return (
            <div key={field.path} className={field.type === 'textarea' ? 'md:col-span-2' : ''}>
              {field.type === 'checkbox' ? (
                <label htmlFor={fieldId} className="flex cursor-pointer items-center gap-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3 text-xs font-semibold text-slate-text-primary">
                  <input id={fieldId} type="checkbox" checked={Boolean(value)} onChange={(event) => onChange(field.path, event.target.checked)} className="h-4 w-4 rounded text-[var(--color-clinical-500)]" />
                  <span>{field.label}</span>
                </label>
              ) : (
                <>
                  <label htmlFor={fieldId} className="mb-1 block text-xs font-semibold text-slate-text-secondary">
                    {field.label} {field.required && <span className="text-[var(--color-safety-critical)]">*</span>}
                  </label>
                  {field.type === 'select' ? (
                    <select id={fieldId} value={String(value ?? '')} onChange={(event) => onChange(field.path, event.target.value)} className={commonClass}>
                      <option value="">Select...</option>
                      {(field.options || []).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                    </select>
                  ) : field.type === 'textarea' ? (
                    <textarea id={fieldId} rows={3} value={String(value ?? '')} placeholder={field.placeholder} onChange={(event) => onChange(field.path, event.target.value)} className={commonClass} />
                  ) : (
                    <input id={fieldId} type={field.type} step={field.step} value={String(value ?? '')} placeholder={field.placeholder} onChange={(event) => onChange(field.path, field.type === 'number' ? (event.target.value ? Number(event.target.value) : undefined) : event.target.value)} className={commonClass} />
                  )}
                  {field.helpText && <p className="mt-1 text-[10px] text-slate-text-muted">{field.helpText}</p>}
                </>
              )}
              <p className="mt-1 text-[10px] text-slate-text-muted">Provided by {field.owners.join(' and ')}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}