import React from 'react';
import { PluginDefinition } from '@/plugins/registry/pluginTypes';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { DynamicClinicalForm } from '@/forms/engine/DynamicClinicalForm';
import { ensureArmdClinicalContractRegistered } from '@/plugins/contracts';
import { SoarClinicalCompletionForm } from '@/plugins/contracts';
import type { SoarInputResolution } from '@/plugins/contracts';
import type { buildSoarExecutionPayload } from '@/plugins/contracts';
import type { ClinicalCase } from '@/types';

interface PluginGeneratedFormProps {
  plugins: PluginDefinition[];
  caseData: ClinicalCase;
  onChange: (path: string, value: unknown) => void;
  onSoarResolved?: (payload: ReturnType<typeof buildSoarExecutionPayload>, resolution: SoarInputResolution) => void;
}

export function PluginGeneratedForm({ plugins, caseData, onChange, onSoarResolved }: PluginGeneratedFormProps) {
  const hasArmd = plugins.some((plugin) => plugin.backendId === 'armd' || plugin.id === 'armd' || plugin.id === 'armd_prediction');
  const hasSoar = plugins.some((plugin) => plugin.backendId === 'soar' || plugin.id === 'soar' || plugin.id === 'soar_prediction');
  if (hasArmd) {
    const contract = ensureArmdClinicalContractRegistered();
    const initialValues = {
      age: caseData.demographics.age,
      temperature: caseData.presentation.vitals.temperature,
      creatinine: caseData.laboratory.creatinine,
      bun: undefined,
      wbc: caseData.laboratory.wbc,
      neutrophils: undefined,
      lymphocytes: undefined,
      lactate: undefined,
      procalcitonin: caseData.laboratory.procalcitonin,
    };
    const updateCase = (values: Record<string, unknown>) => {
      onChange('demographics.age', values.age);
      onChange('presentation.vitals.temperature', values.temperature);
      onChange('laboratory.creatinine', values.creatinine);
      onChange('laboratory.wbc', values.wbc);
      onChange('laboratory.procalcitonin', values.procalcitonin);
    };

    return <div className="space-y-5">
      <DynamicClinicalForm contract={contract} initialValues={initialValues} onChange={updateCase} onSubmit={() => undefined} />
      {hasSoar && <SoarClinicalCompletionForm canonicalClinicalData={{}} onResolved={onSoarResolved || (() => undefined)} />}
    </div>;
  }

  if (hasSoar) {
    return <SoarClinicalCompletionForm canonicalClinicalData={{}} onResolved={onSoarResolved || (() => undefined)} />;
  }

  void plugins;

  return (
    <SafetyAlert level="warning" title="Approved clinical input contract unavailable">
      No approved, versioned, frontend-visible plugin input contract is registered for the selected plugins. Legacy presentation fields are intentionally not rendered as clinical inputs.
    </SafetyAlert>
  );
}