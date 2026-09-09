import React, { useMemo, useState } from 'react';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { DynamicClinicalForm } from '@/forms/engine/DynamicClinicalForm';
import {
  SOAR_DEPLOYMENT_CONTRACTS,
  resolveSoarDeploymentContract,
  toSoarPluginContract,
} from './soarDeploymentContract';
import type { SoarInputResolution } from './soarInputResolver';
import { resolveSoarInputs as resolveInputs, buildSoarExecutionPayload } from './soarInputResolver';
import type { JsonSchema, PluginInputContract } from './types';

interface SoarClinicalCompletionFormProps {
  canonicalClinicalData?: Record<string, unknown>;
  onResolved: (payload: ReturnType<typeof buildSoarExecutionPayload>, resolution: SoarInputResolution) => void;
}

const labels: Record<string, string> = {
  Age: 'Age (years)',
  YearCollected: 'Year collected',
  Region: 'Region',
  BodyLocation_Group: 'Body location group',
  Country: 'Country',
  BetaLactamaseStatus: 'Beta-lactamase status',
};

function contractForMissingFields(contract: ReturnType<typeof resolveSoarDeploymentContract>, missing: string[]): PluginInputContract {
  const pluginContract = toSoarPluginContract(contract);
  const fields = contract.requiredInputs.filter((field) => missing.includes(field.key));
  const properties: Record<string, JsonSchema> = {};
  fields.forEach((field) => {
    const formKey = field.clinicalKey || field.key;
    const schema = field.clinicalKey
      ? { type: 'string' as const, title: labels[formKey], enum: ['POSITIVE', 'NEGATIVE'] }
      : pluginContract.inputSchema.properties?.[field.key];
    if (schema) properties[formKey] = schema;
  });
  return {
    ...pluginContract,
    inputSchema: { ...pluginContract.inputSchema, properties, required: fields.map((field) => field.clinicalKey || field.key) },
    uiSchema: {
      fields: fields.map((field, index) => ({
        field: field.clinicalKey || field.key,
        label: labels[field.clinicalKey || field.key] || field.key,
        order: index + 1,
        widget: field.clinicalKey || pluginContract.inputSchema.properties?.[field.key]?.enum ? 'select' : 'number',
      })),
    },
    requiredFields: fields.map((field) => field.clinicalKey || field.key),
  };
}

export function SoarClinicalCompletionForm({ canonicalClinicalData = {}, onResolved }: SoarClinicalCompletionFormProps) {
  const [deploymentId, setDeploymentId] = useState('');
  const [submitError, setSubmitError] = useState<string | null>(null);

  const selectedContract = deploymentId ? resolveSoarDeploymentContract(deploymentId) : undefined;
  const initialResolution = selectedContract
    ? resolveInputs({ deploymentId, canonicalClinicalData })
    : undefined;
  const blocked = selectedContract?.requiredInputs.some((field) => field.sourceClassification === 'UNKNOWN') === true;
  const formContract = useMemo(() => {
    if (!selectedContract || !initialResolution || blocked) return undefined;
    return contractForMissingFields(selectedContract, initialResolution.missingRequiredInputs.map((item) => item.field));
  }, [blocked, initialResolution, selectedContract]);

  const submit = (clinicianEntered: Record<string, unknown>) => {
    if (!selectedContract) return;
    try {
      const resolution = resolveInputs({ deploymentId, canonicalClinicalData, clinicianEntered });
      const payload = buildSoarExecutionPayload(resolution, selectedContract);
      setSubmitError(null);
      onResolved(payload, resolution);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'SOAR input validation failed.');
    }
  };

  return (
    <section className="space-y-4 rounded-[var(--radius-md)] border border-[var(--color-clinical-800)] bg-[var(--color-clinical-950)]/30 p-4" aria-labelledby="soar-completion-title">
      <div>
        <h3 id="soar-completion-title" className="text-sm font-semibold text-slate-text-primary">SOAR deployment input completion</h3>
        <p className="mt-1 text-xs text-slate-text-muted">Select an exact verified deployment. The form will request only missing contract inputs.</p>
      </div>
      <div>
        <label htmlFor="soar-deployment" className="block text-xs font-semibold text-slate-text-secondary">Verified SOAR deployment</label>
        <select id="soar-deployment" value={deploymentId} onChange={(event) => { setDeploymentId(event.target.value); setSubmitError(null); }} className="mt-1 w-full rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset px-3 py-2 text-xs text-slate-text-primary focus-clinical">
          <option value="">Select a deployment...</option>
          {SOAR_DEPLOYMENT_CONTRACTS.map((contract) => <option key={contract.deploymentId} value={contract.deploymentId}>{contract.antimicrobial} / {contract.organism}</option>)}
        </select>
      </div>
      {selectedContract && (
        <div className="space-y-3">
          <dl className="grid grid-cols-1 gap-2 text-xs md:grid-cols-2">
            <div><dt className="font-semibold text-slate-text-muted">Organism</dt><dd className="text-slate-text-primary">{selectedContract.organism}</dd></div>
            <div><dt className="font-semibold text-slate-text-muted">Antimicrobial</dt><dd className="text-slate-text-primary">{selectedContract.antimicrobial}</dd></div>
          </dl>
          {blocked ? (
            <SafetyAlert level="warning" title="SOAR deployment unavailable">
              This deployment requires Beta-lactamase status, but the repository does not verify the clinical-to-numeric encoding. No value will be invented and execution is blocked.
            </SafetyAlert>
          ) : formContract && formContract.requiredFields && formContract.requiredFields.length > 0 ? (
            <DynamicClinicalForm contract={formContract} initialValues={initialResolution?.resolvedInputs} onSubmit={submit} />
          ) : (
            <SafetyAlert level="info" title="SOAR inputs resolved">All required inputs are already available from approved exact sources.</SafetyAlert>
          )}
          {submitError && <SafetyAlert level="critical" title="SOAR input unavailable">{submitError}</SafetyAlert>}
        </div>
      )}
    </section>
  );
}
