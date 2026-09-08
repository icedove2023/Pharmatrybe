import { pluginContractRegistry } from './registry';
import type { PluginInputContract } from './types';

export const ARMD_CLINICAL_CONTRACT: PluginInputContract = {
  pluginId: 'armd',
  contractId: 'armd-direct-clinical-inputs',
  contractVersion: '1.0.0',
  schemaVersion: '2020-12',
  displayName: 'ARMD resistance-risk inputs',
  description: 'Direct clinical measurements shared by the canonical case and the ARMD runtime. Backend preprocessing remains authoritative.',
  status: 'approved',
  provenance: {
    owner: 'PharmaTrybe clinical case contract and ARMD runtime',
    source: 'Frozen ARMD runtime contract and official Clinical Case Schema',
    artifact: 'docs/contracts/ARMD_RUNTIME_CONTRACT_v1.0.0.md; packages/clinical-schemas/clinical-case.schema.md; apps/api/app/plugins/prediction/armd/armd_prediction_plugin.py',
    artifactVersion: '1.0.0',
    approvedBy: 'Phase 22 repository evidence admission decision',
    approvedAt: '2026-09-06T00:00:00Z',
  },
  inputSchema: {
    $schema: 'https://json-schema.org/draft/2020-12/schema',
    type: 'object',
    properties: {
      age: { type: 'integer', minimum: 0, maximum: 120, title: 'Age', description: 'Patient age in years.' },
      temperature: { type: 'number', title: 'Temperature', description: 'Recorded temperature in the unit used by the clinical case.' },
      creatinine: { type: 'number', minimum: 0, title: 'Creatinine', description: 'Recorded serum creatinine.' },
      bun: { type: 'number', minimum: 0, title: 'BUN', description: 'Recorded blood urea nitrogen.' },
      wbc: { type: 'number', minimum: 0, title: 'White blood cell count', description: 'Recorded white blood cell count.' },
      neutrophils: { type: 'number', minimum: 0, title: 'Neutrophils', description: 'Recorded neutrophil measurement.' },
      lymphocytes: { type: 'number', minimum: 0, title: 'Lymphocytes', description: 'Recorded lymphocyte measurement.' },
      lactate: { type: 'number', minimum: 0, title: 'Lactate', description: 'Recorded lactate measurement.' },
      procalcitonin: { type: 'number', minimum: 0, title: 'Procalcitonin', description: 'Recorded procalcitonin measurement.' },
    },
    required: ['age'],
    additionalProperties: false,
  },
  uiSchema: {
    fields: [
      { field: 'age', widget: 'number', order: 1 },
      { field: 'temperature', widget: 'number', order: 2 },
      { field: 'creatinine', widget: 'number', order: 3 },
      { field: 'bun', widget: 'number', order: 4 },
      { field: 'wbc', widget: 'number', order: 5 },
      { field: 'neutrophils', widget: 'number', order: 6 },
      { field: 'lymphocytes', widget: 'number', order: 7 },
      { field: 'lactate', widget: 'number', order: 8 },
      { field: 'procalcitonin', widget: 'number', order: 9 },
    ],
  },
  requiredFields: ['age'],
  supportedExecutionMode: 'sync',
};

export function ensureArmdClinicalContractRegistered(): PluginInputContract {
  pluginContractRegistry.registerIfAbsent(ARMD_CLINICAL_CONTRACT);
  return pluginContractRegistry.resolve('armd', '1.0.0');
}
